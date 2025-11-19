"""
🍞 Toast Notifications - Красивые ненавязчивые уведомления

Замена для старых messagebox.showinfo/showerror

ИСПРАВЛЕНО:
- Убраны все threading.Timer (причина TclError)
- Используется только self.after() (безопасно для Tkinter)
- Добавлен флаг _destroyed для защиты от ошибок
"""

import customtkinter as ctk
from typing import Literal


class Toast(ctk.CTkFrame):
    """
    Одно toast-уведомление с безопасной анимацией

    Без threading.Timer - только self.after()!
    """

    def __init__(self, parent, message: str, type: Literal['info', 'success', 'warning', 'error'] = 'info', duration: int = 3000):
        print(f"[TOAST DEBUG] Toast.__init__(): parent={parent}, message={message[:30]}, type={type}")  # DEBUG
        from ..themes import ModernTheme

        self.theme = ModernTheme.DARK
        self.duration = duration
        self.type = type
        self._destroyed = False  # 🔥 Флаг для предотвращения TclError
        self._after_ids = []  # 🔥 Список всех after ID для отмены

        print(f"[TOAST DEBUG] Вызываю super().__init__() для создания Frame")  # DEBUG
        super().__init__(
            parent,
            corner_radius=ModernTheme.RADIUS['lg'],
            border_width=1,
        )
        print(f"[TOAST DEBUG] Frame создан")  # DEBUG

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

        # 🔥 Запуск безопасной анимации с self.after() вместо threading.Timer
        if duration > 0:
            self._start_progress_animation()

    def _start_progress_animation(self):
        """
        Безопасная анимация прогресс-бара через self.after()

        Вместо threading.Timer используется рекурсивный self.after()
        """
        if self._destroyed:
            return

        # Параметры анимации
        steps = 30
        step_duration_ms = self.duration / steps

        def update_progress(current_step):
            """Рекурсивное обновление прогресс-бара"""
            if self._destroyed:
                return

            if current_step >= 0:
                # Обновить прогресс
                try:
                    self.progress.set(current_step / steps)
                except:
                    # Если виджет уже уничтожен - выходим
                    return

                # Запланировать следующий шаг
                after_id = self.after(int(step_duration_ms), lambda: update_progress(current_step - 1))
                self._after_ids.append(after_id)
            else:
                # Прогресс завершен - закрыть toast
                after_id = self.after(100, self.dismiss)
                self._after_ids.append(after_id)

        # Начать анимацию
        update_progress(steps)

    def dismiss(self):
        """
        Закрыть toast с безопасным уничтожением

        КРИТИЧНО: Отменяем все after() перед destroy()
        """
        if self._destroyed:
            return

        # 🔥 Установить флаг сразу
        self._destroyed = True

        # 🔥 Отменить все запланированные after()
        for after_id in self._after_ids:
            try:
                self.after_cancel(after_id)
            except:
                pass

        self._after_ids.clear()

        # Уничтожить виджет
        try:
            super().destroy()
        except:
            pass

    def destroy(self):
        """
        Переопределение destroy() для безопасного уничтожения

        Вызывается автоматически при закрытии окна или удалении виджета
        """
        self.dismiss()


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

    def place_container(self, x=None, y=None, relx=None, rely=None, anchor=None):
        """Размещает контейнер в нужном месте окна"""
        print(f"[TOAST DEBUG] place_container() вызван: relx={relx}, rely={rely}, anchor={anchor}")  # DEBUG

        if relx is not None or rely is not None:
            self.container.place(relx=relx or 0.95, rely=rely or 0.95, anchor=anchor or "se")
            print(f"[TOAST DEBUG] Контейнер размещён: place(relx={relx or 0.95}, rely={rely or 0.95}, anchor={anchor or 'se'})")  # DEBUG
        else:
            self.container.place(x=x or 20, y=y or 20, anchor=anchor or "se")
            print(f"[TOAST DEBUG] Контейнер размещён: place(x={x or 20}, y={y or 20}, anchor={anchor or 'se'})")  # DEBUG

        # 🔥 ИСПРАВЛЕНИЕ: Поднять контейнер поверх всех виджетов
        self.container.lift()
        print(f"[TOAST DEBUG] Контейнер поднят: lift()")  # DEBUG

        # Проверка размещения
        self.container.update_idletasks()
        print(f"[TOAST DEBUG] Контейнер после update_idletasks():")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_viewable={self.container.winfo_viewable()}")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_ismapped={self.container.winfo_ismapped()}")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_width={self.container.winfo_width()}")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_height={self.container.winfo_height()}")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_x={self.container.winfo_x()}")  # DEBUG
        print(f"[TOAST DEBUG]   winfo_y={self.container.winfo_y()}")  # DEBUG

    def show(self, message: str, type: Literal['info', 'success', 'warning', 'error'] = 'info', duration: int = 3000):
        """
        Показать toast-уведомление

        Args:
            message: Текст сообщения
            type: Тип уведомления (info, success, warning, error)
            duration: Длительность в мс (0 = бесконечно)
        """
        print(f"[TOAST DEBUG] show() вызван: type={type}, message={message[:50]}")  # DEBUG
        print(f"[TOAST DEBUG] self.container={self.container}")  # DEBUG
        print(f"[TOAST DEBUG] len(self.toasts)={len(self.toasts)}")  # DEBUG

        # Убрать лишние toast если их слишком много
        while len(self.toasts) >= self.max_toasts:
            oldest = self.toasts.pop(0)
            try:
                oldest.dismiss()
            except:
                pass

        # Создать новый toast
        print(f"[TOAST DEBUG] Создаю новый Toast...")  # DEBUG
        toast = Toast(self.container, message, type, duration)
        print(f"[TOAST DEBUG] Toast создан: {toast}")  # DEBUG
        self.toasts.append(toast)

        # Разместить toast в стеке (снизу вверх)
        print(f"[TOAST DEBUG] Вызываю _reposition_toasts()")  # DEBUG
        self._reposition_toasts()

        # 🔥 ИСПРАВЛЕНИЕ: Поднять контейнер поверх всех виджетов после добавления toast
        self.container.lift()
        print(f"[TOAST DEBUG] Контейнер поднят после добавления toast")  # DEBUG

        # Обновить геометрию и принудительно обновить окно
        self.container.update_idletasks()
        self.parent.update()  # Принудительное обновление окна
        print(f"[TOAST DEBUG] После размещения toast:")  # DEBUG
        print(f"[TOAST DEBUG]   container.winfo_width={self.container.winfo_width()}")  # DEBUG
        print(f"[TOAST DEBUG]   container.winfo_height={self.container.winfo_height()}")  # DEBUG
        print(f"[TOAST DEBUG]   container.winfo_ismapped={self.container.winfo_ismapped()}")  # DEBUG
        print(f"[TOAST DEBUG]   container.winfo_viewable={self.container.winfo_viewable()}")  # DEBUG
        print(f"[TOAST DEBUG]   toast.winfo_width={toast.winfo_width()}")  # DEBUG
        print(f"[TOAST DEBUG]   toast.winfo_height={toast.winfo_height()}")  # DEBUG
        print(f"[TOAST DEBUG]   toast.winfo_ismapped={toast.winfo_ismapped()}")  # DEBUG
        print(f"[TOAST DEBUG]   toast.winfo_viewable={toast.winfo_viewable()}")  # DEBUG

        print(f"[TOAST DEBUG] show() завершён, toast должен быть виден!")  # DEBUG

        return toast

    def _reposition_toasts(self):
        """Переставляет все toast в стеке"""
        spacing = 12

        print(f"[TOAST DEBUG] _reposition_toasts(): всего {len(self.toasts)} toast")  # DEBUG

        # Снизу вверх
        for i, toast in enumerate(reversed(self.toasts)):
            try:
                print(f"[TOAST DEBUG] Размещаю toast #{i}: destroyed={toast._destroyed}")  # DEBUG
                if not toast._destroyed:
                    toast.pack(side="bottom", fill="x", pady=(0, spacing if i > 0 else 0))
                    print(f"[TOAST DEBUG] Toast #{i} размещён: side=bottom, fill=x")  # DEBUG
            except Exception as e:
                print(f"[TOAST DEBUG] Ошибка размещения toast #{i}: {e}")  # DEBUG
                # Удалить уничтоженные toast из списка
                if toast in self.toasts:
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
