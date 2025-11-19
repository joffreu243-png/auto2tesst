# 🚀 Installation Guide - auto2tesst v2.0

## Быстрая установка (рекомендуется)

### Windows:

```powershell
# 1. Создать виртуальное окружение (опционально, но рекомендуется)
python -m venv venv
.\venv\Scripts\activate

# 2. Установить все зависимости
pip install -r requirements.txt

# 3. Запустить
python main.py
```

### Linux/macOS:

```bash
# 1. Создать виртуальное окружение (опционально, но рекомендуется)
python3 -m venv venv
source venv/bin/activate

# 2. Установить все зависимости
pip install -r requirements.txt

# 3. Запустить
python main.py
```

---

## ⚠️ Устранение проблем

### Ошибка: `ModuleNotFoundError: No module named 'packaging'`

**Решение:**

```bash
pip install packaging darkdetect
```

Или переустановите все зависимости:

```bash
pip install -r requirements.txt --upgrade
```

### Ошибка: `ModuleNotFoundError: No module named 'customtkinter'`

**Решение:**

```bash
pip install customtkinter
```

### CustomTkinter не работает / есть проблемы с GUI

**Используйте старый UI:**

```bash
python main_legacy.py
```

Это запустит старую версию интерфейса (Tkinter), которая работает без CustomTkinter.

---

## 📦 Полный список зависимостей

```
requests==2.31.0          # HTTP клиент для API
selenium==4.15.2          # Selenium автоматизация
playwright==1.40.0        # Playwright автоматизация
tkinter-tooltip==2.1.0    # Подсказки для GUI
pillow==10.1.0            # Работа с изображениями
openpyxl==3.1.2           # Работа с Excel
customtkinter==5.2.1      # Современный UI (v2.0)
tkinterdnd2==0.3.0        # Drag & Drop (опционально)
packaging>=21.0           # Зависимость CustomTkinter
darkdetect>=0.7.0         # Определение темной темы системы
```

---

## 🐍 Требования

- **Python**: 3.8 или выше
- **ОС**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)

---

## 🔧 Пошаговая установка с нуля

### 1. Проверить версию Python

```bash
python --version
# Должно быть >= 3.8
```

Если Python не установлен:
- **Windows**: [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-pip`

### 2. Клонировать репозиторий (если еще не сделали)

```bash
git clone <repository-url>
cd auto2tesst
```

### 3. Создать виртуальное окружение (рекомендуется)

**Почему виртуальное окружение?**
- Изолирует зависимости проекта
- Избегает конфликтов с другими проектами
- Легко удалить и пересоздать

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

После активации в консоли появится `(venv)` перед командной строкой.

### 4. Обновить pip (рекомендуется)

```bash
python -m pip install --upgrade pip
```

### 5. Установить зависимости

```bash
pip install -r requirements.txt
```

**Что делает эта команда:**
- Читает `requirements.txt`
- Скачивает и устанавливает все указанные пакеты
- Может занять 1-3 минуты

### 6. Проверить установку

```bash
python -c "import customtkinter; print('CustomTkinter:', customtkinter.__version__)"
python -c "import playwright; print('Playwright:', playwright.__version__)"
```

Если обе команды выводят версии - установка успешна!

### 7. Запустить приложение

```bash
python main.py
```

Должно открыться окно с современным UI! 🎉

---

## 🚨 Частые проблемы

### 1. `pip: command not found`

**Решение:**

```bash
# Используйте python -m pip вместо pip
python -m pip install -r requirements.txt
```

### 2. `Permission denied` на Linux/macOS

**Решение:**

```bash
# Используйте --user для установки в домашнюю директорию
pip install -r requirements.txt --user
```

### 3. Медленная установка / таймауты

**Решение:**

```bash
# Используйте зеркало PyPI ближе к вам
pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. `tkinter` не найден на Linux

**Решение:**

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### 5. Окно не открывается / вылетает сразу

**Проверьте:**

1. Запустите legacy UI:
   ```bash
   python main_legacy.py
   ```

2. Если legacy работает - проблема с CustomTkinter

3. Переустановите CustomTkinter:
   ```bash
   pip uninstall customtkinter
   pip install customtkinter==5.2.1
   ```

---

## 💡 Полезные команды

### Деактивировать виртуальное окружение

```bash
deactivate
```

### Удалить и пересоздать виртуальное окружение

```bash
# Windows
rmdir /s venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Показать все установленные пакеты

```bash
pip list
```

### Обновить все зависимости

```bash
pip install -r requirements.txt --upgrade
```

---

## 📞 Поддержка

Если ничего не помогло:

1. Откройте issue на GitHub с описанием проблемы
2. Приложите вывод команд:
   ```bash
   python --version
   pip list
   python main.py  # полный вывод ошибки
   ```

3. Укажите вашу ОС и версию

---

## ✅ Готово!

После успешной установки переходите к [MODERN_UI_GUIDE.md](MODERN_UI_GUIDE.md) для изучения нового интерфейса!
