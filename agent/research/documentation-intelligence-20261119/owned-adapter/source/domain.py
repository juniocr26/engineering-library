from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Balance:
    account_id: str
    available_minor: int
    currency: str

class BalanceUnavailable(RuntimeError):
    pass

class BalancePort(Protocol):
    def read(self, account_id: str) -> Balance:
        ...
