# meta developer: @Ne_Xomyahok
# meta name: AvatarManager
# meta version: 3.0 самая новая

import os
import asyncio
import re
import aiohttp
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from .. import loader, utils

@loader.tds
class AvatarManagerMod(loader.Module):
    strings = {
        "name": "AvatarManager",
    }
    
    strings_ru = {
        "avatarrem.ru_doc": "<количество> - Удалить аватарки",
        "avatarremall.ru_doc": "- Удалить все аватарки",
    }


    async def client_ready(self, client, db):
        self.client = client

    @loader.command(
    )
    async def avataradd(self, message):
        """<count> <reply to photo / link> - Add avatars"""
        reply = await message.get_reply_message()
        args = utils.get_args(message)

        if not args:
            return await utils.answer(message, self.strings("no_args_count"))

        try:
            count = int(args[0])
            if count <= 0:
                return await utils.answer(message, self.strings("invalid_count"))
        except (ValueError, IndexError):
            return await utils.answer(message, self.strings("invalid_count"))

        temp_file = "temp_avatar.jpg"
        
        source_found = False
        if reply and reply.photo:
            await self.client.download_media(reply.photo, temp_file)
            source_found = True
        elif len(args) > 1 and re.match(r'https?://\S+', args[1]):
            url = args[1]
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, ssl=False) as response:
                        if response.status == 200:
                            with open(temp_file, "wb") as f:
                                f.write(await response.read())
                            source_found = True
                        else:
                            return await utils.answer(message, self.strings("invalid_url"))
            except Exception as e:
                error_message = self.strings("invalid_url") + f"\n\n<b>Детали:</b> <code>{e}</code>"
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return await utils.answer(message, error_message)
        
        if not source_found:
            return await utils.answer(message, self.strings("no_reply_or_link"))

        status_message = await utils.answer(message, self.strings("adding"))
        
        try:
            file_handle = await self.client.upload_file(temp_file)
            
            for i in range(count):
                await self.client(UploadProfilePhotoRequest(file=file_handle))
                
                if (i + 1) % 10 == 0 or (i + 1) == count:
                    await utils.answer(status_message, self.strings("added_count").format(i + 1))
                
                await asyncio.sleep(0.3)

        except Exception as e:
            return await utils.answer(status_message, self.strings("error").format(e))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        await utils.answer(status_message, self.strings("added").format(count))

    @loader.command(
        ru_doc="<количество> - Удалить аватарки"
    )
    async def avatarrem(self, message):
        """<count> - Remove avatars"""
        args = utils.get_args_raw(message)

        if not args or not args.isdigit():
            return await utils.answer(message, self.strings("no_args_count"))

        count = int(args)
        if count <= 0:
            return await utils.answer(message, self.strings("invalid_count"))
            
        status_message = await utils.answer(message, self.strings("processing"))

        try:
            photos = await self.client.get_profile_photos('me', limit=count)
            
            if not photos:
                return await utils.answer(status_message, self.strings("no_avatars_to_delete"))
            
            await self.client(DeletePhotosRequest(id=photos))
            await utils.answer(status_message, self.strings("removed").format(len(photos)))
        except Exception as e:
            await utils.answer(status_message, self.strings("error").format(e))

    @loader.command(
        ru_doc="- Удалить все аватарки"
    )
    async def avatarremall(self, message):
        """- Remove all avatars"""
        status_message = await utils.answer(message, self.strings("processing"))
        
        try:
            photos = await self.client.get_profile_photos('me')
            
            if not photos:
                return await utils.answer(status_message, self.strings("no_avatars_to_delete"))

            await self.client(DeletePhotosRequest(id=photos))
            await utils.answer(status_message, self.strings("removed_all"))
        except Exception as e:
            await utils.answer(status_message, self.strings("error").format(e))