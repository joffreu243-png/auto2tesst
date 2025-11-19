#!/usr/bin/env python3
"""
auto2tesst v3.0 EPIC EDITION
Коммерческий уровень за $499!

НОВЫЕ ФИЧИ v3:
- 🧠 Умный парсер данных с Faker
- 📊 Автоматический CSV генератор
- 🌐 Proxy менеджер с тестированием
- 🐙 Полные настройки Octo Browser API
- 📋 Цветные логи с тегами
- 🎯 CTkTabview архитектура
- ⚡ Статусбар с прогрессом
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.modern_main_window_v3 import main

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 auto2tesst v3.0 EPIC EDITION")
    print("=" * 80)
    print("💎 Коммерческий уровень за $499!")
    print()
    print("✨ НОВЫЕ ФИЧИ:")
    print("   🧠 Умный парсер данных с автоопределением типов")
    print("   📊 CSV генератор с Faker integration")
    print("   🌐 Proxy менеджер с rotation & testing")
    print("   🐙 Полные настройки Octobrowser API")
    print("   🏷️  Default Tags, Plugins, Fingerprints")
    print("   📋 Цветные логи (INFO, SUCCESS, ERROR, DATA, API)")
    print("   🎯 CTkTabview - 6 вкладок")
    print("   ⚡ Статусбар с прогрессом и threads")
    print()
    print("⌨️  HOTKEYS:")
    print("   Ctrl+I  - Import Code")
    print("   Ctrl+R  - Run Script")
    print("   Ctrl+S  - Save Script")
    print("   Ctrl+L  - Clear Logs")
    print("   Esc     - Stop Script")
    print("=" * 80)
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n✋ Приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
