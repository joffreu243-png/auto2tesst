"""
Генератор Python скриптов для автоматизации с Octobrowser
"""
from typing import Dict, List, Optional
from datetime import datetime


class ScriptGenerator:
    """Класс для генерации Python скриптов автоматизации"""

    def __init__(self):
        self.imports = set()
        self.code_blocks = []
        self.config = {}

    def reset(self):
        """Сброс состояния генератора"""
        self.imports = set()
        self.code_blocks = []
        self.config = {}

    def set_config(self, config: Dict):
        """Установка конфигурации скрипта"""
        self.config = config

    def add_import(self, import_statement: str):
        """Добавление импорта"""
        self.imports.add(import_statement)

    def add_code_block(self, code: str, priority: int = 100):
        """
        Добавление блока кода

        Args:
            code: Код для добавления
            priority: Приоритет выполнения (меньше = раньше)
        """
        self.code_blocks.append((priority, code))

    def _generate_header(self) -> str:
        """Генерация заголовка скрипта"""
        header = f'''"""
Автоматически сгенерированный скрипт автоматизации
Создан: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Генератор: Octobrowser Script Builder
"""

'''
        return header

    def _generate_imports(self) -> str:
        """Генерация секции импортов"""
        if not self.imports:
            return ""

        imports_code = "\n".join(sorted(self.imports))
        return f"{imports_code}\n\n"

    def _generate_config_section(self) -> str:
        """Генерация секции конфигурации"""
        if not self.config:
            return ""

        config_code = "# Конфигурация\n"
        config_code += f"API_TOKEN = '{self.config.get('api_token', 'YOUR_API_TOKEN')}'\n"
        config_code += f"API_BASE_URL = '{self.config.get('api_base_url', 'https://app.octobrowser.net/api/v2/automation')}'\n\n"

        return config_code

    def _generate_profile_creation(self, profile_config: Dict) -> str:
        """Генерация кода создания профиля"""
        code = '''
def create_profile():
    """Создание профиля в Octobrowser"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    profile_data = {
'''

        # Добавляем настройки профиля
        if profile_config.get('title'):
            code += f"        'title': '{profile_config['title']}',\n"

        if profile_config.get('tags'):
            code += f"        'tags': {profile_config['tags']},\n"

        if profile_config.get('fingerprint'):
            code += f"        'fingerprint': {profile_config['fingerprint']},\n"

        if profile_config.get('proxy'):
            proxy = profile_config['proxy']
            code += f'''        'proxy': {{
            'type': '{proxy.get('type', 'http')}',
            'host': '{proxy.get('host', '')}',
            'port': {proxy.get('port', 0)},
            'login': '{proxy.get('login', '')}',
            'password': '{proxy.get('password', '')}'
        }},\n'''

        code += '''    }

    response = requests.post(
        f"{API_BASE_URL}/profiles",
        headers=headers,
        json=profile_data
    )

    if response.status_code == 200:
        profile = response.json()
        print(f"Профиль создан: {profile.get('uuid')}")
        return profile.get('uuid')
    else:
        print(f"Ошибка создания профиля: {response.text}")
        return None

'''
        return code

    def _generate_profile_start(self) -> str:
        """Генерация кода запуска профиля"""
        code = '''
def start_profile(profile_uuid):
    """Запуск профиля и получение debug port"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"{API_BASE_URL}/profiles/{profile_uuid}/start",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        debug_port = data.get('debug_port')
        print(f"Профиль запущен на порту: {debug_port}")
        return debug_port
    else:
        print(f"Ошибка запуска профиля: {response.text}")
        return None

'''
        return code

    def _generate_selenium_connection(self) -> str:
        """Генерация кода подключения Selenium"""
        code = '''
def connect_selenium(debug_port):
    """Подключение Selenium к профилю"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")

    driver = webdriver.Chrome(options=options)
    print("Selenium подключен к профилю")
    return driver

'''
        return code

    def _generate_profile_stop(self) -> str:
        """Генерация кода остановки профиля"""
        code = '''
def stop_profile(profile_uuid):
    """Остановка профиля"""
    import requests

    headers = {
        'X-Octo-Api-Token': API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        f"{API_BASE_URL}/profiles/{profile_uuid}/stop",
        headers=headers
    )

    if response.status_code == 200:
        print("Профиль остановлен")
        return True
    else:
        print(f"Ошибка остановки профиля: {response.text}")
        return False

'''
        return code

    def _generate_main_function(self, user_code: str, use_profile_creation: bool,
                                use_selenium: bool, cleanup_profile: bool) -> str:
        """Генерация главной функции"""
        code = '''
def main():
    """Главная функция автоматизации"""
    profile_uuid = None
    driver = None

    try:
'''

        # Создание профиля
        if use_profile_creation:
            code += '''        # Создание профиля
        profile_uuid = create_profile()
        if not profile_uuid:
            print("Не удалось создать профиль")
            return

        # Запуск профиля
        debug_port = start_profile(profile_uuid)
        if not debug_port:
            print("Не удалось запустить профиль")
            return

'''

        # Подключение Selenium
        if use_selenium:
            code += '''        # Подключение Selenium
        driver = connect_selenium(debug_port)

'''

        # Пользовательский код
        if user_code.strip():
            code += f'''        # Пользовательский код автоматизации
{self._indent_code(user_code, 2)}

'''

        # Cleanup
        code += '''    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        import traceback
        traceback.print_exc()

    finally:
'''

        if use_selenium:
            code += '''        # Закрытие браузера
        if driver:
            driver.quit()

'''

        if cleanup_profile:
            code += '''        # Остановка и удаление профиля
        if profile_uuid:
            stop_profile(profile_uuid)
            # Можно добавить удаление профиля если нужно

'''

        code += '''
if __name__ == "__main__":
    main()
'''

        return code

    def _indent_code(self, code: str, indent_level: int) -> str:
        """Добавление отступов к коду"""
        indent = "    " * indent_level
        lines = code.split('\n')
        return '\n'.join([indent + line if line.strip() else line for line in lines])

    def generate_script(self, options: Dict, user_code: str = "") -> str:
        """
        Генерация полного скрипта

        Args:
            options: Опции генерации
            user_code: Пользовательский код автоматизации

        Returns:
            Полный код скрипта
        """
        self.reset()

        # Устанавливаем конфигурацию из options
        self.set_config(options)

        # Базовые импорты
        self.add_import("import time")
        self.add_import("import sys")

        script = self._generate_header()
        script += self._generate_imports()
        script += self._generate_config_section()

        # Добавляем функции в зависимости от опций
        if options.get('create_profile', False):
            script += self._generate_profile_creation(options.get('profile_config', {}))
            script += self._generate_profile_start()
            script += self._generate_profile_stop()

        if options.get('use_selenium', False):
            script += self._generate_selenium_connection()

        # Главная функция
        script += self._generate_main_function(
            user_code,
            options.get('create_profile', False),
            options.get('use_selenium', False),
            options.get('cleanup_profile', False)
        )

        return script
