# чатгпт кормит, больные мозги тоже
#
# meta developer: @HikkaZPM
#
# The module is made as a joke, all coincidences are random :P
#
#       кот вахуи
#       /\_____/\
#      /  o   o  \
#     ( ==  ^  == )
#      )         (
#     (           )
#    ( (  )   (  ) )
#   (__(__)___(__)__)
#
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class SSend(loader.Module):

    strings = {
        "name": "SSend",
    }

    @loader.command(ru_doc="Отправить текст с эмодзи")
    async def send(self, message: Message):
        """Отправить текст с эмодзи"""
        args = utils.get_args_raw(message)

        if not args:
            await message.edit(self.strings["error"])
        else:
            await message.delete()
            await message.client.send_message(
                message.to_id,
                args
            )