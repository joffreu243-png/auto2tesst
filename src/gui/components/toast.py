"""
🍞 Toast Notifications - Красивые ненавязчивые уведомления

Замена для старых messagebox.showinfo/showerror
"""

import customtkinter as ctk
from typing import Literal
import threading


class Toast(ctk.CTkFrame):
    """
    Одно toast-уведомление с анимацией появления/исчезновения
    """

    def __init__(self, parent, message: str, type: Literal['info', 'success', 'warning', 'error'] = 'info', duration: int = 3000):
        from ..themes import ModernTheme

        self.theme = ModernTheme.DARK  # Получим правильную тему от parent позже
        self.duration = duration
        self.type = type

        super().__init__(
            parent,
            corner_radius=ModernTheme.RADIUS['lg'],
            border_width=1,
        )

        # Цвета в зависимости от типа
        colors = {
            'info': (self.theme['accent_info'], self.theme['log_info']),
            'success': (self.theme['accent_success'], self.theme['log_success']),
            'warning': (self.theme['accent_warning'], self.theme['log_warning']),
            'error': (self.theme['accent_error'], self.theme['log_error']),
        }

        bg_color, border_color = colors.get(type, colors['info'])

        self.configure(
            fg_color=bg_color,
            border_color=border_color,
        )

        # Иконка
        icons = {
            'info': ModernTheme.ICONS['info'],
            'success': ModernTheme.ICONS['success'],
            'warning': ModernTheme.ICONS['warning'],
            'error': ModernTheme.ICONS['error'],
        }

        icon = icons.get(type, icons['info'])

        # Лейаут
        self.grid_columnconfigure(1, weight=1)

        # Иконка
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_xl']),
            text_color=self.theme['text_on_accent'],
        )
        self.icon_label.grid(row=0, column=0, padx=(16, 8), pady=12, sticky="w")

        # Сообщение
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_md']),
            text_color=self.theme['text_on_accent'],
            wraplength=300,
            justify="left",
        )
        self.message_label.grid(row=0, column=1, padx=(0, 8), pady=12, sticky="w")

        # Кнопка закрытия
        self.close_button = ctk.CTkButton(
            self,
            text=ModernTheme.ICONS['close'],
            width=24,
            height=24,
            corner_radius=ModernTheme.RADIUS['sm'],
            fg_color="transparent",
            hover_color=self.theme['bg_hover'],
            text_color=self.theme['text_on_accent'],
            command=self.dismiss,
            font=(ModernTheme.FONT['family'], ModernTheme.FONT['size_sm']),
        )
        self.close_button.grid(row=0, column=2, padx=(8, 12), pady=12, sticky="e")

        # Прогресс-бар (опционально)
        self.progress = ctk.CTkProgressBar(
            self,
            height=3,
            corner_radius=0,
            fg_color=bg_color,
            progress_color=self.theme['text_on_accent'],
        )
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.progress.set(1.0)

        # Таймер автозакрытия
        if duration > 0:
            self.auto_dismiss_timer = threading.Timer(duration / 1000, self.dismiss)
            self.auto_dismiss_timer.start()

            # Анимация прогресс-бара
            self._animate_progress()

    def _animate_progress(self):
        """Анимирует прогресс-бар от 1.0 до 0.0"""
        steps = 30
        step_duration = self.duration / steps

        def update_progress(step):
            if step >= 0:
                self.progress.set(step / steps)
                timer = threading.Timer(step_duration / 1000, lambda: update_progress(step - 1))
                timer.start()

        update_progress(steps)

    def dismiss(self):
        """Закрыть toast с анимацией"""
        # Простая анимация: fade out (меняем прозрачность через alpha)
        # В CustomTkinter нет встроенной анимации, так что просто удаляем
        try:
            self.destroy()
        except:
            pass


class ToastManager:
    """
    Менеджер toast-уведомлений
    Показывает уведомления в стеке внизу экрана
    """

    def __init__(self, parent):
        """
        Args:
            parent: Родительский CTk или CTkToplevel
        """
        self.parent = parent
        self.toasts = []
        self.max_toasts = 4  # Максимум одновременных toast

        # Контейнер для toast (внизу справа)
        self.container = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        # Позиционируем внизу справа
        # Это будет вызвано из main window после создания

    def place_container(self, x=None, y=None, relx=None, rely=None, anchor=None):
        """Размещает контейнер в нужном месте окна"""
        if relx is not None or rely is not None:
            self.container.place(relx=relx or 0.95, rely=rely or 0.95, anchor=anchor or "se")
        else:
            self.container.place(x=x or 20, y=y or 20, anchor=anchor or "se")

    def show(self, message: str, type: Literal['info', 'success', 'warning', 'error'] = 'info', duration: int = 3000):
        """
        Показать toast-уведомление

        Args:
            message: Текст сообщения
            type: Тип уведомления (info, success, warning, error)
            duration: Длительность в мс (0 = бесконечно)
        """
        # Убрать лишние toast если их слишком много
        while len(self.toasts) >= self.max_toasts:
            oldest = self.toasts.pop(0)
            try:
                oldest.dismiss()
            except:
                pass

        # Создать новый toast
        toast = Toast(self.container, message, type, duration)
        self.toasts.append(toast)

        # Разместить toast в стеке (снизу вверх)
        self._reposition_toasts()

        return toast

    def _reposition_toasts(self):
        """Переставляет все toast в стеке"""
        spacing = 12
        current_y = 0

        # Снизу вверх
        for i, toast in enumerate(reversed(self.toasts)):
            try:
                toast.pack(side="bottom", fill="x", pady=(0, spacing if i > 0 else 0))
            except:
                self.toasts.remove(toast)

    def info(self, message: str, duration: int = 3000):
        """Показать информационное уведомление"""
        return self.show(message, 'info', duration)

    def success(self, message: str, duration: int = 3000):
        """Показать успешное уведомление"""
        return self.show(message, 'success', duration)

    def warning(self, message: str, duration: int = 3000):
        """Показать предупреждение"""
        return self.show(message, 'warning', duration)

    def error(self, message: str, duration: int = 4000):
        """Показать ошибку (длительность больше)"""
        return self.show(message, 'error', duration)

    def clear_all(self):
        """Закрыть все toast"""
        for toast in self.toasts[:]:
            try:
                toast.dismiss()
            except:
                pass
        self.toasts.clear()
