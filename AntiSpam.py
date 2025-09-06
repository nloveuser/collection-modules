from hikka import loader, utils
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from datetime import datetime, timedelta

@loader.tds
class AntiSpamMod(loader.Module):
    
    strings = {"name": "AntiSpam"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "log_chat", None, "ID чата для логов",
            "spam_period", 300, "Время (сек) для спама",
        )
        self.spam_data = {}
        self.local_logs = []
        self.last_violator = None
        self.violators = 0
        self.enabled_chats = set()

    async def client_ready(self, client, db):
        self.client = client

    async def is_admin(self, chat_id, user_id):
        try:
            participant = await self.client(GetParticipantRequest(chat_id, user_id))
            part = participant.participant
            return getattr(part, "admin_rights", None) is not None or getattr(part, "rank", None)
        except Exception:
            return False

    async def watcher(self, event):
        chat_id = getattr(event, "chat_id", None)
        if not getattr(event, "is_group", False) or not getattr(event, "sender_id", None) or chat_id not in self.enabled_chats:
            return
        user_id = event.sender_id
        try:
            user = await event.get_sender()
        except Exception:
            return
        text = getattr(event, "message", "") or ""
        now = datetime.now()
        user_data = self.spam_data.get((chat_id, user_id), {"messages": []})
        user_data["messages"].append((now, text, getattr(event, "id", None)))
        self.spam_data[(chat_id, user_id)] = user_data
        period = max(self.config["spam_period"], self.config["flood_period"])
        user_data["messages"] = [(t, tx, mid) for t, tx, mid in user_data["messages"] if (now - t).seconds <= period]
        if len(user_data["messages"]) >= self.config["spam_trigger"]:
            last_msgs = user_data["messages"][-self.config["spam_trigger"]:]
            if len(set(tx for _, tx, _ in last_msgs)) == 1:
                ids = [mid for _, _, mid in last_msgs if mid]
                await self.punish(chat_id, user, text, ids, "СПАМ")
        if len(user_data["messages"]) >= self.config["flood_trigger"]:
            last_msgs = user_data["messages"][-self.config["flood_trigger"]:]
            if (now - last_msgs[0][0]).seconds <= self.config["flood_period"]:
                ids = [mid for _, _, mid in last_msgs if mid]
                await self.punish(chat_id, user, text, ids, "ФЛУД")

    async def punish(self, chat_id, user, text, ids_to_delete, reason):
        user_id = user.id
        now = datetime.now()
        punishment_type = self.config["punish_type"].lower()
        is_admin = await self.is_admin(chat_id, user_id)
        until_time = None
        rights = None
        if not is_admin:
            if ids_to_delete:
                await self.client.delete_messages(chat_id, ids_to_delete)
            if punishment_type == "mute":
                until_time = now + timedelta(hours=self.config["mute_hours"])
                rights = ChatBannedRights(until_date=until_time, send_messages=True)
            elif punishment_type == "ban":
                until_time = now + timedelta(hours=self.config["ban_hours"])
                rights = ChatBannedRights(until_date=until_time, view_messages=True)
            if rights:
                try:
                    await self.client(EditBannedRequest(chat_id, user_id, rights))
                    self.violators += 1
                    self.last_violator = (user_id, user.first_name, until_time)
                except Exception:
                    pass
            if ids_to_delete:
            if until_time:
                msg += f"\n⏰ До: {until_time.strftime('%Y-%m-%d %H:%M:%S')}"
            try:
                await self.client.send_message(chat_id, msg)
            except Exception:
                pass
        if ids_to_delete and not is_admin:
        if punishment_type in ["mute", "ban"] and not is_admin and until_time:
        elif punishment_type == "warn" and not is_admin:
        if is_admin:
        if text:
        if self.config["log_chat"]:
            try:
                await self.client.send_message(self.config["log_chat"], log)
            except Exception:
                self.local_logs.append((datetime.now(), log))
        else:
            self.local_logs.append((datetime.now(), log))
        if len(self.local_logs) > 20:
            self.local_logs.pop(0)

    @loader.unrestricted
    async def antispamtogglecmd(self, message):
        chat_id = message.chat_id
        if chat_id in self.enabled_chats:
            self.enabled_chats.remove(chat_id)
        else:
            self.enabled_chats.add(chat_id)

    @loader.unrestricted
    async def antispamcheckcmd(self, message):
        args = utils.get_args_raw(message)
        if args:
            try:
                user = await self.client.get_entity(args)
            except Exception:
                return
        elif message.is_reply:
            reply = await message.get_reply_message()
            user = await reply.get_sender()
        else:
            return
        uid = user.id
        chat_id = message.chat_id
        if self.last_violator and self.last_violator[0] == uid:
            _, name, until_time = self.last_violator
            return
        try:
            part = await self.client(GetParticipantRequest(chat_id, uid))
            rights = getattr(part.participant, "banned_rights", None)
            if rights and rights.until_date and rights.until_date > datetime.now():
                return
        except Exception:
            pass

    @loader.unrestricted
    async def antispamstatuscmd(self, message):
        if self.last_violator:
            uid, name, until_time = self.last_violator
        else:
        await utils.answer(message, text)

    @loader.unrestricted
    async def antispamlogscmd(self, message):
        logs = self.local_logs[-10:]
        if not logs:
            return
        for t, log in logs:
            text += f"[{t.strftime('%H:%M:%S')}] {log}\n\n"
        await utils.answer(message, text)

    @loader.owner
    async def setantispamcfgcmd(self, message):
        args = utils.get_args(message)
        if len(args) < 2:
            return
        key, value = args[0], " ".join(args[1:])
        if key not in self.config:
            return
        try:
            if isinstance(self.config[key], int):
                value = int(value)
            elif isinstance(self.config[key], float):
                value = float(value)
        except Exception:
            pass
        self.config[key] = value