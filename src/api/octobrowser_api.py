"""
Модуль для работы с Octobrowser API
"""
import requests
import json
from typing import Dict, List, Optional, Any


class OctobrowserAPI:
    """Класс для взаимодействия с Octobrowser API"""

    def __init__(self, api_token: str, base_url: str = "https://app.octobrowser.net/api/v2/automation"):
        """
        Инициализация API клиента

        Args:
            api_token: API токен из настроек аккаунта
            base_url: Базовый URL API
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'X-Octo-Api-Token': api_token,
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Выполнение HTTP запроса к API

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API
            data: Данные для отправки в теле запроса
            params: Параметры запроса

        Returns:
            Ответ API в виде словаря
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            # Детальная информация об HTTP ошибках
            error_details = {
                "error": str(e),
                "status_code": e.response.status_code,
                "url": url,
                "method": method
            }
            try:
                # Попытка получить детали ошибки из ответа
                error_body = e.response.json()
                error_details["api_error"] = error_body
            except:
                error_details["response_text"] = e.response.text[:200]
            return error_details
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None),
                "url": url,
                "method": method
            }

    # ==================== PROFILES ====================

    def get_profiles(self, page: int = 0, page_len: int = 100, fields: Optional[str] = None) -> Dict:
        """
        Получить список профилей

        Args:
            page: Номер страницы
            page_len: Количество профилей на странице
            fields: Поля для получения (например, "title,uuid")

        Returns:
            Список профилей
        """
        params = {
            'page': page,
            'page_len': page_len
        }
        if fields:
            params['fields'] = fields

        return self._make_request('GET', '/profiles', params=params)

    def get_profile(self, uuid: str) -> Dict:
        """
        Получить информацию о конкретном профиле

        Args:
            uuid: UUID профиля

        Returns:
            Информация о профиле
        """
        return self._make_request('GET', f'/profiles/{uuid}')

    def create_profile(self, profile_data: Dict) -> Dict:
        """
        Создать новый профиль

        Args:
            profile_data: Данные профиля

        Returns:
            Созданный профиль
        """
        return self._make_request('POST', '/profiles', data=profile_data)

    def update_profile(self, uuid: str, profile_data: Dict) -> Dict:
        """
        Обновить профиль

        Args:
            uuid: UUID профиля
            profile_data: Новые данные профиля

        Returns:
            Обновленный профиль
        """
        return self._make_request('PATCH', f'/profiles/{uuid}', data=profile_data)

    def delete_profile(self, uuid: str) -> Dict:
        """
        Удалить профиль

        Args:
            uuid: UUID профиля

        Returns:
            Результат удаления
        """
        return self._make_request('DELETE', f'/profiles/{uuid}')

    def start_profile(self, uuid: str, debug_port: Optional[int] = None) -> Dict:
        """
        Запустить профиль

        Args:
            uuid: UUID профиля
            debug_port: Порт для отладки

        Returns:
            Информация о запущенном профиле (включая debug port)
        """
        data = {}
        if debug_port:
            data['debug_port'] = debug_port

        return self._make_request('POST', f'/profiles/{uuid}/start', data=data)

    def stop_profile(self, uuid: str) -> Dict:
        """
        Остановить профиль

        Args:
            uuid: UUID профиля

        Returns:
            Результат остановки
        """
        return self._make_request('POST', f'/profiles/{uuid}/stop')

    # ==================== TAGS ====================

    def get_tags(self) -> Dict:
        """
        Получить список тегов

        Returns:
            Список тегов
        """
        return self._make_request('GET', '/tags')

    def create_tag(self, tag_name: str) -> Dict:
        """
        Создать новый тег

        Args:
            tag_name: Название тега

        Returns:
            Созданный тег
        """
        return self._make_request('POST', '/tags', data={'name': tag_name})

    def delete_tag(self, tag_id: int) -> Dict:
        """
        Удалить тег

        Args:
            tag_id: ID тега

        Returns:
            Результат удаления
        """
        return self._make_request('DELETE', f'/tags/{tag_id}')

    # ==================== PROXIES ====================

    def get_proxies(self) -> Dict:
        """
        Получить список прокси

        Returns:
            Список прокси
        """
        return self._make_request('GET', '/proxies')

    def create_proxy(self, proxy_data: Dict) -> Dict:
        """
        Добавить новый прокси

        Args:
            proxy_data: Данные прокси (type, host, port, login, password)

        Returns:
            Созданный прокси
        """
        return self._make_request('POST', '/proxies', data=proxy_data)

    def delete_proxy(self, proxy_id: int) -> Dict:
        """
        Удалить прокси

        Args:
            proxy_id: ID прокси

        Returns:
            Результат удаления
        """
        return self._make_request('DELETE', f'/proxies/{proxy_id}')

    # ==================== FINGERPRINTS ====================

    def get_fingerprint_settings(self) -> Dict:
        """
        Получить доступные настройки fingerprint

        Returns:
            Настройки fingerprint
        """
        return self._make_request('GET', '/fingerprints/settings')

    def generate_fingerprint(self, os_type: str = 'win', browser_type: str = 'chrome') -> Dict:
        """
        Сгенерировать случайный fingerprint

        Args:
            os_type: Тип ОС (win, mac, linux)
            browser_type: Тип браузера (chrome, firefox)

        Returns:
            Сгенерированный fingerprint
        """
        params = {
            'os_type': os_type,
            'browser_type': browser_type
        }
        return self._make_request('GET', '/fingerprints/generate', params=params)
