# meta developer: @kotcheat
# СОЗДАНО ДЛЯ t.me/KOTmodule

import random
import string
import asyncio
import io
import json
import time
from datetime import datetime
from .. import loader, utils
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════

@loader.tds
class KOTpassfolder(loader.Module):

    strings = {
        "name": "KOTpassfolder"
    }

    def __init__(self):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        self.saved_credentials = []
        self.last_generated_password = None
        self.last_generated_login = None
        self.private_group_id = None
        self.MAX_CREDENTIALS = 15
        self.backup_interval = 86400
        self.last_backup_time = 0
        
        
        self.regular_emojis = {
            "generate": "🎯",
            "save": "💾", 
            "show": "📋",
            "clear": "🧹",
            "note": "📝",
            "delete": "🗑️",
            "add": "➕",
            "edit": "✏️",
            "export": "📤",
            "backup": "💾",
            "restore": "🔄",
            "group": "🔒",
            "file": "📄",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "💡",
            "time": "⏰",
            "protection": "🛡️",
            "stats": "📊",
            "user": "👤",
            "password": "🔑",
            "length": "📏",
            "lock": "🔒",
            "book": "📖",
            "drop": "💧",
            "service": "📝",
            "bullet": "▫️",
            "sosal": "🆔",
            "vremy": "🕐",
            "datag": "📅",
            "otsosal": "👥"
        }
        
        
        self.premium_emojis = {
        }

    async def client_ready(self, client, db):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        self.db = db
        self.client = client
        
        
        await self._restore_data_with_limit_check()
        
        
        if self.saved_credentials:
            await self._create_backup()

    async def _is_private_chat(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            peer = message.peer_id
            return isinstance(peer, PeerUser)
        except:
            return False

    async def _get_emojis(self, user_id):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            user = await self.client.get_entity(user_id)
            if hasattr(user, 'premium') and user.premium:
                return self.premium_emojis
            else:
                return self.regular_emojis
        except:
            
            return self.regular_emojis

    def _check_limit_strict(self):
        """СТРОГАЯ проверка лимита записей"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule 
        # ═══════════════════════════════════════════════════════════════════
        current_count = len(self.saved_credentials)
        
        
        if current_count >= self.MAX_CREDENTIALS:
            return "BLOCKED"  
        elif current_count >= self.MAX_CREDENTIALS - 2:
            return "WARNING"  
        else:
            return "OK"  

    def _enforce_limit(self):
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule 
        # ═══════════════════════════════════════════════════════════════════
        if len(self.saved_credentials) > self.MAX_CREDENTIALS:
            
            self.saved_credentials = self.saved_credentials[:self.MAX_CREDENTIALS]
            return True
        return False

    async def _add_credential_safely(self, login, password, service):
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule
        # ═══════════════════════════════════════════════════════════════════
        
        
        if self._check_limit_strict() == "BLOCKED":
            return False, "LIMIT_EXCEEDED"
        
        
        self.saved_credentials.append((login, password, service))
        
        
        if len(self.saved_credentials) > self.MAX_CREDENTIALS:
            
            self.saved_credentials.pop()
            return False, "LIMIT_EXCEEDED"
        
        
        success = await self._save_data_securely()
        if success:
            return True, "SUCCESS"
        else:
            
            self.saved_credentials.pop()
            return False, "SAVE_ERROR"

    async def _get_strings(self, user_id):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        emojis = await self._get_emojis(user_id)
        
        return {
                                   f"{emojis['password']} <b>Пароль:</b> <code>{{password}}</code>\n"
            
                               f"{emojis['stats']} <b>Всего записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
            
            
            
            
            
                                  f"{emojis['stats']} <b>Осталось записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
            
                               f"{emojis['service']} <b>Сервис:</b> {{service}}\n"
                               f"{emojis['backup']} <b>Автобэкап:</b> {{backup_time}}\n\n"
            
            
            
            
                             f"{emojis['vremy']} <b>Время бэкапа:</b> {{backup_time}}\n\n"
            
                             f"{emojis['stats']} <b>Records backed up:</b> {{count}}\n"
                             f"{emojis['vremy']} <b>Время:</b> {{backup_time}}\n\n"
            
            
            
            "limit_reached": f"{emojis['warning']} <b>ЛИМИТ ДОСТИГНУТ!</b>\n\n"
                            f"{emojis['error']} <b>ДОБАВЛЕНИЕ ЗАБЛОКИРОВАНО!</b>\n\n"
                            f"{emojis['bullet']} Просмотрите записи: <code>.show</code>\n\n"
            
            "limit_warning": f"{emojis['warning']} <b>ПРЕДУПРЕЖДЕНИЕ О ЛИМИТЕ!</b>\n\n"
                            f"{emojis['stats']} <b>Записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                            f"{emojis['info']} <b>Осталось мест:</b> {{remaining}}\n\n"
            
                           f"{emojis['datag']} <b>Дата экспорта:</b> {{date}}\n"
            
            
            
            
                            f"{emojis['bullet']} <b>Пример:</b> <code>.addcred myuser mypass123 Gmail</code>\n\n"
            
                             f"{emojis['bullet']} <b>Пример:</b> <code>.editcred 1 newuser newpass456 Yahoo</code>\n\n"
            
                           f"{emojis['bullet']} <b>Пример:</b> <code>.exportdata 1</code>\n\n"
            
            "chat_restricted": f"{emojis['warning']} <b>КОМАНДА ЗАБЛОКИРОВАНА В ЧАТАХ!</b>\n\n"
        }

    async def _restore_data_with_limit_check(self):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            main_data = self.db.get("KOTpassfolder", "saved_credentials", [])
            backup_data = self.db.get("KOTpassfolder", "backup_credentials", [])
            
            
            if self._validate_data(main_data):
                self.saved_credentials = main_data
            elif self._validate_data(backup_data):
                
                self.saved_credentials = backup_data
                self.db.set("KOTpassfolder", "saved_credentials", backup_data)
                await self._log_recovery("backup")
            else:
                
                emergency_backup = self.db.get("KOTpassfolder", "emergency_backup", [])
                if self._validate_data(emergency_backup):
                    self.saved_credentials = emergency_backup
                    self.db.set("KOTpassfolder", "saved_credentials", emergency_backup)
                    await self._log_recovery("emergency")
                else:
                    
                    self.saved_credentials = []
            
            
            if self._enforce_limit():
                
                await self._save_data_securely()
                await self._log_recovery("limit_enforced")
            
            
            self.private_group_id = self.db.get("KOTpassfolder", "private_group_id", None)
            
            
            self._restore_settings()
            
        except Exception as e:
            
            self.saved_credentials = []
            self.private_group_id = None

    def _validate_data(self, data):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        if not isinstance(data, list):
            return False
        
        
        if len(data) > self.MAX_CREDENTIALS:
            return False
        
        for item in data:
            if not isinstance(item, (list, tuple)) or len(item) != 3:
                return False
            if not all(isinstance(x, str) for x in item):
                return False
        
        return True

    def _restore_settings(self):
        try:
            settings = self.db.get("KOTpassfolder", "settings", {})
            
            self.backup_interval = settings.get("backup_interval", 300)
            self.last_backup_time = settings.get("last_backup_time", 0)
        except Exception:
            
            self.backup_interval = 300
            self.last_backup_time = 0

    async def _save_data_securely(self):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            if len(self.saved_credentials) > self.MAX_CREDENTIALS:
                self._enforce_limit()
            
            current_time = time.time()
            
            
            self.db.set("KOTpassfolder", "saved_credentials", self.saved_credentials)
            
            
            self.db.set("KOTpassfolder", "backup_credentials", self.saved_credentials)
            
            
            settings = {
                "backup_interval": self.backup_interval,
                "last_backup_time": current_time
            }
            self.db.set("KOTpassfolder", "settings", settings)
            
            
            if current_time - self.last_backup_time >= self.backup_interval:
                await self._create_emergency_backup()
                self.last_backup_time = current_time
            
            return True
            
        except Exception as e:
            
            try:
                self.db.set("KOTpassfolder", "emergency_backup", self.saved_credentials)
                return True
            except:
                return False

    async def _create_backup(self):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            backup_data = {
                "credentials": self.saved_credentials,
                "private_group_id": self.private_group_id,
                "timestamp": time.time(),
                "version": "2.0",
                "limit": self.MAX_CREDENTIALS,
                "watermark": "t.me/KOTmodule"
            }
            
            
            self.db.set("KOTpassfolder", "backup_1", backup_data)
            self.db.set("KOTpassfolder", "backup_2", backup_data)
            self.db.set("KOTpassfolder", "backup_3", backup_data)
            
            return True
        except Exception:
            return False

    async def _create_emergency_backup(self):
        try:
            emergency_data = {
                "credentials": self.saved_credentials,
                "private_group_id": self.private_group_id,
                "timestamp": time.time(),
                "type": "emergency",
                "limit": self.MAX_CREDENTIALS,
                "source": "t.me/KOTmodule"
            }
            
            self.db.set("KOTpassfolder", "emergency_backup", self.saved_credentials)
            self.db.set("KOTpassfolder", "emergency_full", emergency_data)
            
        except Exception:
            pass

    async def _log_recovery(self, source):
        try:
            recovery_log = self.db.get("KOTpassfolder", "recovery_log", [])
            recovery_log.append({
                "timestamp": time.time(),
                "source": source,
                "records_count": len(self.saved_credentials),
                "limit_enforced": len(self.saved_credentials) <= self.MAX_CREDENTIALS,
                "module_source": "t.me/KOTmodule"
            })
            
            
            if len(recovery_log) > 10:
                recovery_log = recovery_log[-10:]
            
            self.db.set("KOTpassfolder", "recovery_log", recovery_log)
        except Exception:
            pass

    async def _delete_message_after_delay(self, message, delay=30):
        try:
            await asyncio.sleep(delay)
            if message and hasattr(message, 'delete'):
                await message.delete()
        except Exception:
            pass

    async def _format_credentials_list(self, credentials, user_id):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        if not credentials:
            return ""
        
        emojis = await self._get_emojis(user_id)
        
        formatted_list = []
        for index, (login, password, service) in enumerate(credentials):
            formatted_list.append(
                f"{emojis['show']} <b>#{index + 1}</b>\n"
                f"{emojis['password']} <b>Пароль:</b> <code>{password}</code>\n"
                f"{emojis['service']} <b>Сервис:</b> {service_text}"
            )
        return "\n\n".join(formatted_list)

    def _generate_txt_content(self):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        if not self.saved_credentials:
        
        content += f"Лимит записей: {self.MAX_CREDENTIALS}\n\n"
        content += "=" * 50 + "\n\n"
        
        for index, (login, password, service) in enumerate(self.saved_credentials):
            content += f"Запись #{index + 1}\n"
            content += f"Пароль: {password}\n"
            content += f"Сервис: {service}\n"
            content += "-" * 30 + "\n\n"
        
        content += f"Всего записей: {len(self.saved_credentials)}/{self.MAX_CREDENTIALS}\n"
        
        return content

    def _get_backup_count(self):
        try:
            count = 0
            for i in range(1, 4):
                if self.db.get("KOTpassfolder", f"backup_{i}", None):
                    count += 1
            return count
        except Exception:
            return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # 💧 КОМАНДЫ МОДУЛЯ - СОЗДАНО ДЛЯ t.me/KOTmodule
    # ═══════════════════════════════════════════════════════════════════════════

    async def gen(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                length = 10
            else:
                try:
                    length = int(args)
                    if length <= 0 or length > 50:
                        generated_message = await utils.answer(message, strings["usage_gen"])
                        asyncio.create_task(self._delete_message_after_delay(generated_message))
                        return
                except ValueError:
                    generated_message = await utils.answer(message, strings["usage_gen"])
                    asyncio.create_task(self._delete_message_after_delay(generated_message))
                    return

            
            characters = string.ascii_letters + string.digits + "@$#%&*"
            password = ''.join(random.choices(characters, k=length))
            
            
            login_characters = string.ascii_letters + string.digits
            login = ''.join(random.choices(login_characters, k=length))

            self.last_generated_password = password
            self.last_generated_login = login

            
            await self._save_data_securely()

            generated_message = await utils.answer(
                message, 
                strings["generate_credentials"].format(
                    login=login, 
                    password=password, 
                    length=length,
                    count=len(self.saved_credentials)
                )
            )

            asyncio.create_task(self._delete_message_after_delay(generated_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def addcred(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                added_message = await utils.answer(message, strings["usage_addcred"])
                asyncio.create_task(self._delete_message_after_delay(added_message))
                return
            
            parts = args.split(maxsplit=2)
            if len(parts) < 2:
                added_message = await utils.answer(message, strings["usage_addcred"])
                asyncio.create_task(self._delete_message_after_delay(added_message))
                return
            
            login = parts[0]
            password = parts[1]

            
            success, result = await self._add_credential_safely(login, password, service)
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            backup_time = datetime.now().strftime('%H:%M:%S')

            response_text = strings["credentials_added"].format(
                login=login, 
                service=service, 
                count=len(self.saved_credentials),
                backup_time=backup_time
            )

            
            limit_status = self._check_limit_strict()
            if limit_status == "WARNING":
                remaining = self.MAX_CREDENTIALS - len(self.saved_credentials)
                emojis = await self._get_emojis(user_id)

            added_message = await utils.answer(message, response_text)
            asyncio.create_task(self._delete_message_after_delay(added_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def editcred(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return
            
            parts = args.split(maxsplit=3)
            if len(parts) < 3:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return
            
            try:
                index = int(parts[0]) - 1
                if index < 0 or index >= len(self.saved_credentials):
                    edited_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(edited_message))
                    return
            except ValueError:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return

            login = parts[1]
            password = parts[2]

            
            await self._create_backup()

            
            self.saved_credentials[index] = (login, password, service)
            
            
            await self._save_data_securely()

            edited_message = await utils.answer(message, strings["credentials_edited"])
            asyncio.create_task(self._delete_message_after_delay(edited_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def save(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if self.last_generated_password is None or self.last_generated_login is None:
                saved_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(saved_message))
                return

            
            success, result = await self._add_credential_safely(
                self.last_generated_login, 
                self.last_generated_password, 
            )
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            backup_time = datetime.now().strftime('%H:%M:%S')

            saved_message = await utils.answer(
                message, 
                strings["credentials_saved"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(saved_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def show(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if not self.saved_credentials:
                show_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(show_message))
                return

            credentials_list = await self._format_credentials_list(self.saved_credentials, user_id)
            backup_count = self._get_backup_count()
            
            show_message = await utils.answer(
                message, 
                strings["saved_credentials"].format(
                    credentials=credentials_list,
                    count=len(self.saved_credentials),
                    backups=backup_count
                )
            )

            
            asyncio.create_task(self._delete_message_after_delay(show_message, 60))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def gensave(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                length = 10
            else:
                try:
                    length = int(args)
                    if length <= 0 or length > 50:
                        gensave_message = await utils.answer(message, strings["usage_gen"])
                        asyncio.create_task(self._delete_message_after_delay(gensave_message))
                        return
                except ValueError:
                    gensave_message = await utils.answer(message, strings["usage_gen"])
                    asyncio.create_task(self._delete_message_after_delay(gensave_message))
                    return

            
            characters = string.ascii_letters + string.digits + "@$#%&*"
            password = ''.join(random.choices(characters, k=length))
            login_characters = string.ascii_letters + string.digits
            login = ''.join(random.choices(login_characters, k=length))

            
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            response_text = strings["generate_credentials"].format(
                login=login, 
                password=password, 
                length=length,
                count=len(self.saved_credentials)

            
            limit_status = self._check_limit_strict()
            if limit_status == "WARNING":
                remaining = self.MAX_CREDENTIALS - len(self.saved_credentials)

            gensave_message = await utils.answer(message, response_text)
            asyncio.create_task(self._delete_message_after_delay(gensave_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def clear(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if not self.saved_credentials:
                clear_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(clear_message))
                return

            
            await self._create_backup()

            
            self.saved_credentials.clear()
            
            
            await self._save_data_securely()

            clear_message = await utils.answer(message, strings["credentials_cleared"])
            asyncio.create_task(self._delete_message_after_delay(clear_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def note(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message).split(maxsplit=1)
            if len(args) < 2:
                note_message = await utils.answer(message, 
                asyncio.create_task(self._delete_message_after_delay(note_message))
                return

            try:
                index = int(args[0]) - 1
                note = args[1]
                if index < 0 or index >= len(self.saved_credentials):
                    note_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(note_message))
                    return
            except ValueError:
                note_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(note_message))
                return

            
            await self._create_backup()

            
            login, password, _ = self.saved_credentials[index]
            self.saved_credentials[index] = (login, password, note)
            
            
            await self._save_data_securely()

            note_message = await utils.answer(message, strings["note_added"])
            asyncio.create_task(self._delete_message_after_delay(note_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def delcred(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            if not args:
                delcred_message = await utils.answer(message, 
                                 f"{emojis['bullet']} <b>Пример:</b> <code>.delcred 1</code>\n\n"
                asyncio.create_task(self._delete_message_after_delay(delcred_message))
                return

            try:
                index = int(args) - 1
                if index < 0 or index >= len(self.saved_credentials):
                    delcred_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(delcred_message))
                    return
            except ValueError:
                delcred_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(delcred_message))
                return

            
            await self._create_backup()

            
            del self.saved_credentials[index]
            
            
            await self._save_data_securely()
            backup_time = datetime.now().strftime('%H:%M:%S')

            delcred_message = await utils.answer(
                message, 
                strings["credentials_deleted"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(delcred_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def createprivategroup(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            if self.private_group_id is not None:
                
                try:
                    await self.client.get_entity(self.private_group_id)
                    exists_message = await utils.answer(
                        message, 
                        strings["private_group_exists"].format(chat_id=self.private_group_id)
                    )
                    asyncio.create_task(self._delete_message_after_delay(exists_message))
                    return
                except Exception:
                    
                    self.private_group_id = None

            try:
                
                result = await self.client(CreateChannelRequest(
                    megagroup=True
                ))
                
                if hasattr(result, 'chats') and result.chats:
                    self.private_group_id = result.chats[0].id
                    
                    
                    self.db.set("KOTpassfolder", "private_group_id", self.private_group_id)
                    await self._save_data_securely()
                    
                    created_message = await utils.answer(
                        message, 
                        strings["private_group_created"].format(chat_id=self.private_group_id)
                    )
                    asyncio.create_task(self._delete_message_after_delay(created_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                    
            except Exception as e:
                
                try:
                    result = await self.client(CreateChatRequest(
                        users=[],
                    ))
                    
                    if hasattr(result, 'chats') and result.chats:
                        self.private_group_id = result.chats[0].id
                        
                        
                        self.db.set("KOTpassfolder", "private_group_id", self.private_group_id)
                        await self._save_data_securely()
                        
                        created_message = await utils.answer(
                            message, 
                            strings["private_group_created"].format(chat_id=self.private_group_id)
                        )
                        asyncio.create_task(self._delete_message_after_delay(created_message))
                    else:
                        error_message = await utils.answer(message, strings["error"])
                        asyncio.create_task(self._delete_message_after_delay(error_message))
                        
                except Exception:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def exportdata(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            if self.private_group_id is None:
                export_message = await utils.answer(message, strings["private_group_not_found"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            args = utils.get_args_raw(message)
            if not args:
                export_message = await utils.answer(message, strings["export_usage"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            try:
                if args.lower() == "all":
                    
                    if not self.saved_credentials:
                        export_message = await utils.answer(message, strings["no_saved_credentials"])
                        asyncio.create_task(self._delete_message_after_delay(export_message))
                        return
                    
                    export_text += await self._format_credentials_list(self.saved_credentials, user_id)
                    
                    
                    await self.client.send_message(self.private_group_id, export_text)
                else:
                    
                    try:
                        index = int(args) - 1
                        if index < 0 or index >= len(self.saved_credentials):
                            export_message = await utils.answer(message, strings["invalid_index"])
                            asyncio.create_task(self._delete_message_after_delay(export_message))
                            return
                    except ValueError:
                        export_message = await utils.answer(message, strings["export_usage"])
                        asyncio.create_task(self._delete_message_after_delay(export_message))
                        return

                    login, password, service = self.saved_credentials[index]
                    export_text = (
                        f"{emojis['password']} <b>Пароль:</b> <code>{password}</code>\n"
                        f"{emojis['service']} <b>Сервис:</b> {service}"
                    )
                    
                    
                    await self.client.send_message(self.private_group_id, export_text)

                
                export_message = await utils.answer(message, strings["data_exported"])
                asyncio.create_task(self._delete_message_after_delay(export_message))

            except Exception as e:
                error_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def exporttxt(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Экспорт в TXT
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            if self.private_group_id is None:
                export_message = await utils.answer(message, strings["private_group_not_found"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            if not self.saved_credentials:
                export_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            try:
                
                txt_content = self._generate_txt_content()
                
                
                txt_file = io.BytesIO(txt_content.encode('utf-8'))
                txt_file.name = f"passwords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                
                await self.client.send_file(
                    self.private_group_id,
                    txt_file,
                           f"{emojis['stats']} <b>Всего записей:</b> {len(self.saved_credentials)}/{self.MAX_CREDENTIALS}\n"
                           f"{emojis['datag']} <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                )
                
                
                await self._save_data_securely()
                
                export_message = await utils.answer(
                    message, 
                    strings["txt_exported"].format(
                        count=len(self.saved_credentials),
                        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    )
                )
                asyncio.create_task(self._delete_message_after_delay(export_message))

            except Exception as e:
                error_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def restore(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            await self._restore_data_with_limit_check()
            
            
            await self._create_backup()
            
            backup_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            restore_message = await utils.answer(
                message,
                strings["data_recovered"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(restore_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    async def backup(self, message):
        # ═══════════════════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            backup_success = await self._create_backup()
            backup_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            if backup_success:
                backup_message = await utils.answer(
                    message,
                    strings["backup_created"].format(
                        count=len(self.saved_credentials),
                        backup_time=backup_time
                    )
                )
            else:
                backup_message = await utils.answer(message, strings["error"])
            
            asyncio.create_task(self._delete_message_after_delay(backup_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════