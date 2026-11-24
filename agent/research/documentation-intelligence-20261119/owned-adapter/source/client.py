from typing import Mapping, Protocol

class GatewayUnavailable(RuntimeError):
    pass

class JsonClient(Protocol):
    def get(self, path: str, *, headers: dict[str, str], timeout: float) -> Mapping[str, object]:
        ...
