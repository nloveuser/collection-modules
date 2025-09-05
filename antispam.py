# meta developer: @Lucky_modules

__version__ = (1, 1, 4)

from .. import loader, utils
import time

class AntiSpamModule(loader.Module):
    strings = {"name": "AntiSpam"}

    def __init__(self):
        self.cache = {}
        self.chat_settings = {}

    async def client_ready(self, client, db):
        self.db = db
        self.chat_settings = self.db.get("antispam", "chat_settings", {})

    async def antispamchatcmd(self, message):
        if message.chat is None:
            return
        
        chat_id = str(message.chat.id)
        if chat_id in self.chat_settings:
            del self.chat_settings[chat_id]
        else:
            self.chat_settings[chat_id] = {
                "enabled": False,
                "time_limit": 1.0
            }
        
        self.db.set("antispam", "chat_settings", self.chat_settings)

    async def antispamcmd(self, message):
        if message.chat is None:
            return
        
        chat_id = str(message.chat.id)
        if chat_id not in self.chat_settings:
            return
        
        self.chat_settings[chat_id]["enabled"] ^= True
        self.db.set("antispam", "chat_settings", self.chat_settings)

    async def antispamtimecmd(self, message):
        if message.chat is None:
            return
        
        chat_id = str(message.chat.id)
        
        if chat_id not in self.chat_settings:
            return
        
        args = utils.get_args_raw(message)
        
        if not args:
            current_limit = self.chat_settings[chat_id]["time_limit"]
            await message.edit(
                f".antispamtime <число>"
            )
            return
        
        try:
            time_limit = float(args)
            if time_limit <= 0:
                raise ValueError
                
            self.chat_settings[chat_id]["time_limit"] = time_limit
            self.db.set("antispam", "chat_settings", self.chat_settings)
            
        except (ValueError, TypeError):

    async def watcher(self, message):
        if not message or not message.sender_id or not message.chat:
            return
        
        chat_id = str(message.chat.id)
        if chat_id not in self.chat_settings or not self.chat_settings[chat_id]["enabled"]:
            return
        
        user_id = message.sender_id
        time_limit = self.chat_settings[chat_id]["time_limit"]
        current_time = time.time()
        last_time = self.cache.get(user_id, 0)
        
        if current_time - last_time < time_limit:
            await message.delete()
            self.cache[user_id] = current_time
            return
        
        self.cache[user_id] = current_time