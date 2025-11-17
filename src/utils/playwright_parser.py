"""
Парсер для Playwright кода
Конвертирует Playwright тесты в формат auto2tesst с параметризацией
"""

import re
from typing import Dict, List, Optional
from .phone_detector import PhoneAndOTPDetector


class PlaywrightParser:
    """Парсер для Playwright тестов"""

    def __init__(self):
        self.extracted_values = []  # Извлеченные значения для параметризации
        self.variable_names = []     # Имена переменных
        self.field_types = []         # Типы полей ('phone', 'otp', 'unknown')
        self.detector = PhoneAndOTPDetector()

    def parse_playwright_code(self, code: str) -> Dict:
        """
        Парсит Playwright код и извлекает действия

        Args:
            code: Исходный код Playwright теста

        Returns:
            Dict с информацией:
            {
                'url': '...',
                'actions': [...],
                'values': [...],
                'csv_headers': [...],
                'converted_code': '...'
            }
        """
        self.extracted_values = []
        self.variable_names = []

        # Извлечь URL
        url = self._extract_url(code)

        # Извлечь все действия
        actions = self._extract_actions(code)

        # Оптимизировать действия
        optimized_actions = self._optimize_actions(actions)

        # Извлечь значения для параметризации
        self._extract_values_from_actions(optimized_actions)

        # Сгенерировать конвертированный код
        converted_code = self._generate_converted_code(optimized_actions, url)

        return {
            'url': url,
            'actions': optimized_actions,
            'values': self.extracted_values,
            'csv_headers': self.variable_names,
            'converted_code': converted_code
        }

    def _extract_url(self, code: str) -> str:
        """Извлекает URL из page.goto()"""
        match = re.search(r'page\.goto\(["\'](.+?)["\']\)', code)
        if match:
            return match.group(1)
        return ''

    def _extract_actions(self, code: str) -> List[Dict]:
        """Извлекает действия из Playwright кода"""
        actions = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Пропустить комментарии и пустые строки
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            # page.goto() - переход на страницу
            if 'page.goto(' in line:
                url_match = re.search(r'page\.goto\(["\'](.+?)["\']\)', line)
                if url_match:
                    actions.append({
                        'type': 'goto',
                        'url': url_match.group(1),
                        'line': i
                    })
                continue

            # .click() - клик
            if '.click()' in line:
                selector = self._extract_playwright_selector(line)
                if selector:
                    actions.append({
                        'type': 'click',
                        'selector': selector,
                        'line': i
                    })
                continue

            # .fill() - ввод текста
            if '.fill(' in line:
                selector = self._extract_playwright_selector(line)
                value_match = re.search(r"\.fill\(['\"](.+?)['\"]\)", line)
                if value_match:
                    # Даже если селектор не распознан, сохраняем действие
                    actions.append({
                        'type': 'fill',
                        'selector': selector or {'type': 'unknown', 'original': line},
                        'value': value_match.group(1),
                        'line': i
                    })
                continue

            # .type() - постепенный ввод текста
            if '.type(' in line:
                selector = self._extract_playwright_selector(line)
                value_match = re.search(r"\.type\(['\"](.+?)['\"]\)", line)
                if value_match:
                    # Даже если селектор не распознан, сохраняем действие
                    actions.append({
                        'type': 'fill',  # Используем fill вместо type
                        'selector': selector or {'type': 'unknown', 'original': line},
                        'value': value_match.group(1),
                        'line': i
                    })
                continue

        return actions

    def _extract_playwright_selector(self, line: str) -> Optional[Dict]:
        """
        Извлекает Playwright селектор из строки кода

        Поддерживает полные цепочки методов:
        - page.locator("div").filter(has_text="...").first.click()
        - page.get_by_role('button', name='Submit').click()
        - page.get_by_test_id('submit').fill("text")
        """
        # Извлечь полную цепочку от page. до действия (.click(), .fill(), .type())
        # Ищем от page. до .click()/.fill()/.type()
        chain_match = re.search(r'page\.(.+?)\.(?:click|fill|type)\s*\(', line)
        if not chain_match:
            return None

        chain = chain_match.group(1)  # Цепочка без page. и без .click()

        # Проверить, есть ли модификаторы (.first, .last, .nth())
        modifier = None
        if '.first' in chain:
            modifier = 'first'
            chain = chain.replace('.first', '')
        elif '.last' in chain:
            modifier = 'last'
            chain = chain.replace('.last', '')
        elif '.nth(' in chain:
            nth_match = re.search(r'\.nth\((\d+)\)', chain)
            if nth_match:
                modifier = f'nth({nth_match.group(1)})'
                chain = re.sub(r'\.nth\(\d+\)', '', chain)

        # Сохранить полную цепочку для генерации
        return {
            'type': 'chain',
            'chain': chain.strip(),
            'modifier': modifier,
            'original': line
        }

    def _optimize_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Оптимизирует действия:
        - Убирает избыточные клики перед fill
        """
        optimized = []
        i = 0

        while i < len(actions):
            current = actions[i]
            next_action = actions[i + 1] if i + 1 < len(actions) else None

            # Если это клик и следующее - fill на том же элементе, пропустить клик
            if (current['type'] == 'click' and
                next_action and
                next_action['type'] == 'fill' and
                current.get('selector') == next_action.get('selector')):
                # Пропустить клик, он избыточен
                i += 1
                continue

            optimized.append(current)
            i += 1

        return optimized

    def _extract_values_from_actions(self, actions: List[Dict]):
        """Извлекает значения из действий для параметризации"""
        self.extracted_values = []
        self.variable_names = []
        self.field_types = []

        # Собрать все значения и метки
        values = []
        labels = []

        for action in actions:
            if action['type'] == 'fill' and 'value' in action:
                values.append(action['value'])
                # Попытаться получить метку из селектора
                label = self._extract_label_from_selector(action.get('selector', {}))
                labels.append(label)

        # Анализировать значения с помощью детектора
        analysis = self.detector.analyze_script_data(values, labels)

        # Сохранить результаты
        for field in analysis['fields']:
            value = field['value']
            field_type = field['type']
            confidence = field['confidence']

            # Генерировать имя переменной на основе типа
            var_name = self._generate_variable_name_with_type(value, field_type, len(self.extracted_values))

            self.extracted_values.append(value)
            self.variable_names.append(var_name)
            self.field_types.append(field_type)

    def _extract_label_from_selector(self, selector: Dict) -> Optional[str]:
        """Извлекает метку из селектора для анализа типа поля"""
        if not selector:
            return None

        sel_type = selector.get('type')

        # Для цепочки методов - попытаться извлечь метку из строки
        if sel_type == 'chain':
            chain = selector.get('chain', '')

            # Искать get_by_label
            label_match = re.search(r"get_by_label\(['\"](.+?)['\"]\)", chain)
            if label_match:
                return label_match.group(1)

            # Искать get_by_placeholder
            placeholder_match = re.search(r"get_by_placeholder\(['\"](.+?)['\"]\)", chain)
            if placeholder_match:
                return placeholder_match.group(1)

            # Искать name= в get_by_role
            name_match = re.search(r"name\s*=\s*['\"](.+?)['\"]", chain)
            if name_match:
                return name_match.group(1)

            # Искать get_by_test_id
            testid_match = re.search(r"get_by_test_id\(['\"](.+?)['\"]\)", chain)
            if testid_match:
                return testid_match.group(1)

            return None

        # Старые типы для обратной совместимости
        if sel_type == 'label':
            return selector.get('value')
        elif sel_type == 'placeholder':
            return selector.get('value')
        elif sel_type == 'role':
            return selector.get('name')
        elif sel_type == 'testid':
            return selector.get('value')

        return None

    def _generate_variable_name_with_type(self, value: str, field_type: str, index: int) -> str:
        """
        Генерирует имя переменной на основе типа поля

        Args:
            value: Значение поля
            field_type: Тип поля ('phone', 'otp', 'unknown')
            index: Индекс поля

        Returns:
            Имя переменной
        """
        # Если тип определен детектором
        if field_type == 'phone':
            # Подсчитать сколько уже есть phone полей
            phone_count = sum(1 for t in self.field_types if t == 'phone')
            if phone_count == 0:
                return 'phone_number'
            else:
                return f'phone_number_{phone_count + 1}'

        elif field_type == 'otp':
            # Подсчитать сколько уже есть OTP полей
            otp_count = sum(1 for t in self.field_types if t == 'otp')
            if otp_count == 0:
                return 'otp_code'
            else:
                return f'otp_code_{otp_count + 1}'

        # Для unknown - используем старую логику
        return self._generate_variable_name_legacy(value, index)

    def _generate_variable_name_legacy(self, value: str, index: int) -> str:
        """Генерирует имя переменной на основе значения (старая логика)"""
        # Определить тип значения
        if '@' in value and '.' in value:
            return 'email'

        # Дата с слешами
        if '/' in value and any(char.isdigit() for char in value):
            return 'date_of_birth'

        if value.isdigit():
            if len(value) == 8:
                return 'date_of_birth'
            else:
                return 'number'

        # Если первое значение - вероятно firstname, второе - lastname
        if index == 0:
            return 'firstname'
        elif index == 1:
            return 'lastname'
        elif index == 2 and '@' not in value:
            return 'address'
        else:
            # Простое текстовое значение
            if len(value) <= 10:
                clean = re.sub(r'[^a-z0-9]', '', value.lower())
                if clean:
                    return clean[:10]
            return f'field_{index + 1}'

    def _generate_converted_code(self, actions: List[Dict], url: str) -> str:
        """Генерирует конвертированный код для Playwright"""
        code_lines = []
        var_index = 0

        # Добавить переход на страницу (если есть)
        if url:
            code_lines.append(f'# Переход на страницу')
            code_lines.append(f'try:')
            code_lines.append(f'    # Используем domcontentloaded вместо load - быстрее и надежнее')
            code_lines.append(f'    await page.goto("{url}", wait_until="domcontentloaded", timeout=60000)')
            code_lines.append(f'    print("[OK] Страница загружена: {url}")')
            code_lines.append(f'    await page.wait_for_timeout(2000)  # Доп. пауза для загрузки JS')
            code_lines.append(f'except Exception as e:')
            code_lines.append(f'    print(f"[WARNING] Проблема при загрузке страницы: {{e}}")')
            code_lines.append(f'    print("[INFO] Продолжаем работу...")')
            code_lines.append('')

        for action in actions:
            if action['type'] == 'goto':
                code_lines.append(f'# Переход на страницу')
                code_lines.append(f'try:')
                code_lines.append(f'    # Используем domcontentloaded вместо load - быстрее и надежнее')
                code_lines.append(f'    await page.goto("{action["url"]}", wait_until="domcontentloaded", timeout=60000)')
                code_lines.append(f'    print("[OK] Страница загружена: {action["url"]}")')
                code_lines.append(f'    await page.wait_for_timeout(2000)  # Доп. пауза для загрузки JS')
                code_lines.append(f'except Exception as e:')
                code_lines.append(f'    print(f"[WARNING] Проблема при загрузке страницы: {{e}}")')
                code_lines.append(f'    print("[INFO] Продолжаем работу...")')
                code_lines.append('')

            elif action['type'] == 'click':
                selector = action['selector']
                selector_code = self._generate_selector_code(selector)
                # Экранировать кавычки для использования в f-строке
                selector_code_escaped = selector_code.replace('"', '\\"')

                code_lines.append('# Клик по элементу')
                code_lines.append(f'print(f"DEBUG: Клик по: {selector_code_escaped}")')
                code_lines.append(f'try:')
                code_lines.append(f'    await page.{selector_code}.wait_for(state="visible", timeout=20000)')
                code_lines.append(f'    await page.{selector_code}.scroll_into_view_if_needed()')
                code_lines.append(f'    await page.wait_for_timeout(500)')
                code_lines.append(f'    await page.{selector_code}.click(timeout=10000)')
                code_lines.append(f'    print("[OK] Клик выполнен")')
                code_lines.append(f'except Exception as e:')
                code_lines.append(f'    print(f"[WARNING] Не удалось кликнуть: {{e}}")')
                code_lines.append(f'    print("[INFO] Пропускаем клик и продолжаем...")')
                code_lines.append('await page.wait_for_timeout(2000)  # Пауза 2 сек')
                code_lines.append('')

            elif action['type'] == 'fill':
                selector = action['selector']
                selector_code = self._generate_selector_code(selector)
                # Экранировать кавычки для использования в f-строке
                selector_code_escaped = selector_code.replace('"', '\\"')
                var_name = self.variable_names[var_index] if var_index < len(self.variable_names) else f'field_{var_index + 1}'
                field_type = self.field_types[var_index] if var_index < len(self.field_types) else 'unknown'

                # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ OTP (с RETRY!)
                if field_type == 'otp' and var_name.startswith('otp'):
                    code_lines.append(f'# ========== ПОЛУЧЕНИЕ OTP (ТОЛЬКО если SMS включен) ==========')
                    code_lines.append(f'if USE_SMS_PROVIDER and sms_activation_id:')
                    code_lines.append(f'    print("[OTP] Ожидание OTP кода...")')
                    code_lines.append(f'    otp_code = get_sms_code(sms_activation_id, timeout=180)')
                    code_lines.append(f'    if otp_code:')
                    code_lines.append(f'        data_row["{var_name}"] = otp_code  # Перезаписать OTP из CSV')
                    code_lines.append(f'        print(f"[OTP] [OK] Получен код: {{otp_code}}")')
                    code_lines.append(f'    else:')
                    code_lines.append(f'        print("[OTP ERROR] Не удалось получить OTP код")')
                    code_lines.append('')
                    code_lines.append(f'# ========== УМНЫЙ ВВОД OTP (множество стратегий) ==========')
                    code_lines.append(f'otp_entered = False')
                    code_lines.append(f'print("[OTP] Начинаем ввод OTP кода...")')
                    code_lines.append('')
                    code_lines.append(f'# СТРАТЕГИЯ 1: Прямой ввод через keyboard (если поле уже в фокусе)')
                    code_lines.append(f'try:')
                    code_lines.append(f'    print("[OTP] [Стратегия 1] Пробуем ввести в активное поле через keyboard...")')
                    code_lines.append(f'    await page.wait_for_timeout(2000)  # Пауза для загрузки поля')
                    code_lines.append(f'    delay = random.randint(80, 120)')
                    code_lines.append(f'    await page.keyboard.type(data_row["{var_name}"], delay=delay)')
                    code_lines.append(f'    print(f"[OTP] [SUCCESS] OTP введен через keyboard: {{data_row[\'{var_name}\']}}")')
                    code_lines.append(f'    otp_entered = True')
                    code_lines.append(f'except Exception as e:')
                    code_lines.append(f'    print(f"[OTP] [Стратегия 1] Не удалась: {{e}}")')
                    code_lines.append('')
                    code_lines.append(f'# СТРАТЕГИЯ 2: Поиск по generic селекторам (если keyboard не сработал)')
                    code_lines.append(f'if not otp_entered:')
                    code_lines.append(f'    fallback_selectors = [')
                    code_lines.append(f'        \'input[type="text"]:focus\',  # Поле в фокусе')
                    code_lines.append(f'        \'input[type="tel"]:focus\',   # Телефонное поле в фокусе')
                    code_lines.append(f'        \'input[autocomplete*="one-time"]\',  # OTP autocomplete')
                    code_lines.append(f'        \'input[name*="otp" i]\',  # name содержит otp')
                    code_lines.append(f'        \'input[name*="code" i]\',  # name содержит code')
                    code_lines.append(f'        \'input[placeholder*="code" i]\',  # placeholder содержит code')
                    code_lines.append(f'        \'input[type="text"]\',  # Любое текстовое поле')
                    code_lines.append(f'        \'input[type="tel"]\'  # Любое телефонное поле')
                    code_lines.append(f'    ]')
                    code_lines.append(f'    ')
                    code_lines.append(f'    for i, fallback_sel in enumerate(fallback_selectors, 1):')
                    code_lines.append(f'        try:')
                    code_lines.append(f'            print(f"[OTP] [Стратегия 2.{{i}}] Пробуем селектор: {{fallback_sel}}")')
                    code_lines.append(f'            otp_field = page.locator(fallback_sel).first')
                    code_lines.append(f'            await otp_field.wait_for(state="visible", timeout=5000)')
                    code_lines.append(f'            await otp_field.click()')
                    code_lines.append(f'            await page.wait_for_timeout(500)')
                    code_lines.append(f'            await otp_field.clear()')
                    code_lines.append(f'            delay = random.randint(80, 120)')
                    code_lines.append(f'            await otp_field.press_sequentially(data_row["{var_name}"], delay=delay)')
                    code_lines.append(f'            print(f"[OTP] [SUCCESS] OTP введен через fallback селектор {{i}}: {{data_row[\'{var_name}\']}}")')
                    code_lines.append(f'            otp_entered = True')
                    code_lines.append(f'            break')
                    code_lines.append(f'        except Exception as e:')
                    code_lines.append(f'            print(f"[OTP] [Стратегия 2.{{i}}] Не удалась: {{e}}")')
                    code_lines.append(f'            continue')
                    code_lines.append('')
                    code_lines.append(f'# СТРАТЕГИЯ 3: Оригинальный селектор из recorder')
                    code_lines.append(f'if not otp_entered:')
                    code_lines.append(f'    try:')
                    code_lines.append(f'        print(f"[OTP] [Стратегия 3] Пробуем оригинальный селектор...")')
                    code_lines.append(f'        await page.{selector_code}.wait_for(state="visible", timeout=10000)')
                    code_lines.append(f'        await page.{selector_code}.click()')
                    code_lines.append(f'        await page.wait_for_timeout(500)')
                    code_lines.append(f'        await page.{selector_code}.clear()')
                    code_lines.append(f'        delay = random.randint(80, 120)')
                    code_lines.append(f'        await page.{selector_code}.press_sequentially(data_row["{var_name}"], delay=delay)')
                    code_lines.append(f'        print(f"[OTP] [SUCCESS] OTP введен через оригинальный селектор: {{data_row[\'{var_name}\']}}")')
                    code_lines.append(f'        otp_entered = True')
                    code_lines.append(f'    except Exception as e:')
                    code_lines.append(f'        print(f"[OTP] [Стратегия 3] Не удалась: {{e}}")')
                    code_lines.append('')
                    code_lines.append(f'if not otp_entered:')
                    code_lines.append(f'    print("[OTP CRITICAL] Не удалось ввести OTP после всех стратегий!")')
                    code_lines.append('')

                # ОБЫЧНЫЕ ПОЛЯ (с имитацией человеческого ввода)
                else:
                    code_lines.append(f'# Ввод текста: {var_name}')
                    code_lines.append(f'print(f"DEBUG: Заполнение поля {var_name}: {selector_code_escaped}")')
                    code_lines.append(f'try:')
                    code_lines.append(f'    await page.{selector_code}.wait_for(state="visible", timeout=20000)')
                    code_lines.append(f'    await page.{selector_code}.scroll_into_view_if_needed()')
                    code_lines.append(f'    await page.wait_for_timeout(500)')
                    code_lines.append(f'    await page.{selector_code}.clear()')
                    code_lines.append(f'    # Имитация человеческого ввода')
                    code_lines.append(f'    delay = random.randint(50, 150)')
                    code_lines.append(f'    await page.{selector_code}.press_sequentially(data_row["{var_name}"], delay=delay)')
                    code_lines.append(f'    print(f"[OK] Введено {{data_row[\'{var_name}\']}}")')
                    code_lines.append(f'except Exception as e:')
                    code_lines.append(f'    print(f"[WARNING] Не удалось заполнить поле {var_name}: {{e}}")')
                    code_lines.append(f'    print("[INFO] Пропускаем поле и продолжаем...")')
                    code_lines.append('await page.wait_for_timeout(1000)  # Пауза 1 сек')
                    code_lines.append('')

                var_index += 1

        return '\n'.join(code_lines)

    def _generate_selector_code(self, selector: Dict) -> str:
        """Генерирует код селектора Playwright"""
        sel_type = selector['type']

        # Новый тип: полная цепочка методов
        if sel_type == 'chain':
            chain = selector['chain']
            modifier = selector.get('modifier')

            # НЕ нормализуем кавычки - оставляем как есть из оригинала
            # Playwright recorder уже создал корректный Python код
            # Замена кавычек ломает апострофы (You're, Let's и т.д.)

            # Построить полный селектор
            result = chain
            if modifier:
                if modifier == 'first':
                    result = f"{result}.first"
                elif modifier == 'last':
                    result = f"{result}.last"
                elif modifier.startswith('nth('):
                    result = f"{result}.{modifier}"

            return result

        # Старые типы для обратной совместимости
        if sel_type == 'role':
            role = selector['role']
            name = selector.get('name')
            if name:
                # Экранировать кавычки
                name_escaped = name.replace("'", "\\'")
                return f"get_by_role('{role}', name='{name_escaped}')"
            else:
                return f"get_by_role('{role}')"

        elif sel_type == 'testid':
            value = selector['value'].replace("'", "\\'")
            return f"get_by_test_id('{value}')"

        elif sel_type == 'text':
            value = selector['value'].replace("'", "\\'")
            return f"get_by_text('{value}')"

        elif sel_type == 'label':
            value = selector['value'].replace("'", "\\'")
            return f"get_by_label('{value}')"

        elif sel_type == 'placeholder':
            value = selector['value'].replace("'", "\\'")
            return f"get_by_placeholder('{value}')"

        elif sel_type == 'filter_text':
            value = selector['value'].replace("'", "\\'")
            return f"filter(has_text='{value}')"

        elif sel_type == 'locator':
            value = selector['value'].replace("'", "\\'")
            return f"locator('{value}')"

        elif sel_type == 'unknown':
            # Если селектор неизвестен, вернуть оригинальную строку
            original = selector.get('original', '')
            # Попробуем извлечь хоть что-то полезное из оригинальной строки
            if 'page.' in original:
                # Извлечь часть после page.
                match = re.search(r'page\.(.+?)(?:\.fill|\.click|\.type|\()', original)
                if match:
                    return match.group(1)
            return "locator('body')"  # Последний fallback

        return "locator('body')"

    def generate_csv_content(self, num_rows: int = 3) -> str:
        """Генерирует содержимое CSV файла"""
        if not self.variable_names:
            return ''

        # Заголовки
        csv_lines = [','.join(self.variable_names)]

        # Первая строка - оригинальные значения
        csv_lines.append(','.join(self.extracted_values))

        # Дополнительные строки с примерами
        for i in range(num_rows - 1):
            row_values = []
            for j, var_name in enumerate(self.variable_names):
                original_value = self.extracted_values[j] if j < len(self.extracted_values) else ''
                example_value = self._generate_example_value(var_name, original_value, i + 1)
                row_values.append(example_value)
            csv_lines.append(','.join(row_values))

        return '\n'.join(csv_lines)

    def _generate_example_value(self, var_name: str, original_value: str, index: int) -> str:
        """Генерирует примерное значение для CSV"""
        if var_name == 'email':
            return f'user{index}@example.com'
        elif var_name == 'firstname':
            names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie']
            return names[index % len(names)]
        elif var_name == 'lastname':
            surnames = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown']
            return surnames[index % len(surnames)]
        elif var_name in ['password', 'date_of_birth', 'phone', 'phone_number', 'number', 'otp_code']:
            # Для номеров и кодов - НЕ изменять оригинальное значение
            # API сам даст реальные номера/OTP
            return original_value
        else:
            return f'{original_value}_{index}' if original_value else f'value_{index}'
