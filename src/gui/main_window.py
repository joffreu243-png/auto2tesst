"""
Главное окно GUI приложения-конструктора скриптов
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
from pathlib import Path
from datetime import datetime

# Импорты из проекта
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.octobrowser_api import OctobrowserAPI
from src.generator.script_generator import ScriptGenerator
from src.generator.playwright_script_generator import PlaywrightScriptGenerator
from src.runner.script_runner import ScriptRunner
from src.utils.script_parser import ScriptParser
from src.utils.selenium_ide_parser import SeleniumIDEParser
from src.utils.playwright_parser import PlaywrightParser
from src.sms.provider_manager import ProviderManager
from src.data.dynamic_field import DynamicFieldManager, DynamicField, FieldType


class OctobrowserScriptBuilder:
    """Главное окно приложения-конструктора"""

    def __init__(self, root):
        self.root = root
        self.root.title("Octobrowser Script Builder - Конструктор скриптов автоматизации")

        # Увеличенное окно для удобства
        self.root.geometry("1400x900")

        # Минимальный размер окна
        self.root.minsize(1200, 700)

        # Загрузка конфигурации
        self.load_config()

        # Инициализация компонентов
        self.api = None
        self.generator = ScriptGenerator()  # Selenium генератор
        self.playwright_generator = PlaywrightScriptGenerator()  # Playwright генератор
        self.runner = ScriptRunner()
        self.runner.set_output_callback(self.append_output)
        self.parser = ScriptParser()
        self.side_parser = SeleniumIDEParser()
        self.playwright_parser = PlaywrightParser()

        # SMS провайдеры
        self.sms_provider_manager = ProviderManager()
        self.dynamic_field_manager = DynamicFieldManager()

        # Данные для импортированного скрипта
        self.imported_data = None  # Извлеченные данные из внешнего скрипта
        self.csv_data_rows = []    # Строки для CSV таблицы

        # Создание интерфейса
        self.create_widgets()

        # Загрузить сохраненные настройки в UI
        self.load_saved_settings()

        # НЕ инициализируем API автоматически - это вызывает лаги
        # Пользователь должен нажать "Подключить API" сам

    def load_config(self):
        """Загрузка конфигурации"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Дефолтная конфигурация
            self.config = {
                'octobrowser': {
                    'api_base_url': 'https://app.octobrowser.net/api/v2/automation',
                    'api_token': ''
                },
                'sms': {
                    'provider': 'daisysms',
                    'api_key': '',
                    'service': 'ds'
                },
                'proxy': {
                    'enabled': False,
                    'type': 'http',
                    'host': '',
                    'port': '',
                    'login': '',
                    'password': ''
                },
                'ui_settings': {
                    'last_csv_path': '',
                    'automation_framework': 'playwright',
                    'playwright_target': 'library'
                },
                'script_settings': {
                    'output_directory': 'generated_scripts',
                    'default_automation_framework': 'playwright'
                }
            }

    def save_config(self):
        """Сохранение конфигурации"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def load_saved_settings(self):
        """Загружает сохраненные настройки в UI поля"""
        # SMS настройки
        sms_config = self.config.get('sms', {})
        if sms_config.get('api_key'):
            self.sms_api_key_entry.insert(0, sms_config['api_key'])
        if sms_config.get('service'):
            self.sms_service_var.set(sms_config['service'])

        # Proxy настройки
        proxy_config = self.config.get('proxy', {})
        if proxy_config.get('enabled'):
            self.use_proxy_var.set(True)
            self.toggle_proxy_options()  # Показать поля прокси

        if proxy_config.get('type'):
            self.proxy_type_var.set(proxy_config['type'])
        if proxy_config.get('host'):
            self.proxy_host_entry.insert(0, proxy_config['host'])
        if proxy_config.get('port'):
            self.proxy_port_entry.insert(0, proxy_config['port'])
        if proxy_config.get('login'):
            self.proxy_login_entry.insert(0, proxy_config['login'])
        if proxy_config.get('password'):
            self.proxy_password_entry.insert(0, proxy_config['password'])

        # Octobrowser API token
        octo_config = self.config.get('octobrowser', {})
        if octo_config.get('api_token'):
            self.api_token_entry.insert(0, octo_config['api_token'])

        # UI настройки
        ui_settings = self.config.get('ui_settings', {})
        if ui_settings.get('automation_framework'):
            self.automation_framework_var.set(ui_settings['automation_framework'])
        if ui_settings.get('playwright_target'):
            self.playwright_target_var.set(ui_settings['playwright_target'])
        if ui_settings.get('last_csv_path'):
            self.csv_path_entry.insert(0, ui_settings['last_csv_path'])

    def save_settings(self):
        """Сохраняет текущие настройки из UI в config"""
        # SMS настройки
        self.config.setdefault('sms', {})
        self.config['sms']['api_key'] = self.sms_api_key_entry.get().strip()
        self.config['sms']['service'] = self.sms_service_var.get()
        self.config['sms']['provider'] = self.sms_provider_var.get()

        # Proxy настройки
        self.config.setdefault('proxy', {})
        self.config['proxy']['enabled'] = self.use_proxy_var.get()
        self.config['proxy']['type'] = self.proxy_type_var.get()
        self.config['proxy']['host'] = self.proxy_host_entry.get().strip()
        self.config['proxy']['port'] = self.proxy_port_entry.get().strip()
        self.config['proxy']['login'] = self.proxy_login_entry.get().strip()
        self.config['proxy']['password'] = self.proxy_password_entry.get().strip()

        # Octobrowser API token
        self.config.setdefault('octobrowser', {})
        self.config['octobrowser']['api_token'] = self.api_token_entry.get().strip()

        # UI настройки
        self.config.setdefault('ui_settings', {})
        self.config['ui_settings']['automation_framework'] = self.automation_framework_var.get()
        self.config['ui_settings']['playwright_target'] = self.playwright_target_var.get()
        self.config['ui_settings']['last_csv_path'] = self.csv_path_entry.get().strip()

        # Сохранить в файл
        self.save_config()

    def init_api(self, show_messages: bool = True):
        """
        Инициализация API клиента

        Args:
            show_messages: Показывать ли сообщения об успехе/ошибках
        """
        try:
            token = self.config['octobrowser']['api_token']
            base_url = self.config['octobrowser']['api_base_url']
            self.api = OctobrowserAPI(token, base_url)

            # Проверяем подключение, получая список профилей
            self.status_label.config(text="⏳ Проверка подключения...", foreground="orange")
            self.root.update_idletasks()

            result = self.api.get_profiles(page=0, page_len=10)

            if 'error' in result:
                error_msg = result.get('error', 'Неизвестная ошибка')
                status_code = result.get('status_code', '')
                url = result.get('url', '')
                api_error = result.get('api_error', {})

                self.status_label.config(
                    text=f"✗ Ошибка API ({status_code})",
                    foreground="red"
                )

                if show_messages:
                    # Формируем детальное сообщение об ошибке
                    error_details = f"Не удалось подключиться к API:\n\n"
                    error_details += f"Код ошибки: {status_code}\n"
                    error_details += f"Сообщение: {error_msg}\n\n"

                    if url:
                        error_details += f"URL: {url}\n\n"

                    if api_error:
                        error_details += f"Детали от API:\n{api_error}\n\n"

                    # Советы по исправлению
                    if status_code == 400:
                        error_details += "❗ Возможные причины:\n"
                        error_details += "- Неверный формат запроса\n"
                        error_details += "- Проверьте правильность API URL в настройках\n"
                        error_details += f"- Должен быть: https://app.octobrowser.net/api/v2/automation\n"
                    elif status_code == 401:
                        error_details += "❗ Возможные причины:\n"
                        error_details += "- Неверный API токен\n"
                        error_details += "- Токен истек или был отозван\n"
                    elif status_code == 429:
                        error_details += "❗ Превышен лимит запросов к API\n"
                        error_details += "Подождите несколько минут и попробуйте снова\n"
                    else:
                        error_details += "Проверьте токен и подключение к интернету."

                    messagebox.showerror("Ошибка подключения", error_details)
            else:
                # Получаем общее количество профилей
                # Проверяем разные возможные ключи для количества
                total_profiles = result.get('total',
                                           result.get('count',
                                           result.get('total_count', 0)))

                # Если total = 0, возможно профили в списке data
                if total_profiles == 0 and 'data' in result:
                    total_profiles = len(result.get('data', []))

                self.status_label.config(
                    text=f"✓ API подключен | Профилей: {total_profiles}",
                    foreground="green"
                )
                if show_messages:
                    # Показываем дополнительную информацию для отладки
                    debug_info = f"API успешно подключен!\n\n"
                    debug_info += f"Всего профилей: {total_profiles}\n\n"
                    debug_info += f"✓ API токен сохранен в config.json\n"
                    debug_info += f"Теперь не нужно вводить токен при каждом запуске!"

                    # Показываем структуру ответа для отладки
                    if total_profiles == 0:
                        debug_info += "📊 Структура ответа API:\n"
                        debug_info += f"Ключи: {', '.join(result.keys())}\n\n"
                        if 'data' in result:
                            debug_info += f"Элементов в data: {len(result.get('data', []))}\n"

                    messagebox.showinfo("Успех", debug_info)
        except Exception as e:
            self.status_label.config(text=f"✗ Ошибка: {str(e)}", foreground="red")
            if show_messages:
                messagebox.showerror("Ошибка", f"Ошибка инициализации API:\n{str(e)}")

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # === ВЕРХНЕЕ МЕНЮ ===
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="📖 Альтернативные сценарии", command=self.show_alternatives_help)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.show_about)

        # Главный контейнер с улучшенными пропорциями
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая панель - настройки (минимум 380px, оптимально 450px)
        left_panel = ttk.Frame(main_container, width=450)
        main_container.add(left_panel, weight=1)

        # Правая панель - код и вывод (больше места для редактора)
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=3)

        # === ЛЕВАЯ ПАНЕЛЬ ===
        self.create_left_panel(left_panel)

        # === ПРАВАЯ ПАНЕЛЬ ===
        self.create_right_panel(right_panel)

    def create_left_panel(self, parent):
        """Создание левой панели с настройками"""
        # Canvas для прокрутки
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ИСПРАВЛЕНИЕ: Добавляем прокрутку колесом мыши
        def on_mousewheel(event):
            """Обработка прокрутки колесом мыши"""
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            """Обработка прокрутки для Linux"""
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        # Привязываем события прокрутки
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/MacOS
        canvas.bind_all("<Button-4>", on_mousewheel_linux)  # Linux scroll up
        canvas.bind_all("<Button-5>", on_mousewheel_linux)  # Linux scroll down

        # Сохраняем canvas для отвязки событий при закрытии
        self.left_panel_canvas = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === API НАСТРОЙКИ ===
        api_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Настройки API", padding=10)
        api_frame.pack(fill=tk.X, padx=5, pady=5)

        # API URL
        ttk.Label(api_frame, text="API URL:").pack(anchor=tk.W)
        self.api_url_entry = ttk.Entry(api_frame, width=40)
        self.api_url_entry.insert(0, self.config['octobrowser']['api_base_url'])
        self.api_url_entry.pack(fill=tk.X, pady=(0, 5))

        # API Token
        ttk.Label(api_frame, text="API Token:").pack(anchor=tk.W)
        self.api_token_entry = ttk.Entry(api_frame, width=50)
        # Токен загружается через load_saved_settings(), не вставляем здесь
        self.api_token_entry.pack(fill=tk.X, pady=(0, 5))

        # Кнопки
        btn_frame = ttk.Frame(api_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Подключить API", command=self.connect_api).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(btn_frame, text="Сбросить", command=self.reset_api_settings).pack(side=tk.LEFT, padx=(2, 0))

        self.status_label = ttk.Label(api_frame, text="✗ API не подключен", foreground="red")
        self.status_label.pack(pady=5)

        # === ФУНКЦИИ ПРОФИЛЯ ===
        profile_frame = ttk.LabelFrame(scrollable_frame, text="👤 Настройки профиля", padding=10)
        profile_frame.pack(fill=tk.X, padx=5, pady=5)

        # Создание профиля
        self.create_profile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(profile_frame, text="Создать новый профиль",
                       variable=self.create_profile_var,
                       command=self.toggle_profile_options).pack(anchor=tk.W)

        # Опции профиля
        self.profile_options_frame = ttk.Frame(profile_frame)
        self.profile_options_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.profile_options_frame, text="Название профиля:").pack(anchor=tk.W)
        self.profile_title_entry = ttk.Entry(self.profile_options_frame, width=35)
        self.profile_title_entry.insert(0, f"AutoProfile_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.profile_title_entry.pack(fill=tk.X, pady=(0, 5))

        # Удалить профиль после выполнения
        self.cleanup_profile_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.profile_options_frame, text="Остановить профиль после выполнения",
                       variable=self.cleanup_profile_var).pack(anchor=tk.W)

        # === FINGERPRINT ===
        fingerprint_frame = ttk.LabelFrame(scrollable_frame, text="🔒 Fingerprint", padding=10)
        fingerprint_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_random_fingerprint_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fingerprint_frame, text="Использовать случайный fingerprint",
                       variable=self.use_random_fingerprint_var).pack(anchor=tk.W)

        ttk.Label(fingerprint_frame, text="Тип ОС:").pack(anchor=tk.W, pady=(5, 0))
        self.os_type_var = tk.StringVar(value="win")
        os_frame = ttk.Frame(fingerprint_frame)
        os_frame.pack(fill=tk.X, padx=20)
        ttk.Radiobutton(os_frame, text="Windows", variable=self.os_type_var, value="win").pack(side=tk.LEFT)
        ttk.Radiobutton(os_frame, text="macOS", variable=self.os_type_var, value="mac").pack(side=tk.LEFT)
        ttk.Radiobutton(os_frame, text="Linux", variable=self.os_type_var, value="linux").pack(side=tk.LEFT)

        # === ФРЕЙМВОРК АВТОМАТИЗАЦИИ ===
        framework_frame = ttk.LabelFrame(scrollable_frame, text="🎭 Фреймворк автоматизации", padding=10)
        framework_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(framework_frame, text="Выберите фреймворк:").pack(anchor=tk.W, pady=(0, 5))
        self.automation_framework_var = tk.StringVar(value="playwright")

        framework_options_frame = ttk.Frame(framework_frame)
        framework_options_frame.pack(fill=tk.X, padx=10)

        ttk.Radiobutton(framework_options_frame, text="🎭 Playwright (рекомендуется)",
                       variable=self.automation_framework_var, value="playwright",
                       command=self.toggle_playwright_target).pack(anchor=tk.W)
        ttk.Radiobutton(framework_options_frame, text="🔧 Selenium",
                       variable=self.automation_framework_var, value="selenium",
                       command=self.toggle_playwright_target).pack(anchor=tk.W)

        # Playwright Target (Library vs CDP)
        self.playwright_target_frame = ttk.Frame(framework_frame)
        self.playwright_target_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Label(self.playwright_target_frame, text="Playwright режим:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W)

        self.playwright_target_var = tk.StringVar(value="library")

        target_options = ttk.Frame(self.playwright_target_frame)
        target_options.pack(fill=tk.X, padx=10, pady=(5, 0))

        ttk.Radiobutton(target_options, text="📚 Library (прямой запуск браузера)",
                       variable=self.playwright_target_var, value="library").pack(anchor=tk.W)
        ttk.Radiobutton(target_options, text="🔌 CDP (подключение к Octobrowser)",
                       variable=self.playwright_target_var, value="cdp").pack(anchor=tk.W)

        target_info = """
