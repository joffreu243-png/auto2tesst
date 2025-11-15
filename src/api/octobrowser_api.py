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

    def generate_fingerprint(self, os_type: str = 'win', browser_type: str = 'chrome',
                           screen_resolution: Optional[str] = None) -> Dict:
        """
        Сгенерировать случайный fingerprint

        Args:
            os_type: Тип ОС (win, mac, linux)
            browser_type: Тип браузера (chrome, firefox)
            screen_resolution: Разрешение экрана (например, "1920x1080")

        Returns:
            Сгенерированный fingerprint
        """
        params = {
            'os_type': os_type,
            'browser_type': browser_type
        }
        if screen_resolution:
            params['screen_resolution'] = screen_resolution
        return self._make_request('GET', '/fingerprints/generate', params=params)

    def create_custom_fingerprint(self, fingerprint_config: Dict) -> Dict:
        """
        Создать кастомный fingerprint с детальными настройками

        Args:
            fingerprint_config: Детальная конфигурация fingerprint
                Поддерживаемые параметры:
                - os: Операционная система (Windows, macOS, Linux)
                - browser_version: Версия браузера
                - user_agent: User-Agent строка
                - screen: Параметры экрана (width, height, color_depth)
                - canvas: Canvas fingerprint настройки
                - webgl: WebGL настройки
                - webrtc: WebRTC настройки (mode: disabled/real/altered)
                - geolocation: Геолокация (latitude, longitude, accuracy)
                - timezone: Временная зона
                - languages: Список языков
                - do_not_track: Do Not Track (0/1)
                - hardware: Аппаратные параметры (cpu_cores, ram, gpu)
                - media_devices: Медиа устройства
                - fonts: Список шрифтов

        Returns:
            Созданный fingerprint
        """
        return fingerprint_config  # Возвращаем конфигурацию для использования в профиле

    # ==================== COOKIES ====================

    def get_profile_cookies(self, uuid: str) -> Dict:
        """
        Получить cookies профиля

        Args:
            uuid: UUID профиля

        Returns:
            Список cookies профиля
        """
        return self._make_request('GET', f'/profiles/{uuid}/cookies')

    def add_profile_cookies(self, uuid: str, cookies: List[Dict]) -> Dict:
        """
        Добавить cookies в профиль

        Args:
            uuid: UUID профиля
            cookies: Список cookies для добавления

        Returns:
            Результат операции
        """
        return self._make_request('POST', f'/profiles/{uuid}/cookies', data={'cookies': cookies})

    def update_profile_cookies(self, uuid: str, cookies: List[Dict]) -> Dict:
        """
        Обновить cookies профиля

        Args:
            uuid: UUID профиля
            cookies: Список cookies для обновления

        Returns:
            Результат операции
        """
        return self._make_request('PUT', f'/profiles/{uuid}/cookies', data={'cookies': cookies})

    def delete_profile_cookies(self, uuid: str, cookie_names: Optional[List[str]] = None) -> Dict:
        """
        Удалить cookies из профиля

        Args:
            uuid: UUID профиля
            cookie_names: Список имен cookies для удаления (если None - удалить все)

        Returns:
            Результат операции
        """
        data = {'cookie_names': cookie_names} if cookie_names else {}
        return self._make_request('DELETE', f'/profiles/{uuid}/cookies', data=data)

    # ==================== BOOKMARKS ====================

    def get_profile_bookmarks(self, uuid: str) -> Dict:
        """
        Получить закладки профиля

        Args:
            uuid: UUID профиля

        Returns:
            Список закладок профиля
        """
        return self._make_request('GET', f'/profiles/{uuid}/bookmarks')

    def add_profile_bookmarks(self, uuid: str, bookmarks: List[Dict]) -> Dict:
        """
        Добавить закладки в профиль

        Args:
            uuid: UUID профиля
            bookmarks: Список закладок (title, url)

        Returns:
            Результат операции
        """
        return self._make_request('POST', f'/profiles/{uuid}/bookmarks', data={'bookmarks': bookmarks})

    def delete_profile_bookmarks(self, uuid: str, bookmark_ids: Optional[List[int]] = None) -> Dict:
        """
        Удалить закладки из профиля

        Args:
            uuid: UUID профиля
            bookmark_ids: Список ID закладок для удаления (если None - удалить все)

        Returns:
            Результат операции
        """
        data = {'bookmark_ids': bookmark_ids} if bookmark_ids else {}
        return self._make_request('DELETE', f'/profiles/{uuid}/bookmarks', data=data)

    # ==================== EXTENSIONS ====================

    def get_profile_extensions(self, uuid: str) -> Dict:
        """
        Получить расширения профиля

        Args:
            uuid: UUID профиля

        Returns:
            Список расширений профиля
        """
        return self._make_request('GET', f'/profiles/{uuid}/extensions')

    def add_profile_extension(self, uuid: str, extension_path: str) -> Dict:
        """
        Добавить расширение в профиль

        Args:
            uuid: UUID профиля
            extension_path: Путь к CRX файлу расширения

        Returns:
            Результат операции
        """
        return self._make_request('POST', f'/profiles/{uuid}/extensions', data={'path': extension_path})

    def delete_profile_extension(self, uuid: str, extension_id: str) -> Dict:
        """
        Удалить расширение из профиля

        Args:
            uuid: UUID профиля
            extension_id: ID расширения

        Returns:
            Результат операции
        """
        return self._make_request('DELETE', f'/profiles/{uuid}/extensions/{extension_id}')

    # ==================== TEAMS ====================

    def get_teams(self) -> Dict:
        """
        Получить список команд

        Returns:
            Список команд
        """
        return self._make_request('GET', '/teams')

    def create_team(self, team_data: Dict) -> Dict:
        """
        Создать новую команду

        Args:
            team_data: Данные команды (name, description)

        Returns:
            Созданная команда
        """
        return self._make_request('POST', '/teams', data=team_data)

    def get_team(self, team_id: int) -> Dict:
        """
        Получить информацию о команде

        Args:
            team_id: ID команды

        Returns:
            Информация о команде
        """
        return self._make_request('GET', f'/teams/{team_id}')

    def update_team(self, team_id: int, team_data: Dict) -> Dict:
        """
        Обновить команду

        Args:
            team_id: ID команды
            team_data: Новые данные команды

        Returns:
            Обновленная команда
        """
        return self._make_request('PATCH', f'/teams/{team_id}', data=team_data)

    def delete_team(self, team_id: int) -> Dict:
        """
        Удалить команду

        Args:
            team_id: ID команды

        Returns:
            Результат удаления
        """
        return self._make_request('DELETE', f'/teams/{team_id}')

    def add_team_member(self, team_id: int, member_data: Dict) -> Dict:
        """
        Добавить участника в команду

        Args:
            team_id: ID команды
            member_data: Данные участника (email, role, permissions)

        Returns:
            Добавленный участник
        """
        return self._make_request('POST', f'/teams/{team_id}/members', data=member_data)

    def remove_team_member(self, team_id: int, member_id: int) -> Dict:
        """
        Удалить участника из команды

        Args:
            team_id: ID команды
            member_id: ID участника

        Returns:
            Результат удаления
        """
        return self._make_request('DELETE', f'/teams/{team_id}/members/{member_id}')

    # ==================== IMPORT/EXPORT ====================

    def import_profiles(self, profiles_data: List[Dict]) -> Dict:
        """
        Импортировать профили

        Args:
            profiles_data: Список профилей для импорта

        Returns:
            Результат импорта
        """
        return self._make_request('POST', '/profiles/import', data={'profiles': profiles_data})

    def export_profiles(self, profile_uuids: Optional[List[str]] = None) -> Dict:
        """
        Экспортировать профили

        Args:
            profile_uuids: Список UUID профилей для экспорта (если None - экспортировать все)

        Returns:
            Экспортированные профили
        """
        params = {'uuids': ','.join(profile_uuids)} if profile_uuids else {}
        return self._make_request('GET', '/profiles/export', params=params)

    # ==================== BATCH OPERATIONS ====================

    def batch_start_profiles(self, profile_uuids: List[str]) -> Dict:
        """
        Массовый запуск профилей

        Args:
            profile_uuids: Список UUID профилей для запуска

        Returns:
            Результат операции
        """
        return self._make_request('POST', '/profiles/batch/start', data={'uuids': profile_uuids})

    def batch_stop_profiles(self, profile_uuids: List[str]) -> Dict:
        """
        Массовая остановка профилей

        Args:
            profile_uuids: Список UUID профилей для остановки

        Returns:
            Результат операции
        """
        return self._make_request('POST', '/profiles/batch/stop', data={'uuids': profile_uuids})

    def batch_delete_profiles(self, profile_uuids: List[str]) -> Dict:
        """
        Массовое удаление профилей

        Args:
            profile_uuids: Список UUID профилей для удаления

        Returns:
            Результат операции
        """
        return self._make_request('POST', '/profiles/batch/delete', data={'uuids': profile_uuids})

    # ==================== QUICK LAUNCH ====================

    def get_profile_quick_launch(self, uuid: str) -> Dict:
        """
        Получить quick launch URL для профиля

        Args:
            uuid: UUID профиля

        Returns:
            Quick launch URL
        """
        return self._make_request('GET', f'/profiles/{uuid}/quick-launch')
