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

        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

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
        self.base_url_entry.insert(0, "https://app.octobrowser.net/api/v2")
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
        token = self.token_entry.get().strip()
        base_url = self.base_url_entry.get().strip()

        if not token:
            if self.toast:
                self.toast.warning("Введите API Token")
            return

        if self.toast:
            self.toast.info("Тестирую подключение...")

        try:
            from ...api.octobrowser_api import OctobrowserAPI

            api = OctobrowserAPI(token, base_url)
            result = api.get_profiles(page=0, page_len=1)

            if 'error' in result:
                if self.toast:
                    self.toast.error(f"Ошибка API: {result.get('error', 'Unknown error')}")
            else:
                if self.toast:
                    self.toast.success("✅ Подключение успешно!")

        except Exception as e:
            if self.toast:
                self.toast.error(f"Ошибка: {str(e)}")

    def save_settings(self):
        """Сохранить все настройки"""
        # Update config
        self.config.setdefault('octobrowser', {})
        self.config['octobrowser']['api_token'] = self.token_entry.get().strip()
        self.config['octobrowser']['api_base_url'] = self.base_url_entry.get().strip()

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
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            if self.toast:
                self.toast.success("Настройки сохранены!")

        except Exception as e:
            if self.toast:
                self.toast.error(f"Ошибка сохранения: {e}")

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
