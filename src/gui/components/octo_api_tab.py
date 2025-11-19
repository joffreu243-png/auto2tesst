"""
🐙 Octo API Tab - Полные настройки Octobrowser API

Функции:
- API Token configuration
- Default Tags управление
- Default Plugins (upload .zip or folder)
- Fingerprint overrides (OS, WebRTC, Canvas, Fonts, etc.)
- Notes field
- Profile templates
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List, Optional
from pathlib import Path
import json


class OctoAPITab(ctk.CTkScrollableFrame):
    """
    Вкладка настроек Octobrowser API
    """

    def __init__(self, parent, theme: Dict, config: Dict, toast_manager=None):
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.theme = theme
        self.config = config
        self.toast = toast_manager

        print(f"[OCTO_TAB] __init__ вызван")
        print(f"[OCTO_TAB] config id: {id(config)}")
        token = config.get('octobrowser', {}).get('api_token', '')
        print(f"[OCTO_TAB] Токен при инициализации: {token[:10]}..." if token else "[OCTO_TAB] Токен при инициализации пуст")

        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

        # 🔥 ЗАГРУЗИТЬ СОХРАНЕННЫЕ НАСТРОЙКИ
        self.load_saved_settings()

    def create_widgets(self):
        """Создать виджеты"""
        # === HEADER ===
        header = ctk.CTkLabel(
            self,
            text="🐙 Octobrowser API Settings",
            font=('Segoe UI', 24, 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w"
        )
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")

        # === API TOKEN SECTION ===
        token_section = self.create_collapsible_section(
            "🔐 API Token Configuration",
            row=1
        )

        ctk.CTkLabel(
            token_section,
            text="Access Token:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.token_entry = ctk.CTkEntry(
            token_section,
            placeholder_text="Enter your Octobrowser API token",
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            border_width=1
        )
        self.token_entry.pack(fill="x", padx=16, pady=(0, 8))

        # Load saved token
        saved_token = self.config.get('octobrowser', {}).get('api_token', '')
        if saved_token:
            self.token_entry.insert(0, saved_token)

        ctk.CTkLabel(
            token_section,
            text="Base URL:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(8, 4))

        self.base_url_entry = ctk.CTkEntry(
            token_section,
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary']
        )
        # 🔥 ПРАВИЛЬНЫЙ Base URL с /automation согласно официальной документации
        # https://documenter.getpostman.com/view/1801428/UVC6i6eA
        # Загружаем сохраненный URL или используем default
        saved_base_url = self.config.get('octobrowser', {}).get('api_base_url', '')
        if not saved_base_url:
            saved_base_url = "https://app.octobrowser.net/api/v2/automation"
        self.base_url_entry.insert(0, saved_base_url)
        self.base_url_entry.pack(fill="x", padx=16, pady=(0, 8))

        test_btn = ctk.CTkButton(
            token_section,
            text="🔍 Test Connection",
            command=self.test_connection,
            height=44,
            fg_color=self.theme['accent_info'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 11, 'bold')
        )
        test_btn.pack(fill="x", padx=16, pady=(8, 16))

        # === TAGS SECTION ===
        tags_section = self.create_collapsible_section(
            "🏷️ Default Tags",
            row=2
        )

        ctk.CTkLabel(
            tags_section,
            text="Tags (comma-separated):",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self.tags_entry = ctk.CTkEntry(
            tags_section,
            placeholder_text="leadgen, us, automation",
            height=44,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary']
        )
        self.tags_entry.pack(fill="x", padx=16, pady=(0, 16))

        # === PLUGINS SECTION ===
        plugins_section = self.create_collapsible_section(
            "🔌 Default Plugins",
            row=3
        )

        self.plugins_listbox = ctk.CTkTextbox(
            plugins_section,
            height=100,
            font=('Consolas', 10),
            fg_color=self.theme['bg_tertiary']
        )
        self.plugins_listbox.pack(fill="x", padx=16, pady=(16, 8))

        plugins_btn_frame = ctk.CTkFrame(plugins_section, fg_color="transparent")
        plugins_btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            plugins_btn_frame,
            text="📂 Add Plugin (.zip)",
            command=self.add_plugin_zip,
            height=36,
            fg_color=self.theme['accent_secondary'],
            font=('Segoe UI', 10)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            plugins_btn_frame,
            text="📁 Add Folder",
            command=self.add_plugin_folder,
            height=36,
            fg_color=self.theme['accent_secondary'],
            font=('Segoe UI', 10)
        ).pack(side="left")

        # === FINGERPRINT OVERRIDES ===
        fp_section = self.create_collapsible_section(
            "🔍 Fingerprint Overrides",
            row=4
        )

        # OS Selection
        os_frame = ctk.CTkFrame(fp_section, fg_color="transparent")
        os_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            os_frame,
            text="Operating System:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 8))

        self.os_var = tk.StringVar(value="random")
        os_segment = ctk.CTkSegmentedButton(
            os_frame,
            values=["Random", "Windows", "macOS", "Linux"],
            variable=self.os_var,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=('Segoe UI', 10)
        )
        os_segment.pack(side="left", fill="x", expand=True)
        os_segment.set("Random")

        # WebRTC Mode
        webrtc_frame = ctk.CTkFrame(fp_section, fg_color="transparent")
        webrtc_frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            webrtc_frame,
            text="WebRTC Mode:",
            font=('Segoe UI', 11),
            text_color=self.theme['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=(0, 8))

        self.webrtc_var = tk.StringVar(value="altered")
        webrtc_segment = ctk.CTkSegmentedButton(
            webrtc_frame,
            values=["Disabled", "Real", "Altered"],
            variable=self.webrtc_var,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=('Segoe UI', 10)
        )
        webrtc_segment.pack(side="left", fill="x", expand=True)
        webrtc_segment.set("Altered")

        # Canvas Protection
        self.canvas_var = tk.BooleanVar(value=True)
        canvas_switch = ctk.CTkSwitch(
            fp_section,
            text="Canvas Protection",
            variable=self.canvas_var,
            font=('Segoe UI', 11)
        )
        canvas_switch.pack(anchor="w", padx=16, pady=8)

        # WebGL Protection
        self.webgl_var = tk.BooleanVar(value=True)
        webgl_switch = ctk.CTkSwitch(
            fp_section,
            text="WebGL Protection",
            variable=self.webgl_var,
            font=('Segoe UI', 11)
        )
        webgl_switch.pack(anchor="w", padx=16, pady=8)

        # Fonts Protection
        self.fonts_var = tk.BooleanVar(value=True)
        fonts_switch = ctk.CTkSwitch(
            fp_section,
            text="Fonts Protection",
            variable=self.fonts_var,
            font=('Segoe UI', 11)
        )
        fonts_switch.pack(anchor="w", padx=16, pady=(8, 16))

        # === GEOLOCATION ===
        geo_section = self.create_collapsible_section(
            "🌍 Geolocation Settings",
            row=5
        )

        self.geo_enabled_var = tk.BooleanVar(value=False)
        geo_switch = ctk.CTkSwitch(
            geo_section,
            text="Enable Custom Geolocation",
            variable=self.geo_enabled_var,
            command=self.toggle_geo,
            font=('Segoe UI', 11)
        )
        geo_switch.pack(anchor="w", padx=16, pady=16)

        self.geo_frame = ctk.CTkFrame(geo_section, fg_color="transparent")

        geo_grid = ctk.CTkFrame(self.geo_frame, fg_color="transparent")
        geo_grid.pack(fill="x", padx=16, pady=(0, 16))
        geo_grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            geo_grid,
            text="Latitude:",
            font=('Segoe UI', 10),
            text_color=self.theme['text_secondary']
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.lat_entry = ctk.CTkEntry(
            geo_grid,
            placeholder_text="40.7128",
            height=36,
            font=('Consolas', 10)
        )
        self.lat_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(
            geo_grid,
            text="Longitude:",
            font=('Segoe UI', 10),
            text_color=self.theme['text_secondary']
        ).grid(row=0, column=1, sticky="w", pady=4)

        self.lon_entry = ctk.CTkEntry(
            geo_grid,
            placeholder_text="-74.0060",
            height=36,
            font=('Consolas', 10)
        )
        self.lon_entry.grid(row=1, column=1, sticky="ew")

        # === NOTES ===
        notes_section = self.create_collapsible_section(
            "📝 Profile Notes",
            row=6
        )

        self.notes_textbox = ctk.CTkTextbox(
            notes_section,
            height=120,
            font=('Consolas', 10),
            fg_color=self.theme['bg_tertiary']
        )
        self.notes_textbox.pack(fill="both", padx=16, pady=16)

        # === SAVE BUTTON ===
        save_btn = ctk.CTkButton(
            self,
            text="💾 Save API Settings",
            command=self.save_settings,
            height=56,
            fg_color=self.theme['accent_primary'],
            hover_color=self.theme['bg_hover'],
            font=('Segoe UI', 14, 'bold')
        )
        save_btn.grid(row=7, column=0, padx=32, pady=32, sticky="ew")

    def create_collapsible_section(self, title: str, row: int) -> ctk.CTkFrame:
        """Создать сворачиваемую секцию"""
        from .collapsible_frame import CollapsibleFrame

        section = CollapsibleFrame(self, title=title)
        section.grid(row=row, column=0, padx=32, pady=8, sticky="ew")
        return section.content_frame

    def toggle_geo(self):
        """Переключить геолокацию"""
        if self.geo_enabled_var.get():
            self.geo_frame.pack(fill="x", padx=0, pady=0)
        else:
            self.geo_frame.pack_forget()

    def add_plugin_zip(self):
        """Добавить плагин из .zip"""
        filepath = filedialog.askopenfilename(
            title="Select Plugin ZIP",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )

        if filepath:
            current_text = self.plugins_listbox.get("1.0", "end-1c")
            if current_text.strip():
                self.plugins_listbox.insert("end", "\n")
            self.plugins_listbox.insert("end", filepath)

            if self.toast:
                self.toast.success(f"Плагин добавлен: {Path(filepath).name}")

    def add_plugin_folder(self):
        """Добавить плагин из папки"""
        folderpath = filedialog.askdirectory(title="Select Plugin Folder")

        if folderpath:
            current_text = self.plugins_listbox.get("1.0", "end-1c")
            if current_text.strip():
                self.plugins_listbox.insert("end", "\n")
            self.plugins_listbox.insert("end", folderpath)

            if self.toast:
                self.toast.success(f"Папка плагина добавлена: {Path(folderpath).name}")

    def test_connection(self):
        """Тестировать подключение к API"""
        import requests

        print("[DEBUG] test_connection() вызван")  # DEBUG
        print(f"[DEBUG] self.toast = {self.toast}")  # DEBUG

        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        print(f"[DEBUG] token = {token[:10]}..." if token else "[DEBUG] token пуст")  # DEBUG
        print(f"[DEBUG] base_url = {base_url}")  # DEBUG

        if not token:
            print("[DEBUG] Токен пуст, показываю warning")  # DEBUG
            if self.toast:
                self.toast.warning("Введите API Token")
            return

        print("[DEBUG] Показываю info toast")  # DEBUG
        if self.toast:
            self.toast.info("Тестирую подключение...")

        print("[DEBUG] Начинаю запрос к API")  # DEBUG
        try:
            # Прямой запрос с правильным заголовком X-Octo-Api-Token
            # Официальная документация: https://docs.octobrowser.net/
            # Для теста подключения просто запрашиваем список профилей без параметров
            response = requests.get(
                f"{base_url}/profiles",
                headers={"X-Octo-Api-Token": token},
                timeout=10
            )

            print(f"[DEBUG] Получен ответ: status_code={response.status_code}")  # DEBUG

            # Вывод полного ответа для отладки 400 ошибок
            if response.status_code == 400:
                print(f"[DEBUG] Response body: {response.text}")  # DEBUG

            if response.status_code == 200:
                print("[DEBUG] Успех! Показываю success toast")  # DEBUG
                if self.toast:
                    self.toast.success("✅ Octo API подключён успешно!")
                # Автосохранение после успешного подключения
                self.save_settings()
            elif response.status_code == 401:
                print("[DEBUG] 401 Unauthorized")  # DEBUG
                if self.toast:
                    self.toast.error("❌ Неверный токен (401 Unauthorized)")
            elif response.status_code == 403:
                print("[DEBUG] 403 Forbidden")  # DEBUG
                if self.toast:
                    self.toast.error("❌ Доступ запрещён (403 Forbidden)")
            else:
                print(f"[DEBUG] Другой код: {response.status_code}")  # DEBUG
                if self.toast:
                    self.toast.error(f"Ошибка {response.status_code}: {response.text[:100]}")

        except requests.exceptions.ConnectionError as e:
            print(f"[DEBUG] ConnectionError: {e}")  # DEBUG
            if self.toast:
                self.toast.error("❌ Нет соединения с Octo Browser")
        except requests.exceptions.Timeout as e:
            print(f"[DEBUG] Timeout: {e}")  # DEBUG
            if self.toast:
                self.toast.error("❌ Превышено время ожидания")
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")  # DEBUG
            import traceback
            traceback.print_exc()  # DEBUG
            if self.toast:
                self.toast.error(f"Ошибка: {str(e)}")

    def save_settings(self):
        """Сохранить все настройки"""
        print("[OCTO_TAB] === НАЧАЛО save_settings() ===")

        # Update config
        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        print(f"[OCTO_TAB] Сохраняю токен: {token[:10]}..." if token else "[OCTO_TAB] Токен пуст")
        print(f"[OCTO_TAB] Сохраняю base_url: {base_url}")

        self.config.setdefault('octobrowser', {})
        self.config['octobrowser']['api_token'] = token
        self.config['octobrowser']['api_base_url'] = base_url

        self.config.setdefault('octo_defaults', {})
        self.config['octo_defaults']['tags'] = [
            tag.strip() for tag in self.tags_entry.get().split(',') if tag.strip()
        ]
        self.config['octo_defaults']['plugins'] = [
            plugin.strip() for plugin in self.plugins_listbox.get("1.0", "end-1c").split('\n') if plugin.strip()
        ]
        self.config['octo_defaults']['notes'] = self.notes_textbox.get("1.0", "end-1c").strip()

        # Fingerprint settings
        self.config.setdefault('fingerprint', {})
        self.config['fingerprint']['os'] = self.os_var.get().lower()
        self.config['fingerprint']['webrtc'] = self.webrtc_var.get().lower()
        self.config['fingerprint']['canvas_protection'] = self.canvas_var.get()
        self.config['fingerprint']['webgl_protection'] = self.webgl_var.get()
        self.config['fingerprint']['fonts_protection'] = self.fonts_var.get()

        # Geolocation
        self.config.setdefault('geolocation', {})
        self.config['geolocation']['enabled'] = self.geo_enabled_var.get()
        self.config['geolocation']['latitude'] = self.lat_entry.get().strip()
        self.config['geolocation']['longitude'] = self.lon_entry.get().strip()

        # Save to file
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        print(f"[OCTO_TAB] Путь к config: {config_path}")
        print(f"[OCTO_TAB] config существует: {config_path.exists()}")
        print(f"[OCTO_TAB] id(self.config) = {id(self.config)}")
        print(f"[OCTO_TAB] self.config is dict: {isinstance(self.config, dict)}")

        try:
            print(f"[OCTO_TAB] Записываю в файл...")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"[OCTO_TAB] ✅ Файл записан на диск!")
            print(f"[OCTO_TAB] Токен в self.config: {self.config.get('octobrowser', {}).get('api_token', '')[:10]}...")

            # 🔥 ПРОВЕРКА: Прочитаем файл обратно, чтобы убедиться что он обновился
            print(f"[OCTO_TAB] === ПРОВЕРКА: Читаю файл обратно ===")
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            saved_token = saved_config.get('octobrowser', {}).get('api_token', '')
            print(f"[OCTO_TAB] Токен в ФАЙЛЕ: {saved_token[:10]}..." if saved_token else "[OCTO_TAB] ❌ ТОКЕН В ФАЙЛЕ ПУСТОЙ!")

            if saved_token != token:
                print(f"[OCTO_TAB] ⚠️ ВНИМАНИЕ: Токены не совпадают!")
                print(f"[OCTO_TAB]   Ожидали: {token[:10]}...")
                print(f"[OCTO_TAB]   В файле: {saved_token[:10]}..." if saved_token else "пусто")

            if self.toast:
                self.toast.success("Настройки сохранены!")

        except Exception as e:
            print(f"[OCTO_TAB] ❌ ОШИБКА сохранения: {e}")
            import traceback
            traceback.print_exc()
            if self.toast:
                self.toast.error(f"Ошибка сохранения: {e}")

    def load_saved_settings(self):
        """Загрузить сохраненные настройки из config"""
        # Tags
        saved_tags = self.config.get('octo_defaults', {}).get('tags', [])
        if saved_tags:
            self.tags_entry.insert(0, ', '.join(saved_tags))

        # Plugins
        saved_plugins = self.config.get('octo_defaults', {}).get('plugins', [])
        if saved_plugins:
            self.plugins_listbox.delete("1.0", "end")
            self.plugins_listbox.insert("1.0", '\n'.join(saved_plugins))

        # Notes
        saved_notes = self.config.get('octo_defaults', {}).get('notes', '')
        if saved_notes:
            self.notes_textbox.delete("1.0", "end")
            self.notes_textbox.insert("1.0", saved_notes)

        # Fingerprint
        fingerprint = self.config.get('fingerprint', {})
        if fingerprint:
            os_value = fingerprint.get('os', 'win').capitalize()
            if os_value.lower() == 'random':
                os_value = 'Random'
            self.os_var.set(os_value)

            webrtc_value = fingerprint.get('webrtc', 'altered').capitalize()
            self.webrtc_var.set(webrtc_value)

            self.canvas_var.set(fingerprint.get('canvas_protection', True))
            self.webgl_var.set(fingerprint.get('webgl_protection', True))
            self.fonts_var.set(fingerprint.get('fonts_protection', True))

        # Geolocation
        geo = self.config.get('geolocation', {})
        if geo:
            self.geo_enabled_var.set(geo.get('enabled', False))

            lat = geo.get('latitude', '')
            if lat:
                self.lat_entry.insert(0, lat)

            lon = geo.get('longitude', '')
            if lon:
                self.lon_entry.insert(0, lon)

    def get_profile_config(self) -> Dict:
        """
        Получить конфигурацию профиля для создания через API

        Returns:
            Словарь с настройками профиля
        """
        config = {
            'tags': [tag.strip() for tag in self.tags_entry.get().split(',') if tag.strip()],
            'notes': self.notes_textbox.get("1.0", "end-1c").strip(),
            'fingerprint': {
                'os': self.os_var.get().lower() if self.os_var.get() != 'Random' else 'random',
                'webrtc': {
                    'mode': self.webrtc_var.get().lower()
                },
                'canvas': {
                    'mode': 'noise' if self.canvas_var.get() else 'off'
                },
                'webgl': {
                    'mode': 'noise' if self.webgl_var.get() else 'off'
                },
                'fonts': {
                    'enable_masking': self.fonts_var.get()
                }
            }
        }

        # Geolocation
        if self.geo_enabled_var.get():
            try:
                lat = float(self.lat_entry.get())
                lon = float(self.lon_entry.get())
                config['geolocation'] = {
                    'mode': 'manual',
                    'latitude': lat,
                    'longitude': lon
                }
            except:
                pass

        return config
