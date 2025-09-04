# meta developer: @kotcheat

import requests
from .. import loader, utils

class URLShortenerMod(loader.Module):

    strings = {"name": "KOTURLShortener"}

    def __init__(self):
        self.name = self.strings["name"]

    async def urlsoccmd(self, message):
        """Сокращает URL"""
        args = utils.get_args_raw(message)
        if not args:
            return

        url = args.strip()
        shorten_url = await self.shorten_url(url)

        if shorten_url:
        else:

    async def shorten_url(self, url):
        response = requests.get(f"https://clck.ru/--?url={url}")

        if response.status_code == 200:
            return response.text
        else:
            return None