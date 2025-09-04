# Proprietary License Agreement

# Copyright (c) 2024-29 CodWiz

# Permission is hereby granted to any person obtaining a copy of this software and associated documentation files (the "Software"), to use the Software for personal and non-commercial purposes, subject to the following conditions:

# 1. The Software may not be modified, altered, or otherwise changed in any way without the explicit written permission of the author.

# 2. Redistribution of the Software, in original or modified form, is strictly prohibited without the explicit written permission of the author.

# 3. The Software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the author or copyright holder be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Software or the use or other dealings in the Software.

# 4. Any use of the Software must include the above copyright notice and this permission notice in all copies or substantial portions of the Software.

# 5. By using the Software, you agree to be bound by the terms and conditions of this license.

# For any inquiries or requests for permissions, please contact codwiz@yandex.ru.

# ---------------------------------------------------------------------------------
# Name: HAFK
# Description: Your personal assistant while you are in AFK mode
# Author: @hikka_mods
# ---------------------------------------------------------------------------------
# meta developer: @hikka_mods
# scope: HAFK
# scope: HAFK 0.0.1
# --------------------------------------------------------------------------------

import datetime
import logging
import time
import asyncio

from telethon import types
from telethon.utils import get_peer_id

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class HAFK(loader.Module):
    strings = {
        "name": "HAFK",
        "afk_set_failed": "<b>Failed to set AFK status. Check logs.</b>",
        "added_excluded_chat": "<b>Chat {} added to excluded chats.</b>",
        "removed_excluded_chat": "<b>Chat {} removed from excluded chats.</b>",
        "excluded_chats_list": "<b>Excluded chats:</b>\n{}",
        "no_excluded_chats": "<b>No chats are excluded.</b>",
        "invalid_chat_id": "<b>Invalid chat ID.</b>",
        "already_excluded": "<b>Chat {} is already excluded.</b>",
        "not_excluded": "<b>Chat {} is not excluded.</b>",
    }

    strings_ru = {
    }

    DEFAULT_AFK_TIMEOUT = 60
    DEFAULT_DELETE_TIMEOUT = 5

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "excluded_chats",
                [],
                lambda: "List of chat IDs where AFK mode will not be activated",
                validator=loader.validators.Series(
                    validator=loader.validators.Integer()
                ),
            )
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._me = await client.get_me()
        self._ratelimit_cache = {}

        self.global_afk = self.db.get(__name__, "afk", False)
        self.global_afk_reason = self.db.get(__name__, "afk_reason", None)
        self.global_gone_time = self.db.get(__name__, "gone_afk", None)

        logger.debug(
            f"Initial global AFK state: afk={self.global_afk}, reason={self.global_afk_reason}, gone_time={self.global_gone_time}"
        )

    @loader.command(
        en_doc="[reason / none] – Set AFK mode globally",
    )
    async def afk(self, message):
        await self._afk_toggle(message, global_afk=True)

    @loader.command(
        en_doc="[reason / none] – Set AFK mode in current chat only.",
    )
    async def afkhere(self, message):
        await self._afk_toggle(message, global_afk=False)

    async def _afk_toggle(self, message, global_afk: bool):
        chat_id = utils.get_chat_id(message)
        db_key = "afk" if global_afk else f"afk_here_{chat_id}"
        already_afk_string = "already_afk" if global_afk else "already_afk_here"
        afk_on_string = "afk_on" if global_afk else "afk_here_on"
        afk_on_reason_string = "afk_on_reason" if global_afk else "afk_here_on_reason"

        if self._is_afk_enabled(chat_id, global_afk):
            await utils.answer(message, self.strings(already_afk_string, message))
            return

        reason = utils.get_args_raw(message) or None
        success = self._set_afk(
            True, reason=reason, chat_id=chat_id if not global_afk else None
        )

        if not success:
            await utils.answer(message, self.strings("afk_set_failed", message))
            return

        await utils.answer(
            message,
            self.strings(afk_on_reason_string, message).format(reason)
            if reason
            else self.strings(afk_on_string, message),
        )

    @loader.command(
        en_doc="Exit AFK mode",
    )
    async def unafk(self, message):
        await self._unafk_toggle(message, global_afk=True)

    @loader.command(
        en_doc="Exit AFK mode in this chat",
    )
    async def unafkhere(self, message):
        await self._unafk_toggle(message, global_afk=False)

    async def _unafk_toggle(self, message, global_afk: bool):
        chat_id = utils.get_chat_id(message)
        not_afk_string = "not_afk" if global_afk else "not_afk_here"
        afk_off_time_string = "afk_off_time" if global_afk else "afk_off_here_time"

        if not self._is_afk_enabled(chat_id, global_afk):
            await utils.answer(message, self.strings(not_afk_string, message))
            return

        total_gone_time = self._calculate_total_afk_time(
            datetime.datetime.now().replace(microsecond=0),
            chat_id=chat_id if not global_afk else None,
        )

        self._set_afk(False, chat_id=chat_id if not global_afk else None)

        await self.allmodules.log("unafk" if global_afk else "unafkhere")
        await utils.answer(
            message, self.strings(afk_off_time_string, message).format(total_gone_time)
        )

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return

        chat_id = get_peer_id(message.peer_id)
        user_id = getattr(message.to_id, "user_id", None)
        is_mentioned = message.mentioned or user_id == self._me.id
        is_private = isinstance(message.to_id, types.PeerUser)

        if not (is_mentioned or is_private) or chat_id in self.config["excluded_chats"]:
            return

        reason = None
        gone_time = None

        if self._is_afk_enabled(chat_id, False):
            reason = self.db.get(__name__, f"afk_here_{chat_id}_reason", None)
            gone_time = self.db.get(__name__, f"gone_afk_here_{chat_id}", None)
        elif self.global_afk:
            reason = self.global_afk_reason
            gone_time = self.global_gone_time
        else:
            return

        if gone_time is None:
            logger.warning(f"No 'gone' time found for chat {chat_id}. Cannot send AFK.")
            return

        afk_message = await self._send_afk_message(message, reason, gone_time)
        if afk_message:
            await self._delete_message(afk_message, self.DEFAULT_DELETE_TIMEOUT)

    def _set_afk(self, value: bool, reason: str = None, chat_id: int = None) -> bool:
        try:
            key_prefix = f"afk_here_{chat_id}" if chat_id else "afk"
            self.db.set(__name__, key_prefix, value)
            self.db.set(__name__, f"{key_prefix}_reason", reason)

            gone_key = f"gone_{key_prefix}"
            gone_time = time.time() if value else None
            self.db.set(__name__, gone_key, gone_time)
            logger.debug(f"AFK status updated. {gone_key} set to {gone_time}")

            if chat_id is None:
                self.global_afk = value
                self.global_afk_reason = reason
                self.global_gone_time = gone_time
                logger.debug("Updated global AFK vars")

            return True
        except Exception as e:
            logger.exception(f"Error setting AFK status: {e}")
            return False

    def _calculate_total_afk_time(
        self, now: datetime.datetime, chat_id: int = None
    ) -> datetime.timedelta:
        key_prefix = f"afk_here_{chat_id}" if chat_id else "afk"
        gone_time = self.db.get(__name__, f"gone_{key_prefix}")

        if gone_time is None:
            return datetime.timedelta(seconds=0)

        try:
            gone = datetime.datetime.fromtimestamp(gone_time).replace(microsecond=0)
            return now - gone
        except Exception as e:
            logger.error(f"Error calculating AFK time: {e}")
            return datetime.timedelta(seconds=0)

    async def _send_afk_message(self, message, reason, gone_time):
        user = await utils.get_user(message)
        if user.is_self or user.bot or user.verified:
            logger.debug("User is self, bot, or verified. Not sending AFK message.")
            return None

        now = datetime.datetime.now().replace(microsecond=0)
        try:
            gone = datetime.datetime.fromtimestamp(gone_time).replace(microsecond=0)
        except (TypeError, ValueError) as e:
            logger.error(f"Error converting timestamp: {e}")
            return None

        time_string = str(now - gone)
        ret = (
            self.strings("afk_message_reason", message).format(reason, time_string)
            if reason
            else self.strings("afk_message", message).format(time_string)
        )

        try:
            reply = await utils.answer(message, ret, reply_to=message)
            return reply
        except Exception as e:
            logger.exception(f"Error sending AFK message: {e}")
            return None

    def _is_afk_enabled(self, chat_id: int = None, global_afk: bool = False) -> bool:
        return (
            self.global_afk
            if global_afk
            else self.db.get(__name__, f"afk_here_{chat_id}", False)
        )

    async def _delete_message(self, message, delay):
        await asyncio.sleep(delay)
        try:
            await self.client.delete_messages(message.chat_id, message.id)
        except Exception as e:
            logger.exception(f"Error deleting message: {e}")