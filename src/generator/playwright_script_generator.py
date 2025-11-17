"""
Генератор Playwright скриптов для автоматизации с Octobrowser
"""

import json
from typing import Dict, List


class PlaywrightScriptGenerator:
    """Генератор Playwright скриптов"""

    def generate_script(self, user_code: str, config: Dict) -> str:
        """
        Генерирует полный Playwright скрипт

        Args:
            user_code: Пользовательский код автоматизации
            config: Конфигурация (API token, proxy, sms, target, etc.)

        Returns:
            Полный исполняемый Python скрипт
        """
        # Извлечь настройки
        api_token = config.get('api_token', '')
        use_proxy = config.get('use_proxy', False)
        proxy_config = config.get('proxy', {})
        csv_filename = config.get('csv_filename', 'data.csv')
        use_sms = config.get('use_sms', False)
        sms_config = config.get('sms', {})
        target = config.get('target', 'library')  # library или cdp

        # Генерация скрипта
        script = self._generate_imports()
        script += self._generate_config(api_token, proxy_config, use_proxy, csv_filename, use_sms, sms_config, target)

        # Добавить функции Octobrowser (всегда нужны для CDP подключения)
        script += self._generate_octobrowser_functions()

        # Добавить SMS функции если включено
        if use_sms:
            script += self._generate_sms_functions(sms_config)

        script += self._generate_csv_loader(use_sms)
        script += self._generate_main_iteration(user_code, use_sms, target)
        script += self._generate_main_function()

        return script

    def _generate_imports(self) -> str:
        """Генерирует импорты"""
        return '''#!/usr/bin/env python3
"""
Автоматически сгенерированный скрипт автоматизации
Фреймворк: Playwright
Браузер: Octobrowser (через CDP)
"""

import asyncio
import csv
import time
import requests
from playwright.async_api import async_playwright
from typing import Dict, List, Optional

'''

    def _generate_config(self, api_token: str, proxy_config: Dict, use_proxy: bool,
                         csv_filename: str, use_sms: bool, sms_config: Dict, target: str) -> str:
        """Генерирует конфигурацию"""
        config = f'''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Playwright target (формат импортированного скрипта)
PLAYWRIGHT_TARGET = "{target}"  # library или cdp (только для справки, не влияет на выполнение)

# Octobrowser API
API_BASE_URL = "https://app.octobrowser.net/api/v2/automation"
API_TOKEN = "{api_token}"
LOCAL_API_URL = "http://localhost:58888/api"

# CSV файл с данными
CSV_FILENAME = "{csv_filename}"

# Прокси настройки
USE_PROXY = {use_proxy}
'''

        if use_proxy:
            config += f'''PROXY_TYPE = "{proxy_config.get('type', 'http')}"
PROXY_HOST = "{proxy_config.get('host', '')}"
PROXY_PORT = "{proxy_config.get('port', '')}"
PROXY_LOGIN = "{proxy_config.get('login', '')}"
PROXY_PASSWORD = "{proxy_config.get('password', '')}"
'''

        # SMS настройки
        config += f'''
# SMS провайдер для получения номеров и OTP
USE_SMS_PROVIDER = {use_sms}
'''

        if use_sms:
            sms_provider = sms_config.get('provider', 'daisysms')
            sms_api_key = sms_config.get('api_key', '')
            sms_service = sms_config.get('service', 'ds')

            config += f'''SMS_PROVIDER = "{sms_provider}"
SMS_API_KEY = "{sms_api_key}"
SMS_SERVICE = "{sms_service}"  # ds=Discord, go=Google, wa=WhatsApp, tg=Telegram
SMS_API_BASE_URL = "https://daisysms.com/stubs/handler_api.php"
'''

        config += '\n\n'
        return config

    def _generate_octobrowser_functions(self) -> str:
        """Генерирует функции работы с Octobrowser API"""
        return '''# ============================================================
# ФУНКЦИИ OCTOBROWSER API
# ============================================================

def create_profile() -> Optional[str]:
    """Создание профиля через Octobrowser API"""
    url = f"{API_BASE_URL}/profiles"
    headers = {"X-Octo-Api-Token": API_TOKEN}

    profile_data = {
        "title": f"AutoProfile_{int(time.time())}",
    }

    # Добавить прокси если включено
    if USE_PROXY:
        profile_data["proxy"] = {
            "type": PROXY_TYPE,
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "login": PROXY_LOGIN,
            "password": PROXY_PASSWORD
        }
        print(f"[PROXY] Установлен прокси: {PROXY_TYPE}://{PROXY_HOST}:{PROXY_PORT}")

    try:
        response = requests.post(url, headers=headers, json=profile_data)
        response.raise_for_status()
        result = response.json()

        if result.get('success') and 'data' in result:
            profile_uuid = result['data']['uuid']
            print(f"[OK] Профиль создан: {profile_uuid}")
            return profile_uuid
        else:
            print(f"[ERROR] Не удалось создать профиль: {result}")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка создания профиля: {e}")
        return None


def start_profile(profile_uuid: str) -> Optional[str]:
    """Запуск профиля через локальный API"""
    url = f"{LOCAL_API_URL}/profiles/start"
    payload = {
        "uuid": profile_uuid,
        "headless": False,
        "debug_port": True
    }

    try:
        print(f"Запуск профиля {profile_uuid}...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        debug_port = result.get('debug_port')
        if debug_port:
            print(f"[OK] Профиль запущен на порту: {debug_port}")
            # Подождать инициализации
            time.sleep(3)
            return str(debug_port)
        else:
            print(f"[ERROR] Не получен debug_port: {result}")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка запуска профиля: {e}")
        return None


def stop_profile(profile_uuid: str) -> bool:
    """Остановка профиля"""
    url = f"{LOCAL_API_URL}/profiles/stop"
    payload = {"uuid": profile_uuid}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"[OK] Профиль {profile_uuid} остановлен")
        return True
    except Exception as e:
        print(f"[WARNING] Не удалось остановить профиль: {e}")
        return False


'''

    def _generate_sms_functions(self, sms_config: Dict) -> str:
        """Генерирует функции для работы с SMS API"""
        return '''# ============================================================
# ФУНКЦИИ SMS ПРОВАЙДЕРА (DaisySMS)
# ============================================================

def get_phone_number() -> Optional[Dict]:
    """
    Получить номер телефона от SMS провайдера

    Returns:
        Dict: {'activation_id': str, 'phone_number': str} или None
    """
    url = SMS_API_BASE_URL
    params = {
        'api_key': SMS_API_KEY,
        'action': 'getNumber',
        'service': SMS_SERVICE
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.text.strip()

        # Формат: ACCESS_NUMBER:ID:PHONE_NUMBER
        if result.startswith('ACCESS_NUMBER:'):
            parts = result.split(':')
            activation_id = parts[1]
            phone_number = parts[2]

            print(f"[SMS] Получен номер: {phone_number} (ID: {activation_id})")
            return {
                'activation_id': activation_id,
                'phone_number': phone_number
            }
        else:
            print(f"[SMS ERROR] Ошибка получения номера: {result}")
            return None

    except Exception as e:
        print(f"[SMS ERROR] Ошибка запроса: {e}")
        return None


def get_sms_code(activation_id: str, timeout: int = 180) -> Optional[str]:
    """
    Получить SMS код (OTP)

    Args:
        activation_id: ID активации от get_phone_number
        timeout: Максимальное время ожидания в секундах

    Returns:
        str: OTP код или None
    """
    url = SMS_API_BASE_URL
    start_time = time.time()
    poll_interval = 3  # Минимум 3 секунды между запросами

    print(f"[SMS] Ожидание SMS кода (макс. {timeout}s)...")

    while (time.time() - start_time) < timeout:
        params = {
            'api_key': SMS_API_KEY,
            'action': 'getStatus',
            'id': activation_id
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.text.strip()

            # STATUS_OK:CODE - SMS получено
            if result.startswith('STATUS_OK:'):
                code = result.split(':')[1]
                print(f"[SMS] [OK] Получен OTP код: {code}")
                return code

            # STATUS_WAIT_CODE - ожидание
            elif result == 'STATUS_WAIT_CODE':
                elapsed = int(time.time() - start_time)
                print(f"[SMS] Ожидание... ({elapsed}s/{timeout}s)")
                time.sleep(poll_interval)
                continue

            # STATUS_CANCEL - отменено
            elif result == 'STATUS_CANCEL':
                print(f"[SMS ERROR] Активация отменена")
                return None

            # NO_ACTIVATION - неверный ID
            elif result == 'NO_ACTIVATION':
                print(f"[SMS ERROR] Активация не найдена")
                return None

            else:
                print(f"[SMS] Статус: {result}")
                time.sleep(poll_interval)

        except Exception as e:
            print(f"[SMS ERROR] Ошибка запроса: {e}")
            time.sleep(poll_interval)

    print(f"[SMS ERROR] Превышено время ожидания ({timeout}s)")
    return None


def cancel_sms_activation(activation_id: str) -> bool:
    """Отменить SMS активацию"""
    url = SMS_API_BASE_URL
    params = {
        'api_key': SMS_API_KEY,
        'action': 'setStatus',
        'id': activation_id,
        'status': 8  # 8 = отмена
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        result = response.text.strip()

        if result == 'ACCESS_CANCEL':
            print(f"[SMS] Активация {activation_id} отменена")
            return True
        else:
            print(f"[SMS ERROR] Не удалось отменить: {result}")
            return False

    except Exception as e:
        print(f"[SMS ERROR] Ошибка отмены: {e}")
        return False


'''

    def _generate_csv_loader(self, use_sms: bool = False) -> str:
        """Генерирует функцию загрузки CSV"""
        return '''# ============================================================
# ЗАГРУЗКА ДАННЫХ ИЗ CSV
# ============================================================

def load_data_from_csv(filename: str) -> List[Dict]:
    """Загружает данные из CSV файла"""
    try:
        data_rows = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_rows.append(row)

        print(f"[OK] CSV файл найден: {filename}")
        print(f"Загружено {len(data_rows)} строк данных")
        return data_rows

    except FileNotFoundError:
        print(f"[ERROR] CSV файл не найден: {filename}")
        print("Создайте CSV файл с данными перед запуском!")
        return []
    except Exception as e:
        print(f"[ERROR] Ошибка чтения CSV: {e}")
        return []


'''

    def _generate_main_iteration(self, user_code: str, use_sms: bool = False, target: str = 'library') -> str:
        """Генерирует главную функцию итерации"""
        # Отступ для user_code (12 пробелов - внутри async with блока)
        indented_code = '\n'.join(' ' * 12 + line if line.strip() else ''
                                  for line in user_code.split('\n'))

        # Добавить SMS блок если включено
        sms_block = ''
        if use_sms:
            sms_block = '''
        # ============================================================
        # ПОЛУЧЕНИЕ НОМЕРА И OTP ОТ SMS ПРОВАЙДЕРА
        # ============================================================

        sms_activation_id = None

        if USE_SMS_PROVIDER:
            print("[SMS] Получение номера телефона...")

            # Получить номер
            sms_data = get_phone_number()
            if sms_data:
                sms_activation_id = sms_data['activation_id']
                phone_number = sms_data['phone_number']

                # Добавить номер в данные
                data_row['phone_number'] = phone_number
                print(f"[SMS] [OK] Номер добавлен в data_row: {phone_number}")
            else:
                print("[SMS ERROR] Не удалось получить номер")
                # Продолжаем выполнение - возможно номер не нужен
'''

        # Добавить OTP блок в user_code если используется SMS
        otp_helper = ''
        if use_sms:
            otp_helper = '''
            # ============================================================
            # ХЕЛПЕР ДЛЯ ПОЛУЧЕНИЯ OTP
            # ============================================================
            # Если в data_row запрашивается 'otp_code', получить его из SMS
            if USE_SMS_PROVIDER and 'otp_code' in data_row and sms_activation_id:
                if not data_row.get('otp_code'):  # Если еще не получен
                    print("[SMS] Получение OTP кода...")
                    otp_code = get_sms_code(sms_activation_id, timeout=180)
                    if otp_code:
                        data_row['otp_code'] = otp_code
                        print(f"[SMS] [OK] OTP добавлен в data_row: {otp_code}")
                    else:
                        print("[SMS ERROR] Не удалось получить OTP")
                        data_row['otp_code'] = ""

'''

        # ВСЕГДА используем Octobrowser (CDP режим)
        # Target влияет только на парсинг импортированного скрипта, но не на выполнение
        browser_launch_code = f'''
        # Создать профиль
        profile_uuid = create_profile()
        if not profile_uuid:
            print("[ERROR] Не удалось создать профиль")
            return False

        # Запустить профиль
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("[ERROR] Не удалось запустить профиль")
            return False

        # Подключиться к браузеру через CDP
        async with async_playwright() as p:
            cdp_url = f"http://127.0.0.1:{{debug_port}}"
            print(f"[CDP MODE] Подключение к Octobrowser через CDP: {{cdp_url}}")

            try:
                browser = await p.chromium.connect_over_cdp(cdp_url)
                print("[OK] Playwright подключен к Octobrowser")
            except Exception as e:
                print(f"[ERROR] Не удалось подключиться к CDP: {{e}}")
                return False

            # Получить контекст и страницу
            if browser.contexts:
                context = browser.contexts[0]
                if context.pages:
                    page = context.pages[0]
                else:
                    page = await context.new_page()
            else:
                print("[ERROR] Нет доступных контекстов браузера")
                return False

            print(f"[OK] Страница готова к автоматизации")
{otp_helper}
            # ============================================================
            # ПОЛЬЗОВАТЕЛЬСКИЙ КОД АВТОМАТИЗАЦИИ
            # ============================================================

{indented_code}

            # ============================================================

            print(f"[OK] Итерация #{{iteration_number}} успешно завершена")
            return True'''

        return f'''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ ИТЕРАЦИИ
# ============================================================

async def run_automation_iteration(iteration_number: int, data_row: Dict):
    """
    Запуск одной итерации автоматизации с Playwright

    Args:
        iteration_number: Номер итерации
        data_row: Данные из CSV для этой итерации
    """
    profile_uuid = None
    browser = None
    context = None
    page = None

    print("\\n" + "="*60)
    print(f"Итерация #{{iteration_number}}")
    print(f"Данные: {{data_row}}")
    print("="*60 + "\\n")

    try:{sms_block}{browser_launch_code}

    except Exception as e:
        error_msg = str(e)
        if "target closed" in error_msg.lower() or "browser has been closed" in error_msg.lower():
            print(f"[!] ВНИМАНИЕ: Браузер был закрыт вручную!")
            print(f"Итерация #{{iteration_number}} прервана")
        elif "timeout" in error_msg.lower():
            print(f"[TIMEOUT] Элемент не найден в итерации #{{iteration_number}}")
            print(f"Возможно страница загружается слишком долго")
        else:
            print(f"[ERROR] Ошибка в итерации #{{iteration_number}}: {{e}}")

        import traceback
        traceback.print_exc()
        return False

    finally:
        # Закрыть браузер
        if browser:
            try:
                await browser.close()
                print("[OK] Браузер закрыт")
            except:
                pass

        # Остановить профиль
        if profile_uuid:
            try:
                stop_profile(profile_uuid)
            except:
                pass


'''

    def _generate_main_function(self) -> str:
        """Генерирует главную функцию"""
        return '''# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

async def main():
    """Главная функция с мультизапуском"""
    try:
        # Загрузить данные из CSV
        data_rows = load_data_from_csv(CSV_FILENAME)

        if not data_rows:
            print("[ERROR] Нет данных для обработки!")
            return

        # Статистика
        total_iterations = len(data_rows)
        successful_iterations = 0
        failed_iterations = 0

        print(f"\\nЗапуск автоматизации для {{total_iterations}} строк данных\\n")

        # Запуск для каждой строки
        for i, data_row in enumerate(data_rows, start=1):
            success = await run_automation_iteration(i, data_row)

            if success:
                successful_iterations += 1
            else:
                failed_iterations += 1

            # Пауза между итерациями
            if i < total_iterations:
                pause_seconds = 5
                print(f"\\nПауза {{pause_seconds}} секунд перед следующей итерацией...")
                await asyncio.sleep(pause_seconds)

        # Итоговая статистика
        print("\\n" + "="*60)
        print("ИТОГО:")
        print(f"Всего итераций: {{total_iterations}}")
        print(f"Успешных: {{successful_iterations}}")
        print(f"С ошибками: {{failed_iterations}}")
        print("="*60)

    except KeyboardInterrupt:
        print("\\n[ПРЕРВАНО] Выполнение остановлено пользователем")
    except Exception as e:
        print(f"\\n[ERROR] Критическая ошибка: {{e}}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Octobrowser Automation Script (Playwright)")
    print("="*60)
    asyncio.run(main())
'''


def generate_playwright_script(user_code: str, config: Dict) -> str:
    """
    Вспомогательная функция для генерации Playwright скрипта

    Args:
        user_code: Код автоматизации
        config: Конфигурация

    Returns:
        Полный скрипт
    """
    generator = PlaywrightScriptGenerator()
    return generator.generate_script(user_code, config)
