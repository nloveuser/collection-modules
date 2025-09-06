from hikka import loader, utils
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator
from datetime import datetime, timedelta


@loader.tds
class AntiSpamMod(loader.Module):
    """
    strings = {"name": "AntiSpaming"}

    def __init__(self):
        self.config = loader.ModuleConfig(
        )
        self.violators = 0
        self.last_violator = None
        self.enabled_chats = set()

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.spam_data = {}

    async def is_admin(self, chat_id, user_id):
        try:
            participant = await self.client(GetParticipantRequest(chat_id, user_id))
            return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
        except Exception:
            return False

    async def punish(self, chat_id, user, text, ids_to_delete, reason):
        user_id = user.id
        now = datetime.now()

        if ids_to_delete:
            await self.client.delete_messages(chat_id, ids_to_delete)

        punishment_type = self.config["punish_type"].lower()
        is_admin = await self.is_admin(chat_id, user_id)

        if not is_admin:
            until_time = None
            rights = None
            if punishment_type == "mute":
                until_time = now + timedelta(hours=self.config["mute_hours"])
                rights = ChatBannedRights(until_date=until_time, send_messages=True)
            elif punishment_type == "ban":
                until_time = now + timedelta(hours=self.config["ban_hours"])
                rights = ChatBannedRights(until_date=until_time, view_messages=True)
            elif punishment_type == "warn":
                until_time = None
                rights = None

            if rights:
                try:
                    await self.client(EditBannedRequest(chat_id, user_id, rights))
                    self.violators += 1
                    self.last_violator = (user_id, user.first_name, until_time)
                except Exception:
                    pass

            if ids_to_delete:
            if punishment_type != "warn":
                message_text += f"\n⏰ До: {until_time.strftime('%Y-%m-%d %H:%M:%S')}" if until_time else ""
            await utils.answer(message=None, message_text=message_text)

        if self.config["log_chat"]:
            if punishment_type in ["mute", "ban"] and not is_admin:
            elif punishment_type == "warn":
            if is_admin:
            if text:
            await self.client.send_message(self.config["log_chat"], log_text)

    async def watcher(self, message):
        if not message or not getattr(message, "chat_id", None):
            return

        chat_id = message.chat_id
        if chat_id not in self.enabled_chats:
            return

        try:
            user = await message.get_sender()
        except AttributeError:
            if hasattr(message, "sender_id") and message.sender_id:
                user = await self.client.get_entity(message.sender_id)
            else:
                return

        if not user or getattr(user, "bot", False):
            return

        user_id = user.id
        text = getattr(message, "raw_text", "") or ""
        now = datetime.now()

        if chat_id not in self.spam_data:
            self.spam_data[chat_id] = {}
        if user_id not in self.spam_data[chat_id]:
            self.spam_data[chat_id][user_id] = []

        self.spam_data[chat_id][user_id].append((text, now, message.id))

        interval = max(self.config["spam_interval"], self.config["flood_interval"])
        self.spam_data[chat_id][user_id] = [
            (t, ts, mid) for t, ts, mid in self.spam_data[chat_id][user_id]
            if now - ts <= timedelta(seconds=interval)
        ]

        spam_msgs = {}
        for t, ts, mid in self.spam_data[chat_id][user_id]:
            spam_msgs[t] = spam_msgs.get(t, []) + [mid]

        for msg_text, mids in spam_msgs.items():
            if len(mids) >= self.config["spam_count"]:
                self.spam_data[chat_id][user_id] = [
                    (t, ts, mid) for t, ts, mid in self.spam_data[chat_id][user_id] if mid not in mids
                ]
                return

        msgs_last_interval = [
            mid for _, ts, mid in self.spam_data[chat_id][user_id]
            if now - ts <= timedelta(seconds=self.config["flood_interval"])
        ]
        if len(msgs_last_interval) > self.config["flood_limit"]:
            await self.punish(
                chat_id,
                user,
                None,
                msgs_last_interval,
            )
            self.spam_data[chat_id][user_id] = []

    @loader.unrestricted
    async def antispamstatuscmd(self, message):
        log_chat = self.config["log_chat"]
        if self.config['punish_type'] == 'mute':
        elif self.config['punish_type'] == 'ban':
        if self.last_violator:
            uid, name, until = self.last_violator
        else:

        chat_id = message.chat_id

        await utils.answer(message, text)

    @loader.unrestricted
    async def antispamtogglecmd(self, message):
        chat_id = message.chat_id
        if chat_id in self.enabled_chats:
            self.enabled_chats.remove(chat_id)
        else:
            self.enabled_chats.add(chat_id)