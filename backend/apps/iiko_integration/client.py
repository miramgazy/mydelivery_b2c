import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class IikoAPIException(Exception):
    """Exception raised for errors in iiko API."""
    pass

class IikoClient:
    HOST = "https://api-ru.iiko.services"
    BASE_URL = "https://api-ru.iiko.services/api/1"
    BASE_URL_V2 = "https://api-ru.iiko.services/api/2"

    EP_AUTH_V2 = "https://api-ru.iiko.services/api/v2/access_token"
    EP_AUTH_V1 = "https://api-ru.iiko.services/api/1/access_token"

    # Таймауты для всех запросов (connect, read). Предотвращают зависание воркеров при сбоях iiko.
    REQUEST_TIMEOUT = (10, 45)  # (connect, read) в секундах

    def __init__(
        self,
        api_key: Optional[Any] = None,
        app_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_version: str = '2'
    ):
        # Поддержка передачи объекта Organization напрямую первым аргументом
        if api_key is not None and (hasattr(api_key, 'org_id') or hasattr(api_key, 'api_key')):
            org = api_key
            self.api_key = (getattr(org, 'api_key', None) or '').strip() or None
            self.app_id = (getattr(org, 'iiko_app_id', None) or '').strip() or None
            self.client_secret = (getattr(org, 'iiko_client_secret', None) or '').strip() or None
            self.api_version = str(getattr(org, 'iiko_api_version', '2') or '2')
        else:
            self.api_key = (str(api_key).strip() if api_key else None)
            self.app_id = (str(app_id).strip() if app_id else None)
            self.client_secret = (str(client_secret).strip() if client_secret else None)
            self.api_version = str(api_version or '2')

            # Автоподтягивание настроек из Organization, если был передан только api_key (строка)
            if self.api_key and (not self.app_id or not self.client_secret):
                try:
                    from apps.organizations.models import Organization
                    org = Organization.objects.filter(api_key=self.api_key, is_active=True).first()
                    if org:
                        if not self.app_id and org.iiko_app_id:
                            self.app_id = org.iiko_app_id.strip()
                        if not self.client_secret and org.iiko_client_secret:
                            self.client_secret = org.iiko_client_secret.strip()
                        if org.iiko_api_version:
                            self.api_version = str(org.iiko_api_version)
                except Exception as e:
                    logger.debug("Auto-lookup organization by api_key failed: %s", e)
        self.token = None

    @classmethod
    def from_organization(cls, organization) -> 'IikoClient':
        """Фабрика для создания клиента из объекта Organization."""
        return cls(organization)

    @staticmethod
    def _extract_error_description(response) -> str:
        if response is None:
            return ""
        try:
            data = response.json()
            return data.get("errorDescription") or data.get("message") or data.get("error") or response.text
        except Exception:
            return getattr(response, 'text', '') or ""

    def authenticate(self):
        """
        Authenticate and get access token.
        1. Если заданы app_id и client_secret -> POST /api/v2/access_token {"appId": ..., "clientSecret": ...}
        2. Иначе -> POST /api/1/access_token {"apiLogin": ...}
        """
        # Авторизация v2 через appId + clientSecret
        if self.app_id and self.client_secret:
            try:
                v2_payload = {
                    "appId": self.app_id,
                    "clientSecret": self.client_secret,
                }
                if self.api_key:
                    v2_payload["apiKey"] = self.api_key
                    v2_payload["apiLogin"] = self.api_key

                response = requests.post(
                    self.EP_AUTH_V2,
                    json=v2_payload,
                    timeout=self.REQUEST_TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("token") or data.get("accessToken")
                    if self.token:
                        return
                    raise IikoAPIException("No token received from iiko API v2")

                err_desc = self._extract_error_description(response)
                raise IikoAPIException(f"iiko API v2 Auth error ({response.status_code}): {err_desc}")
            except requests.RequestException as e:
                err_desc = self._extract_error_description(getattr(e, 'response', None))
                msg = f"Failed to authenticate with iiko v2: {e} {err_desc}".strip()
                logger.error(msg)
                raise IikoAPIException(msg)

        if not self.api_key:
            raise IikoAPIException(
                "Не настроены параметры доступа к iiko Cloud (не указаны ни appId + clientSecret, ни api_key)"
            )

        # Классическая авторизация v1 через /api/1/access_token
        url = self.EP_AUTH_V1
        try:
            response = requests.post(
                url, json={"apiLogin": self.api_key}, timeout=self.REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if not self.token:
                    raise IikoAPIException("No token received from iiko API v1")
                return

            err_desc = self._extract_error_description(response)
            if "does not support /api/1/access_token" in err_desc or response.status_code == 403:
                raise IikoAPIException(
                    "Данный API-ключ iiko требует авторизации через API v2. "
                    "Пожалуйста, укажите в настройках организации 'iiko App ID' и 'iiko Client Secret' из кабинета разработчика iiko."
                )
            raise IikoAPIException(f"Authentication failed ({response.status_code}): {err_desc}")
        except requests.RequestException as e:
            err_desc = self._extract_error_description(getattr(e, 'response', None))
            if "does not support /api/1/access_token" in err_desc:
                raise IikoAPIException(
                    "Данный API-ключ iiko требует авторизации через API v2. "
                    "Пожалуйста, укажите в настройках организации 'iiko App ID' и 'iiko Client Secret' из кабинета разработчика iiko."
                )
            logger.error(f"Failed to authenticate with iiko: {e} | {err_desc}")
            raise IikoAPIException(f"Authentication failed: {e} {err_desc}".strip())

    def get_headers(self) -> Dict[str, str]:
        if not self.token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}"}

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic POST helper with re-auth logic."""
        try:
            response = requests.post(
                url, json=payload, headers=self.get_headers(), timeout=self.REQUEST_TIMEOUT
            )
            
            if not response.ok:
                logger.error(f"IIKO API ERROR: {response.status_code} | Response: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            if e.response and e.response.status_code == 401:
                logger.info("Token expired, re-authenticating...")
                self.token = None
                try:
                    response = requests.post(
                        url, json=payload, headers=self.get_headers(), timeout=self.REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as retry_e:
                     raise IikoAPIException(f"POST {url} failed after retry: {retry_e}")
            
            error_msg = f"POST {url} failed: {e}"
            if e.response is not None:
                error_msg += f" Response: {e.response.text}"
            raise IikoAPIException(error_msg)

    def get_organizations(self, return_additional_info: bool = False, include_disabled: bool = False) -> Dict[str, Any]:
        """Fetch list of organizations available for this API key."""
        url = f"{self.BASE_URL}/organizations"
        payload = {
            "returnAdditionalInfo": return_additional_info,
            "includeDisabled": include_disabled
        }
        return self._post(url, payload)

    def get_menu(self, organization_id: str) -> Dict[str, Any]:
        """Fetch nomenclature (internal menu) for the organization."""
        url = f"{self.BASE_URL}/nomenclature"
        payload = {
            "organizationId": organization_id,
            "startRevision": 0
        }
        return self._post(url, payload)

    def get_external_menus(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch list of external menus for organizations (API v2 /menu).
        Response may include priceCategories per menu."""
        url = f"{self.BASE_URL_V2}/menu"
        payload = {
            "organizationIds": organization_ids
        }
        return self._post(url, payload)

    def get_external_menu_by_id(
        self,
        organization_ids: List[str],
        external_menu_id: str,
        price_category_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Запрос внешнего меню по id (API v2 POST /menu/by_id).
        Тело: organizationIds, externalMenuId; при наличии — priceCategoryId (одна категория)."""
        url = f"{self.BASE_URL_V2}/menu/by_id"
        payload = {
            "organizationIds": list(organization_ids),
            "externalMenuId": str(external_menu_id),
        }
        if price_category_id:
            payload["priceCategoryId"] = str(price_category_id)
        return self._post(url, payload)

    def get_terminal_groups(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch terminal groups for the specified organizations."""
        url = f"{self.BASE_URL}/terminal_groups"
        payload = {
            "organizationIds": organization_ids
        }
        return self._post(url, payload)

    def create_delivery_order(self, data: Dict) -> Dict:
        """Create a delivery order in iiko Cloud."""
        url = f"{self.BASE_URL}/deliveries/create"
        return self._post(url, data)

    def get_order_status(self, org_id: str, order_id: str) -> Dict:
        """Get order status from iiko Cloud."""
        url = f"{self.BASE_URL}/deliveries/by_id"
        payload = {
            "organizationIds": [org_id],
            "organizationId": org_id, # Added singular for compatibility
            "orderIds": [order_id]
        }
        return self._post(url, payload)

    def get_creation_status(self, org_id: str, correlation_id: str) -> Dict:
        """Get order creation task status from iiko Cloud."""
        url = f"{self.BASE_URL}/commands/status"
        payload = {
            "organizationId": org_id,
            "correlationId": correlation_id
        }
        return self._post(url, payload)

    def get_payment_types(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch payment types for the specified organizations."""
        url = f"{self.BASE_URL}/payment_types"
        payload = {
            "organizationIds": organization_ids
        }
        return self._post(url, payload)

    def get_stop_lists(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch stop lists for the specified organizations."""
        url = f"{self.BASE_URL}/stop_lists"
        payload = {
            "organizationIds": organization_ids
        }
        return self._post(url, payload)

    def get_discounts(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch discounts for the specified organizations."""
        url = f"{self.BASE_URL}/discounts"
        payload = {
            "organizationIds": [str(oid) for oid in organization_ids]
        }
        return self._post(url, payload)
