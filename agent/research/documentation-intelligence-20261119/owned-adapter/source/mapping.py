from typing import Mapping
from domain import Balance

def balance_from_payload(account_id: str, payload: Mapping[str, object]) -> Balance:
    amount = payload["available_minor"]
    currency = payload["currency"]
    if type(amount) is not int:
        raise ValueError("available_minor must be an integer")
    if not isinstance(currency, str) or len(currency) != 3:
        raise ValueError("currency must have three characters")
    return Balance(account_id=account_id, available_minor=amount, currency=currency)
