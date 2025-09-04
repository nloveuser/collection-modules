# requires: google-genai google nltk
# meta developer: @Lucky_modules

import random
import json
import re
from .. import loader, utils
from google import genai

try:
    import nltk
    from nltk.corpus import words
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@loader.tds
class UsernameMod(loader.Module):
    strings = {
        "name": "Username",
        "take_username": "📥 Забрать",
        "show_all": "📋 Показать все",
        "use_ai_yes": "✅ Да, использовать",
    }

    def __init__(self):
        self.word_list = []
        self.nltk_ready = False
        self.config = loader.ModuleConfig(
            loader.ConfigValue("api_key", "", self.strings["cfg_api_key_doc"], validator=loader.validators.Hidden()),
            loader.ConfigValue("model", "gemini-2.5-flash", self.strings["cfg_model_doc"]),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        if NLTK_AVAILABLE:
            await self.init_nltk()

    async def init_nltk(self):
        try:
            try:
                words.words()
            except:
                nltk.download('words', quiet=True)
            self.word_list = [w.lower() for w in words.words() if w.isalpha() and len(w) > 2]
            self.nltk_ready = True
        except:
            self.nltk_ready = False

    def generate_username(self):
        if not self.nltk_ready or not self.word_list:
            return None
        return f"{random.choice(self.word_list)}_{random.choice(self.word_list)}"

    async def check_username_availability(self, username):
        try:
            await self.client.get_entity(username)
            return False
        except:
            return True

    async def find_available_username(self):
        for _ in range(50):
            username = self.generate_username()
            if username and await self.check_username_availability(username):
                return username
        return None

    def number_to_emoji(self, n):
        emoji_map = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
                     '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}
        return ''.join(emoji_map[d] for d in str(n))

    async def generate_multiple_usernames(self, count):
        usernames = set()
        attempts = 0
        while len(usernames) < count and attempts < 500:
            username = self.generate_username()
            if username and username not in usernames:
                if await self.check_username_availability(username):
                    usernames.add(username)
            attempts += 1
        return list(usernames)

    async def filter_with_gemini(self, usernames):
        api_key = self.config["api_key"]
        model_name = self.config["model"]
        if not api_key:

        prompt = (
                "\n".join([f"@{u}" for u in usernames])
            )

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
        )
        
        if not response.text:
            return usernames

        text = response.text.strip()

        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return usernames  

        try:
            parsed = json.loads(match.group(0))
            return [u.replace("@", "") for u in parsed]
        except:
            return usernames

    def format_usernames_list(self, usernames):
        return "\n".join(f"{self.number_to_emoji(i+1)} @{u}" for i, u in enumerate(usernames))

    async def usernamecmd(self, message):
        if not NLTK_AVAILABLE:
            return await utils.answer(message, self.strings["nltk_not_available"])
        if not self.nltk_ready:
            await utils.answer(message, self.strings["downloading_words"])
            await self.init_nltk()
            if not self.nltk_ready:
        msg = await utils.answer(message, self.strings["generating"])
        username = await self.find_available_username()
        if not username:
        await msg.delete()
        await self.inline.form(
            message=message,
            text=self.strings["username_found"].format(username),
            reply_markup=[
                [{"text": self.strings["take_username"], "callback": self.take_username, "args": (username,)}],
                [{"text": self.strings["next_username"], "callback": self.generate_next_username, "args": ()}],
                [{"text": self.strings["show_all"], "callback": self.show_all_handler, "args": ()}]
            ],
            silent=True
        )

    async def take_username(self, call, username):
        try:
            from telethon.tl.functions.account import UpdateUsernameRequest
            await self.client(UpdateUsernameRequest(username=username))
            await call.edit(self.strings["username_set"].format(username))
        except Exception as e:
            await call.edit(self.strings["username_error"].format(str(e)))

    async def generate_next_username(self, call):
        await call.edit(self.strings["checking_availability"])
        username = await self.find_available_username()
        if not username:
        await call.edit(
            self.strings["username_found"].format(username),
            reply_markup=[
                [{"text": self.strings["take_username"], "callback": self.take_username, "args": (username,)}],
                [{"text": self.strings["next_username"], "callback": self.generate_next_username, "args": ()}],
                [{"text": self.strings["show_all"], "callback": self.show_all_handler, "args": ()}]
            ]
        )

    async def show_all_handler(self, call):
        await call.edit(
            self.strings["choose_amount"],
            reply_markup=[
            ]
        )

    async def generate_usernames_amount(self, call, amount):
        await call.edit(self.strings["generating_usernames"].format(amount))
        usernames = await self.generate_multiple_usernames(amount)
        if not usernames:
        await call.edit(
            self.strings["ai_filter_prompt"].format(self.config["model"]),
            reply_markup=[
                [{"text": self.strings["use_ai_yes"], "callback": self.process_with_ai, "args": (usernames, amount, True)}],
                [{"text": self.strings["use_ai_no"], "callback": self.process_with_ai, "args": (usernames, amount, False)}]
            ]
        )

    async def process_with_ai(self, call, usernames, amount, use_ai):
        footer = ""
        if use_ai:
            await call.edit(self.strings["filtering_ai"])
            try:
                usernames = await self.filter_with_gemini(usernames)
                footer = self.strings["ai_footer"].format(self.config["model"])
            except Exception as e:
                footer = "\n\n" + self.strings["ai_error"].format(str(e))
        count = len(usernames)
        if count < amount:
            text = self.strings["not_enough_usernames"].format(count, amount, self.format_usernames_list(usernames)) + footer
        else:
            text = self.strings["available_usernames"].format(count, self.format_usernames_list(usernames)) + footer
        await call.edit(text)
