"""
📁 Collapsible Frame - Сворачиваемые секции

Умные секции которые можно сворачивать/разворачивать одним кликом
Заменяют громоздкие scrollbars и ползунки
"""

import customtkinter as ctk
from typing import Callable, Optional


class CollapsibleFrame(ctk.CTkFrame):
    """
    Сворачиваемая секция с анимацией

    Usage:
        section = CollapsibleFrame(parent, title="Settings")
        section.pack(fill="x", padx=10, pady=5)

        # Добавить виджеты внутрь
        label = ctk.CTkLabel(section.content_frame, text="Hello")
        label.pack()
    """

    def __init__(
        self,
        parent,
        title: str = "Section",
        collapsed: bool = False,
        on_toggle: Optional[Callable] = None,
        **kwargs
    ):
        from ..themes import ModernTheme

        self.theme = ModernTheme.DARK
        self.title_text = title
        self.is_collapsed = collapsed
        self.on_toggle_callback = on_toggle

        super().__init__(
            parent,
            corner_radius=ModernTheme.RADIUS['lg'],
            border_width=1,
            fg_color=self.theme['bg_secondary'],
            border_color=self.theme['border_primary'],
            **kwargs
        )

        self.grid_columnconfigure(0, weight=1)

        # === HEADER (кликабельный заголовок) ===
        self.header = ctk.CTkFrame(
            self,
            corner_radius=ModernTheme.RADIUS['md'],
            fg_color="transparent",
            cursor="hand2",
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        self.header.grid_columnconfigure(1, weight=1)

        # Иконка expand/collapse
        self.icon_label = ctk.CTkLabel(
            self.header,
            text=ModernTheme.ICONS['collapse'] if not collapsed else ModernTheme.ICONS['expand'],
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md']),
            text_color=self.theme['accent_primary'],
            width=24,
        )
        self.icon_label.grid(row=0, column=0, padx=(4, 8), sticky="w")

        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.header,
            text=title,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md'], 'bold'),
            text_color=self.theme['text_primary'],
            anchor="w",
        )
        self.title_label.grid(row=0, column=1, sticky="ew")

        # Сделать header кликабельным
        self.header.bind("<Button-1>", lambda e: self.toggle())
        self.icon_label.bind("<Button-1>", lambda e: self.toggle())
        self.title_label.bind("<Button-1>", lambda e: self.toggle())

        # === CONTENT FRAME (сворачиваемое содержимое) ===
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
        )

        if not collapsed:
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        else:
            self.content_frame.grid_remove()

        self.grid_rowconfigure(1, weight=1)

    def toggle(self):
        """Переключить состояние (свернуто/развернуто)"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()

        # Вызвать callback если есть
        if self.on_toggle_callback:
            self.on_toggle_callback(self.is_collapsed)

    def expand(self):
        """Развернуть секцию"""
        from ..themes import ModernTheme

        self.is_collapsed = False
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.icon_label.configure(text=ModernTheme.ICONS['collapse'])

    def collapse(self):
        """Свернуть секцию"""
        from ..themes import ModernTheme

        self.is_collapsed = True
        self.content_frame.grid_remove()
        self.icon_label.configure(text=ModernTheme.ICONS['expand'])

    def set_theme(self, theme_dict):
        """Обновить тему"""
        self.theme = theme_dict
        self.configure(
            fg_color=self.theme['bg_secondary'],
            border_color=self.theme['border_primary'],
        )
        self.icon_label.configure(text_color=self.theme['accent_primary'])
        self.title_label.configure(text_color=self.theme['text_primary'])


class CollapsibleSection:
    """
    Упрощенная обертка для создания collapsible sections
    С автоматическим добавлением виджетов внутрь
    """

    def __init__(self, parent, title: str, collapsed: bool = False):
        self.frame = CollapsibleFrame(parent, title=title, collapsed=collapsed)
        self.content = self.frame.content_frame

    def pack(self, **kwargs):
        """Pack the collapsible frame"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the collapsible frame"""
        self.frame.grid(**kwargs)

    def add_widget(self, widget_class, **kwargs):
        """Добавить виджет внутрь секции"""
        widget = widget_class(self.content, **kwargs)
        return widget

    def add_label(self, text, **kwargs):
        """Быстрое добавление Label"""
        return self.add_widget(ctk.CTkLabel, text=text, **kwargs)

    def add_entry(self, placeholder="", **kwargs):
        """Быстрое добавление Entry"""
        return self.add_widget(ctk.CTkEntry, placeholder_text=placeholder, **kwargs)

    def add_button(self, text, command=None, **kwargs):
        """Быстрое добавление Button"""
        return self.add_widget(ctk.CTkButton, text=text, command=command, **kwargs)

    def toggle(self):
        """Toggle expanded/collapsed"""
        self.frame.toggle()

    def expand(self):
        """Expand"""
        self.frame.expand()

    def collapse(self):
        """Collapse"""
        self.frame.collapse()
