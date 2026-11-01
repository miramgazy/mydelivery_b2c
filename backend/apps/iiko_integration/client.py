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
            self.app_id = (app_id or '').strip() or None
            self.client_secret = (client_secret or '').strip() or None
            self.api_version = str(api_version or '2')
        self.token = None

    @classmethod
    def from_organization(cls, organization) -> 'IikoClient':
        """Фабрика для создания клиента из объекта Organization."""
        return cls(organization)

    def authenticate(self):
        """
        Authenticate and get access token.
        Логика зависит от выбранной версии (api_version):
        - Версия 1: Только классический /api/1/access_token с apiLogin
        - Версия 2: При наличии appId + clientSecret -> /api/v2/access_token, иначе apiLogin через v2/v1
        """
        # Если выбрана версия 1
        if self.api_version == '1':
            if not self.api_key:
                raise IikoAPIException("api_key is required for iiko API v1")
            url = self.EP_AUTH_V1
            try:
                response = requests.post(
                    url, json={"apiLogin": self.api_key}, timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                self.token = data.get("token")
                if not self.token:
                    raise IikoAPIException("No token received from iiko API v1")
                return
            except requests.RequestException as e:
                logger.error(f"Failed to authenticate with iiko v1: {e}")
                raise IikoAPIException(f"v1 Authentication failed: {e}")

        # Версия 2 (по умолчанию)
        if self.app_id and self.client_secret:
            try:
                response = requests.post(
                    self.EP_AUTH_V2,
                    json={"appId": self.app_id, "clientSecret": self.client_secret},
                    timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                self.token = data.get("token") or data.get("accessToken")
                if self.token:
                    return
            except requests.RequestException as e:
                logger.warning(f"Failed to authenticate with iiko v2 (appId/clientSecret): {e}")
                if not self.api_key:
                    raise IikoAPIException(f"v2 Authentication failed: {e}")
                logger.info("Falling back to api_key authentication...")

        if not self.api_key:
            raise IikoAPIException("Neither (app_id + client_secret) nor api_key is configured for iiko")

        # Пробуем v2 access_token с apiLogin
        try:
            response = requests.post(
                self.EP_AUTH_V2, json={"apiLogin": self.api_key}, timeout=self.REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token") or data.get("accessToken")
                if self.token:
                    return
        except requests.RequestException:
            pass

        # Fallback на классический v1 access_token
        url = self.EP_AUTH_V1
        try:
            response = requests.post(
                url, json={"apiLogin": self.api_key}, timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            if not self.token:
                raise IikoAPIException("No token received from iiko")
        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with iiko: {e}")
            raise IikoAPIException(f"Authentication failed: {e}")

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