Library: Playwright запускает свой браузер напрямую
• Быстрее и проще
• Не требует Octobrowser
• Подходит для большинства задач

CDP: Подключение к запущенному Octobrowser
• Использует профили Octobrowser
• Нужен запущенный Octobrowser
• Для работы с fingerprints и прокси
        """
        ttk.Label(self.playwright_target_frame, text=target_info.strip(), justify=tk.LEFT,
                 foreground="blue", font=("TkDefaultFont", 7)).pack(anchor=tk.W, padx=10, pady=(5, 0))

        # Описание фреймворков
        info_text = """
Playwright:
• Автоматические ожидания элементов
• Стабильнее работает
• Надёжные селекторы (role, testId)

Selenium:
• Классический подход
• Ручные ожидания WebDriverWait
• XPath, CSS селекторы
        """
        ttk.Label(framework_frame, text=info_text.strip(), justify=tk.LEFT,
                 foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=10, pady=5)

        # === PROXY ===
        proxy_frame = ttk.LabelFrame(scrollable_frame, text="🌐 Прокси", padding=10)
        proxy_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_proxy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(proxy_frame, text="Использовать прокси",
                       variable=self.use_proxy_var,
                       command=self.toggle_proxy_options).pack(anchor=tk.W)

        self.proxy_options_frame = ttk.Frame(proxy_frame)
        self.proxy_options_frame.pack(fill=tk.X, padx=20, pady=5)

        # Тип прокси
        ttk.Label(self.proxy_options_frame, text="Тип:").grid(row=0, column=0, sticky=tk.W)
        self.proxy_type_var = tk.StringVar(value="http")
        proxy_type_combo = ttk.Combobox(self.proxy_options_frame, textvariable=self.proxy_type_var,
                                       values=["http", "https", "socks5"], width=10, state="readonly")
        proxy_type_combo.grid(row=0, column=1, sticky=tk.W, pady=2)

        # Хост и порт
        ttk.Label(self.proxy_options_frame, text="Хост:").grid(row=1, column=0, sticky=tk.W)
        self.proxy_host_entry = ttk.Entry(self.proxy_options_frame, width=25)
        self.proxy_host_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)

        ttk.Label(self.proxy_options_frame, text="Порт:").grid(row=2, column=0, sticky=tk.W)
        self.proxy_port_entry = ttk.Entry(self.proxy_options_frame, width=10)
        self.proxy_port_entry.grid(row=2, column=1, sticky=tk.W, pady=2)

        # Логин и пароль
        ttk.Label(self.proxy_options_frame, text="Логин:").grid(row=3, column=0, sticky=tk.W)
        self.proxy_login_entry = ttk.Entry(self.proxy_options_frame, width=25)
        self.proxy_login_entry.grid(row=3, column=1, sticky=tk.W+tk.E, pady=2)

        ttk.Label(self.proxy_options_frame, text="Пароль:").grid(row=4, column=0, sticky=tk.W)
        self.proxy_password_entry = ttk.Entry(self.proxy_options_frame, width=25, show="*")
        self.proxy_password_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=2)

        self.toggle_proxy_options()

        # === TAGS ===
        tags_frame = ttk.LabelFrame(scrollable_frame, text="🏷️ Теги", padding=10)
        tags_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_tags_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tags_frame, text="Добавить теги к профилю",
                       variable=self.use_tags_var,
                       command=self.toggle_tags_options).pack(anchor=tk.W)

        self.tags_options_frame = ttk.Frame(tags_frame)
        self.tags_options_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.tags_options_frame, text="Теги (через запятую):").pack(anchor=tk.W)
        self.tags_entry = ttk.Entry(self.tags_options_frame, width=35)
        self.tags_entry.pack(fill=tk.X)

        self.toggle_tags_options()

        # === COOKIES ===
        cookies_frame = ttk.LabelFrame(scrollable_frame, text="🍪 Cookies", padding=10)
        cookies_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_cookies_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cookies_frame, text="Добавить cookies в профиль",
                       variable=self.use_cookies_var,
                       command=self.toggle_cookies_options).pack(anchor=tk.W)

        self.cookies_options_frame = ttk.Frame(cookies_frame)
        self.cookies_options_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.cookies_options_frame, text="Cookies (JSON): [{}]").pack(anchor=tk.W)
        self.cookies_text = scrolledtext.ScrolledText(self.cookies_options_frame, height=3, wrap=tk.WORD,
                                                       font=("Consolas", 9))
        self.cookies_text.pack(fill=tk.X)
        # Не вставляем пример - для ускорения загрузки

        self.toggle_cookies_options()

        # === BOOKMARKS ===
        bookmarks_frame = ttk.LabelFrame(scrollable_frame, text="📚 Закладки", padding=10)
        bookmarks_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_bookmarks_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bookmarks_frame, text="Добавить закладки в профиль",
                       variable=self.use_bookmarks_var,
                       command=self.toggle_bookmarks_options).pack(anchor=tk.W)

        self.bookmarks_options_frame = ttk.Frame(bookmarks_frame)
        self.bookmarks_options_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.bookmarks_options_frame, text="Закладки (JSON): [{}]").pack(anchor=tk.W)
        self.bookmarks_text = scrolledtext.ScrolledText(self.bookmarks_options_frame, height=3, wrap=tk.WORD,
                                                         font=("Consolas", 9))
        self.bookmarks_text.pack(fill=tk.X)
        # Не вставляем пример - для ускорения загрузки

        self.toggle_bookmarks_options()

        # === EXTENSIONS ===
        extensions_frame = ttk.LabelFrame(scrollable_frame, text="🧩 Расширения", padding=10)
        extensions_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_extensions_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(extensions_frame, text="Добавить расширения в профиль",
                       variable=self.use_extensions_var,
                       command=self.toggle_extensions_options).pack(anchor=tk.W)

        self.extensions_options_frame = ttk.Frame(extensions_frame)
        self.extensions_options_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.extensions_options_frame, text="Пути к .crx (по строке)").pack(anchor=tk.W)
        self.extensions_text = scrolledtext.ScrolledText(self.extensions_options_frame, height=2, wrap=tk.WORD,
                                                          font=("Consolas", 9))
        self.extensions_text.pack(fill=tk.X)
        # Не вставляем пример - для ускорения загрузки

        self.toggle_extensions_options()

        # === ПАРАМЕТРИЗАЦИЯ И МУЛЬТИЗАПУСК ===
        param_frame = ttk.LabelFrame(scrollable_frame, text="🔄 Параметризация и мультизапуск", padding=10)
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_parametrization_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(param_frame, text="Использовать параметризацию (мультизапуск с данными из CSV)",
                       variable=self.use_parametrization_var,
                       command=self.toggle_parametrization_options).pack(anchor=tk.W)

        self.param_options_frame = ttk.Frame(param_frame)
        self.param_options_frame.pack(fill=tk.X, padx=20, pady=5)

        # Путь к CSV файлу
        ttk.Label(self.param_options_frame, text="CSV файл с данными:").pack(anchor=tk.W, pady=(5, 0))

        csv_path_frame = ttk.Frame(self.param_options_frame)
        csv_path_frame.pack(fill=tk.X, pady=(0, 5))

        self.csv_path_entry = ttk.Entry(csv_path_frame, width=30)
        self.csv_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(csv_path_frame, text="📁 Выбрать", command=self.select_csv_file, width=10).pack(side=tk.LEFT, padx=(5, 0))

        # Кнопка создания примера
        ttk.Button(self.param_options_frame, text="📄 Создать пример CSV",
                  command=self.create_sample_csv).pack(anchor=tk.W, pady=(0, 5))

        # Инфо о переменных
        ttk.Label(self.param_options_frame, text="💡 Используйте {{variable_name}} в коде для параметризации",
                 foreground="blue").pack(anchor=tk.W, pady=(5, 0))

        ttk.Label(self.param_options_frame,
                 text="Пример: driver.find_element(By.ID, 'search').send_keys({{search_query}})",
                 font=("Consolas", 8), foreground="gray").pack(anchor=tk.W)

        # Найденные переменные
        ttk.Label(self.param_options_frame, text="Найденные переменные в коде:").pack(anchor=tk.W, pady=(10, 0))
        self.variables_listbox = tk.Listbox(self.param_options_frame, height=4, font=("Consolas", 9))
        self.variables_listbox.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(self.param_options_frame, text="🔍 Обновить список переменных",
                  command=self.update_variables_list).pack(anchor=tk.W)

        self.toggle_parametrization_options()

        # === SMS SERVICES ===
        sms_frame = ttk.LabelFrame(scrollable_frame, text="📱 SMS сервисы (номера и OTP)", padding=10)
        sms_frame.pack(fill=tk.X, padx=5, pady=5)

        # ПРЕДУПРЕЖДЕНИЕ для ветки network-parser
        warning_label = ttk.Label(sms_frame,
                                 text="⚠️ ОТКЛЮЧЕНО в ветке network-parser: работаем только со статическими данными из CSV",
                                 foreground="red", font=('TkDefaultFont', 9, 'bold'))
        warning_label.pack(anchor=tk.W, pady=(0, 5))

        self.use_sms_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sms_frame, text="Использовать SMS сервис для получения номеров и OTP (НЕДОСТУПНО)",
                       variable=self.use_sms_var,
                       command=self.toggle_sms_options,
                       state="disabled").pack(anchor=tk.W)

        self.sms_options_frame = ttk.Frame(sms_frame)
        self.sms_options_frame.pack(fill=tk.X, padx=20, pady=5)

        # Провайдер
        ttk.Label(self.sms_options_frame, text="Провайдер:").pack(anchor=tk.W)
        self.sms_provider_var = tk.StringVar(value="daisysms")
        provider_combo = ttk.Combobox(self.sms_options_frame, textvariable=self.sms_provider_var,
                                     values=["daisysms"], width=25, state="readonly")
        provider_combo.pack(fill=tk.X, pady=(0, 5))

        # API ключ
        ttk.Label(self.sms_options_frame, text="API ключ:").pack(anchor=tk.W)
        self.sms_api_key_entry = ttk.Entry(self.sms_options_frame, width=35, show="*")
        self.sms_api_key_entry.pack(fill=tk.X, pady=(0, 5))

        # Сервис (Discord, Google, WhatsApp и т.д.)
        ttk.Label(self.sms_options_frame, text="Сервис для активации:").pack(anchor=tk.W)
        self.sms_service_var = tk.StringVar(value="ds")

        services_frame = ttk.Frame(self.sms_options_frame)
        services_frame.pack(fill=tk.X, pady=(0, 5))

        service_combo = ttk.Combobox(services_frame, textvariable=self.sms_service_var,
                                    values=["ds", "go", "wa", "tg", "fb", "ig", "tw", "other"],
                                    width=10, state="readonly")
        service_combo.pack(side=tk.LEFT)

        # Описание кодов сервисов
        service_desc = ttk.Label(services_frame,
                                text="ds=Discord, go=Google, wa=WhatsApp, tg=Telegram",
                                font=("TkDefaultFont", 7), foreground="gray")
        service_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Кнопки управления
        sms_buttons_frame = ttk.Frame(self.sms_options_frame)
        sms_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(sms_buttons_frame, text="🔌 Подключить",
                  command=self.connect_sms_provider).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sms_buttons_frame, text="💰 Баланс",
                  command=self.check_sms_balance).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sms_buttons_frame, text="📋 Все сервисы",
                  command=self.show_all_services).pack(side=tk.LEFT, padx=(0, 5))

        # Статус подключения
        self.sms_status_label = ttk.Label(self.sms_options_frame, text="✗ Не подключен",
                                         foreground="red")
        self.sms_status_label.pack(pady=(5, 0))

        # Инфо
        info_text = """
