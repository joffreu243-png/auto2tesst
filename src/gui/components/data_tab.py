"""
📊 Data Tab - Таблица данных с CSV генератором

Умная таблица для управления тестовыми данными с:
- Автоматическим определением типов полей
- Генерацией реалистичных данных через Faker
- Import/Export CSV
- Smart Fill
- Right-click меню с альтернативами
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Dict, Optional, Callable, Tuple
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..themes import ModernTheme
from ...utils.data_parser import SmartDataParser


class DataTableRow(ctk.CTkFrame):
    """
    Одна строка таблицы данных
    """

    def __init__(self, parent, headers: List[str], values: List[str], row_index: int,
                 on_delete: Callable, on_edit: Callable, theme: Dict):
        super().__init__(parent, fg_color="transparent")

        self.headers = headers
        self.values = values
        self.row_index = row_index
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.theme = theme
        self.entries = []

        self.create_widgets()

    def create_widgets(self):
        """Создать виджеты строки"""
        # Row number
        row_num_label = ctk.CTkLabel(
            self,
            text=str(self.row_index + 1),
            width=40,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
            text_color=self.theme['text_secondary']
        )
        row_num_label.grid(row=0, column=0, padx=4, pady=4)

        # Data cells
        for col, (header, value) in enumerate(zip(self.headers, self.values), start=1):
            entry = ctk.CTkEntry(
                self,
                width=150,
                height=32,
                corner_radius=ModernTheme.RADIUS['sm'],
                fg_color=self.theme['bg_tertiary'],
                border_width=1,
                border_color=self.theme['border_primary'],
                font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'])
            )
            entry.insert(0, value)
            entry.grid(row=0, column=col, padx=4, pady=4, sticky="ew")

            # Bind right-click для контекстного меню
            entry.bind("<Button-3>", lambda e, c=col-1: self.show_context_menu(e, c))

            self.entries.append(entry)

        # Delete button
        delete_btn = ctk.CTkButton(
            self,
            text="🗑️",
            width=40,
            height=32,
            corner_radius=ModernTheme.RADIUS['sm'],
            fg_color=self.theme['accent_error'],
            hover_color=self.theme['bg_hover'],
            command=self.delete_row,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'])
        )
        delete_btn.grid(row=0, column=len(self.headers) + 1, padx=4, pady=4)

    def show_context_menu(self, event, col_index):
        """Показать контекстное меню"""
        menu = tk.Menu(self, tearoff=0)

        menu.add_command(label="✨ Generate Random", command=lambda: self.generate_random(col_index))
        menu.add_command(label="📋 Copy", command=lambda: self.copy_cell(col_index))
        menu.add_command(label="📝 Paste", command=lambda: self.paste_cell(col_index))
        menu.add_separator()
        menu.add_command(label="🔄 Regenerate All", command=lambda: self.on_edit(self.row_index, 'regenerate'))

        menu.post(event.x_root, event.y_root)

    def generate_random(self, col_index):
        """Генерировать случайное значение для ячейки"""
        parser = SmartDataParser()
        header = self.headers[col_index]
        field_type = parser.detect_field_type('', header)
        new_value = parser.generate_value(field_type, count=1)[0]
        self.entries[col_index].delete(0, 'end')
        self.entries[col_index].insert(0, new_value)

    def copy_cell(self, col_index):
        """Копировать содержимое ячейки"""
        value = self.entries[col_index].get()
        self.clipboard_clear()
        self.clipboard_append(value)

    def paste_cell(self, col_index):
        """Вставить в ячейку"""
        try:
            value = self.clipboard_get()
            self.entries[col_index].delete(0, 'end')
            self.entries[col_index].insert(0, value)
        except:
            pass

    def delete_row(self):
        """Удалить строку"""
        self.on_delete(self.row_index)

    def get_values(self) -> List[str]:
        """Получить значения строки"""
        return [entry.get() for entry in self.entries]


class DataTab(ctk.CTkFrame):
    """
    Вкладка управления данными с таблицей и CSV генератором
    """

    def __init__(self, parent, theme: Dict, toast_manager=None):
        super().__init__(parent, fg_color="transparent")

        self.theme = theme
        self.toast = toast_manager
        self.parser = SmartDataParser()

        # Данные таблицы
        self.headers = []
        self.rows = []
        self.row_widgets = []

        self.create_widgets()

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
            text="📊 Data Generator & CSV Manager",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xxl'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")

        # Кнопки управления
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        buttons = [
            ("➕ Add Row", self.add_row, self.theme['accent_success']),
            ("✨ Smart Fill", self.smart_fill_all, self.theme['accent_primary']),
            ("📥 Import CSV", self.import_csv, self.theme['accent_secondary']),
            ("📤 Export CSV", self.export_csv, self.theme['accent_info'])
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                height=40,
                width=120,
                corner_radius=ModernTheme.RADIUS['lg'],
                fg_color=color,
                hover_color=self.theme['bg_hover'],
                font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'], 'bold')
            )
            btn.grid(row=0, column=i, padx=4)

        # === TABLE CONTAINER ===
        table_container = ctk.CTkFrame(
            self,
            corner_radius=ModernTheme.RADIUS['xl'],
            fg_color=self.theme['bg_secondary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        table_container.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 32))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)

        # Table header
        table_header_frame = ctk.CTkFrame(table_container, fg_color=self.theme['bg_tertiary'], height=50)
        table_header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        table_header_frame.grid_propagate(False)

        self.table_header_container = table_header_frame

        # Scrollable table
        self.table_scroll = ctk.CTkScrollableFrame(
            table_container,
            corner_radius=0,
            fg_color=self.theme['bg_primary']
        )
        self.table_scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        self.table_scroll.grid_columnconfigure(0, weight=1)

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.table_scroll,
            text="📊 No data yet. Import code or CSV to get started!",
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_lg']),
            text_color=self.theme['text_tertiary']
        )
        self.placeholder.pack(expand=True, pady=100)

    def set_data(self, headers: List[str], rows: List[List[str]]):
        """
        Установить данные таблицы

        Args:
            headers: Заголовки столбцов
            rows: Строки данных
        """
        self.headers = headers
        self.rows = rows

        # Очистить таблицу
        self.clear_table()

        # Создать заголовки
        self.create_header_row()

        # Создать строки
        for row_data in rows:
            self._add_row_widget(row_data)

        # Скрыть placeholder
        if self.rows:
            self.placeholder.pack_forget()

        if self.toast:
            self.toast.success(f"Загружено {len(rows)} строк с {len(headers)} колонками")

    def create_header_row(self):
        """Создать строку заголовков"""
        # Очистить предыдущие заголовки
        for widget in self.table_header_container.winfo_children():
            widget.destroy()

        # Row number
        num_label = ctk.CTkLabel(
            self.table_header_container,
            text="#",
            width=40,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'], 'bold'),
            text_color=self.theme['text_primary']
        )
        num_label.grid(row=0, column=0, padx=4, pady=12)

        # Column headers
        for col, header in enumerate(self.headers, start=1):
            label = ctk.CTkLabel(
                self.table_header_container,
                text=header[:20] + "..." if len(header) > 20 else header,
                width=150,
                font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'], 'bold'),
                text_color=self.theme['text_primary']
            )
            label.grid(row=0, column=col, padx=4, pady=12, sticky="ew")

        # Actions
        actions_label = ctk.CTkLabel(
            self.table_header_container,
            text="Actions",
            width=40,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm'], 'bold'),
            text_color=self.theme['text_primary']
        )
        actions_label.grid(row=0, column=len(self.headers) + 1, padx=4, pady=12)

    def _add_row_widget(self, row_data: List[str]):
        """Добавить виджет строки"""
        row_widget = DataTableRow(
            self.table_scroll,
            self.headers,
            row_data,
            len(self.row_widgets),
            self.delete_row,
            self.edit_row,
            self.theme
        )
        row_widget.pack(fill="x", pady=2)
        self.row_widgets.append(row_widget)

    def add_row(self):
        """Добавить новую строку"""
        if not self.headers:
            if self.toast:
                self.toast.warning("Сначала импортируйте данные или установите заголовки")
            return

        # Генерировать умную строку
        new_row = self.parser.smart_fill_row(self.headers)
        self.rows.append(new_row)
        self._add_row_widget(new_row)

        # Скрыть placeholder
        self.placeholder.pack_forget()

        if self.toast:
            self.toast.success("Добавлена новая строка")

    def delete_row(self, row_index: int):
        """Удалить строку"""
        if 0 <= row_index < len(self.row_widgets):
            # Удалить виджет
            self.row_widgets[row_index].destroy()
            self.row_widgets.pop(row_index)
            self.rows.pop(row_index)

            # Обновить индексы
            for i, row_widget in enumerate(self.row_widgets):
                row_widget.row_index = i

            if self.toast:
                self.toast.success("Строка удалена")

            # Показать placeholder если пусто
            if not self.rows:
                self.placeholder.pack(expand=True, pady=100)

    def edit_row(self, row_index: int, action: str):
        """Редактировать строку"""
        if action == 'regenerate' and 0 <= row_index < len(self.row_widgets):
            new_row = self.parser.smart_fill_row(self.headers)
            row_widget = self.row_widgets[row_index]

            for entry, value in zip(row_widget.entries, new_row):
                entry.delete(0, 'end')
                entry.insert(0, value)

            if self.toast:
                self.toast.success("Строка перегенерирована")

    def smart_fill_all(self):
        """Умное заполнение всех строк"""
        if not self.headers:
            if self.toast:
                self.toast.warning("Сначала импортируйте данные или установите заголовки")
            return

        # Спросить количество строк
        dialog = ctk.CTkInputDialog(
            text="Сколько строк сгенерировать?",
            title="Smart Fill"
        )
        num_rows_str = dialog.get_input()

        if num_rows_str:
            try:
                num_rows = int(num_rows_str)
                if num_rows <= 0 or num_rows > 1000:
                    if self.toast:
                        self.toast.error("Введите число от 1 до 1000")
                    return

                # Очистить текущие данные
                self.clear_table()

                # Генерировать строки
                for _ in range(num_rows):
                    row = self.parser.smart_fill_row(self.headers)
                    self.rows.append(row)
                    self._add_row_widget(row)

                # Скрыть placeholder
                self.placeholder.pack_forget()

                if self.toast:
                    self.toast.success(f"Сгенерировано {num_rows} строк с реалистичными данными!")

            except ValueError:
                if self.toast:
                    self.toast.error("Некорректное число")

    def import_csv(self):
        """Импортировать CSV файл"""
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filepath:
            headers, rows = self.parser.import_from_csv(filepath)

            if headers and rows:
                self.set_data(headers, rows)
                if self.toast:
                    self.toast.success(f"Импортировано из {Path(filepath).name}")
            else:
                if self.toast:
                    self.toast.error("Ошибка чтения CSV файла")

    def export_csv(self):
        """Экспортировать в CSV файл"""
        if not self.headers or not self.rows:
            if self.toast:
                self.toast.warning("Нет данных для экспорта")
            return

        # Получить актуальные значения из виджетов
        current_rows = []
        for row_widget in self.row_widgets:
            current_rows.append(row_widget.get_values())

        filepath = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filepath:
            success = self.parser.export_to_csv(filepath, self.headers, current_rows)
            if success:
                if self.toast:
                    self.toast.success(f"Экспортировано в {Path(filepath).name}")
            else:
                if self.toast:
                    self.toast.error("Ошибка записи CSV файла")

    def clear_table(self):
        """Очистить таблицу"""
        for row_widget in self.row_widgets:
            row_widget.destroy()

        self.row_widgets = []
        self.rows = []

    def get_data(self) -> Tuple[List[str], List[List[str]]]:
        """
        Получить текущие данные таблицы

        Returns:
            (headers, rows)
        """
        current_rows = []
        for row_widget in self.row_widgets:
            current_rows.append(row_widget.get_values())

        return self.headers, current_rows
