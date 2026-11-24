"""Executable documentation example using only the preserved synthetic fake."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
from adapter import BalanceAdapter
from service import BalanceService
from test_adapter import FakeClient

client = FakeClient({"available_minor": 7, "currency": "TST"})
service = BalanceService(BalanceAdapter(client, "SYNTHETIC-NOT-A-CREDENTIAL"))
print(json.dumps(service.summary("fixture-account"), sort_keys=True))
