#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
#
# You CANNOT edit, distribute or redistribute this file without direct permission from the author.
#
# ORIGINAL MODULE: https://raw.githubusercontent.com/hikariatama/ftg/master/spotify.py
# meta developer: @cachedfiles, @kamekuro_hmods, @extracli
# requires: telethon spotipy pillow requests

import asyncio
import contextlib
import functools
import io
import logging
import textwrap
import time
import traceback
from types import FunctionType

import requests
import spotipy
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
logging.getLogger("spotipy").setLevel(logging.CRITICAL)


@loader.tds
class SpotifyMod(loader.Module):
    """Card with the currently playing track on Spotify. Idea: t.me/fuccsoc. Implementation: t.me/hikariatama. Developer channel: t.me/hikarimods. Banners from YaMusic by @kamekuro_hmods"""

    strings = {
        "name": "SpotifyMod",
        "need_auth": (
            " </b><code>.sauth</code><b> before performing this action.</b>"
        ),
        "on-repeat": (
        ),
        "off-repeat": (
            " repeat.</b>"
        ),
        "skipped": (
        ),
        "back": (
            " track</b>"
        ),
        "restarted": (
            " from the"
            " beginning</b>"
        ),
        "liked": (
            " playback</b>"
        ),
        "unlike": (
            " <b>Unliked current playback</b>"
        ),
        "err": (
            "</b>\n<code>{}</code>"
        ),
        "already_authed": (
        ),
        "authed": (
            " successful</b>"
        ),
        "deauth": (
            " of account</b>"
        ),
        "auth": (
            " link</a>, allow access, then enter <code>.scode https://...</code> with"
            " the link you received."
        ),
        "no_music": (
        ),
        "dl_err": (
            " track.</b>"
        ),
    }

    strings_ru = {
        "need_auth": (
        ),
        "err": (
            "</b>\n<code>{}</code>"
        ),
        "on-repeat": (
        ),
        "off-repeat": (
        ),
        "skipped": (
        ),
        "back": (
        ),
        "restarted": (
        ),
        "liked": (
        ),
        "unlike": (
        ),
        "already_authed": (
        ),
        "authed": (
        ),
        "deauth": (
        ),
        "auth": (
        ),
        "no_music": (
        ),
        "dl_err": (
        ),
    }

    def __init__(self):
        self._client_id = "e0708753ab60499c89ce263de9b4f57a"
        self._client_secret = "80c927166c664ee98a43a2c0e2981b4a"
        self.scope = (
            "user-read-playback-state playlist-read-private playlist-read-collaborative"
            " app-remote-control user-modify-playback-state user-library-modify"
            " user-library-read"
        )
        self.sp_auth = spotipy.oauth2.SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri="https://thefsch.github.io/spotify/",
            scope=self.scope,
        )
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "show_banner",
                True,
                "Show banner with track info",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_text",
                (
                ),
                """Custom text, supports {track}, {artists}, {album}, {playlist}, {playlist_owner}, {spotify_url}, {songlink}, {progress}, {duration}, {device} placeholders""",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "banner_gen_text",
                "Custom banner generation text",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "download_track_text",
                "Custom download text for snowt",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "title_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Bold.ttf",
                "Custom font for title. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "artists_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Regular.ttf",
                "Custom font for artists. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "time_font",
                "https://raw.githubusercontent.com/kamekuro/assets/master/fonts/Onest-Bold.ttf",
                "Custom font for time. Specify URL to .ttf file",
                validator=loader.validators.String(),
            ),
        )

    async def client_ready(self, client, db):
        self.font_ready = asyncio.Event()

        self._premium = getattr(await client.get_me(), "premium", False)
        try:
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        except Exception:
            self.set("acs_tkn", None)
            self.sp = None

        with contextlib.suppress(Exception):
            await utils.dnd(client, "@DirectLinkGenerator_Bot", archive=True)

        with contextlib.suppress(Exception):
            await utils.dnd(client, "@LosslessRobot", archive=True)

    def tokenized(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if not args[0].get("acs_tkn", False) or not args[0].sp:
                await utils.answer(args[1], args[0].strings("need_auth"))
                return

            return await func(*args, **kwargs)

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def error_handler(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception(traceback.format_exc())
                with contextlib.suppress(Exception):
                    await utils.answer(
                        args[1],
                        args[0].strings("err").format(traceback.format_exc()),
                    )

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def _create_banner(
        self,
        title: str, artists: list,
        duration: int, progress: int,
        track_cover: bytes
    ):
        w, h = 1920, 768
        title_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["title_font"]
        ).content), 80)
        art_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["artists_font"]
        ).content), 55)
        time_font = ImageFont.truetype(io.BytesIO(requests.get(
            self.config["time_font"]
        ).content), 36)

        track_cov = Image.open(io.BytesIO(track_cover)).convert("RGBA")
        banner = track_cov.resize((w, w)).crop(
            (0, (w-h)//2, w, ((w-h)//2)+h)
        ).filter(ImageFilter.GaussianBlur(radius=14))
        banner = ImageEnhance.Brightness(banner).enhance(0.3)

        track_cov = track_cov.resize((banner.size[1]-150, banner.size[1]-150))
        mask = Image.new("L", track_cov.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, track_cov.size[0], track_cov.size[1]), radius=35, fill=255)
        track_cov.putalpha(mask)
        track_cov = track_cov.crop(track_cov.getbbox())
        banner.paste(track_cov, (75, 75), mask)

        title_lines = textwrap.wrap(title, 23)
        if len(title_lines) > 1:
            title_lines[1] = title_lines[1] + "..." if len(title_lines) > 2 else title_lines[1]
        title_lines = title_lines[:2]
        artists_lines = textwrap.wrap(", ".join(artists), width=40)
        if len(artists_lines) > 1:
            for index, art in enumerate(artists_lines):
                if "," in art[-2:]:
                    artists_lines[index] = art[:art.rfind(",") - 1]

        draw = ImageDraw.Draw(banner)
        x, y = 150+track_cov.size[0], 110
        for index, line in enumerate(title_lines):
            draw.text((x, y), line, font=title_font, fill="#FFFFFF")
            if index != len(title_lines)-1:
                y += 70
        x, y = 150+track_cov.size[0], 110*2
        if len(title_lines) > 1: y += 70
        for index, line in enumerate(artists_lines):
            draw.text((x, y), line, font=art_font, fill="#A0A0A0")
            if index != len(artists_lines)-1:
                y += 50

        draw.rounded_rectangle([768, 650, 768+1072, 650+15], radius=15//2, fill="#A0A0A0")
        if duration > 0:
             draw.rounded_rectangle([768, 650, 768+int(1072*(progress/duration)), 650+15], radius=15//2, fill="#FFFFFF")
        draw.text((768, 600), f"{(progress//1000//60):02}:{(progress//1000%60):02}", font=time_font, fill="#FFFFFF")
        draw.text((1745, 600), f"{(duration//1000//60):02}:{(duration//1000%60):02}", font=time_font, fill="#FFFFFF")

        by = io.BytesIO()
        banner.save(by, format="PNG"); by.seek(0)
        by.name = "banner.png"
        return by

    async def _dl_track(self, client, track, artists):
        query = f"{track} - {artists}"
        async with client.conversation("@LosslessRobot") as conv:
            await conv.send_message(query)
            response = await conv.get_response()
            candidate_pos = None
            if response.buttons:
                for i, row in enumerate(response.buttons):
                    for j, button in enumerate(row):
                        if track.lower() and artists.lower() in button.text.lower():
                            candidate_pos = (i, j)
                            break
                    if candidate_pos:
                        break
                if candidate_pos is None:
                    candidate_pos = (0, 0)
                await response.click(*candidate_pos)
                track_msg = await conv.get_response()
                return track_msg
            return None

    @error_handler
    @tokenized
    @loader.command(
    )
    async def srepeatcmd(self, message: Message):
        """💫 Repeat"""
        self.sp.repeat("track")
        await utils.answer(message, self.strings("on-repeat"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def sderepeatcmd(self, message: Message):
        """✋ Stop repeat"""
        self.sp.repeat("context")
        await utils.answer(message, self.strings("off-repeat"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def snextcmd(self, message: Message):
        """👉 Next track"""
        self.sp.next_track()
        await utils.answer(message, self.strings("skipped"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def sresumecmd(self, message: Message):
        """- 🤚 Resume"""
        self.sp.start_playback()
        await utils.answer(message, self.strings("playing"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def spausecmd(self, message: Message):
        """- 🤚 Pause"""
        self.sp.pause_playback()
        await utils.answer(message, self.strings("paused"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def sbackcmd(self, message: Message):
        """- ⏮ Previous track"""
        self.sp.previous_track()
        await utils.answer(message, self.strings("back"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def sbegincmd(self, message: Message):
        """- ⏪ Restart track"""
        self.sp.seek_track(0)
        await utils.answer(message, self.strings("restarted"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def slikecmd(self, message: Message):
        """- ❤️ Like current track"""
        cupl = self.sp.current_playback()
        self.sp.current_user_saved_tracks_add([cupl["item"]["id"]])
        await utils.answer(message, self.strings("liked"))
    
    @error_handler
    @tokenized
    @loader.command(
    )
    async def sunlikecmd(self, message: Message):
        """- 💔 Unlike current track"""
        cupl = self.sp.current_playback()
        self.sp.current_user_saved_tracks_delete([cupl["item"]["id"]])
        await utils.answer(message, self.strings("unlike"))

    @error_handler
    @loader.command(
    )
    async def sauthcmd(self, message: Message):
        """- Get authorization link"""
        if self.get("acs_tkn", False) and not self.sp:
            await utils.answer(message, self.strings("already_authed"))
        else:
            self.sp_auth.get_authorize_url()
            await utils.answer(
                message,
                self.strings("auth").format(self.sp_auth.get_authorize_url()),
            )

    @error_handler
    @loader.command(
        ru_doc="- Вставить код авторизации"
    )
    async def scodecmd(self, message: Message):
        """- Paste authorization code"""
        url = message.message.split(" ")[1]
        code = self.sp_auth.parse_auth_response_url(url)
        self.set("acs_tkn", self.sp_auth.get_access_token(code, True, False))
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    @loader.command(
    )
    async def unauthcmd(self, message: Message):
        """- Log out of account"""
        self.set("acs_tkn", None)
        del self.sp
        await utils.answer(message, self.strings("deauth"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def stokrefreshcmd(self, message: Message):
        """- Refresh authorization token"""
        self.set(
            "acs_tkn",
            self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
        )
        self.set("NextRefresh", time.time() + 45 * 60)
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    @tokenized
    @loader.command(
    )
    async def snowcmd(self, message: Message):
        """- 🎧 View current track card."""
        current_playback = self.sp.current_playback()
        if not current_playback or not current_playback.get("is_playing", False):
            await utils.answer(message, self.strings("no_music"))
            return

        track = current_playback["item"]["name"]
        track_id = current_playback["item"]["id"]
        artists = ", ".join([a["name"] for a in current_playback["item"]["artists"]])
        album_name = current_playback["item"]["album"].get("name", "Unknown Album")
        duration_ms = current_playback["item"].get("duration_ms", 0)
        progress_ms = current_playback.get("progress_ms", 0)

        duration = f"{duration_ms//1000//60}:{duration_ms//1000%60:02}"
        progress = f"{progress_ms//1000//60}:{progress_ms//1000%60:02}"

        spotify_url = f"https://open.spotify.com/track/{track_id}"
        songlink = f"https://song.link/s/{track_id}"

        try:
            device_raw = (
                current_playback["device"]["name"]
                + " "
                + current_playback["device"]["type"].lower()
            )
            device = device_raw.replace("computer", "").replace("smartphone", "").strip()
        except Exception:
            device = None

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", None)
            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">'
                    f'{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = playlist.get("owner", {}).get("display_name", "")
        except Exception:
            playlist_name = ""
            playlist_owner = ""

        text = self.config["custom_text"].format(
            track=utils.escape_html(track),
            artists=utils.escape_html(artists),
            album=utils.escape_html(album_name),
            duration=duration,
            progress=progress,
            device=device,
            spotify_url=spotify_url,
            songlink=songlink,
            playlist=utils.escape_html(playlist_name) if playlist_name else "",
            playlist_owner=playlist_owner or "",
        )

        if self.config["show_banner"]:
            cover_url = current_playback["item"]["album"]["images"][0]["url"]
            cover_bytes = await utils.run_sync(requests.get, cover_url)

            tmp_msg = await utils.answer(message, text + f'\n\n{self.config["banner_gen_text"]}')

            banner_file = await utils.run_sync(
                self._create_banner,
                title=track,
                artists=[a["name"] for a in current_playback["item"]["artists"]],
                duration=duration_ms,
                progress=progress_ms,
                track_cover=cover_bytes.content,
            )
            await utils.answer(tmp_msg, text, file=banner_file)
        else:
            await utils.answer(message, text)

    @error_handler
    @tokenized
    @loader.command(
    )
    async def snowtcmd(self, message: Message):
        """- 🎧 Download current track."""
        current_playback = self.sp.current_playback()
        if not current_playback or not current_playback.get("is_playing", False):
            await utils.answer(message, self.strings("no_music"))
            return

        track = current_playback["item"]["name"]
        artists = ", ".join([a["name"] for a in current_playback["item"]["artists"]])
        album_name = current_playback["item"]["album"].get("name", "Unknown Album")
        duration_ms = current_playback["item"].get("duration_ms", 0)
        progress_ms = current_playback.get("progress_ms", 0)

        duration = f"{duration_ms//1000//60}:{duration_ms//1000%60:02}"
        progress = f"{progress_ms//1000//60}:{progress_ms//1000%60:02}"

        spotify_url = f"https://open.spotify.com/track/{current_playback['item']['id']}"
        songlink = f"https://song.link/s/{current_playback['item']['id']}"

        try:
            device_raw = (
                current_playback["device"]["name"]
                + " "
                + current_playback["device"]["type"].lower()
            )
            device = device_raw.replace("computer", "").replace("smartphone", "").strip()
        except Exception:
            device = None

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", None)
            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">'
                    f'{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = playlist.get("owner", {}).get("display_name", "")
        except Exception:
            playlist_name = ""
            playlist_owner = ""

        text = self.config["custom_text"].format(
            track=utils.escape_html(track),
            artists=utils.escape_html(artists),
            album=utils.escape_html(album_name),
            duration=duration,
            progress=progress,
            device=device,
            spotify_url=spotify_url,
            songlink=songlink,
            playlist=utils.escape_html(playlist_name) if playlist_name else "",
            playlist_owner=playlist_owner or "",
        )

        msg = await utils.answer(message, text + f'\n\n{self.config["download_track_text"]}')
        track_msg = await self._dl_track(message.client, track, artists)

        if (
            track_msg
            and track_msg.media
            and hasattr(track_msg.media, "document")
            and getattr(track_msg.media.document, "mime_type", "").startswith("audio/")
        ):
            await utils.answer(msg, text, file=track_msg.media)
        else:
            await utils.answer(msg, self.strings("dl_err"))

    async def watcher(self, message: Message):
        """Watcher is used to update token"""
        if not self.sp:
            return

        if self.get("NextRefresh", False):
            ttc = self.get("NextRefresh", 0)
            crnt = time.time()
            if ttc < crnt:
                self.set(
                    "acs_tkn",
                    self.sp_auth.refresh_access_token(
                        self.get("acs_tkn")["refresh_token"]
                    ),
                )
                self.set("NextRefresh", time.time() + 45 * 60)
                self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        else:
            self.set(
                "acs_tkn",
                self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
            )
            self.set("NextRefresh", time.time() + 45 * 60)
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])