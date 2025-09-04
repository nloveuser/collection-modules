# meta developer: @kotcheat

import secrets
from telethon.tl.types import Message
from .. import loader, utils
from ..inline.types import InlineCall

@loader.tds
class KOTbanvote(loader.Module):
    
    Как использовать:
    Пример: .vote @user 5 !ban

    strings = {
        "name": "KOTbanvote",
        "vote_count": "Проголосовали: {}/{}\n{}",
    }

    async def client_ready(self, client, db):
        self._client = client
        self._votes = {}

    async def votecmd(self, message: Message):
        args = utils.get_args(message)
        if len(args) < 3:
            return

        user = args[0]
        try:
            vote_count = int(args[1])
            if vote_count < 1 or vote_count > 100:
                raise ValueError
        except ValueError:
            await message.reply(self.strings("invalid_count"))
            return

        command = " ".join(args[2:])
        if not command:
            await message.reply(self.strings("invalid_command"))
            return

        uid = secrets.token_hex(8)
        self._votes[uid] = {
            "user": user,
            "voters": set(),
            "voter_names": [],
            "chat_id": message.chat_id,
            "vote_count": vote_count,
            "command": command
        }

        await self.inline.form(
            self.strings("vote_start").format(user, vote_count),
            message=message,
            reply_markup=[
                [{"text": "🔨 Голосовать", "callback": self.inline__vote, "args": (uid,)},
            ],
            ttl=10 * 60,
            disable_security=True,
        )

    async def inline__vote(self, call: InlineCall, uid: str):
        vote = self._votes.get(uid)
        if not vote:
            await call.answer(self.strings("vote_cancelled"))
            return

        user_id = call.from_user.id
        user_name = call.from_user.first_name

        if user_id in vote["voters"]:
            await call.answer(self.strings("already_voted"))
            return

        vote["voters"].add(user_id)
        vote["voter_names"].append(user_name)
        count = len(vote["voters"])

        if count >= vote["vote_count"]:
            user = vote["user"]
            chat_id = vote["chat_id"]
            command = vote["command"]
            await self._client.send_message(chat_id, f"{command} {user}")
            await call.edit(self.strings("ban_success").format(user), reply_markup=None)
            del self._votes[uid]
        else:
            await call.edit(
                self.strings("vote_start").format(vote["user"], vote["vote_count"]) +
                f"\n\n{self.strings('vote_count').format(count, vote['vote_count'], ', '.join(vote['voter_names']))}",
                reply_markup=[
                    [{"text": "🔨 Голосовать", "callback": self.inline__vote, "args": (uid,)},
                ],
            )

    async def inline__remove_vote(self, call: InlineCall, uid: str):
        vote = self._votes.get(uid)
        if not vote:
            await call.answer(self.strings("vote_cancelled"))
            return

        user_id = call.from_user.id
        user_name = call.from_user.first_name

        if user_id in vote["voters"]:
            vote["voters"].remove(user_id)
            vote["voter_names"].remove(user_name)
            await call.answer(self.strings("vote_removed"))
        else:

        count = len(vote["voters"])
        await call.edit(
            self.strings("vote_start").format(vote["user"], vote["vote_count"]) +
                f"\n\n{self.strings('vote_count').format(count, vote['vote_count'], ', '.join(vote['voter_names']))}",
            reply_markup=[
                [{"text": "🔨 Голосовать", "callback": self.inline__vote, "args": (uid,)},
            ],
        )