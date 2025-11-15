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
from src.runner.script_runner import ScriptRunner


class OctobrowserScriptBuilder:
    """Главное окно приложения-конструктора"""

    def __init__(self, root):
        self.root = root
        self.root.title("Octobrowser Script Builder - Конструктор скриптов автоматизации")
        self.root.geometry("1200x800")

        # Загрузка конфигурации
        self.load_config()

        # Инициализация компонентов
        self.api = None
        self.generator = ScriptGenerator()
        self.runner = ScriptRunner()
        self.runner.set_output_callback(self.append_output)

        # Создание интерфейса
        self.create_widgets()

        # Инициализация API если токен есть (без показа messagebox при старте)
        if self.config.get('octobrowser', {}).get('api_token') != 'YOUR_API_TOKEN_HERE':
            self.init_api(show_messages=False)

    def load_config(self):
        """Загрузка конфигурации"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'octobrowser': {
                    'api_base_url': 'https://app.octobrowser.net/api/v2/automation',
                    'api_token': 'YOUR_API_TOKEN_HERE'
                },
                'script_settings': {
                    'output_directory': 'generated_scripts',
                    'default_automation_framework': 'selenium'
                }
            }

    def save_config(self):
        """Сохранение конфигурации"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

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
        # Главный контейнер
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая панель - настройки
        left_panel = ttk.Frame(main_container, width=400)
        main_container.add(left_panel, weight=1)

        # Правая панель - код и вывод
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)

        # === ЛЕВАЯ ПАНЕЛЬ ===
        self.create_left_panel(left_panel)

        # === ПРАВАЯ ПАНЕЛЬ ===
        self.create_right_panel(right_panel)

    def create_left_panel(self, parent):
        """Создание левой панели с настройками"""
        # Canvas для прокрутки
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

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
        self.api_token_entry = ttk.Entry(api_frame, width=40, show="*")
        self.api_token_entry.insert(0, self.config['octobrowser']['api_token'])
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

        ttk.Label(self.cookies_options_frame, text="Cookies (JSON массив):").pack(anchor=tk.W)
        self.cookies_text = scrolledtext.ScrolledText(self.cookies_options_frame, height=4, wrap=tk.WORD,
                                                       font=("Consolas", 9))
        self.cookies_text.pack(fill=tk.X)
        self.cookies_text.insert("1.0", '''[
  {"name": "session", "value": "abc123", "domain": ".example.com"},
  {"name": "user_id", "value": "12345", "domain": ".example.com"}
]''')

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

        ttk.Label(self.bookmarks_options_frame, text="Закладки (JSON массив):").pack(anchor=tk.W)
        self.bookmarks_text = scrolledtext.ScrolledText(self.bookmarks_options_frame, height=4, wrap=tk.WORD,
                                                         font=("Consolas", 9))
        self.bookmarks_text.pack(fill=tk.X)
        self.bookmarks_text.insert("1.0", '''[
  {"title": "Google", "url": "https://google.com"},
  {"title": "GitHub", "url": "https://github.com"}
]''')

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

        ttk.Label(self.extensions_options_frame, text="Пути к расширениям (по одному на строку):").pack(anchor=tk.W)
        self.extensions_text = scrolledtext.ScrolledText(self.extensions_options_frame, height=3, wrap=tk.WORD,
                                                          font=("Consolas", 9))
        self.extensions_text.pack(fill=tk.X)
        self.extensions_text.insert("1.0", '''C:/path/to/extension1.crx
C:/path/to/extension2.crx''')

        self.toggle_extensions_options()

        # === AUTOMATION FRAMEWORK ===
        framework_frame = ttk.LabelFrame(scrollable_frame, text="🤖 Фреймворк автоматизации", padding=10)
        framework_frame.pack(fill=tk.X, padx=5, pady=5)

        self.use_selenium_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(framework_frame, text="Использовать Selenium",
                       variable=self.use_selenium_var).pack(anchor=tk.W)

    def create_right_panel(self, parent):
        """Создание правой панели с кодом"""
        # Верхняя часть - редактор кода
        code_frame = ttk.LabelFrame(parent, text="📝 Код автоматизации (ваш код)", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(code_frame, text="Введите ваш код автоматизации (будет выполняться в контексте driver):").pack(anchor=tk.W)

        self.code_editor = scrolledtext.ScrolledText(code_frame, height=15, wrap=tk.WORD,
                                                     font=("Consolas", 10))
        self.code_editor.pack(fill=tk.BOTH, expand=True, pady=5)

        # Пример кода
        example_code = '''# Пример: навигация и действия
driver.get("https://example.com")
time.sleep(2)

# Найти элемент и кликнуть
from selenium.webdriver.common.by import By
element = driver.find_element(By.ID, "some-button")
element.click()

print("Автоматизация выполнена!")
'''
        self.code_editor.insert("1.0", example_code)

        # Кнопки управления
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttons_frame, text="🔨 Сгенерировать скрипт",
                  command=self.generate_script, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="💾 Сохранить скрипт",
                  command=self.save_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="▶️ Запустить скрипт",
                  command=self.run_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="⏹️ Остановить",
                  command=self.stop_script).pack(side=tk.LEFT, padx=2)

        # Нижняя часть - вывод
        output_frame = ttk.LabelFrame(parent, text="📊 Вывод выполнения", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD,
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

        # Сохраняем настройки
        self.config['octobrowser']['api_token'] = token
        self.config['octobrowser']['api_base_url'] = url
        self.save_config()
        self.init_api()

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
            'use_selenium': self.use_selenium_var.get(),
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
                profile_config['proxy'] = {
                    'type': self.proxy_type_var.get(),
                    'host': self.proxy_host_entry.get(),
                    'port': self.proxy_port_entry.get(),
                    'login': self.proxy_login_entry.get(),
                    'password': self.proxy_password_entry.get()
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

        return options

    def generate_script(self):
        """Генерация скрипта"""
        try:
            options = self.collect_options()
            user_code = self.code_editor.get("1.0", tk.END).strip()

            # Генерация
            script_content = self.generator.generate_script(options, user_code)

            # Сохранение
            output_dir = Path(__file__).parent.parent.parent / 'generated_scripts'
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_name = f"automation_script_{timestamp}.py"
            script_path = output_dir / script_name

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

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
