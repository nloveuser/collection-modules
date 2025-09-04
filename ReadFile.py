# Copyright 2025, werpyock
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__version__ = (1, 0, 9)
# meta developer: @wmodules
import os
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class ReadFileMod(loader.Module):

    strings = {"name": "ReadFile"}

    def __init__(self):
        self.chunks = []
        self.file_info = {}
        self.file_content = ""
        self.file_path = ""

    async def rfcmd(self, message: Message):
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            return

        self.file_path = await reply.download_media()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.file_content = f.read()
        except Exception as e:
            return

        self.chunks = self._split_text(self.file_content, 1500)
        self.file_info = {
            "Имя": os.path.basename(self.file_path),
            "Размер": f"{os.path.getsize(self.file_path)} байт",
        }

        await self._show_page(message, 0)

    def _split_text(self, text, size):
        return [text[i:i + size] for i in range(0, len(text), size)]

    async def _show_page(self, msg_or_call, index):
        total = len(self.chunks)
        index = max(0, min(index, total - 1))
        buttons = [
            [
                {"text": "⬅️", "callback": self._page_cb, "args": (index - 1,)},
                {"text": "➡️", "callback": self._page_cb, "args": (index + 1,)}
            ],
            [
            ]
        ]

        if isinstance(msg_or_call, Message):
            await self.inline.form(text=text, message=msg_or_call, reply_markup=buttons)
        elif hasattr(msg_or_call, "edit"):
            await msg_or_call.edit(text=text, reply_markup=buttons)

    async def _page_cb(self, call, index):
        await self._show_page(call, index)

    async def _info_cb(self, call, return_index):
        info_text = "\n".join([f"<b>{k}:</b> {utils.escape_html(str(v))}" for k, v in self.file_info.items()])
        await call.edit(
            reply_markup=[
                [{"text": "↩️ Назад", "callback": self._page_cb, "args": (return_index,)}]
            ]
      )