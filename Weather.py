# meta developer: @xdesai
# requires: requests

from .. import loader, utils
import requests


@loader.tds
class Weather(loader.Module):
    strings_ru = {
        "url": "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru",
        "error": "<b>Ошибка:</b> <code>{e}</code>",
    }

    strings_jp = {
        "url": "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ja",
        "error": "<b>エラー:</b> <code>{e}</code>",
        "api_error": "<b>都市が見つかりませんでした: {city}\nAPIの応答:</b> <code>{data}</code>",
    }

    strings = {
        "name": "Weather",
        "url": "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=en",
        "error": "<b>Error:</b> <code>{e}</code>",
        "api_error": "<b>City not found: {city}\nAPI response:</b> <code>{data}</code>",
    }

    @loader.command(
        jp_doc="指定された都市の天気を確認してください",
    )
    async def weather(self, message):
        """Check the weather in the specified city"""
        args = utils.get_args_raw(message).split()
        if len(args) < 1:
            await utils.answer(message, self.strings["invalid_args"])
            return
        if isinstance(args, list):
            args = args[0]
        city = args
        api_key = "934e9392018dd900103f54e50b870c02"
        url = self.strings["url"].format(api_key=api_key, city=city)
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("cod") != 200:
                await utils.answer(
                    message,
                    self.strings["api_error"].format(city=city, data=data),
                )
                return

            country = data["sys"]["country"]
            weather_data = data["main"]
            temperature = weather_data["temp"]
            feels_like = weather_data["feels_like"]
            wind_data = data["wind"]["speed"]
            wind_speed = wind_data
            humidity = weather_data["humidity"]
            description = data["weather"][0]["description"].capitalize()
            await utils.answer(
                message,
                self.strings["weather_info"].format(
                    city=city.capitalize(),
                    country=country,
                    description=description,
                    temperature=temperature,
                    feels_like=feels_like,
                    humidity=humidity,
                    wind_speed=wind_speed,
                ),
            )
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(e=e))