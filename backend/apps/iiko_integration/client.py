import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class IikoAPIException(Exception):
    """Exception raised for errors in iiko API."""
    pass

class IikoClient:
    BASE_URL = "https://api-ru.iiko.services/api/1"
    BASE_URL_V2 = "https://api-ru.iiko.services/api/2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.token = None

    def authenticate(self):
        """Authenticate and get access token."""
        url = f"{self.BASE_URL}/access_token"
        try:
            response = requests.post(url, json={"apiLogin": self.api_key})
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
            response = requests.post(url, json=payload, headers=self.get_headers())
            
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
                    response = requests.post(url, json=payload, headers=self.get_headers())
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as retry_e:
                     raise IikoAPIException(f"POST {url} failed after retry: {retry_e}")
            
            error_msg = f"POST {url} failed: {e}"
            if e.response is not None:
                error_msg += f" Response: {e.response.text}"
            raise IikoAPIException(error_msg)

    def get_organizations(self) -> Dict[str, Any]:
        """Fetch list of organizations available for this API key."""
        url = f"{self.BASE_URL}/organizations"
        return self._post(url, {})

    def get_menu(self, organization_id: str) -> Dict[str, Any]:
        """Fetch nomenclature (internal menu) for the organization."""
        url = f"{self.BASE_URL}/nomenclature"
        payload = {
            "organizationId": organization_id,
            "startRevision": 0
        }
        return self._post(url, payload)

    def get_external_menus(self, organization_ids: List[str]) -> Dict[str, Any]:
        """Fetch list of external menus for organizations."""
        url = f"{self.BASE_URL_V2}/menu"
        payload = {
            "organizationIds": organization_ids
        }
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
