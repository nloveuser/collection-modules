from .. import loader, utils

class DelmeMod(loader.Module):
    strings = {'name': 'DelMe'}
    @loader.sudo
    async def delmecmd(self, message):
        chat = message.chat
        if chat:
            args = utils.get_args_raw(message)
            if args != str(message.chat.id+message.sender_id):
                return
            await delete(chat, message, True)
        else:
    @loader.sudo
    async def delmenowcmd(self, message):
        chat = message.chat
        if chat:
            await delete(chat, message, False)
        else:

async def delete(chat, message, now):
    if now:
        all = (await message.client.get_messages(chat, from_user="me")).total
    else: await message.delete()
    _ = not now
    async for msg in message.client.iter_messages(chat, from_user="me"):
        if _:
            await msg.delete()
        else:
            _ = "_"