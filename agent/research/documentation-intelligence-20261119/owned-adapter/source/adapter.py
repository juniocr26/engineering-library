from client import GatewayUnavailable, JsonClient
from domain import Balance, BalanceUnavailable
from mapping import balance_from_payload

class BalanceAdapter:
    def __init__(self, client: JsonClient, token: str, timeout: float = 2.0):
        self._client = client
        self._token = token
        self._timeout = timeout

    def read(self, account_id: str) -> Balance:
        if not account_id or "/" in account_id:
            raise ValueError("invalid account identifier")
        try:
            payload = self._client.get(
                f"/sandbox/accounts/{account_id}/balance",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=self._timeout,
            )
        except GatewayUnavailable as error:
            raise BalanceUnavailable("gateway unavailable") from error
        return balance_from_payload(account_id, payload)
