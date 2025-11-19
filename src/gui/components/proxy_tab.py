"""
🌐 Proxy Tab - Управление прокси

Функции:
- Добавление/удаление прокси
- Import from file (txt with proxy list)
- Test proxy connection
- Random rotation per thread
- Support for HTTP, HTTPS, SOCKS5
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Optional, Callable
from pathlib import Path
import re


class ProxyRow(ctk.CTkFrame):
    """Одна строка прокси"""

    def __init__(self, parent, proxy_string: str, row_index: int,
                 on_delete: Callable, on_test: Callable, theme: Dict):
        super().__init__(parent, fg_color="transparent")

        self.proxy_string = proxy_string
        self.row_index = row_index
        self.on_delete = on_delete
        self.on_test = on_test
        self.theme = theme

        self.create_widgets()

    def create_widgets(self):
        """Создать виджеты строки"""
        # Row number
        row_num = ctk.CTkLabel(
            self,
            text=str(self.row_index + 1),
            width=40,
            font=('Consolas', 11),
            text_color=self.theme['text_secondary']
        )
        row_num.pack(side="left", padx=4)

        # Proxy string entry
        self.proxy_entry = ctk.CTkEntry(
            self,
            width=400,
            height=32,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        self.proxy_entry.insert(0, self.proxy_string)
        self.proxy_entry.pack(side="left", padx=4, fill="x", expand=True)

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="⚪ Not tested",
            width=100,
            font=('Consolas', 10),
            text_color=self.theme['text_tertiary']
        )
        self.status_label.pack(side="left", padx=4)

        # Test button
        test_btn = ctk.CTkButton(
            self,
            text="🔍 Test",
            width=80,
            height=32,
            fg_color=self.theme['accent_info'],
            hover_color=self.theme['bg_hover'],
            command=self.test_proxy,
            font=('Consolas', 10)
        )
        test_btn.pack(side="left", padx=4)

        # Delete button
        delete_btn = ctk.CTkButton(
            self,
            text="🗑️",
            width=40,
            height=32,
            fg_color=self.theme['accent_error'],
            hover_color=self.theme['bg_hover'],
            command=self.delete,
            font=('Consolas', 10)
        )
        delete_btn.pack(side="left", padx=4)

    def test_proxy(self):
        """Тестировать прокси"""
        proxy_string = self.proxy_entry.get()
        self.on_test(self.row_index, proxy_string, self.update_status)

    def update_status(self, success: bool, message: str):
        """Обновить статус тестирования"""
        if success:
            self.status_label.configure(
                text=f"✅ {message}",
                text_color=self.theme['log_success']
            )
        else:
            self.status_label.configure(
                text=f"❌ {message}",
                text_color=self.theme['log_error']
            )

    def delete(self):
        """Удалить прокси"""
        self.on_delete(self.row_index)

    def get_proxy(self) -> str:
        """Получить прокси строку"""
        return self.proxy_entry.get()


class ProxyTab(ctk.CTkFrame):
    """
    Вкладка управления прокси
    """

    def __init__(self, parent, theme: Dict, config: Dict, toast_manager=None, save_callback=None):
        super().__init__(parent, fg_color="transparent")

        self.theme = theme
        self.config = config
        self.toast = toast_manager
        self.save_callback = save_callback  # 🔥 Callback для централизованного сохранения

        # Список прокси
        self.proxies = []
        self.proxy_widgets = []

        self.create_widgets()

        # Загрузить сохраненные прокси
        self.load_proxies()

    def create_widgets(self):
        """Создать виджеты"""
        # Конфигурация layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === HEADER ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="🌐 Proxy Manager",
            font=('Segoe UI', 24, 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")

        # Кнопки управления
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        buttons = [
            ("➕ Add Proxy", self.add_proxy, self.theme['accent_success']),
            ("📂 Import File", self.import_proxies, self.theme['accent_secondary']),
            ("💾 Save", self.save_proxies, self.theme['accent_primary']),
            ("🔍 Test All", self.test_all_proxies, self.theme['accent_info']),
            ("🗑️ Clear All", self.clear_all, self.theme['accent_error'])
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                height=40,
                width=120,
                fg_color=color,
                hover_color=self.theme['bg_hover'],
                font=('Segoe UI', 11, 'bold')
            )
            btn.grid(row=0, column=i, padx=4)

        # === PROXY LIST CONTAINER ===
        list_container = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        list_container.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 16))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        # Info bar
        info_frame = ctk.CTkFrame(list_container, fg_color=self.theme['bg_tertiary'], height=60)
        info_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        info_frame.grid_propagate(False)

        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Format: protocol://user:pass@ip:port or ip:port:user:pass",
            font=('Consolas', 11),
            text_color=self.theme['text_secondary'],
            anchor="w"
        )
        info_label.pack(side="left", padx=24, pady=20)

        self.count_label = ctk.CTkLabel(
            info_frame,
            text="Total: 0 proxies",
            font=('Consolas', 11, 'bold'),
            text_color=self.theme['accent_primary']
        )
        self.count_label.pack(side="right", padx=24, pady=20)

        # Scrollable proxy list
        self.proxy_scroll = ctk.CTkScrollableFrame(
            list_container,
            corner_radius=0,
            fg_color=self.theme['bg_primary']
        )
        self.proxy_scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        self.proxy_scroll.grid_columnconfigure(0, weight=1)

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.proxy_scroll,
            text="📡 No proxies yet. Add manually or import from file!",
            font=('Segoe UI', 14),
            text_color=self.theme['text_tertiary']
        )
        self.placeholder.pack(expand=True, pady=100)

        # === SETTINGS ===
        settings_frame = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary'],
            height=120
        )
        settings_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 32))
        settings_frame.grid_propagate(False)
        settings_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Rotation mode
        rotation_label = ctk.CTkLabel(
            settings_frame,
            text="Rotation Mode:",
            font=('Segoe UI', 12, 'bold'),
            text_color=self.theme['text_primary']
        )
        rotation_label.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="w")

        self.rotation_var = tk.StringVar(value="random")
        rotation_segment = ctk.CTkSegmentedButton(
            settings_frame,
            values=["Random", "Round-Robin", "Sticky"],
            variable=self.rotation_var,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=('Segoe UI', 11)
        )
        rotation_segment.grid(row=1, column=0, padx=24, pady=(0, 20), sticky="ew")
        rotation_segment.set("Random")

        # Retry settings
        retry_label = ctk.CTkLabel(
            settings_frame,
            text="Retry on Failure:",
            font=('Segoe UI', 12, 'bold'),
            text_color=self.theme['text_primary']
        )
        retry_label.grid(row=0, column=1, padx=24, pady=(20, 8), sticky="w")

        self.retry_var = tk.BooleanVar(value=True)
        retry_switch = ctk.CTkSwitch(
            settings_frame,
            text="Enabled",
            variable=self.retry_var,
            font=('Segoe UI', 11)
        )
        retry_switch.grid(row=1, column=1, padx=24, pady=(0, 20), sticky="w")

        # Timeout
        timeout_label = ctk.CTkLabel(
            settings_frame,
            text="Timeout (seconds):",
            font=('Segoe UI', 12, 'bold'),
            text_color=self.theme['text_primary']
        )
        timeout_label.grid(row=0, column=2, padx=24, pady=(20, 8), sticky="w")

        self.timeout_entry = ctk.CTkEntry(
            settings_frame,
            width=100,
            height=40,
            font=('Consolas', 12),
            fg_color=self.theme['bg_tertiary']
        )
        self.timeout_entry.insert(0, "10")
        self.timeout_entry.grid(row=1, column=2, padx=24, pady=(0, 20), sticky="w")

    def add_proxy(self):
        """Добавить новый прокси"""
        dialog = ctk.CTkInputDialog(
            text="Enter proxy (e.g., http://user:pass@ip:port):",
            title="Add Proxy"
        )
        proxy_string = dialog.get_input()

        if proxy_string:
            proxy_string = proxy_string.strip()
            if proxy_string:
                self._add_proxy_widget(proxy_string)
                self.update_count()

                if self.toast:
                    self.toast.success("Прокси добавлен")

    def _add_proxy_widget(self, proxy_string: str):
        """Добавить виджет прокси"""
        proxy_widget = ProxyRow(
            self.proxy_scroll,
            proxy_string,
            len(self.proxy_widgets),
            self.delete_proxy,
            self.test_proxy,
            self.theme
        )
        proxy_widget.pack(fill="x", pady=2)
        self.proxy_widgets.append(proxy_widget)
        self.proxies.append(proxy_string)

        # Скрыть placeholder
        self.placeholder.pack_forget()

    def delete_proxy(self, row_index: int):
        """Удалить прокси"""
        if 0 <= row_index < len(self.proxy_widgets):
            self.proxy_widgets[row_index].destroy()
            self.proxy_widgets.pop(row_index)
            self.proxies.pop(row_index)

            # Обновить индексы
            for i, widget in enumerate(self.proxy_widgets):
                widget.row_index = i

            self.update_count()

            if self.toast:
                self.toast.success("Прокси удалён")

            # Показать placeholder если пусто
            if not self.proxies:
                self.placeholder.pack(expand=True, pady=100)

    def import_proxies(self):
        """Импортировать прокси из файла"""
        filepath = filedialog.askopenfilename(
            title="Select proxy list file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                imported_count = 0
                for line in lines:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        self._add_proxy_widget(proxy)
                        imported_count += 1

                self.update_count()

                if self.toast:
                    self.toast.success(f"Импортировано {imported_count} прокси из {Path(filepath).name}")

            except Exception as e:
                if self.toast:
                    self.toast.error(f"Ошибка импорта: {e}")

    def test_proxy(self, row_index: int, proxy_string: str, callback: Callable):
        """
        Тестировать прокси

        Args:
            row_index: Индекс строки
            proxy_string: Прокси строка
            callback: Функция обратного вызова для обновления статуса
        """
        # TODO: Реализовать реальное тестирование через requests
        # Пока что - заглушка
        import threading
        import time

        def test_thread():
            time.sleep(1)  # Симуляция теста
            # Простая валидация формата
            is_valid = self._validate_proxy_format(proxy_string)
            if is_valid:
                callback(True, "Valid")
            else:
                callback(False, "Invalid format")

        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()

    def _validate_proxy_format(self, proxy_string: str) -> bool:
        """Валидация формата прокси"""
        # Поддерживаемые форматы:
        # http://user:pass@ip:port
        # socks5://ip:port
        # ip:port:user:pass
        # ip:port

        patterns = [
            r'^(http|https|socks5)://[\w.-]+:\d+$',  # protocol://ip:port
            r'^(http|https|socks5)://[\w.-]+:[\w.-]+@[\w.-]+:\d+$',  # protocol://user:pass@ip:port
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$',  # ip:port
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+:[\w.-]+:[\w.-]+$'  # ip:port:user:pass
        ]

        for pattern in patterns:
            if re.match(pattern, proxy_string):
                return True

        return False

    def test_all_proxies(self):
        """Тестировать все прокси"""
        if not self.proxy_widgets:
            if self.toast:
                self.toast.warning("Нет прокси для тестирования")
            return

        if self.toast:
            self.toast.info(f"Тестирую {len(self.proxy_widgets)} прокси...")

        for widget in self.proxy_widgets:
            widget.test_proxy()

    def clear_all(self):
        """Очистить все прокси"""
        if not self.proxy_widgets:
            return

        for widget in self.proxy_widgets:
            widget.destroy()

        self.proxy_widgets = []
        self.proxies = []
        self.update_count()
        self.placeholder.pack(expand=True, pady=100)

        if self.toast:
            self.toast.success("Все прокси удалены")

    def update_count(self):
        """Обновить счётчик прокси"""
        self.count_label.configure(text=f"Total: {len(self.proxies)} proxies")

    def get_proxies(self) -> List[str]:
        """Получить список прокси"""
        return [widget.get_proxy() for widget in self.proxy_widgets]

    def get_settings(self) -> Dict:
        """Получить настройки прокси"""
        return {
            'proxies': self.get_proxies(),
            'rotation_mode': self.rotation_var.get().lower(),
            'retry_on_failure': self.retry_var.get(),
            'timeout': int(self.timeout_entry.get()) if self.timeout_entry.get().isdigit() else 10
        }

    def load_proxies(self):
        """Загрузить прокси из config"""
        saved_proxies = self.config.get('proxy_list', {}).get('proxies', [])
        for proxy_string in saved_proxies:
            if proxy_string.strip():
                self._add_proxy_widget(proxy_string.strip())

    def save_proxies(self):
        """
        Сохранить прокси в config (в памяти)

        Файл сохраняется через централизованный метод главного окна.
        """
        print("[PROXY_TAB] === save_proxies() - обновление config в памяти ===")

        self.config.setdefault('proxy_list', {})
        proxies = self.get_proxies()
        self.config['proxy_list']['proxies'] = proxies
        self.config['proxy_list']['rotation_mode'] = self.rotation_var.get().lower()
        self.config['proxy_list']['retry_on_failure'] = self.retry_var.get()
        self.config['proxy_list']['timeout'] = int(self.timeout_entry.get()) if self.timeout_entry.get().isdigit() else 10

        print(f"[PROXY_TAB] Config обновлён: {len(proxies)} прокси")

        # 🔥 СИНХРОНИЗАЦИЯ: Установить первый прокси в config['proxy'] для создания профилей
        self.config.setdefault('proxy', {})
        if proxies and len(proxies) > 0:
            first_proxy = proxies[0]
            parsed = self._parse_proxy_string(first_proxy)
            if parsed:
                self.config['proxy']['enabled'] = True
                self.config['proxy']['type'] = parsed.get('type', 'http')
                self.config['proxy']['host'] = parsed.get('host', '')
                self.config['proxy']['port'] = str(parsed.get('port', ''))
                self.config['proxy']['login'] = parsed.get('login', '')
                self.config['proxy']['password'] = parsed.get('password', '')
                print(f"[PROXY_TAB] Первый прокси установлен для создания профилей: {parsed['type']}://{parsed['host']}:{parsed['port']}")
        else:
            # Нет прокси - отключить
            self.config['proxy']['enabled'] = False
            print(f"[PROXY_TAB] Прокси отключены (список пуст)")

        # 🔥 ЦЕНТРАЛИЗОВАННОЕ СОХРАНЕНИЕ через callback
        if self.save_callback:
            print(f"[PROXY_TAB] Вызываю save_callback() для записи на диск...")
            self.save_callback()
        else:
            print(f"[PROXY_TAB] save_callback не установлен!")
            if self.toast:
                self.toast.warning("Прокси обновлены, но не сохранены")

    def _parse_proxy_string(self, proxy_string: str) -> Optional[Dict]:
        """
        Парсинг прокси строки в компоненты

        Поддерживаемые форматы:
        - type://host:port
        - type://login:password@host:port
        - host:port (по умолчанию http)

        Returns:
            Dict с полями: type, host, port, login, password
        """
        try:
            proxy_string = proxy_string.strip()

            # Паттерн: type://login:password@host:port
            pattern1 = r'^(https?|socks5)://([^:]+):([^@]+)@([^:]+):(\d+)$'
            match = re.match(pattern1, proxy_string)
            if match:
                return {
                    'type': match.group(1),
                    'login': match.group(2),
                    'password': match.group(3),
                    'host': match.group(4),
                    'port': match.group(5)
                }

            # Паттерн: type://host:port
            pattern2 = r'^(https?|socks5)://([^:]+):(\d+)$'
            match = re.match(pattern2, proxy_string)
            if match:
                return {
                    'type': match.group(1),
                    'host': match.group(2),
                    'port': match.group(3),
                    'login': '',
                    'password': ''
                }

            # Паттерн: host:port (без типа, по умолчанию http)
            pattern3 = r'^([^:]+):(\d+)$'
            match = re.match(pattern3, proxy_string)
            if match:
                return {
                    'type': 'http',
                    'host': match.group(1),
                    'port': match.group(2),
                    'login': '',
                    'password': ''
                }

            print(f"[PROXY_TAB] Не удалось распарсить прокси: {proxy_string}")
            return None

        except Exception as e:
            print(f"[PROXY_TAB] Ошибка парсинга прокси: {e}")
            return None

