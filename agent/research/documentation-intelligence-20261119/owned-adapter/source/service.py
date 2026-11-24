from domain import BalancePort

class BalanceService:
    def __init__(self, port: BalancePort):
        self._port = port

    def summary(self, account_id: str) -> dict[str, object]:
        balance = self._port.read(account_id)
        return {"account": balance.account_id, "available_minor": balance.available_minor, "currency": balance.currency}
