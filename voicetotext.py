# meta developer: @cachedfiles
# scope: ffmpeg
# requires: pydub SpeechRecognition

from .. import loader, utils
import os
import speech_recognition as sr
from pydub import AudioSegment

@loader.tds
class VoiceToTextMod(loader.Module):
    strings = {
        "name": "VoiceToText",
    }

    strings_ru = {
    }

    @loader.command(
    )
    async def vttcmd(self, message):
        """- recognizes text from voice or video messages."""
        await self._vtt_process(message)

    async def _vtt_process(self, message):
        """processing voice/video messages to text"""
        reply = await message.get_reply_message()

        if not reply or not (reply.voice or reply.video_note):
            await message.respond(self.strings["vtt_invalid"].format(self.get_prefix()))
            return

        waiting_message = await utils.answer(
            message, self.strings["process_text"], reply_to=message.id
        )

        media_file = await reply.download_media()
        wav_file = media_file.replace('.mp4', '.wav') if reply.video_note else media_file.replace('.oga', '.wav')

        try:
            AudioSegment.from_file(media_file).export(wav_file, format='wav')
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language='ru-RU')
                    await reply.reply(self.strings["vtt_success"].format(text))
                    await waiting_message.edit(self.strings["vtt_successful"])
                except sr.UnknownValueError:
                    await waiting_message.delete()
                    await reply.reply(self.strings["vtt_failure"])
                except sr.RequestError as e:
                    await waiting_message.delete()
                    await reply.reply(self.strings["vtt_request_error"].format(e))
        finally:
            os.remove(media_file)
            os.remove(wav_file)
