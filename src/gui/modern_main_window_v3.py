"""
🚀 auto2tesst v3 - EPIC EDITION
Самый продвинутый Playwright-автотестер 2025 года

НОВЫЕ ФИЧИ:
- CTkTabview архитектура
- Умный парсер данных с Faker
- CSV генератор
- Proxy менеджер
- Полные настройки Octo API
- Цветные логи
- Статусбар с прогрессом
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import json
import os
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

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
from src.utils.data_parser import SmartDataParser
from src.sms.provider_manager import ProviderManager
from src.data.dynamic_field import DynamicFieldManager

# Modern UI Components
from .themes import ModernTheme, ButtonStyles
from .components import ToastManager, DataTab, ProxyTab, OctoAPITab


class ModernAppV3(ctk.CTk):
    """
    🎨 auto2tesst v3 - EPIC EDITION

    Коммерческий уровень за $499!
    """

    def __init__(self):
        super().__init__()

        # === НАСТРОЙКИ ОКНА ===
        self.title("auto2tesst v3.0 EPIC - Modern Playwright Automation")
        self.geometry("1600x1000")
        self.minsize(1400, 800)

        # === ТЕМА ===
        ctk.set_appearance_mode("dark")
        self.current_theme = 'dark'
        self.theme = ModernTheme.DARK

        # === ДАННЫЕ ===
        self.config = {}
        self.load_config()

        # === КОМПОНЕНТЫ ===
        self.api: Optional[OctobrowserAPI] = None
        self.generator = ScriptGenerator()
        self.playwright_generator = PlaywrightScriptGenerator()
        self.runner = ScriptRunner()
        self.runner.set_output_callback(self.append_log)
        self.parser = ScriptParser()
        self.side_parser = SeleniumIDEParser()
        self.playwright_parser = PlaywrightParser()
        self.data_parser = SmartDataParser()
        self.sms_provider_manager = ProviderManager()
        self.dynamic_field_manager = DynamicFieldManager()

        # Данные импорта
        self.imported_data = None
        self.csv_data_rows = []

        # === TOAST MANAGER (создаём ДО create_ui!) ===
        self.toast = ToastManager(self)
        self.toast.place_container(relx=0.98, rely=0.98, anchor="se")

        # === СОЗДАНИЕ UI ===
        self.create_ui()

        # 🔥 КРИТИЧНО: Поднять toast контейнер ПОСЛЕ создания всех виджетов!
        # Иначе CTkTabview и другие виджеты закрывают toast
        self.toast.container.lift()
        print("[MAIN WINDOW] Toast контейнер поднят после create_ui()")

        # === ГОРЯЧИЕ КЛАВИШИ ===
        self.setup_hotkeys()

        # Показать приветствие (увеличен delay для полной отрисовки окна)
        self.after(1000, lambda: self.toast.success("🚀 auto2tesst v3 EPIC загружен!", duration=3000))

    # ========================================================================
    # КОНФИГУРАЦИЯ
    # ========================================================================

    def load_config(self):
        """Загрузка конфигурации из config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        print(f"[MAIN] Загрузка config из: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            token = self.config.get('octobrowser', {}).get('api_token', '')
            print(f"[MAIN] ✅ Config загружен. Токен: {token[:10]}..." if token else "[MAIN] ✅ Config загружен. Токен пуст")
        except FileNotFoundError:
            # 🔥 СОЗДАТЬ ДЕФОЛТНЫЙ CONFIG И СОХРАНИТЬ В ФАЙЛ
            self.config = {
                'octobrowser': {'api_base_url': 'https://app.octobrowser.net/api/v2/automation', 'api_token': ''},
                'sms': {'provider': 'daisysms', 'api_key': '', 'service': 'ds'},
                'proxy': {'enabled': False, 'type': 'http', 'host': '', 'port': '', 'login': '', 'password': ''},
                'proxy_list': {'proxies': [], 'rotation_mode': 'sequential', 'retry_on_failure': True, 'timeout': 10},
                'octo_defaults': {'tags': [], 'plugins': [], 'notes': ''},
                'fingerprint': {'os': 'win', 'webrtc': 'altered', 'canvas_protection': True, 'webgl_protection': True, 'fonts_protection': True},
                'geolocation': {'enabled': False, 'latitude': '', 'longitude': ''},
                'ui_settings': {'last_csv_path': '', 'automation_framework': 'playwright', 'playwright_target': 'library'},
                'script_settings': {'output_directory': 'generated_scripts', 'default_automation_framework': 'playwright'}
            }
            # СОХРАНИТЬ ДЕФОЛТНЫЙ CONFIG В ФАЙЛ
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                print(f"[CONFIG] Создан новый config.json с дефолтными настройками")
            except Exception as e:
                print(f"[CONFIG ERROR] Не удалось создать config.json: {e}")

    def save_config(self):
        """Сохранение конфигурации"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.toast.success("Конфигурация сохранена")
        except Exception as e:
            self.toast.error(f"Ошибка сохранения: {e}")

    # ========================================================================
    # СОЗДАНИЕ UI
    # ========================================================================

    def create_ui(self):
        """Создание интерфейса"""
        # 🔥 Конфигурация grid
        self.grid_rowconfigure(0, weight=0)     # Topbar
        self.grid_rowconfigure(1, weight=1)     # Main content with tabs
        self.grid_rowconfigure(2, weight=0)     # Statusbar
        self.grid_columnconfigure(0, weight=1)

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        self.create_top_bar()

        # === ГЛАВНАЯ ОБЛАСТЬ С ТАБАМИ ===
        self.create_main_content()

        # === НИЖНИЙ СТАТУСБАР ===
        self.create_statusbar()

    def create_top_bar(self):
        """Верхняя панель"""
        topbar = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=0
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        # Логотип
        title_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=24, pady=15, sticky="w")

        logo = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=(ModernTheme.FONT['family'], 32)
        )
        logo.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_col.pack(side="left")

        title = ctk.CTkLabel(
            title_col,
            text="auto2tesst v3 EPIC",
            font=(ModernTheme.FONT['family'], 22, 'bold'),
            text_color=self.theme['text_primary']
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_col,
            text="Ultimate Playwright Automation Builder",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_secondary']
        )
        subtitle.pack(anchor="w")

        # Версия
        version = ctk.CTkLabel(
            topbar,
            text="v3.0 EPIC",
            font=(ModernTheme.FONT['family'], 11, 'bold'),
            text_color=self.theme['accent_primary']
        )
        version.grid(row=0, column=1, padx=20, sticky="e")

        # Переключатель темы
        theme_switch = ctk.CTkSegmentedButton(
            topbar,
            values=["🌙 Dark", "☀️ Light"],
            command=self.toggle_theme,
            width=200,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=(ModernTheme.FONT['family'], 11)
        )
        theme_switch.grid(row=0, column=2, padx=24, pady=15, sticky="e")
        theme_switch.set("🌙 Dark")
        self.theme_switch = theme_switch

    def create_main_content(self):
        """Главная область с CTkTabview"""
        # Main container
        main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme['bg_primary']
        )
        main_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # === CTkTabview ===
        self.tabview = ctk.CTkTabview(
            main_container,
            corner_radius=16,
            fg_color=self.theme['bg_secondary'],
            segmented_button_fg_color=self.theme['bg_tertiary'],
            segmented_button_selected_color=self.theme['accent_primary'],
            segmented_button_selected_hover_color=self.theme['bg_hover'],
            segmented_button_unselected_color=self.theme['bg_tertiary'],
            segmented_button_unselected_hover_color=self.theme['bg_hover'],
            text_color=self.theme['text_primary']
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        # Добавить вкладки
        self.tab_import = self.tabview.add("📥 Import Code")
        self.tab_edit = self.tabview.add("✏️ Preview & Edit")
        self.tab_data = self.tabview.add("📊 Data")
        self.tab_proxies = self.tabview.add("🌐 Proxies")
        self.tab_octo = self.tabview.add("🐙 Octo API")
        self.tab_logs = self.tabview.add("📋 Logs")

        # Настроить вкладки
        self.setup_import_tab()
        self.setup_edit_tab()
        self.setup_data_tab()
        self.setup_proxies_tab()
        self.setup_octo_tab()
        self.setup_logs_tab()

    def setup_import_tab(self):
        """Настроить вкладку Import"""
        tab = self.tab_import
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Кнопки импорта
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent", height=80)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
        btn_frame.grid_propagate(False)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="📂 Open Python File",
            command=self.import_from_file,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_primary'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=0, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="📋 Paste from Clipboard",
            command=self.import_from_clipboard,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=1, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="✨ Parse Data → CSV",
            command=self.parse_and_generate_csv,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_success'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=2, padx=8, sticky="ew")

        # Код превью
        preview_container = ctk.CTkFrame(
            tab,
            corner_radius=16,
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        preview_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        self.import_preview = ctk.CTkTextbox(
            preview_container,
            font=('Consolas', 12),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="none",
            border_width=0
        )
        self.import_preview.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # Placeholder
        self.import_preview.insert("1.0", "# 📂 Import your Playwright code here...\n# Use buttons above to load code from file or clipboard")
        self.import_preview.configure(state="disabled")

    def setup_edit_tab(self):
        """Настроить вкладку Preview & Edit"""
        tab = self.tab_edit
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Control buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent", height=80)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
        btn_frame.grid_propagate(False)
        btn_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # 🔥 НОВАЯ КНОПКА: Generate Script
        ctk.CTkButton(
            btn_frame,
            text="⚙️ GENERATE",
            command=self.generate_playwright_script,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_primary'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=0, padx=8, sticky="ew")

        self.run_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ RUN",
            command=self.start_script,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_success'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        )
        self.run_btn.grid(row=0, column=1, padx=8, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️ STOP",
            command=self.stop_script,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_error'],
            state="disabled",
            font=(ModernTheme.FONT['family'], 14, 'bold')
        )
        self.stop_btn.grid(row=0, column=2, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="💾 SAVE",
            command=self.save_script,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_info'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=3, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="🔄 RELOAD",
            command=self.reload_script,
            height=56,
            corner_radius=16,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 14, 'bold')
        ).grid(row=0, column=4, padx=8, sticky="ew")

        # Code editor
        editor_container = ctk.CTkFrame(
            tab,
            corner_radius=16,
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        editor_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        editor_container.grid_columnconfigure(0, weight=1)
        editor_container.grid_rowconfigure(0, weight=1)

        self.code_editor = ctk.CTkTextbox(
            editor_container,
            font=('Consolas', 12),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="none",
            border_width=0
        )
        self.code_editor.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

    def setup_data_tab(self):
        """Настроить вкладку Data"""
        self.data_tab_widget = DataTab(self.tab_data, self.theme, self.toast)
        self.data_tab_widget.pack(fill="both", expand=True)

    def setup_proxies_tab(self):
        """Настроить вкладку Proxies"""
        # 🔥 ИСПРАВЛЕНИЕ: Передаем config для сохранения настроек прокси
        self.proxy_tab_widget = ProxyTab(self.tab_proxies, self.theme, self.config, self.toast)
        self.proxy_tab_widget.pack(fill="both", expand=True)

    def setup_octo_tab(self):
        """Настроить вкладку Octo API"""
        print(f"[MAIN] setup_octo_tab(): config id = {id(self.config)}")
        token = self.config.get('octobrowser', {}).get('api_token', '')
        print(f"[MAIN] Передаю config с токеном: {token[:10]}..." if token else "[MAIN] Передаю config с пустым токеном")
        self.octo_tab_widget = OctoAPITab(self.tab_octo, self.theme, self.config, self.toast)
        self.octo_tab_widget.pack(fill="both", expand=True)

    def setup_logs_tab(self):
        """Настроить вкладку Logs"""
        tab = self.tab_logs
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Control buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent", height=60)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
        btn_frame.grid_propagate(False)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear Logs",
            command=self.clear_logs,
            height=44,
            width=150,
            corner_radius=12,
            fg_color=self.theme['accent_error'],
            font=(ModernTheme.FONT['family'], 12, 'bold')
        ).pack(side="right")

        # Logs display
        log_container = ctk.CTkFrame(
            tab,
            corner_radius=16,
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(
            log_container,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="word",
            border_width=0
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # Configure tags for colored logs
        self.setup_log_tags()

    def setup_log_tags(self):
        """Настроить теги для цветных логов"""
        self.log_textbox.tag_config("INFO", foreground=self.theme['log_info'])
        self.log_textbox.tag_config("SUCCESS", foreground=self.theme['log_success'])
        self.log_textbox.tag_config("ERROR", foreground=self.theme['log_error'])
        self.log_textbox.tag_config("WARNING", foreground=self.theme['log_warning'])
        self.log_textbox.tag_config("DATA", foreground=self.theme['log_smart'])
        self.log_textbox.tag_config("API", foreground=self.theme['accent_primary'])
        self.log_textbox.tag_config("SMART", foreground=self.theme['log_smart'])

    def create_statusbar(self):
        """Нижний статусбар"""
        statusbar = ctk.CTkFrame(
            self,
            height=50,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        statusbar.grid(row=2, column=0, sticky="ew")
        statusbar.grid_propagate(False)
        statusbar.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(
            statusbar,
            text="⚡ Ready",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_primary']
        )
        self.status_label.grid(row=0, column=0, padx=24, pady=12, sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            statusbar,
            width=300,
            height=12,
            corner_radius=6,
            fg_color=self.theme['bg_tertiary'],
            progress_color=self.theme['accent_primary']
        )
        self.progress_bar.grid(row=0, column=1, padx=24, pady=12, sticky="e")
        self.progress_bar.set(0)

        # Thread counter
        self.thread_label = ctk.CTkLabel(
            statusbar,
            text="Threads: 0/1",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_secondary']
        )
        self.thread_label.grid(row=0, column=2, padx=24, pady=12, sticky="e")

    # ========================================================================
    # ИМПОРТ КОДА
    # ========================================================================

    def import_from_file(self):
        """Импорт из файла"""
        filepath = filedialog.askopenfilename(
            title="Select Playwright Python file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.process_imported_code(code)
                self.toast.success(f"✅ Импортирован: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка чтения: {e}")

    def import_from_clipboard(self):
        """Импорт из буфера"""
        try:
            code = self.clipboard_get()
            if code.strip():
                self.process_imported_code(code)
                self.toast.success("✅ Код импортирован из буфера")
            else:
                self.toast.warning("Буфер обмена пуст")
        except Exception as e:
            self.toast.error(f"Ошибка: {e}")

    def process_imported_code(self, code: str):
        """
        Обработка импортированного кода

        НОВАЯ ФИЧА: Автоматический парсинг данных!
        """
        try:
            # Определить тип
            if code.strip().startswith('{'):
                result = self.side_parser.parse_side_json(code)
            else:
                result = self.playwright_parser.parse_playwright_code(code)

            self.imported_data = result

            # Показать в preview
            self.import_preview.configure(state="normal")
            self.import_preview.delete("1.0", "end")
            self.import_preview.insert("1.0", result.get('converted_code', code))
            self.import_preview.configure(state="disabled")

            # Показать в редакторе
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", result.get('converted_code', code))

            # 🔥 АВТОМАТИЧЕСКИЙ ПАРСИНГ ДАННЫХ
            self.auto_parse_data(code)

            self.append_log(f"[INFO] Импортирован код с {len(result.get('actions', []))} действиями", "INFO")
            self.toast.success(f"Найдено {len(result.get('actions', []))} действий")

        except Exception as e:
            self.toast.error(f"Ошибка парсинга: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    def auto_parse_data(self, code: str):
        """
        🔥 АВТОМАТИЧЕСКИЙ ПАРСИНГ ДАННЫХ ИЗ КОДА

        Это ЛЕГЕНДАРНАЯ функция!
        """
        try:
            # Парсить .fill() действия
            fields = self.data_parser.parse_fill_actions(code)

            if not fields:
                self.append_log("[DATA] Данные для CSV не найдены", "DATA")
                return

            # Генерировать CSV данные
            headers, rows = self.data_parser.generate_csv_data(fields, num_rows=10)

            # Установить в Data Tab
            self.data_tab_widget.set_data(headers, rows)

            self.append_log(f"[DATA] Сгенерировано {len(rows)} строк с {len(headers)} полями", "DATA")
            self.append_log(f"[SMART] Автоопределение типов: {', '.join(set(f['type'] for f in fields))}", "SMART")

            self.toast.success(f"🎯 Умный парсинг: {len(fields)} полей → {len(rows)} строк CSV!")

        except Exception as e:
            self.append_log(f"[ERROR] Ошибка парсинга данных: {e}", "ERROR")

    def parse_and_generate_csv(self):
        """Ручной парсинг и генерация CSV"""
        code = self.import_preview.get("1.0", "end-1c")
        if not code or code.startswith("# 📂"):
            self.toast.warning("Сначала импортируйте код")
            return

        self.auto_parse_data(code)

    # ========================================================================
    # ГЕНЕРАЦИЯ СКРИПТА
    # ========================================================================

    def generate_playwright_script(self):
        """Генерация Playwright скрипта"""
        print("[DEBUG] generate_playwright_script() вызван")  # DEBUG

        try:
            # 🔥 ПОЛУЧИТЬ НАСТРОЙКИ ПРОФИЛЯ ИЗ OCTO API TAB
            profile_config = self.octo_tab_widget.get_profile_config()

            # Собрать конфигурацию из всех табов
            config = {
                'api_token': self.config.get('octobrowser', {}).get('api_token', ''),
                'csv_filename': self.config.get('ui_settings', {}).get('last_csv_path', 'data.csv'),
                'target': 'library',  # По умолчанию library mode
                'use_proxy': self.config.get('proxy', {}).get('enabled', False),
                'proxy': self.config.get('proxy', {}),
                'use_sms': False,  # Пока отключено
                'sms': self.config.get('sms', {}),
                # 🔥 ДОБАВЛЯЕМ НАСТРОЙКИ ПРОФИЛЯ
                'profile': profile_config
            }

            print(f"[DEBUG] API Token: {config['api_token'][:10]}..." if config['api_token'] else "[DEBUG] API Token: пуст")  # DEBUG
            print(f"[DEBUG] Profile config: tags={profile_config.get('tags')}, os={profile_config.get('fingerprint', {}).get('os')}")  # DEBUG

            # Проверка токена
            if not config['api_token']:
                self.toast.warning("⚠️ Введите API Token во вкладке Octo API")
                return

            # Получить пользовательский код из редактора или использовать placeholder
            user_code = self.code_editor.get("1.0", "end-1c").strip()
            if not user_code:
                # Если редактор пуст, используем placeholder код
                user_code = '''    # ==== ВАШ КОД АВТОМАТИЗАЦИИ ЗДЕСЬ ====
    # Примеры:
    # page.goto("https://example.com")
    # page.fill("#username", "myuser")
    # page.click("button[type='submit']")
    # page.wait_for_load_state("networkidle")

    print(f"[ITERATION {iteration_number}] Начало автоматизации")
    page.goto("https://example.com")
    print(f"[SUCCESS] Страница загружена")
'''

            print(f"[DEBUG] Длина user_code: {len(user_code)} символов")  # DEBUG

            # Генерация скрипта
            self.append_log("[INFO] Генерация Playwright скрипта...", "INFO")
            generated_script = self.playwright_generator.generate_script(user_code, config)

            # Вставить в редактор
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", generated_script)

            self.append_log("[SUCCESS] ✅ Скрипт сгенерирован успешно!", "SUCCESS")
            self.toast.success("✅ Playwright скрипт сгенерирован!")

        except Exception as e:
            print(f"[DEBUG] Ошибка генерации: {e}")  # DEBUG
            import traceback
            traceback.print_exc()  # DEBUG
            self.toast.error(f"❌ Ошибка генерации: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    # ========================================================================
    # ЗАПУСК СКРИПТА
    # ========================================================================

    def start_script(self):
        """Запуск скрипта"""
        print("[DEBUG] start_script() вызван")  # DEBUG
        code = self.code_editor.get("1.0", "end-1c").strip()
        print(f"[DEBUG] Длина кода в редакторе: {len(code)} символов")  # DEBUG

        if not code:
            print("[DEBUG] Редактор пуст! Нужно сгенерировать скрипт")  # DEBUG
            self.toast.error("⚠️ Редактор пуст! Сначала напишите код или сгенерируйте скрипт")
            return

        try:
            # Сохранить скрипт
            output_dir = Path(self.config['script_settings']['output_directory'])
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_path = output_dir / f"auto2tesst_{timestamp}.py"

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)

            self.append_log(f"[INFO] Скрипт сохранен: {script_path}", "INFO")

            # UI обновление
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="▶️ Running...")
            self.progress_bar.set(0.5)

            # Запуск в потоке
            def run_thread():
                try:
                    self.runner.run_script(str(script_path))
                    self.after(0, lambda: self.toast.success("✅ Скрипт завершен"))
                    self.after(0, lambda: self.append_log("[SUCCESS] Выполнение завершено", "SUCCESS"))
                except Exception as e:
                    self.after(0, lambda: self.toast.error(f"❌ Ошибка: {e}"))
                    self.after(0, lambda: self.append_log(f"[ERROR] {e}", "ERROR"))
                finally:
                    self.after(0, self.script_finished)

            thread = threading.Thread(target=run_thread, daemon=True)
            thread.start()

            self.toast.info("▶️ Скрипт запущен")

        except Exception as e:
            self.toast.error(f"Ошибка запуска: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    def stop_script(self):
        """Остановка скрипта"""
        try:
            self.runner.stop()
            self.toast.warning("⏹️ Скрипт остановлен")
            self.append_log("[WARNING] Скрипт остановлен пользователем", "WARNING")
            self.script_finished()
        except Exception as e:
            self.toast.error(f"Ошибка остановки: {e}")

    def script_finished(self):
        """Завершение скрипта"""
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="⚡ Ready")
        self.progress_bar.set(0)

    def save_script(self):
        """Сохранить скрипт"""
        code = self.code_editor.get("1.0", "end-1c")
        if not code.strip():
            self.toast.warning("Нечего сохранять")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Script",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.toast.success(f"💾 Сохранено: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка сохранения: {e}")

    def reload_script(self):
        """Перезагрузить скрипт"""
        if self.imported_data:
            code = self.imported_data.get('converted_code', '')
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", code)
            self.toast.info("🔄 Скрипт перезагружен")
        else:
            self.toast.warning("Нет импортированного кода")

    # ========================================================================
    # ЛОГИ
    # ========================================================================

    def append_log(self, message: str, tag: str = "INFO"):
        """
        Добавить сообщение в лог с цветом

        Args:
            message: Сообщение
            tag: Тег для цвета (INFO, SUCCESS, ERROR, WARNING, DATA, API, SMART)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"

        self.log_textbox.insert("end", formatted, tag)
        self.log_textbox.see("end")

    def clear_logs(self):
        """Очистить логи"""
        self.log_textbox.delete("1.0", "end")
        self.toast.info("Логи очищены")

    # ========================================================================
    # ДРУГОЕ
    # ========================================================================

    def toggle_theme(self, value):
        """Переключить тему"""
        if "Dark" in value:
            ctk.set_appearance_mode("dark")
            self.toast.info("Темная тема 🌙")
        else:
            ctk.set_appearance_mode("light")
            self.toast.info("Светлая тема ☀️")

    def setup_hotkeys(self):
        """Горячие клавиши"""
        self.bind("<Control-i>", lambda e: self.import_from_file())
        self.bind("<Control-r>", lambda e: self.start_script())
        self.bind("<Escape>", lambda e: self.stop_script() if self.stop_btn.cget("state") == "normal" else None)
        self.bind("<Control-s>", lambda e: self.save_script())
        self.bind("<Control-l>", lambda e: self.clear_logs())


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Запуск приложения"""
    print("=" * 60)
    print("🚀 auto2tesst v3.0 EPIC EDITION")
    print("=" * 60)
    print("✨ Умный парсер данных с Faker")
    print("📊 CSV генератор")
    print("🌐 Proxy менеджер")
    print("🐙 Полные настройки Octo API")
    print("📋 Цветные логи")
    print("=" * 60)

    app = ModernAppV3()
    app.mainloop()


if __name__ == "__main__":
    main()