💡 SMS сервис используется для динамического получения
номеров телефонов и OTP кодов.

Как это работает:
1. Включите опцию "Использовать SMS сервис"
2. Введите API ключ от DaisySMS
3. Выберите сервис (Discord, Google и т.д.)
4. Импортируйте скрипт - система автоматически
   определит поля phone_number и otp_code
5. При выполнении скрипта номер и OTP будут
   получены автоматически из API!
        """
        ttk.Label(self.sms_options_frame, text=info_text.strip(), justify=tk.LEFT,
                 foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, pady=(10, 0))

        self.toggle_sms_options()

        # Инициализировать видимость Playwright таргета
        self.toggle_playwright_target()

    def create_right_panel(self, parent):
        """Создание правой панели с кодом"""
        # Используем PanedWindow для регулируемых пропорций между редактором и выводом
        right_paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        right_paned.pack(fill=tk.BOTH, expand=True)

        # Верхняя часть - редактор кода (больше места)
        code_frame = ttk.LabelFrame(right_paned, text="📝 Код автоматизации (ваш код)", padding=10)
        right_paned.add(code_frame, weight=2)

        ttk.Label(code_frame, text="Введите ваш код автоматизации (будет выполняться в контексте driver):").pack(anchor=tk.W)

        self.code_editor = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD,
                                                     font=("Consolas", 10))
        self.code_editor.pack(fill=tk.BOTH, expand=True, pady=5)

        # Пример кода с реальными действиями
        # ВАЖНО: Импорты добавляются автоматически при генерации скрипта!
        # Не нужно писать импорты вручную - просто пишите код действий.
        example_code = '''# Пример 1: Переход на сайт и взаимодействие
driver.get("https://www.google.com")
print("Открыта страница Google")
time.sleep(2)

# Пример 2: Поиск и клик по элементу с ожиданием загрузки
try:
    # Ожидание загрузки поля поиска (WebDriverWait добавляется автоматически)
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.send_keys("Selenium automation")
    print("Введен поисковый запрос")
    time.sleep(1)

    # Отправка формы
    search_box.submit()
    print("Форма отправлена")
    time.sleep(3)
except Exception as e:
    print(f"Ошибка при поиске: {e}")

# 💡 СОВЕТ: Используйте Chrome Extension "Selenium Chrome Recorder"
# для автоматической записи действий и генерации надежного кода!
# Он создаст правильные селекторы и добавит все необходимое.

# С параметризацией: {{variable}}
# Пример: driver.get("{{url}}")
# Пример: search_box.send_keys("{{search_query}}")
'''
        self.code_editor.insert("1.0", example_code)

        # Кнопки управления
        buttons_frame = ttk.Frame(code_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(buttons_frame, text="🎭 Импорт Playwright",
                  command=self.import_playwright_code, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📥 Импорт Selenium IDE",
                  command=self.import_selenium_ide_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📋 Импорт скрипта",
                  command=self.import_external_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🔨 Сгенерировать скрипт",
                  command=self.generate_script, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="💾 Сохранить скрипт",
                  command=self.save_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="▶️ Запустить скрипт",
                  command=self.run_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="⏹️ Остановить",
                  command=self.stop_script).pack(side=tk.LEFT, padx=2)

        # Нижняя часть - вывод (меньше места, регулируется разделителем)
        output_frame = ttk.LabelFrame(right_paned, text="📊 Вывод выполнения", padding=10)
        right_paned.add(output_frame, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                     font=("Consolas", 9), background="#1e1e1e",
                                                     foreground="#ffffff")
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def toggle_profile_options(self):
        """Переключение опций профиля"""
        if self.create_profile_var.get():
            for child in self.profile_options_frame.winfo_children():
                child.configure(state="normal")
        else:
            for child in self.profile_options_frame.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Checkbutton)):
                    child.configure(state="disabled")

    def toggle_proxy_options(self):
        """Переключение опций прокси"""
        state = "normal" if self.use_proxy_var.get() else "disabled"
        for child in self.proxy_options_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox)):
                child.configure(state=state)

    def toggle_tags_options(self):
        """Переключение опций тегов"""
        state = "normal" if self.use_tags_var.get() else "disabled"
        for child in self.tags_options_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                child.configure(state=state)

    def toggle_cookies_options(self):
        """Переключение опций cookies"""
        state = "normal" if self.use_cookies_var.get() else "disabled"
        for child in self.cookies_options_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                child.configure(state=state)

    def toggle_bookmarks_options(self):
        """Переключение опций закладок"""
        state = "normal" if self.use_bookmarks_var.get() else "disabled"
        for child in self.bookmarks_options_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                child.configure(state=state)

    def toggle_extensions_options(self):
        """Переключение опций расширений"""
        state = "normal" if self.use_extensions_var.get() else "disabled"
        for child in self.extensions_options_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                child.configure(state=state)

    def toggle_parametrization_options(self):
        """Переключение опций параметризации"""
        state = "normal" if self.use_parametrization_var.get() else "disabled"

        # Включение/выключение всех элементов управления
        for child in self.param_options_frame.winfo_children():
            try:
                if isinstance(child, (ttk.Entry, ttk.Button, tk.Listbox)):
                    child.configure(state=state)
                elif isinstance(child, ttk.Frame):
                    # Для фреймов обрабатываем дочерние элементы
                    for subchild in child.winfo_children():
                        if isinstance(subchild, (ttk.Entry, ttk.Button)):
                            subchild.configure(state=state)
            except:
                pass

    def toggle_sms_options(self):
        """Переключение опций SMS сервисов"""
        state = "normal" if self.use_sms_var.get() else "disabled"

        # Включение/выключение всех элементов управления
        for child in self.sms_options_frame.winfo_children():
            try:
                if isinstance(child, (ttk.Entry, ttk.Button, ttk.Combobox)):
                    child.configure(state=state)
                elif isinstance(child, ttk.Frame):
                    # Для фреймов обрабатываем дочерние элементы
                    for subchild in child.winfo_children():
                        if isinstance(subchild, (ttk.Entry, ttk.Button, ttk.Combobox)):
                            subchild.configure(state=state)
            except:
                pass

    def toggle_playwright_target(self):
        """Показать/скрыть опции таргета Playwright"""
        if self.automation_framework_var.get() == "playwright":
            # Показать опции таргета
            self.playwright_target_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        else:
            # Скрыть опции таргета для Selenium
            self.playwright_target_frame.pack_forget()

    def connect_sms_provider(self):
        """Подключение к SMS провайдеру"""
        provider_name = self.sms_provider_var.get()
        api_key = self.sms_api_key_entry.get().strip()

        if not api_key:
            messagebox.showwarning("Предупреждение", "Введите API ключ")
            return

        try:
            # Создать провайдер
            provider = self.sms_provider_manager.create_provider(provider_name, api_key)

            # Проверить подключение
            self.sms_status_label.config(text="⏳ Подключение...", foreground="orange")
            self.root.update_idletasks()

            balance_info = provider.get_balance()

            if balance_info['success']:
                balance = balance_info['balance']
                currency = balance_info['currency']

                self.sms_status_label.config(
                    text=f"✓ Подключен | Баланс: ${balance:.2f} {currency}",
                    foreground="green"
                )

                messagebox.showinfo(
                    "Успех",
                    f"Успешно подключено к {provider_name}!\n\n"
                    f"Баланс: ${balance:.2f} {currency}\n\n"
                    f"Теперь система автоматически будет получать\n"
                    f"номера телефонов и OTP коды из API."
                )
            else:
                error = balance_info.get('error', 'Неизвестная ошибка')
                self.sms_status_label.config(
                    text=f"✗ Ошибка подключения",
                    foreground="red"
                )
                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось подключиться к {provider_name}:\n\n{error}"
                )

        except Exception as e:
            self.sms_status_label.config(text="✗ Ошибка", foreground="red")
            messagebox.showerror("Ошибка", f"Ошибка подключения:\n{str(e)}")

    def check_sms_balance(self):
        """Проверка баланса SMS провайдера"""
        provider = self.sms_provider_manager.get_active_provider()

        if not provider:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала подключитесь к SMS провайдеру"
            )
            return

        try:
            balance_info = provider.get_balance()

            if balance_info['success']:
                balance = balance_info['balance']
                currency = balance_info['currency']

                # Получить список сервисов
                services_info = provider.get_services()
                services_list = ""

                if services_info['success']:
                    for service in services_info['services'][:10]:  # Первые 10
                        code = service['code']
                        name = service['name']
                        price = service['price']
                        services_list += f"  • {name} ({code}): ${price:.2f}\n"

                messagebox.showinfo(
                    "Баланс",
                    f"Баланс: ${balance:.2f} {currency}\n\n"
                    f"Популярные сервисы:\n{services_list}\n"
                    f"Выбранный сервис: {self.sms_service_var.get()}"
                )
            else:
                error = balance_info.get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка", f"Ошибка получения баланса:\n{error}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка:\n{str(e)}")

    def show_all_services(self):
        """Показать окно со всеми доступными сервисами"""
        provider = self.sms_provider_manager.get_active_provider()

        if not provider:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала подключитесь к SMS провайдеру"
            )
            return

        # Создать новое окно
        services_window = tk.Toplevel(self.root)
        services_window.title("Все доступные сервисы DaisySMS")
        services_window.geometry("900x600")

        # Фрейм для поиска
        search_frame = ttk.Frame(services_window, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Статус загрузки
        status_label = ttk.Label(search_frame, text="Загрузка...", foreground="blue")
        status_label.pack(side=tk.LEFT)

        # Фрейм для таблицы
        table_frame = ttk.Frame(services_window, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Создать Treeview для отображения таблицы
        columns = ("code", "name", "country", "price", "count")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Настроить колонки
        tree.heading("code", text="Код сервиса")
        tree.heading("name", text="Название")
        tree.heading("country", text="Страна")
        tree.heading("price", text="Цена ($)")
        tree.heading("count", text="Доступно номеров")

        tree.column("code", width=100, anchor=tk.W)
        tree.column("name", width=250, anchor=tk.W)
        tree.column("country", width=80, anchor=tk.CENTER)
        tree.column("price", width=100, anchor=tk.E)
        tree.column("count", width=150, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка для выбора сервиса
        button_frame = ttk.Frame(services_window, padding=10)
        button_frame.pack(fill=tk.X)

        def select_service():
            """Выбрать выделенный сервис"""
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                service_code = item['values'][0]
                self.sms_service_var.set(service_code)
                messagebox.showinfo("Успех", f"Выбран сервис: {service_code}")
                services_window.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Выберите сервис из списка")

        ttk.Button(button_frame, text="Выбрать выделенный сервис",
                  command=select_service).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Закрыть",
                  command=services_window.destroy).pack(side=tk.LEFT)

        # Информация о сортировке
        ttk.Label(button_frame, text="💡 Нажмите на заголовок колонки для сортировки",
                 foreground="blue", font=("TkDefaultFont", 8)).pack(side=tk.RIGHT)

        # Функция для загрузки и отображения сервисов
        all_services = []

        def load_services():
            """Загрузить сервисы из API"""
            nonlocal all_services
            try:
                status_label.config(text="Загрузка сервисов из API...", foreground="blue")
                services_window.update()

                result = provider.get_all_services_with_prices()

                if result['success']:
                    all_services = result['services']
                    total = result.get('total_services', len(all_services))
                    status_label.config(
                        text=f"Загружено {total} сервисов",
                        foreground="green"
                    )
                    update_table()
                else:
                    error = result.get('error', 'Неизвестная ошибка')
                    status_label.config(text=f"Ошибка: {error}", foreground="red")
                    messagebox.showerror("Ошибка", f"Не удалось загрузить сервисы:\n{error}")

            except Exception as e:
                status_label.config(text=f"Ошибка: {str(e)}", foreground="red")
                messagebox.showerror("Ошибка", f"Ошибка загрузки:\n{str(e)}")

        def update_table(services=None):
            """Обновить таблицу с фильтрацией"""
            # Очистить таблицу
            for item in tree.get_children():
                tree.delete(item)

            # Если сервисы не переданы, используем все
            if services is None:
                services = all_services

            # Применить фильтр поиска
            search_text = search_var.get().lower()
            if search_text:
                services = [
                    s for s in services
                    if search_text in s['name'].lower() or
                       search_text in s['code'].lower() or
                       search_text in s['country'].lower()
                ]

            # Добавить данные в таблицу
            for service in services:
                tree.insert("", tk.END, values=(
                    service['code'],
                    service['name'],
                    service['country'],
                    f"${service['price']:.2f}",
                    service['count'] if service['count'] > 0 else "Нет в наличии"
                ))

            # Обновить статус
            if search_text:
                status_label.config(
                    text=f"Показано {len(services)} из {len(all_services)} сервисов",
                    foreground="blue"
                )
            else:
                status_label.config(
                    text=f"Загружено {len(all_services)} сервисов",
                    foreground="green"
                )

        # Привязать поиск к обновлению таблицы
        search_var.trace('w', lambda *args: update_table())

        # Загрузить сервисы в отдельном потоке (чтобы GUI не зависало)
        import threading
        thread = threading.Thread(target=load_services, daemon=True)
        thread.start()

    def select_csv_file(self):
        """Выбор CSV файла"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл с данными",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            self.csv_path_entry.delete(0, tk.END)
            self.csv_path_entry.insert(0, file_path)

            # Попробуем загрузить и показать превью
            try:
                from src.data.data_source import DataSource

                ds = DataSource(file_path)
                messagebox.showinfo(
                    "CSV загружен",
                    f"Файл успешно загружен!\n\n"
                    f"Количество строк: {ds.get_row_count()}\n"
                    f"Колонки: {', '.join(ds.get_headers())}"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить CSV:\n{str(e)}")

    def create_sample_csv(self):
        """Создание примера CSV файла"""
        from tkinter import filedialog
        from src.data.data_source import DataSource

        file_path = filedialog.asksaveasfilename(
            title="Сохранить пример CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                ds = DataSource()
                ds.create_sample_csv(file_path)

                messagebox.showinfo(
                    "Успех",
                    f"Пример CSV создан:\n{file_path}\n\n"
                    "Содержит примеры колонок:\n"
                    "- search_query\n"
                    "- quantity\n"
                    "- color\n\n"
                    "Отредактируйте файл под свои нужды!"
                )

                # Автоматически вставляем путь
                self.csv_path_entry.delete(0, tk.END)
                self.csv_path_entry.insert(0, file_path)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{str(e)}")

    def update_variables_list(self):
        """Обновление списка найденных переменных"""
        from src.data.template_engine import TemplateEngine

        # Получаем код пользователя
        user_code = self.code_editor.get("1.0", tk.END).strip()

        # Находим переменные
        engine = TemplateEngine()
        variables = engine.find_variables(user_code)

        # Обновляем listbox
        self.variables_listbox.delete(0, tk.END)

        if variables:
            for var in sorted(variables):
                self.variables_listbox.insert(tk.END, f"{{{{ {var} }}}}")
        else:
            self.variables_listbox.insert(tk.END, "(переменные не найдены)")

        # Показываем количество
        messagebox.showinfo(
            "Найденные переменные",
            f"Найдено переменных: {len(variables)}\n\n" +
            (f"Переменные:\n" + "\n".join([f"- {{{{{v}}}}}" for v in sorted(variables)])
             if variables else "Используйте {{variable_name}} в коде")
        )

    def connect_api(self):
        """Подключение к API"""
        token = self.api_token_entry.get().strip()
        url = self.api_url_entry.get().strip()

        # Валидация токена
        if not token or token == 'YOUR_API_TOKEN_HERE':
            messagebox.showwarning("Предупреждение", "Введите корректный API токен")
            return

        # Валидация URL
        if not url:
            messagebox.showwarning("Предупреждение", "Введите API URL")
            return

        if not url.startswith('http'):
            messagebox.showwarning("Предупреждение",
                                 "API URL должен начинаться с http:// или https://")
            return

        # Проверка правильности URL
        expected_url = "https://app.octobrowser.net/api/v2/automation"
        if url != expected_url:
            response = messagebox.askyesno("Нестандартный URL",
                                          f"Вы используете нестандартный URL:\n{url}\n\n"
                                          f"Стандартный URL:\n{expected_url}\n\n"
                                          f"Продолжить с текущим URL?")
            if not response:
                return

        # Сохраняем настройки в config.json
        self.config['octobrowser']['api_token'] = token
        self.config['octobrowser']['api_base_url'] = url
        self.save_config()

        # Подключаемся к API (с показом сообщений)
        self.init_api(show_messages=True)

    def reset_api_settings(self):
        """Сброс настроек API к значениям по умолчанию"""
        response = messagebox.askyesno("Подтверждение",
                                      "Сбросить настройки API к значениям по умолчанию?")
        if response:
            # Значения по умолчанию
            default_url = "https://app.octobrowser.net/api/v2/automation"
            default_token = "YOUR_API_TOKEN_HERE"

            # Обновляем поля
            self.api_url_entry.delete(0, tk.END)
            self.api_url_entry.insert(0, default_url)

            self.api_token_entry.delete(0, tk.END)
            self.api_token_entry.insert(0, default_token)

            # Сохраняем
            self.config['octobrowser']['api_base_url'] = default_url
            self.config['octobrowser']['api_token'] = default_token
            self.save_config()

            self.status_label.config(text="✗ API не подключен", foreground="red")
            messagebox.showinfo("Готово", "Настройки API сброшены к значениям по умолчанию")

    def collect_options(self) -> dict:
        """Сбор всех опций из GUI"""
        options = {
            'api_token': self.config['octobrowser']['api_token'],
            'api_base_url': self.config['octobrowser']['api_base_url'],
            'create_profile': self.create_profile_var.get(),
            'cleanup_profile': self.cleanup_profile_var.get(),
            'use_selenium': self.automation_framework_var.get() == 'selenium',  # True только для Selenium
            'use_cookies': self.use_cookies_var.get(),
            'use_bookmarks': self.use_bookmarks_var.get(),
            'use_extensions': self.use_extensions_var.get(),
            'profile_config': {}
        }

        if self.create_profile_var.get():
            profile_config = {
                'title': self.profile_title_entry.get()
            }

            # Fingerprint
            if self.use_random_fingerprint_var.get():
                profile_config['fingerprint'] = {
                    'os_type': self.os_type_var.get(),
                    'random': True
                }

            # Proxy
            if self.use_proxy_var.get():
                proxy_host = self.proxy_host_entry.get().strip()
                proxy_port = self.proxy_port_entry.get().strip()

                # Проверка что хост и порт заполнены
                if proxy_host and proxy_port:
                    try:
                        profile_config['proxy'] = {
                            'type': self.proxy_type_var.get(),
                            'host': proxy_host,
                            'port': int(proxy_port),  # Конвертируем в int!
                            'login': self.proxy_login_entry.get().strip(),
                            'password': self.proxy_password_entry.get().strip()
                        }
                    except ValueError:
                        # Если порт не число - используем 0
                        profile_config['proxy'] = {
                            'type': self.proxy_type_var.get(),
                            'host': proxy_host,
                            'port': 0,
                            'login': self.proxy_login_entry.get().strip(),
                            'password': self.proxy_password_entry.get().strip()
                        }

            # Tags
            if self.use_tags_var.get():
                tags_text = self.tags_entry.get().strip()
                if tags_text:
                    profile_config['tags'] = [t.strip() for t in tags_text.split(',')]

            options['profile_config'] = profile_config

        # Cookies
        if self.use_cookies_var.get():
            try:
                cookies_text = self.cookies_text.get("1.0", tk.END).strip()
                if cookies_text:
                    options['cookies_data'] = json.loads(cookies_text)
            except json.JSONDecodeError:
                options['cookies_data'] = []

        # Bookmarks
        if self.use_bookmarks_var.get():
            try:
                bookmarks_text = self.bookmarks_text.get("1.0", tk.END).strip()
                if bookmarks_text:
                    options['bookmarks_data'] = json.loads(bookmarks_text)
            except json.JSONDecodeError:
                options['bookmarks_data'] = []

        # Extensions
        if self.use_extensions_var.get():
            extensions_text = self.extensions_text.get("1.0", tk.END).strip()
            if extensions_text:
                options['extensions_data'] = [line.strip() for line in extensions_text.split('\n') if line.strip()]

        # Параметризация
        options['use_parametrization'] = self.use_parametrization_var.get()
        if self.use_parametrization_var.get():
            csv_path = self.csv_path_entry.get().strip()
            if csv_path:
                options['data_file_path'] = csv_path

        return options

    def generate_script(self):
        """Генерация скрипта"""
        try:
            # Сохранить текущие настройки
            self.save_settings()

            options = self.collect_options()
            user_code = self.code_editor.get("1.0", tk.END).strip()

            # Определить выбранный фреймворк
            framework = self.automation_framework_var.get()

            # Валидация пользовательского кода (только для Selenium)
            if user_code and framework == 'selenium':
                try:
                    # Пытаемся скомпилировать код как Python (только для синхронного кода)
                    compile(user_code, '<user_code>', 'exec')
                except SyntaxError as e:
                    error_msg = f"Ошибка синтаксиса в вашем коде автоматизации:\n\n"
                    error_msg += f"Строка {e.lineno}: {e.msg}\n"
                    error_msg += f"Текст: {e.text}\n\n"
                    error_msg += "Исправьте код и попробуйте снова."
                    messagebox.showerror("Синтаксическая ошибка", error_msg)
                    return

            # Генерация с правильным генератором
            if framework == 'playwright':
                # Для Playwright адаптируем опции
                playwright_config = {
                    'api_token': options.get('api_token', ''),
                    'use_proxy': 'proxy' in options.get('profile_config', {}),
                    'proxy': options.get('profile_config', {}).get('proxy', {}),
                    'csv_filename': Path(options.get('data_file_path', 'data.csv')).name if options.get('data_file_path') else 'data.csv',
                    # ОТКЛЮЧЕНО для ветки network-parser: работаем только со статическими данными из CSV
                    'use_sms': False,  # Было: self.use_sms_var.get()
                    'sms': {
                        'provider': self.sms_provider_var.get(),
                        'api_key': self.sms_api_key_entry.get().strip(),
                        'service': self.sms_service_var.get()
                    },
                    'target': self.playwright_target_var.get()  # library или cdp
                }
                script_content = self.playwright_generator.generate_script(user_code, playwright_config)
            else:
                # Для Selenium используем стандартный генератор
                script_content = self.generator.generate_script(options, user_code)

            # Сохранение
            output_dir = Path(__file__).parent.parent.parent / 'generated_scripts'
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_name = f"automation_script_{timestamp}.py"
            script_path = output_dir / script_name

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Копирование CSV файла в директорию скрипта (если используется параметризация)
            if self.use_parametrization_var.get():
                csv_path = self.csv_path_entry.get().strip()
                if csv_path and Path(csv_path).exists():
                    import shutil
                    csv_filename = Path(csv_path).name
                    csv_dest = output_dir / csv_filename
                    shutil.copy2(csv_path, csv_dest)
                    self.append_output(f"✓ CSV файл скопирован: {csv_dest}\n")

            self.last_generated_script = str(script_path)
            self.append_output(f"✓ Скрипт сгенерирован: {script_path}\n")
            messagebox.showinfo("Успех", f"Скрипт сгенерирован:\n{script_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации скрипта:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def save_script(self):
        """Сохранение скрипта в выбранное место"""
        if not hasattr(self, 'last_generated_script'):
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте скрипт")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(self.last_generated_script, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(file_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                messagebox.showinfo("Успех", f"Скрипт сохранен:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def run_script(self):
        """Запуск сгенерированного скрипта"""
        if not hasattr(self, 'last_generated_script'):
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте скрипт")
            return

        self.output_text.delete("1.0", tk.END)
        self.runner.run_script(self.last_generated_script, async_mode=True)

    def stop_script(self):
        """Остановка выполнения скрипта"""
        self.runner.stop_script()

    def append_output(self, text: str):
        """Добавление текста в вывод"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()

    def import_playwright_code(self):
        """Импортирует код Playwright теста"""
        # Создать адаптивное диалоговое окно
        import_window = tk.Toplevel(self.root)
        import_window.title("🎭 Импорт Playwright кода")
        import_window.geometry("1000x700")
        import_window.minsize(800, 600)

        # Компактная инструкция
        instruction_frame = ttk.Frame(import_window)
        instruction_frame.pack(fill=tk.X, padx=10, pady=5)

        instruction_text = "💡 Вставьте код Playwright теста (npx playwright codegen). Система автоматически извлечёт значения и создаст параметры для CSV."
        ttk.Label(instruction_frame, text=instruction_text, justify=tk.LEFT, wraplength=950).pack(anchor=tk.W)

        # Поле для ввода кода (больше места)
        code_frame = ttk.LabelFrame(import_window, text="📝 Код Playwright теста", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD)
        code_text.pack(fill=tk.BOTH, expand=True)

        # Кнопки
        buttons_frame = ttk.Frame(import_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        def load_example():
            example_code = """import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://www.testpagekfkfe.com/');
  await page.getByTestId('nav').getByRole('link', { name: 'Get started' }).click();
  await page.getByRole('textbox', { name: 'First name' }).fill('Adam');
  await page.getByRole('textbox', { name: 'Last name' }).fill('Fisher');
  await page.getByRole('textbox', { name: 'Email' }).fill('test@gmail.com');
  await page.getByRole('button', { name: 'Next' }).click();
  await page.getByRole('textbox', { name: 'Date of birth' }).fill('10 / 30 / 1995');
  await page.getByRole('button', { name: 'Next' }).click();
});"""
            code_text.delete("1.0", tk.END)
            code_text.insert("1.0", example_code)

        def process_import():
            code = code_text.get("1.0", tk.END).strip()
            if not code:
                messagebox.showwarning("Предупреждение", "Вставьте код Playwright для импорта")
                return

            # ОТКЛЮЧЕНО для ветки network-parser: не запрашиваем phone/OTP
            # Парсим напрямую без подсказок
            self.playwright_parser.set_manual_field_hints(phone_value=None, otp_value=None)
            self.process_playwright_import(code, import_window)

        ttk.Button(buttons_frame, text="📋 Загрузить пример", command=load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="✅ Импортировать", command=process_import,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="❌ Отмена",
                  command=import_window.destroy).pack(side=tk.LEFT, padx=2)

    # УДАЛЕНО: show_field_hints_dialog - не нужна в ветке network-parser
    # Работаем только со статическими данными из CSV, phone/OTP не запрашиваются

    def process_playwright_import(self, code: str, import_window):
        """
        Обработать импорт Playwright кода (после установки подсказок)

        Args:
            code: Код Playwright теста
            import_window: Окно импорта
        """
        try:
            # Парсим Playwright код
            self.imported_data = self.playwright_parser.parse_playwright_code(code)

            # Показать информацию
            info_msg = f"✅ Playwright тест успешно импортирован!\n\n"
            info_msg += f"URL: {self.imported_data['url']}\n"
            info_msg += f"Действий: {len(self.imported_data['actions'])}\n"
            info_msg += f"Извлечено значений: {len(self.imported_data['values'])}\n\n"

            # Добавить список действий с селекторами
            info_msg += "СПИСОК ДЕЙСТВИЙ:\n"
            info_msg += "=" * 50 + "\n"
            for i, action in enumerate(self.imported_data['actions'], 1):
                action_type = action['type'].upper()
                if action['type'] == 'goto':
                    info_msg += f"{i}. {action_type}: {action['url']}\n"
                elif 'selector' in action:
                    sel = action['selector']
                    sel_type = sel.get('type', 'unknown')
                    info_msg += f"{i}. {action_type}: {sel_type}\n"
                else:
                    info_msg += f"{i}. {action_type}\n"
            info_msg += "=" * 50 + "\n\n"

            if self.imported_data['values']:
                info_msg += f"Параметры: {', '.join(self.imported_data['csv_headers'])}\n\n"
                info_msg += "Переходим к редактированию данных..."
                messagebox.showinfo("Успешный импорт", info_msg)

                # Инициализировать данные для CSV
                self.csv_data_rows = [self.imported_data['values']]

                # Закрыть окно импорта
                import_window.destroy()

                # Показать редактор данных
                self.show_imported_data_editor()
            else:
                info_msg += "Значения для параметризации не найдены.\n"
                info_msg += "Код вставлен в редактор."
                messagebox.showinfo("Успешный импорт", info_msg)

                # Вставить код в редактор
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", self.imported_data['converted_code'])
                import_window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта Playwright кода:\n{str(e)}")

    def import_selenium_ide_file(self):
        """Импортирует .side файл Selenium IDE"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл Selenium IDE",
            filetypes=[
                ("Selenium IDE files", "*.side"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Прочитать файл
            with open(file_path, 'r', encoding='utf-8') as f:
                side_content = f.read()

            # Парсить .side файл
            self.imported_data = self.side_parser.parse_side_file(side_content)

            # Показать информацию
            info_msg = f"✅ Selenium IDE тест успешно импортирован!\n\n"
            info_msg += f"URL: {self.imported_data['url']}\n"
            info_msg += f"Действий: {len(self.imported_data['actions'])}\n"
            info_msg += f"Извлечено значений: {len(self.imported_data['values'])}\n\n"

            # Добавить список действий с селекторами
            info_msg += "СПИСОК ДЕЙСТВИЙ И СЕЛЕКТОРОВ:\n"
            info_msg += "=" * 50 + "\n"
            for i, action in enumerate(self.imported_data['actions'], 1):
                action_type = action['type'].upper()
                if action['type'] == 'open':
                    info_msg += f"{i}. {action_type}: {action['url']}\n"
                elif 'selector' in action:
                    sel = action['selector']
                    info_msg += f"{i}. {action_type}: {sel['by']}, \"{sel['selector']}\"\n"
                else:
                    info_msg += f"{i}. {action_type}\n"
            info_msg += "=" * 50 + "\n\n"

            if self.imported_data['values']:
                info_msg += f"Параметры: {', '.join(self.imported_data['csv_headers'])}\n\n"
                info_msg += "Переходим к редактированию данных..."
                messagebox.showinfo("Успешный импорт", info_msg)

                # Инициализировать данные для CSV
                self.csv_data_rows = [self.imported_data['values']]

                # Показать редактор данных
                self.show_imported_data_editor()
            else:
                info_msg += "Значения для параметризации не найдены.\n"
                info_msg += "Код вставлен в редактор."
                messagebox.showinfo("Успешный импорт", info_msg)

                # Вставить код в редактор
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", self.imported_data['converted_code'])

        except Exception as e:
            messagebox.showerror("Ошибка импорта", f"Не удалось импортировать .side файл:\n\n{str(e)}")

    def import_external_script(self):
        """Открывает диалог для импорта внешнего скрипта"""
        # Создать диалоговое окно
        import_window = tk.Toplevel(self.root)
        import_window.title("📥 Импорт внешнего скрипта")
        import_window.geometry("900x700")

        # Инструкция
        instruction_frame = ttk.LabelFrame(import_window, text="📖 Инструкция", padding=10)
        instruction_frame.pack(fill=tk.X, padx=10, pady=5)

        instruction_text = """
Вставьте код скрипта из Chrome Web Store расширений (Selenium IDE, Katalon Recorder и т.д.)

Поддерживаемые форматы:
• driver.find_element(By.XPATH, "...").click()
• driver.find_element(By.XPATH, get_xpath(driver, 'ID')).click()
• driver.find_element(By.ID, "...").send_keys("text")

После импорта:
1. Программа извлечет все введенные значения (имена, email, пароли и т.д.)
2. Создаст таблицу для редактирования данных
3. Сгенерирует CSV файл для параметризации
4. Конвертирует код в формат auto2tesst
        """
        ttk.Label(instruction_frame, text=instruction_text, justify=tk.LEFT).pack()

        # Поле для вставки скрипта
        script_frame = ttk.LabelFrame(import_window, text="📝 Вставьте код скрипта", padding=10)
        script_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        script_text = scrolledtext.ScrolledText(script_frame, height=20, wrap=tk.WORD,
                                                font=("Consolas", 10))
        script_text.pack(fill=tk.BOTH, expand=True)

        # Пример для демонстрации
        example_script = """from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# to click on the element(First name) found
driver.find_element(By.XPATH,get_xpath(driver,'YIFjT9kq3o5PEb_')).click()

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'fYsTI13_rml3tMs')).send_keys('Adam')

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'wIKmzLjQdTQwQ05')).send_keys('Fisher')

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'tJZm6UxdZNuMAQD')).send_keys('jfeuheghuihegj9egh@gmail.com')

# to type content in input field
driver.find_element(By.XPATH,get_xpath(driver,'Mcl9ZktzIHeZ8kH')).send_keys('10101900')
"""

        # Кнопки
        buttons_frame = ttk.Frame(import_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        def load_example():
            script_text.delete("1.0", tk.END)
            script_text.insert("1.0", example_script)

        def process_import():
            code = script_text.get("1.0", tk.END).strip()
            if not code:
                messagebox.showwarning("Предупреждение", "Вставьте код скрипта для импорта")
                return

            try:
                # Парсим скрипт
                self.imported_data = self.parser.parse_external_script(code)

                # Проверить есть ли custom селекторы (требуют замены)
                has_custom_selectors = 'custom[@id=' in self.imported_data['converted_code']

                if has_custom_selectors:
                    warning_msg = "⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ!\n\n"
                    warning_msg += "Импортированный скрипт содержит внутренние ID расширения,\n"
                    warning_msg += "которые НЕ РАБОТАЮТ напрямую на сайте.\n\n"
                    warning_msg += "ВАМ НУЖНО ВРУЧНУЮ ЗАМЕНИТЬ СЕЛЕКТОРЫ:\n\n"
                    warning_msg += "1. Откройте вашу тестовую страницу в браузере\n"
                    warning_msg += "2. Нажмите F12 (откроется DevTools)\n"
                    warning_msg += "3. Нажмите Ctrl+Shift+C (инспектор элементов)\n"
                    warning_msg += "4. Кликните на нужный элемент (поле ввода/кнопку)\n"
                    warning_msg += "5. В DevTools: правая кнопка → Copy → Copy XPath\n"
                    warning_msg += "6. В редакторе кода замените селектор на скопированный\n\n"
                    warning_msg += "ПРИОРИТЕТ СЕЛЕКТОРОВ:\n"
                    warning_msg += "✅ By.ID - лучший вариант (если у элемента есть id)\n"
                    warning_msg += "✅ By.NAME - хороший вариант (если есть name)\n"
                    warning_msg += "⚠️ By.XPATH - только если нет ID/NAME\n\n"
                    warning_msg += "В коде есть комментарии с инструкциями!\n"
                    messagebox.showwarning("Требуется замена селекторов", warning_msg)

                if not self.imported_data['values']:
                    messagebox.showinfo("Информация",
                                      "Скрипт импортирован, но не найдены значения для параметризации.\n"
                                      "Код вставлен в редактор.")
                    # Вставить конвертированный код в редактор
                    self.code_editor.delete("1.0", tk.END)
                    self.code_editor.insert("1.0", self.imported_data['converted_code'])
                    import_window.destroy()
                    return

                # Инициализировать данные для CSV таблицы
                self.csv_data_rows = [self.imported_data['values']]

                # Закрыть окно импорта и открыть окно редактирования данных
                import_window.destroy()

                # Показать результаты
                self.show_imported_data_editor()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта скрипта:\n{str(e)}")

        ttk.Button(buttons_frame, text="📋 Вставить пример", command=load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="✅ Импортировать", command=process_import,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="❌ Отмена",
                  command=import_window.destroy).pack(side=tk.LEFT, padx=2)

    def show_imported_data_editor(self):
        """Показывает редактор извлеченных данных"""
        if not self.imported_data:
            return

        # Создать окно редактора
        editor_window = tk.Toplevel(self.root)
        editor_window.title("📊 Редактирование данных для параметризации")
        editor_window.geometry("1200x700")
        editor_window.minsize(1000, 600)

        # === БЫСТРОЕ ДОБАВЛЕНИЕ ДАННЫХ ===
        quick_add_frame = ttk.LabelFrame(editor_window, text="⚡ Быстрое добавление строки", padding=10)
        quick_add_frame.pack(fill=tk.X, padx=10, pady=5)

        hint_label = ttk.Label(quick_add_frame,
                              text="💡 Вставьте имя и фамилию в любом формате (остальные данные сгенерируются автоматически)",
                              foreground="blue")
        hint_label.pack(anchor=tk.W, pady=(0, 5))

        quick_entry = ttk.Entry(quick_add_frame, width=100)
        quick_entry.pack(fill=tk.X, pady=(0, 5))

        def parse_and_add_row(event=None):
            """Умный парсер: извлекает имя/дату из ЛЮБОГО формата, генерирует остальное"""
            import random
            import re

            text = quick_entry.get().strip()
            if not text:
                return

            try:
                # ZIP всегда 33071 (Coral Springs, FL)
                zip_code = "33071"

                # === ИЗВЛЕЧЕНИЕ ИМЕНИ (ищем строку только с буквами) ===
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                first_name = "John"
                last_name = "Doe"

                # Ищем первую строку с именем (только буквы и пробелы, БЕЗ цифр)
                for line in lines:
                    # Удаляем все небуквенные символы, кроме пробелов
                    clean_line = re.sub(r'[^a-zA-Z\s]', ' ', line).strip()
                    words = [w for w in clean_line.split() if len(w) > 1]  # Слова длиннее 1 буквы

                    if len(words) >= 2:
                        first_name = words[0]
                        last_name = words[-1]  # Последнее слово (пропускаем средний инициал)
                        break

                # === УМНЫЙ ПАРСИНГ ДАТЫ (множество форматов) ===
                birth_month = None
                birth_day = None
                birth_year = None

                # Паттерны для поиска дат:
                # 1. MM/DD/YYYY или MM-DD-YYYY (с разделителями)
                date_with_sep = re.search(r'\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b', text)
                if date_with_sep:
                    mm = date_with_sep.group(1)
                    dd = date_with_sep.group(2)
                    yyyy = date_with_sep.group(3)
                    # Проверяем валидность
                    if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
                        birth_month = mm.zfill(2)
                        birth_day = dd.zfill(2)
                        birth_year = yyyy

                if not birth_month:
                    # 2. MMDDYYYY (8 цифр подряд, например: 01241986)
                    date_no_sep = re.search(r'\b(\d{2})(\d{2})(\d{4})\b', text)
                    if date_no_sep:
                        mm = date_no_sep.group(1)
                        dd = date_no_sep.group(2)
                        yyyy = date_no_sep.group(3)
                        # Проверяем валидность
                        if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
                            birth_month = mm
                            birth_day = dd
                            birth_year = yyyy

                # Если дата не найдена - генерируем случайную
                if not birth_month:
                    birth_month = str(random.randint(1, 12)).zfill(2)
                    birth_day = str(random.randint(1, 28)).zfill(2)
                    birth_year = str(random.randint(1960, 2000))

                # === ГЕНЕРАЦИЯ АДРЕСА (идентично HTML файлу) ===
                streets = [
                    "Riverside Dr", "NW 14th St", "NW 110th Ave", "Forest Hills Blvd",
                    "Royal Palm Blvd", "W Atlantic Blvd", "Sample Rd", "Coral Springs Dr",
                    "University Dr", "Wiles Rd", "Holmberg Rd", "Turtle Run Blvd"
                ]
                street_number = random.randint(100, 9999)
                street_name = random.choice(streets)
                address = f"{street_number} {street_name}"

                # === ГЕНЕРАЦИЯ EMAIL (идентично HTML файлу) ===
                email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com"]
                domain = random.choice(email_domains)
                fname_lower = first_name.lower()
                lname_lower = last_name.lower()

                email_formats = [
                    f"{fname_lower}.{lname_lower}@{domain}",
                    f"{fname_lower}{lname_lower}@{domain}",
                    f"{fname_lower}_{lname_lower}@{domain}",
                    f"{fname_lower}{random.randint(1, 999)}@{domain}",
                    f"{fname_lower}.{lname_lower}{random.randint(1, 99)}@{domain}"
                ]
                email = random.choice(email_formats)

                # === ГЕНЕРАЦИЯ ТЕЛЕФОНА (Florida area codes: 954, 754) ===
                area_code = random.choice(["954", "754"])
                exchange = random.randint(100, 999)
                subscriber = random.randint(1000, 9999)
                phone = f"({area_code}) {exchange}-{subscriber}"

                # === УМНЫЙ МАППИНГ ПОЛЕЙ ===
                # Собираем строку для CSV с учетом позиций и названий headers
                headers = self.imported_data['csv_headers']
                new_row = []

                for idx, header in enumerate(headers):
                    h_lower = header.lower().strip()

                    # ZIP только в первом поле (индекс 0)
                    if idx == 0:
                        new_row.append(zip_code)
                    # Месяц - второе поле или содержит "month"/"mm"
                    elif idx == 1 or 'month' in h_lower or h_lower == 'mm':
                        new_row.append(birth_month)
                    # День - третье поле или содержит "day"/"dd"
                    elif idx == 2 or 'day' in h_lower or h_lower == 'dd':
                        new_row.append(birth_day)
                    # Год - четвертое поле или содержит "year"/"yyyy"
                    elif idx == 3 or 'year' in h_lower or h_lower == 'yyyy':
                        new_row.append(birth_year)
                    # Имя - пятое поле или содержит "first"/"fname"
                    elif idx == 4 or 'first' in h_lower or 'fname' in h_lower:
                        new_row.append(first_name)
                    # Фамилия - шестое поле или содержит "last"/"lname"
                    elif idx == 5 or 'last' in h_lower or 'lname' in h_lower:
                        new_row.append(last_name)
                    # Адрес - седьмое поле или содержит "address"/"street"/"field"
                    elif idx == 6 or 'address' in h_lower or 'street' in h_lower or 'field' in h_lower:
                        new_row.append(address)
                    # Email - содержит "email"/"mail"
                    elif 'email' in h_lower or 'mail' in h_lower:
                        new_row.append(email)
                    # Телефон - содержит "phone"/"tel"
                    elif 'phone' in h_lower or 'tel' in h_lower:
                        new_row.append(phone)
                    else:
                        # Для остальных полей - пустое значение
                        new_row.append('')

                # Добавляем в данные
                self.csv_data_rows.append(new_row)
                tree.insert('', tk.END, values=new_row)

                # Очистить поле
                quick_entry.delete(0, tk.END)
                quick_entry.insert(0, f"✅ Добавлено: {first_name} {last_name}")

                # Автоочистка через 1 секунду
                editor_window.after(1000, lambda: quick_entry.delete(0, tk.END))

            except Exception as e:
                quick_entry.delete(0, tk.END)
                quick_entry.insert(0, f"❌ Ошибка: {str(e)}")

        # Автоматическое добавление при вставке (Ctrl+V) или Enter
        quick_entry.bind('<Return>', parse_and_add_row)
        quick_entry.bind('<KP_Enter>', parse_and_add_row)

        # Автоматический парсинг при изменении текста (после вставки)
        def on_text_change(event=None):
            text = quick_entry.get().strip()
            # Если вставлен полный текст с запятыми, автоматически парсим
            if ',' in text and len(text) > 20:
                editor_window.after(100, parse_and_add_row)

        quick_entry.bind('<KeyRelease>', on_text_change)

        # === ИНФОРМАЦИЯ (компактная) ===
        info_frame = ttk.Frame(editor_window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = f"📋 Извлечено полей: {len(self.imported_data['csv_headers'])} | Переменные: {', '.join(self.imported_data['csv_headers'])}"
        ttk.Label(info_frame, text=info_text, foreground="gray").pack(anchor=tk.W)

        # Таблица данных
        table_frame = ttk.LabelFrame(editor_window, text="📋 Данные для CSV", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создать Treeview для таблицы
        columns = self.imported_data['csv_headers']
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Настроить заголовки
        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=150)

        # Заполнить данные
        for row in self.csv_data_rows:
            tree.insert('', tk.END, values=row)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления
        buttons_frame = ttk.Frame(editor_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        def add_row():
            """Добавить новую строку"""
            # Генерировать пример значений
            new_row = []
            for i, header in enumerate(self.imported_data['csv_headers']):
                original_value = self.imported_data['values'][i] if i < len(self.imported_data['values']) else ''
                example_value = self.parser._generate_example_value(header, original_value, len(self.csv_data_rows))
                new_row.append(example_value)

            self.csv_data_rows.append(new_row)
            tree.insert('', tk.END, values=new_row)

        def edit_row():
            """Редактировать выбранную строку"""
            selected = tree.selection()
            if not selected:
                # messagebox убран - просто выходим
                return

            item = tree.item(selected[0])
            values = item['values']

            # Создать диалог редактирования
            edit_dialog = tk.Toplevel(editor_window)
            edit_dialog.title("✏️ Редактирование строки")
            edit_dialog.geometry("500x400")

            entries = []
            for i, (header, value) in enumerate(zip(columns, values)):
                frame = ttk.Frame(edit_dialog)
                frame.pack(fill=tk.X, padx=10, pady=5)

                ttk.Label(frame, text=f"{header}:", width=15).pack(side=tk.LEFT)
                entry = ttk.Entry(frame, width=40)
                entry.insert(0, value)
                entry.pack(side=tk.LEFT, padx=5)
                entries.append(entry)

            def save_edit():
                new_values = [entry.get() for entry in entries]
                tree.item(selected[0], values=new_values)

                # Обновить в csv_data_rows
                index = tree.index(selected[0])
                self.csv_data_rows[index] = new_values

                edit_dialog.destroy()

            ttk.Button(edit_dialog, text="💾 Сохранить", command=save_edit).pack(pady=10)

        def delete_row():
            """Удалить выбранную строку"""
            selected = tree.selection()
            if not selected or len(self.csv_data_rows) <= 1:
                # messagebox убраны - просто выходим
                return

            index = tree.index(selected[0])
            tree.delete(selected[0])
            del self.csv_data_rows[index]

        def save_csv():
            """Сохранить CSV файл"""
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                try:
                    import csv
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(self.imported_data['csv_headers'])
                        writer.writerows(self.csv_data_rows)

                    # messagebox убран - просто сохраняем

                    # Автоматически установить путь в параметризацию
                    self.use_parametrization_var.set(True)
                    self.toggle_parametrization_options()
                    self.csv_path_entry.delete(0, tk.END)
                    self.csv_path_entry.insert(0, file_path)

                except Exception as e:
                    # messagebox убран - просто игнорируем ошибку
                    print(f"Ошибка сохранения CSV: {e}")

        def apply_to_editor():
            """Применить конвертированный код к редактору"""
            # Вставить код в редактор
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", self.imported_data['converted_code'])

            # messagebox убран - просто применяем и закрываем
            editor_window.destroy()

        ttk.Button(buttons_frame, text="➕ Добавить строку", command=add_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="✏️ Редактировать", command=edit_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🗑️ Удалить", command=delete_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="💾 Сохранить CSV", command=save_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="✅ Применить к редактору", command=apply_to_editor,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=2)

    def show_alternatives_help(self):
        """Показать справку по альтернативным сценариям"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 Справка: Альтернативные сценарии")
        help_window.geometry("900x700")
        help_window.transient(self.root)

        # Создать прокручиваемый текстовый виджет
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Текст справки
        help_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        help_text.pack(fill=tk.BOTH, expand=True)

        # Содержание справки с примерами из вашего кода
        content = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   АЛЬТЕРНАТИВНЫЕ СЦЕНАРИИ - ШПАРГАЛКА                        ║
║                                                                              ║
║  Используйте эту функцию, когда UI может показывать РАЗНЫЕ варианты:        ║
║  • A/B тесты (разные версии интерфейса)                                     ║
║  • Модальные окна (появляются/не появляются)                                ║
║  • Разные состояния (залогинен/не залогинен)                                ║
║  • Условные элементы (промо, баннеры, попапы)                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 КАК ИСПОЛЬЗОВАТЬ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Запишите код в Playwright Recorder
2. Вставьте специальные маркеры в код
3. Генератор автоматически создаст try-except для каждого варианта

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 ПРИМЕР ИЗ ВАШЕГО КОДА:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ALTERNATIVE START
page.get_by_role("button", name="Pick your color").click()
page.get_by_test_id("desktop-view").get_by_test_id("testpagekfkfe_card").click()
page.get_by_role("button", name="Select", exact=True).nth(2).click()
# ALTERNATIVE
page.get_by_role("button", name="Pick your color").click()
page.get_by_role("button", name="Select", exact=True).click()
# ALTERNATIVE
page.get_by_role("button", name="Continue", exact=True).click()
page.get_by_role("button", name="Select", exact=True).click()
# ALTERNATIVE END

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ ЧТО ПРОИСХОДИТ ПРИ ГЕНЕРАЦИИ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Генератор создаст код с тремя вариантами:

# ========== АЛЬТЕРНАТИВНЫЕ СЦЕНАРИИ ==========
alternative_success = False

# --- Вариант 1 ---
if not alternative_success:
    try:
        print("[ALTERNATIVE] Пробуем вариант 1...")
        await page.get_by_role("button", name="Pick your color").click()
        await page.get_by_test_id("desktop-view").get_by_test_id("testpagekfkfe_card").click()
        await page.get_by_role("button", name="Select", exact=True).nth(2).click()
        print("[ALTERNATIVE] [SUCCESS] Вариант 1 сработал!")
        alternative_success = True
    except Exception as e:
        print(f"[ALTERNATIVE] Вариант 1 не сработал: {e}")

# --- Вариант 2 ---
if not alternative_success:
    try:
        print("[ALTERNATIVE] Пробуем вариант 2...")
        await page.get_by_role("button", name="Pick your color").click()
        await page.get_by_role("button", name="Select", exact=True).click()
        print("[ALTERNATIVE] [SUCCESS] Вариант 2 сработал!")
        alternative_success = True
    except Exception as e:
        print(f"[ALTERNATIVE] Вариант 2 не сработал: {e}")

# --- Вариант 3 ---
if not alternative_success:
    try:
        print("[ALTERNATIVE] Пробуем вариант 3...")
        await page.get_by_role("button", name="Continue", exact=True).click()
        await page.get_by_role("button", name="Select", exact=True).click()
        print("[ALTERNATIVE] [SUCCESS] Вариант 3 сработал!")
        alternative_success = True
    except Exception as e:
        print(f"[ALTERNATIVE] Вариант 3 не сработал: {e}")

if not alternative_success:
    print("[ALTERNATIVE] [WARNING] Ни один из вариантов не сработал, продолжаем...")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ПРАВИЛА ИСПОЛЬЗОВАНИЯ МАРКЕРОВ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. # ALTERNATIVE START      ← Начало блока альтернатив (обязательно!)
2. <код варианта 1>          ← Первый вариант
3. # ALTERNATIVE              ← Разделитель между вариантами
4. <код варианта 2>          ← Второй вариант
5. # ALTERNATIVE              ← Еще разделитель (можно добавлять сколько угодно)
6. <код варианта 3>          ← Третий вариант
7. # ALTERNATIVE END         ← Конец блока (обязательно!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 ВАЖНО:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Можно использовать СКОЛЬКО УГОДНО вариантов (2, 3, 5, 10...)
✓ Скрипт попробует варианты ПО ПОРЯДКУ
✓ Как только один вариант сработает - остальные пропустятся
✓ Если ВСЕ варианты провалятся - скрипт продолжит работу
✓ Работает с любыми действиями: click, fill, goto

✗ НЕ забывайте закрывать блок с # ALTERNATIVE END
✗ НЕ используйте маркеры внутри обычных комментариев

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 СОВЕТ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Когда записываете код в Playwright Recorder:
1. Пройдите сценарий ПОЛНОСТЬЮ один раз (записывается вариант 1)
2. Закройте браузер, откройте снова
3. Пройдите ВТОРОЙ вариант сценария (записывается вариант 2)
4. Вставьте ОБА варианта в редактор
5. Добавьте маркеры # ALTERNATIVE START/ALTERNATIVE/END
6. Нажмите "Сгенерировать скрипт"

ГОТОВО! Теперь скрипт автоматически выберет нужный вариант! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Даже если вы запустите эту программу через НЕСКОЛЬКО ЛЕТ, эта справка
всегда будет доступна в меню "Справка → Альтернативные сценарии" 📚
        """

        help_text.insert("1.0", content)
        help_text.config(state=tk.DISABLED)

        # Кнопка закрытия
        ttk.Button(help_window, text="Закрыть", command=help_window.destroy).pack(pady=10)

    def show_about(self):
        """Показать информацию о программе"""
        about_text = (
            "Octobrowser Script Builder\n\n"
            "Конструктор скриптов автоматизации\n"
            "для Octobrowser API\n\n"
            "Версия: 2.0\n"
            "Поддержка: Playwright + Selenium\n"
            "Включает: DaisySMS интеграцию"
        )
        messagebox.showinfo("О программе", about_text)


def main():
    """Точка входа приложения"""
    root = tk.Tk()

    # Настройка стилей
    style = ttk.Style()
    style.theme_use('clam')

    app = OctobrowserScriptBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
