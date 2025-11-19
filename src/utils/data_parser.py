"""
🧠 Smart Data Parser 2025 - Умный парсер данных с AI-подобной детекцией

Автоматически определяет типы полей и генерирует реалистичные данные
используя Faker и умные паттерны распознавания.

Это СЕРДЦЕ проекта auto2tesst!
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
import csv
from pathlib import Path


class SmartDataParser:
    """
    Умный парсер данных с автоматической детекцией типов полей

    Умеет:
    - Определять тип поля по значению и контексту
    - Генерировать реалистичные данные через Faker
    - Поддерживать #random синтаксис
    - Парсить вопросы и предлагать умные ответы
    - Экспортировать/импортировать CSV
    """

    def __init__(self):
        try:
            from faker import Faker
            self.faker = Faker('en_US')
            self.faker_available = True
        except ImportError:
            self.faker = None
            self.faker_available = False
            print("[WARNING] Faker не установлен. Установите: pip install faker")

        # База данных паттернов для детекции типов
        self.patterns = {
            'email': [
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                r'.*email.*', r'.*e-mail.*', r'.*mail.*'
            ],
            'phone': [
                r'^\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})$',
                r'^\d{10}$', r'^\d{3}-\d{3}-\d{4}$',
                r'.*phone.*', r'.*mobile.*', r'.*cell.*', r'.*tel.*'
            ],
            'zip_code': [
                r'^\d{5}(-\d{4})?$',
                r'.*zip.*', r'.*postal.*', r'.*postcode.*'
            ],
            'ssn': [
                r'^\d{3}-\d{2}-\d{4}$', r'^\d{9}$',
                r'.*ssn.*', r'.*social.*security.*'
            ],
            'name': [
                r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',
                r'.*name.*', r'.*first.*name.*', r'.*last.*name.*',
                r'.*full.*name.*'
            ],
            'address': [
                r'^\d+\s+[A-Za-z\s]+$',
                r'.*address.*', r'.*street.*', r'.*avenue.*', r'.*road.*'
            ],
            'city': [
                r'.*city.*', r'.*town.*'
            ],
            'state': [
                r'^[A-Z]{2}$',
                r'.*state.*', r'.*province.*'
            ],
            'date': [
                r'^\d{1,2}/\d{1,2}/\d{2,4}$',
                r'^\d{4}-\d{2}-\d{2}$',
                r'.*date.*', r'.*birth.*', r'.*dob.*'
            ],
            'credit_card': [
                r'^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$',
                r'.*card.*number.*', r'.*credit.*card.*'
            ],
            'cvv': [
                r'^\d{3,4}$',
                r'.*cvv.*', r'.*cvc.*', r'.*security.*code.*'
            ],
            'url': [
                r'^https?://[^\s]+$',
                r'.*url.*', r'.*website.*', r'.*link.*'
            ],
            'username': [
                r'^[a-z0-9_]{3,20}$',
                r'.*username.*', r'.*login.*', r'.*user.*id.*'
            ],
            'password': [
                r'.*password.*', r'.*pwd.*', r'.*pass.*'
            ],
            'company': [
                r'.*company.*', r'.*business.*', r'.*employer.*', r'.*organization.*'
            ],
            'job_title': [
                r'.*job.*', r'.*title.*', r'.*position.*', r'.*occupation.*'
            ],
            'age': [
                r'^\d{1,3}$',
                r'.*age.*'
            ],
            'income': [
                r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$',
                r'.*income.*', r'.*salary.*', r'.*wage.*'
            ]
        }

        # Умные вопрос-ответ паттерны
        self.smart_qa_patterns = {
            'credit_score': {
                'keywords': ['credit', 'score', 'rating'],
                'options': ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']
            },
            'car_year': {
                'keywords': ['car', 'vehicle', 'year', 'model year'],
                'generator': lambda: str(random.randint(2015, 2025))
            },
            'education': {
                'keywords': ['education', 'degree', 'school'],
                'options': ['High School', 'Associates', 'Bachelors', 'Masters', 'Doctorate', 'Some College']
            },
            'employment': {
                'keywords': ['employment', 'work', 'job status'],
                'options': ['Employed Full-Time', 'Employed Part-Time', 'Self-Employed', 'Unemployed', 'Retired', 'Student']
            },
            'marital_status': {
                'keywords': ['marital', 'married', 'relationship'],
                'options': ['Single', 'Married', 'Divorced', 'Widowed', 'Separated']
            },
            'gender': {
                'keywords': ['gender', 'sex'],
                'options': ['Male', 'Female', 'Other', 'Prefer not to say']
            },
            'yes_no': {
                'keywords': ['yes', 'no', 'agree', 'confirm'],
                'options': ['Yes', 'No']
            }
        }

    def detect_field_type(self, value: str, question: Optional[str] = None) -> str:
        """
        Определяет тип поля по значению и контексту вопроса

        Args:
            value: Значение поля (например: "john@gmail.com")
            question: Текст вопроса/лейбла (опционально)

        Returns:
            Тип поля (например: "email")
        """
        if not value or not isinstance(value, str):
            return 'text'

        value = value.strip()

        # Проверка через все паттерны
        for field_type, patterns in self.patterns.items():
            for pattern in patterns:
                # Проверка значения
                if re.match(pattern, value, re.IGNORECASE):
                    return field_type

                # Проверка вопроса (если есть)
                if question and re.search(pattern, question, re.IGNORECASE):
                    return field_type

        # Умная детекция по содержимому
        if value.isdigit():
            if len(value) == 5:
                return 'zip_code'
            elif len(value) == 10:
                return 'phone'
            elif len(value) == 9:
                return 'ssn'
            elif int(value) >= 1900 and int(value) <= 2100:
                return 'year'
            else:
                return 'number'

        # Если есть @ - скорее всего email
        if '@' in value and '.' in value:
            return 'email'

        # Если есть цифры и буквы - адрес или username
        if any(c.isdigit() for c in value) and any(c.isalpha() for c in value):
            if ' ' in value:
                return 'address'
            else:
                return 'username'

        # По умолчанию - текст
        return 'text'

    def detect_smart_answer_type(self, question: str) -> Optional[Dict]:
        """
        Определяет тип умного ответа на вопрос

        Args:
            question: Текст вопроса

        Returns:
            Словарь с типом и опциями или None
        """
        if not question:
            return None

        question_lower = question.lower()

        for qa_type, config in self.smart_qa_patterns.items():
            for keyword in config['keywords']:
                if keyword in question_lower:
                    return {
                        'type': qa_type,
                        'options': config.get('options'),
                        'generator': config.get('generator')
                    }

        return None

    def generate_value(self, field_type: str, count: int = 1) -> List[str]:
        """
        Генерирует реалистичные значения для типа поля

        Args:
            field_type: Тип поля
            count: Количество значений для генерации

        Returns:
            Список сгенерированных значений
        """
        if not self.faker_available:
            return [f"<{field_type}>"] * count

        values = []

        for _ in range(count):
            try:
                if field_type == 'email':
                    values.append(self.faker.email())
                elif field_type == 'phone':
                    values.append(self.faker.phone_number())
                elif field_type == 'name':
                    values.append(self.faker.name())
                elif field_type == 'first_name':
                    values.append(self.faker.first_name())
                elif field_type == 'last_name':
                    values.append(self.faker.last_name())
                elif field_type == 'address':
                    values.append(self.faker.street_address())
                elif field_type == 'city':
                    values.append(self.faker.city())
                elif field_type == 'state':
                    values.append(self.faker.state_abbr())
                elif field_type == 'zip_code':
                    values.append(self.faker.zipcode())
                elif field_type == 'ssn':
                    values.append(self.faker.ssn())
                elif field_type == 'date':
                    values.append(self.faker.date_of_birth(minimum_age=18, maximum_age=80).strftime('%m/%d/%Y'))
                elif field_type == 'credit_card':
                    values.append(self.faker.credit_card_number())
                elif field_type == 'cvv':
                    values.append(self.faker.credit_card_security_code())
                elif field_type == 'url':
                    values.append(self.faker.url())
                elif field_type == 'username':
                    values.append(self.faker.user_name())
                elif field_type == 'password':
                    values.append(self.faker.password(length=12))
                elif field_type == 'company':
                    values.append(self.faker.company())
                elif field_type == 'job_title':
                    values.append(self.faker.job())
                elif field_type == 'age':
                    values.append(str(random.randint(18, 80)))
                elif field_type == 'income':
                    values.append(f"${random.randint(30000, 150000):,}")
                elif field_type == 'year':
                    values.append(str(random.randint(2015, 2025)))
                else:
                    values.append(self.faker.word())
            except Exception as e:
                values.append(f"<{field_type}>")
                print(f"[ERROR] Ошибка генерации {field_type}: {e}")

        return values

    def parse_fill_actions(self, code: str) -> List[Dict]:
        """
        Парсит .fill() действия из Playwright кода

        Args:
            code: Playwright код

        Returns:
            Список словарей с информацией о полях
        """
        fields = []

        # Паттерн для .fill("value") или .fill('value')
        # Улучшенный паттерн для любых .fill() вызовов
        fill_pattern = r'\.fill\(["\']([^"\']+)["\']\)'

        # Расширенный паттерн для селектора + контекста
        # Поддержка: get_by_label, get_by_placeholder, locator, get_by_role, get_by_test_id
        selector_pattern = r'(page|[\w]+)\.(?:get_by_label|get_by_placeholder|locator|get_by_role|get_by_test_id|get_by_text)\(["\']([^"\']+?)["\']\)(?:\.\w+\([^\)]*\))*\.fill\(["\']([^"\']+)["\']\)'

        lines = code.split('\n')

        for i, line in enumerate(lines):
            # Пропустить комментарии и пустые строки
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Попытка найти с контекстом
            match = re.search(selector_pattern, line)
            if match:
                page_var = match.group(1)
                selector = match.group(2)
                value = match.group(3)

                # Определить тип поля
                field_type = self.detect_field_type(value, selector)

                # Проверить на #random
                is_random = False
                random_range = None
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line.startswith('#random'):
                        is_random = True
                        range_match = re.search(r'#random\[(\d+)-(\d+)\]', prev_line)
                        if range_match:
                            random_range = (int(range_match.group(1)), int(range_match.group(2)))

                # Проверить на умный вопрос
                smart_answer = self.detect_smart_answer_type(selector)

                fields.append({
                    'selector': selector,
                    'value': value,
                    'type': field_type,
                    'line': i,
                    'is_random': is_random,
                    'random_range': random_range,
                    'smart_answer': smart_answer
                })
            else:
                # Простой .fill() - FALLBACK для любых случаев
                match = re.search(fill_pattern, line)
                if match:
                    value = match.group(1)

                    # Пропустить пустые значения
                    if not value or value.strip() == '':
                        continue

                    field_type = self.detect_field_type(value)

                    fields.append({
                        'selector': 'unknown',
                        'value': value,
                        'type': field_type,
                        'line': i,
                        'is_random': False,
                        'random_range': None,
                        'smart_answer': None
                    })

        return fields

    def generate_csv_data(self, fields: List[Dict], num_rows: int = 10) -> Tuple[List[str], List[List[str]]]:
        """
        Генерирует CSV данные на основе полей

        Args:
            fields: Список полей из parse_fill_actions
            num_rows: Количество строк для генерации

        Returns:
            (headers, rows) - заголовки и строки данных
        """
        # Создать заголовки
        headers = []
        field_counter = 1
        for field in fields:
            if field['selector'] != 'unknown':
                header = field['selector'].replace('"', '').replace("'", '')
            else:
                # Fallback: создать "Field N" если селектор неизвестен
                header = f"Field {field_counter}"
                field_counter += 1
            headers.append(header)

        # Генерировать строки
        rows = []
        for _ in range(num_rows):
            row = []
            for field in fields:
                if field['is_random'] and field['smart_answer']:
                    # Случайный выбор из опций
                    if field['smart_answer'].get('options'):
                        value = random.choice(field['smart_answer']['options'])
                    elif field['smart_answer'].get('generator'):
                        value = field['smart_answer']['generator']()
                    else:
                        value = field['value']
                elif field['is_random'] and field['random_range']:
                    # Генерировать случайное число
                    min_val, max_val = field['random_range']
                    value = str(random.randint(min_val, max_val))
                else:
                    # Генерировать по типу
                    generated = self.generate_value(field['type'], count=1)
                    value = generated[0] if generated else field['value']

                row.append(value)
            rows.append(row)

        return headers, rows

    def export_to_csv(self, filepath: str, headers: List[str], rows: List[List[str]]) -> bool:
        """
        Экспортирует данные в CSV файл

        Args:
            filepath: Путь к файлу
            headers: Заголовки
            rows: Строки данных

        Returns:
            True если успешно
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка экспорта CSV: {e}")
            return False

    def import_from_csv(self, filepath: str) -> Tuple[Optional[List[str]], Optional[List[List[str]]]]:
        """
        Импортирует данные из CSV файла

        Args:
            filepath: Путь к файлу

        Returns:
            (headers, rows) или (None, None) при ошибке
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
            return headers, rows
        except Exception as e:
            print(f"[ERROR] Ошибка импорта CSV: {e}")
            return None, None

    def smart_fill_row(self, headers: List[str]) -> List[str]:
        """
        Умное заполнение одной строки данными

        Args:
            headers: Заголовки столбцов

        Returns:
            Строка данных
        """
        row = []
        for header in headers:
            # Определить тип поля по заголовку
            field_type = self.detect_field_type('', header)

            # Проверить на умный ответ
            smart_answer = self.detect_smart_answer_type(header)

            if smart_answer:
                if smart_answer.get('options'):
                    value = random.choice(smart_answer['options'])
                elif smart_answer.get('generator'):
                    value = smart_answer['generator']()
                else:
                    value = self.generate_value(field_type, count=1)[0]
            else:
                value = self.generate_value(field_type, count=1)[0]

            row.append(value)

        return row
