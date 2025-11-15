# Octobrowser Script Builder 🚀

**Конструктор скриптов автоматизации для Octobrowser**

Графическое приложение для визуального создания Python скриптов автоматизации с использованием Octobrowser API. Позволяет настраивать профили, прокси, fingerprints и добавлять свой код автоматизации без необходимости вручную писать весь boilerplate код.

---

## 📋 Возможности

### Управление профилями
- ✅ Создание новых профилей через API
- ✅ Настройка названия профиля
- ✅ Автоматический запуск и остановка профилей
- ✅ Опциональное удаление профиля после выполнения

### Fingerprint
- ✅ Генерация случайных fingerprints
- ✅ Выбор типа ОС (Windows, macOS, Linux)
- ✅ Настройка параметров браузера

### Прокси
- ✅ Поддержка HTTP, HTTPS, SOCKS5
- ✅ Настройка хоста и порта
- ✅ Аутентификация (логин/пароль)

### Теги
- ✅ Добавление тегов к профилям
- ✅ Управление несколькими тегами

### Автоматизация
- ✅ Интеграция с Selenium
- ✅ Редактор кода для пользовательских скриптов
- ✅ Генерация готовых Python скриптов
- ✅ Запуск скриптов прямо из приложения
- ✅ Вывод логов в реальном времени

---

## 🛠️ Установка

### Требования
- Python 3.8 или выше
- Octobrowser установлен и запущен
- API токен от Octobrowser

### Шаги установки

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd auto2tesst
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**

Отредактируйте файл `config.json` и укажите ваш API токен:
```json
{
  "octobrowser": {
    "api_base_url": "https://app.octobrowser.net/api/v2/automation",
    "api_token": "ВАШ_API_ТОКЕН_ЗДЕСЬ"
  }
}
```

**Где найти API токен:**
1. Откройте Octobrowser
2. Перейдите в настройки аккаунта
3. Вкладка "Дополнительно" (Additional)
4. Скопируйте API Token

---

## 🚀 Запуск

```bash
python main.py
```

Или сделайте файл исполняемым:
```bash
chmod +x main.py
./main.py
```

---

## 📖 Использование

### 1. Подключение API

При первом запуске:
1. Вставьте ваш API токен в поле "API Token"
2. Нажмите "Подключить API"
3. Дождитесь подтверждения "✓ API подключен"

### 2. Настройка профиля

**Создание профиля:**
- ☑️ Отметьте "Создать новый профиль"
- Введите название профиля (или оставьте автоматическое)
- ☑️ "Остановить профиль после выполнения" - закрывает профиль после работы скрипта

### 3. Настройка Fingerprint

- ☑️ "Использовать случайный fingerprint"
- Выберите тип ОС: Windows / macOS / Linux

### 4. Настройка прокси (опционально)

- ☑️ "Использовать прокси"
- Выберите тип: HTTP / HTTPS / SOCKS5
- Укажите хост и порт
- При необходимости - логин и пароль

### 5. Добавление тегов (опционально)

- ☑️ "Добавить теги к профилю"
- Введите теги через запятую, например: `automation, test, facebook`

### 6. Написание кода автоматизации

В правой части окна находится редактор кода. Введите ваш код автоматизации:

```python
# Пример: навигация на сайт
driver.get("https://example.com")
time.sleep(2)

# Найти элемент и кликнуть
from selenium.webdriver.common.by import By
element = driver.find_element(By.ID, "login-button")
element.click()

# Заполнить форму
username_field = driver.find_element(By.NAME, "username")
username_field.send_keys("myusername")

password_field = driver.find_element(By.NAME, "password")
password_field.send_keys("mypassword")

# Отправить форму
submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
submit_button.click()

print("Автоматизация завершена!")
```

### 7. Генерация скрипта

1. Нажмите **"🔨 Сгенерировать скрипт"**
2. Скрипт будет создан в папке `generated_scripts/`
3. Появится уведомление с путем к файлу

### 8. Запуск скрипта

**Вариант 1: Из приложения**
- Нажмите **"▶️ Запустить скрипт"**
- Наблюдайте вывод в нижней панели
- При необходимости нажмите **"⏹️ Остановить"**

**Вариант 2: Вручную**
```bash
python generated_scripts/automation_script_YYYYMMDD_HHMMSS.py
```

### 9. Сохранение скрипта

Для сохранения в другое место:
1. Нажмите **"💾 Сохранить скрипт"**
2. Выберите расположение и имя файла

---

## 📁 Структура проекта

