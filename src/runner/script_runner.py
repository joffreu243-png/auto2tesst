"""
Модуль для запуска сгенерированных скриптов
"""
import subprocess
import sys
import os
from typing import Optional, Callable
import threading


class ScriptRunner:
    """Класс для запуска Python скриптов"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_callback: Optional[Callable] = None

    def set_output_callback(self, callback: Callable[[str], None]):
        """
        Установка callback для вывода

        Args:
            callback: Функция для обработки вывода
        """
        self.output_callback = callback

    def run_script(self, script_path: str, async_mode: bool = True) -> bool:
        """
        Запуск скрипта

        Args:
            script_path: Путь к скрипту
            async_mode: Асинхронный режим запуска

        Returns:
            True если запуск успешен
        """
        if not os.path.exists(script_path):
            if self.output_callback:
                self.output_callback(f"Ошибка: Файл {script_path} не найден\n")
            return False

        if async_mode:
            thread = threading.Thread(target=self._run_script_sync, args=(script_path,))
            thread.daemon = True
            thread.start()
            return True
        else:
            return self._run_script_sync(script_path)

    def _run_script_sync(self, script_path: str) -> bool:
        """
        Синхронный запуск скрипта

        Args:
            script_path: Путь к скрипту

        Returns:
            True если выполнение успешно
        """
        try:
            if self.output_callback:
                self.output_callback(f"Запуск скрипта: {script_path}\n")
                self.output_callback("-" * 50 + "\n")

            # Запуск процесса
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Чтение вывода построчно
            for line in self.process.stdout:
                if self.output_callback:
                    self.output_callback(line)

            # Ожидание завершения
            return_code = self.process.wait()

            if self.output_callback:
                self.output_callback("-" * 50 + "\n")
                if return_code == 0:
                    self.output_callback("Скрипт выполнен успешно\n")
                else:
                    self.output_callback(f"Скрипт завершен с кодом: {return_code}\n")

            return return_code == 0

        except Exception as e:
            if self.output_callback:
                self.output_callback(f"Ошибка выполнения: {str(e)}\n")
            return False

    def stop_script(self):
        """Остановка выполняющегося скрипта"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            if self.output_callback:
                self.output_callback("\nСкрипт остановлен пользователем\n")
