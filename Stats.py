# meta developer: @xdesai

from .. import loader, utils
from telethon.tl.functions.contacts import GetBlockedRequest


@loader.tds
class Stats(loader.Module):

    strings = {
        "name": "Stats",
        "stats": """


    }

    strings_ru = {
        "name": "Stats",
        "stats": """


    }

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command()
    async def stats(self, message):
        await utils.answer(message, self.strings["loading_stats"])
        users = 0
        bots = 0
        groups = 0
        channels = 0
        all_chats = 0
        archived = 0
        blocked_bots = 0
        blocked_users = 0

        limit = 100
        offset = 0
        total_blocked = 0
        while True:
            blocked_chats = await self._client(
                GetBlockedRequest(offset=offset, limit=limit)
            )
            for user in blocked_chats.users:
                if user.bot:
                    blocked_bots += 1
                else:
                    blocked_users += 1
            blocked = len(blocked_chats.users)
            total_blocked += blocked

            if blocked < limit:
                break

            offset += limit

        async for dialog in self._client.iter_dialogs():
            if getattr(dialog, "archived", False):
                archived += 1
            if dialog.is_user:
                if getattr(dialog.entity, "bot", False):
                    bots += 1
                    all_chats += 1
                else:
                    users += 1
                    all_chats += 1
            elif getattr(dialog, "is_group", False):
                groups += 1
                all_chats += 1
            elif dialog.is_channel:
                if getattr(dialog.entity, "megagroup", False) or getattr(
                    dialog.entity, "gigagroup", False
                ):
                    groups += 1
                    all_chats += 1
                elif getattr(dialog.entity, "broadcast", False):
                    channels += 1
                    all_chats += 1

        await utils.answer(
            message,
            self.strings["stats"].format(
                users=users,
                bots=bots,
                channels=channels,
                groups=groups,
                all_chats=all_chats,
                blocked=total_blocked,
                archived=archived,
                blocked_users=blocked_users,
                blocked_bots=blocked_bots,
            ),
        )