# -*- coding: utf-8 -*-
# meta developer: @Rezoxss
# scope: hikka_only

from .. import loader, utils
import logging
import random
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

@loader.tds
class SglypaMod(loader.Module):
    
    strings = {
        "name": "Sglypa",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reply_chance",
                40,
                validator=loader.validators.Integer(minimum=1, maximum=100)
            )
        )
        self.active_chats = set()
        self.chat_history = defaultdict(list)
        self.words_db = self.load_words_database()

    def load_words_database(self):
        return {
            "nouns": [
            ],
            "adjectives": [
            ],
            "verbs": [
            ]
        }

    async def client_ready(self, client, db):
        self._client = client

    def add_to_history(self, chat_id, text):
        if text and len(text) > 2:
            words = re.findall(r'\b[а-яё]{3,}\b', text.lower())
            for word in words:
                if word not in ['это', 'вот', 'как', 'что', 'там', 'здесь']:
                    self.chat_history[chat_id].append(word)

    def generate_sglypa(self, chat_id):
        if chat_id in self.chat_history and self.chat_history[chat_id]:
            chat_words = list(self.chat_history[chat_id])
            noun = random.choice(chat_words)
        else:
            noun = random.choice(self.words_db["nouns"])
        
        adjective = random.choice(self.words_db["adjectives"])
        verb = random.choice(self.words_db["verbs"])

        patterns = [
            f"{adjective} {noun} {verb}",
            f"{noun} {verb} {adjective}",
            f"{verb} {adjective} {noun}",
            f"{adjective} {verb} {noun}",
            f"{noun} {adjective} {verb}",
            f"{verb} {noun} {adjective}"
        ]
        
        prefixes = [
        ]
        
        return f"{random.choice(prefixes)} {random.choice(patterns)}"

    @loader.command()
    async def sglypa(self, message):
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        
        if message.text:
            self.add_to_history(chat_id, message.text)

        if not args:
            sglypa_text = self.generate_sglypa(chat_id)
            await utils.answer(message, sglypa_text)
            return
            
        if args.lower() == "on":
            if chat_id in self.active_chats:
                await utils.answer(message, self.strings("already_on"))
            else:
                self.active_chats.add(chat_id)
                await utils.answer(message, self.strings("on"))
                
        elif args.lower() == "off":
            if chat_id not in self.active_chats:
                await utils.answer(message, self.strings("already_off"))
            else:
                self.active_chats.discard(chat_id)
                await utils.answer(message, self.strings("off"))
                
        elif args.lower() == "clear":
            if chat_id in self.chat_history:
                self.chat_history[chat_id].clear()
            await utils.answer(message, self.strings("cleared"))
            
        elif args.lower() == "stats":
            count = len(self.chat_history.get(chat_id, []))
            await utils.answer(message, self.strings("stats").format(count))
            
        else:
            sglypa_text = self.generate_sglypa(chat_id)
            await utils.answer(message, sglypa_text)

    @loader.watcher()
    async def watcher(self, message):
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self.active_chats:
            return
            
        if not message.text or message.out or message.text.startswith('.'):
            return
            
        self.add_to_history(chat_id, message.text)
        
            sglypa_text = self.generate_sglypa(chat_id)
            await message.reply(sglypa_text)
            return
            
        if random.randint(1, 100) <= 40:
            sglypa_text = self.generate_sglypa(chat_id)
            await message.reply(sglypa_text)

    async def on_unload(self):
        self.active_chats.clear()
        self.chat_history.clear()