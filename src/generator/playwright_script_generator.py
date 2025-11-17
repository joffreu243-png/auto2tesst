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
            config: Конфигурация (API token, proxy, etc.)

        Returns:
            Полный исполняемый Python скрипт
        """
        # Извлечь настройки
        api_token = config.get('api_token', '')
        use_proxy = config.get('use_proxy', False)
        proxy_config = config.get('proxy', {})
        csv_filename = config.get('csv_filename', 'data.csv')

        # Генерация скрипта
        script = self._generate_imports()
        script += self._generate_config(api_token, proxy_config, use_proxy, csv_filename)
        script += self._generate_octobrowser_functions()
        script += self._generate_csv_loader()
        script += self._generate_main_iteration(user_code)
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

    def _generate_config(self, api_token: str, proxy_config: Dict, use_proxy: bool, csv_filename: str) -> str:
        """Генерирует конфигурацию"""
        config = f'''# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

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

    def _generate_csv_loader(self) -> str:
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

    def _generate_main_iteration(self, user_code: str) -> str:
        """Генерирует главную функцию итерации"""
        # Отступ для user_code
        indented_code = '\n'.join('    ' + line if line.strip() else ''
                                  for line in user_code.split('\n'))

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

    print(f"\\n{{'='*60}}")
    print(f"Итерация #{{iteration_number}}")
    print(f"Данные: {{data_row}}")
    print(f"{{'='*60}}\\n")

    try:
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
            print(f"Подключение к Octobrowser через CDP: {{cdp_url}}")

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

            # ============================================================
            # ПОЛЬЗОВАТЕЛЬСКИЙ КОД АВТОМАТИЗАЦИИ
            # ============================================================

{indented_code}

            # ============================================================

            print(f"[OK] Итерация #{{iteration_number}} успешно завершена")
            return True

    except Exception as e:
        error_msg = str(e)
        if "target closed" in error_msg.lower() or "browser has been closed" in error_msg.lower():
            print(f"⚠️ ВНИМАНИЕ: Браузер был закрыт вручную!")
            print(f"Итерация #{{iteration_number}} прервана")
        elif "timeout" in error_msg.lower():
            print(f"⏱️ TIMEOUT: Элемент не найден в итерации #{{iteration_number}}")
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
        print(f"\\n{{'='*60}}")
        print(f"ИТОГО:")
        print(f"Всего итераций: {{total_iterations}}")
        print(f"Успешных: {{successful_iterations}}")
        print(f"С ошибками: {{failed_iterations}}")
        print(f"{{'='*60}}")

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
