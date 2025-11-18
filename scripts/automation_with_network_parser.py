"""
Автоматизация с парсингом Network данных
- Читает данные из CSV файла
- Выполняет автоматизацию с использованием данных
- Перехватывает Network responses
- Сохраняет результаты обратно в CSV
"""

import sys
import os
import time
from pathlib import Path

# Добавляем путь к модулям проекта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import Playwright, sync_playwright, expect
from src.utils.csv_manager import CSVManager
from src.utils.network_parser import NetworkParser, parse_quote_response


def run(playwright: Playwright, data_row: dict, row_index: int, csv_manager: CSVManager) -> None:
    """
    Основная функция автоматизации

    Args:
        playwright: Playwright instance
        data_row: Строка данных из CSV
        row_index: Индекс строки в CSV
        csv_manager: Менеджер CSV для сохранения результатов
    """

    # Инициализация Network Parser
    network_parser = NetworkParser()

    # Добавляем фильтры для интересующих нас endpoints
    # Примеры - замените на реальные URL из вашего приложения
    network_parser.add_filter(r'.*api.*quote.*', parse_quote_response)
    network_parser.add_filter(r'.*bind.*')
    network_parser.add_filter(r'.*policy.*')
    network_parser.add_filter(r'.*prefill.*')

    # Запускаем браузер
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Подключаем Network Parser к странице
    network_parser.attach_to_page(page)

    print(f"\n{'='*60}")
    print(f"Начало автоматизации для: {data_row['first_name']} {data_row['last_name']}")
    print(f"Email: {data_row['email']}")
    print(f"Phone: {data_row['phone']}")
    print(f"{'='*60}\n")

    try:
        # === НАЧАЛО АВТОМАТИЗАЦИИ ===

        # Шаг 1: Открываем сайт и вводим zip code
        page.goto("https://www.mytestsite.org/")
        page.get_by_role("textbox", name="Enter your  code").click()
        page.get_by_role("textbox", name="Enter your type code").fill(data_row['zip_code'])
        page.get_by_role("button", name="See My Shampoo").click()

        # Шаг 2: Начало опросника
        page.goto("https://www.mytestsite.org/sqaf/#/start/")
        page.get_by_role("button", name="No").click()
        page.get_by_role("button", name="No").click()
        page.get_by_role("button", name="Own").click()
        page.get_by_role("button", name="2014").click()
        page.get_by_role("button", name="Ford icon Ford").click()
        page.get_by_role("button", name="Escape").click()
        page.get_by_role("button", name="I don't know").click()
        page.get_by_role("button", name="Commuting or personal use").click()
        page.get_by_role("button", name="15 es").click()
        page.get_by_role("button", name="Owned").click()
        page.get_by_role("button", name="No").click()
        page.get_by_role("button", name="No").click()

        # Шаг 3: Дата рождения из CSV
        page.get_by_role("textbox", name="MM").click()
        page.get_by_role("textbox", name="MM").fill(data_row['birth_month'])
        page.get_by_role("textbox", name="DD").fill(data_row['birth_day'])
        page.get_by_role("textbox", name="YYYY").fill(data_row['birth_year'])
        page.get_by_role("button", name="Next").click()

        # Шаг 4: Пол и образование из CSV
        page.get_by_role("button", name=data_row['gender'], exact=True).click()
        page.get_by_role("button", name="Yes").click()
        page.get_by_role("button", name="16").click()
        page.get_by_role("button", name="Excellent").click()
        page.get_by_role("button", name=data_row['education']).click()
        page.get_by_role("button", name="No").click()
        page.get_by_role("button", name="Continue").click()

        # Шаг 5: История страхования
        page.get_by_role("button", name="No").click()
        page.get_by_role("button", name="My policy expired").click()
        page.get_by_role("button", name="More than a month").click()
        page.get_by_role("button", name="0").click()
        page.get_by_role("button", name="0").click()
        page.get_by_role("button", name="0").click()
        page.get_by_role("button", name="0").click()
        page.get_by_role("button", name="No Common choice").click()

        # Шаг 6: Личные данные из CSV
        page.get_by_role("textbox", name="Fe").click()
        page.get_by_role("textbox", name="Fe").fill(data_row['first_name'])
        page.locator("div").filter(has_text="💰an save up").nth(2).click()
        page.get_by_role("textbox", name="Last name").click()
        page.get_by_role("textbox", name="Last name").fill(data_row['last_name'])
        page.get_by_role("button", name="Next").click()

        # Шаг 7: Адрес из CSV
        page.get_by_role("button", name="No").click()
        page.get_by_role("textbox", name="Enter col").click()
        page.get_by_role("textbox", name="Enter col").fill(data_row['address'])

        # Ждем появления автокомплита и кликаем
        time.sleep(2)
        try:
            # Пытаемся кликнуть на первый результат автокомплита
            page.locator("[role='option']").first.click()
        except:
            # Если автокомплит не появился, просто продолжаем
            pass

        page.get_by_role("textbox", name="type code").click()
        page.get_by_role("button", name="Next").click()

        # Шаг 8: Email и телефон из CSV
        page.get_by_role("textbox", name="Email address").click()
        page.get_by_role("textbox", name="Email address").fill(data_row['email'])
        page.get_by_test_id("app").click()
        page.get_by_role("button", name="Next").click()

        # Форматируем телефон
        formatted_phone = csv_manager.format_phone(data_row['phone'])
        page.get_by_role("textbox", name="Phone number").click()
        page.get_by_role("textbox", name="Phone number").fill(formatted_phone)

        # Шаг 9: Открытие результатов (новая вкладка page1)
        with page.expect_popup() as page1_info:
            page.get_by_role("button", name="View my Shampoo").click()
        page1 = page1_info.value

        # Подключаем Network Parser к новой вкладке
        network_parser.attach_to_page(page1)

        page1.goto("https://www.mytestsite.org/compare/#/Shampoo/carte_list")
        page.goto("https://www.mytestsite.org/save/more")
        page1.goto("https://www.mytestsite.org/compare/#/Shampoo/carte_list")
        page.goto("https://www.mytestsite.org/save/more/")

        # Шаг 10: Выбор предложения
        page1.get_by_text("See more").click()
        page1.locator("#carte-item-248441766").get_by_role("button", name="View").click()
        page1.locator("#carte-item-248441766").get_by_role("button", name="View").click()

        # Шаг 11: Открытие формы покупки (новая вкладка page2)
        with page1.expect_popup() as page2_info:
            page1.get_by_role("button", name="Buy online").click()
        page2 = page2_info.value

        # Подключаем Network Parser к третьей вкладке
        network_parser.attach_to_page(page2)

        page2.goto("https://carte.mytestsite2.org/partner_prefill_review/0")
        page2.get_by_role("button", name="Looks good").click()
        page2.get_by_role("button", name="Continue with this address").click()

        # Шаг 12: Финальные шаги
        page2.goto("https://carte.mytestsite2.org/prefill_report_review/0")
        page2.get_by_role("button", name="Let's go").click()
        page2.get_by_role("button", name="Continue").click()
        page2.get_by_role("button", name="Continue and exclude").click()

        # Переключение автомобилей
        page2.get_by_role("switch", name="Ford Escape Covered").uncheck()
        page2.get_by_role("switch", name="Chevrolet Trailblazer Not Covered").check()
        page2.get_by_role("button", name="Continue").click()
        page2.get_by_role("button", name="Continue to carte").click()

        # Финальная страница
        page2.goto("https://bind.joinmytestsite2.org/bind/loading")

        # Ждем загрузки всех Network запросов
        time.sleep(3)

        print("\n" + "="*60)
        print("ПАРСИНГ NETWORK ДАННЫХ")
        print("="*60)

        # === ПАРСИНГ NETWORK RESPONSES ===

        # Получаем все захваченные responses
        all_responses = network_parser.get_all_responses()
        print(f"\nВсего захвачено responses: {len(all_responses)}")

        # Пример 1: Поиск quote ID
        quote_id = network_parser.extract_json_field(r'.*quote.*', 'quote_id')
        if not quote_id:
            quote_id = network_parser.extract_json_field(r'.*quote.*', 'id')
        if not quote_id:
            quote_id = network_parser.extract_json_field(r'.*quote.*', 'data.id')

        # Пример 2: Поиск premium price
        premium_price = network_parser.extract_json_field(r'.*quote.*', 'premium_price')
        if not premium_price:
            premium_price = network_parser.extract_json_field(r'.*quote.*', 'premium')
        if not premium_price:
            premium_price = network_parser.extract_json_field(r'.*quote.*', 'data.premium')

        # Пример 3: Поиск carrier name
        carrier_name = network_parser.extract_json_field(r'.*quote.*', 'carrier_name')
        if not carrier_name:
            carrier_name = network_parser.extract_json_field(r'.*quote.*', 'carrier')

        # Пример 4: Поиск policy URL
        policy_url = network_parser.extract_json_field(r'.*policy.*', 'policy_url')
        if not policy_url:
            policy_url = network_parser.extract_json_field(r'.*bind.*', 'url')

        # Выводим найденные данные
        print(f"\n📊 Извлеченные данные:")
        print(f"  Quote ID: {quote_id or 'Не найден'}")
        print(f"  Premium Price: {premium_price or 'Не найден'}")
        print(f"  Carrier Name: {carrier_name or 'Не найден'}")
        print(f"  Policy URL: {policy_url or 'Не найден'}")

        # Сохраняем все responses в JSON файл для отладки
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        responses_file = project_root / "data" / f"network_responses_{timestamp}.json"
        network_parser.save_responses_to_file(str(responses_file))

        # === СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В CSV ===

        result_data = {
            'quote_id': quote_id or '',
            'premium_price': premium_price or '',
            'carrier_name': carrier_name or '',
            'policy_url': policy_url or '',
        }

        # Отмечаем строку как выполненную
        csv_manager.mark_as_completed(row_index, result_data)
        print(f"\n✅ Результаты сохранены в CSV (строка {row_index})")

        print("\n" + "="*60)
        print("АВТОМАТИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("="*60)

        # Небольшая пауза чтобы увидеть результат
        time.sleep(2)

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        csv_manager.mark_as_failed(row_index, str(e))

    finally:
        # Закрываем браузер
        context.close()
        browser.close()


def main():
    """Главная функция"""

    # Путь к CSV файлу
    csv_file = project_root / "data" / "test_data.csv"

    # Инициализируем CSV Manager
    csv_manager = CSVManager(str(csv_file))

    print("\n" + "="*60)
    print("АВТОМАТИЗАЦИЯ С ПАРСИНГОМ NETWORK ДАННЫХ")
    print("="*60)

    # Получаем следующую pending строку
    data_row = csv_manager.get_next_pending_row()

    if not data_row:
        print("\n❌ Нет pending записей в CSV файле")
        print(f"Всего pending: {csv_manager.get_all_pending_count()}")
        return

    row_index = csv_manager.current_row_index

    print(f"\nНайдена pending запись (индекс: {row_index})")
    print(f"Имя: {data_row['first_name']} {data_row['last_name']}")
    print(f"Email: {data_row['email']}")

    # Запускаем автоматизацию
    with sync_playwright() as playwright:
        run(playwright, data_row, row_index, csv_manager)

    print(f"\n✅ Обработка завершена")
    print(f"Осталось pending записей: {csv_manager.get_all_pending_count()}")


if __name__ == "__main__":
    main()