```
auto2tesst/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── octobrowser_api.py      # API клиент для Octobrowser
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py          # Главное окно приложения
│   │   └── components/             # GUI компоненты
│   ├── generator/
│   │   ├── __init__.py
│   │   └── script_generator.py     # Генератор Python скриптов
│   ├── runner/
│   │   ├── __init__.py
│   │   └── script_runner.py        # Запуск сгенерированных скриптов
│   └── utils/
│       └── __init__.py
├── generated_scripts/              # Сгенерированные скрипты
├── templates/                      # Шаблоны кода
├── config.json                     # Конфигурация
├── main.py                         # Точка входа
├── requirements.txt                # Зависимости
├── README.md                       # Этот файл
└── CLAUDE.md                       # Документация для AI
```

---

## 🔧 API Octobrowser

Приложение использует официальный Octobrowser API v2:

**Документация:**
- Swagger: https://swagger.octobrowser.net/
- Postman: https://documenter.getpostman.com/view/1801428/UVC6i6eA
- Официальные docs: https://docs.octobrowser.net/

**Основные endpoint'ы:**
- `GET /profiles` - Получить список профилей
- `POST /profiles` - Создать профиль
- `POST /profiles/{uuid}/start` - Запустить профиль
- `POST /profiles/{uuid}/stop` - Остановить профиль
- `GET /tags` - Получить теги
- `POST /tags` - Создать тег
- `GET /proxies` - Получить прокси
- `POST /proxies` - Добавить прокси

---

## 🎯 Примеры использования

### Пример 1: Простая навигация

```python
# Код в редакторе
driver.get("https://google.com")
print("Открыта Google")
```

**Что делает скрипт:**
1. Создает профиль с настройками
2. Запускает профиль
3. Подключает Selenium
4. Открывает Google
5. Закрывает браузер
6. Останавливает профиль

### Пример 2: Автоматизация с формами

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver.get("https://example.com/login")

# Ожидание загрузки
wait = WebDriverWait(driver, 10)

# Заполнение формы
username = wait.until(EC.presence_of_element_located((By.ID, "username")))
username.send_keys("myuser")

password = driver.find_element(By.ID, "password")
password.send_keys("mypass")

submit = driver.find_element(By.ID, "submit")
submit.click()

time.sleep(5)
print("Вход выполнен!")
```

### Пример 3: Работа с cookies

```python
driver.get("https://example.com")

# Добавить cookie
driver.add_cookie({
    'name': 'session_id',
    'value': 'abc123',
    'domain': 'example.com'
})

driver.refresh()
print("Cookie добавлен и страница обновлена")
```

---

## ⚙️ Настройки

### config.json

```json
{
  "octobrowser": {
    "api_base_url": "https://app.octobrowser.net/api/v2/automation",
    "api_token": "YOUR_API_TOKEN_HERE"
  },
  "script_settings": {
    "output_directory": "generated_scripts",
    "default_automation_framework": "selenium"
  }
}
```

**Параметры:**
- `api_base_url` - URL API Octobrowser (обычно не нужно менять)
- `api_token` - Ваш API токен
- `output_directory` - Папка для сохранения скриптов
- `default_automation_framework` - Фреймворк по умолчанию (selenium/puppeteer/playwright)

---

## 🐛 Решение проблем

### Ошибка: "API не подключен"
- Проверьте правильность API токена
- Убедитесь, что Octobrowser запущен
- Проверьте интернет-соединение

### Ошибка: "Selenium не может подключиться"
- Убедитесь, что ChromeDriver установлен
- Проверьте, что профиль успешно запущен
- Попробуйте обновить Selenium: `pip install --upgrade selenium`

### Скрипт не запускается
- Проверьте, что все зависимости установлены
- Убедитесь, что Python 3.8+
- Проверьте логи в панели вывода

### Профиль не создается
- Проверьте лимиты вашего тарифа Octobrowser
- Убедитесь, что API токен имеет необходимые права
- Проверьте, что все обязательные поля заполнены

---

## 📝 Roadmap

- [ ] Поддержка Puppeteer/Playwright
- [ ] Импорт/экспорт настроек профилей
- [ ] Шаблоны готовых скриптов
- [ ] Управление cookies через GUI
- [ ] Расширенные настройки fingerprint
- [ ] Поддержка multiple профилей одновременно
- [ ] Визуальный конструктор действий (drag & drop)
- [ ] История сгенерированных скриптов
- [ ] Планировщик задач

---

## 🤝 Вклад в проект

Приветствуются pull requests и issue reports!

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📄 Лицензия

MIT License - см. файл LICENSE

---

## 🔗 Полезные ссылки

- [Octobrowser](https://octobrowser.net/)
- [Octobrowser Docs](https://docs.octobrowser.net/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Python Requests](https://requests.readthedocs.io/)

---

## 📧 Контакты

Если у вас есть вопросы или предложения, создайте issue в репозитории.

---

**Создано с ❤️ для автоматизации с Octobrowser**
