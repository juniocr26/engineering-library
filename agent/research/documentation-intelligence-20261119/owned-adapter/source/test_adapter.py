import unittest
from adapter import BalanceAdapter
from client import GatewayUnavailable
from domain import BalanceUnavailable
from service import BalanceService

class FakeClient:
    def __init__(self, payload=None, error=None):
        self.payload = {"available_minor": 7, "currency": "TST"} if payload is None else payload
        self.error = error
        self.calls = []
    def get(self, path, *, headers, timeout):
        self.calls.append((path, headers, timeout))
        if self.error:
            raise self.error
        return self.payload

class AdapterTest(unittest.TestCase):
    def test_service_consumes_adapter_and_exact_request_mapping(self):
        client = FakeClient()
        result = BalanceService(BalanceAdapter(client, "SYNTHETIC-NOT-A-CREDENTIAL")).summary("fixture-account")
        self.assertEqual({"account": "fixture-account", "available_minor": 7, "currency": "TST"}, result)
        self.assertEqual([("/sandbox/accounts/fixture-account/balance", {"Authorization": "Bearer SYNTHETIC-NOT-A-CREDENTIAL"}, 2.0)], client.calls)
    def test_gateway_error_translates_once_with_cause(self):
        original = GatewayUnavailable("fixture failure")
        client = FakeClient(error=original)
        with self.assertRaises(BalanceUnavailable) as raised:
            BalanceAdapter(client, "SYNTHETIC").read("fixture-account")
        self.assertIs(original, raised.exception.__cause__)
        self.assertEqual(1, len(client.calls))
    def test_mapping_rejects_boolean_amount(self):
        client = FakeClient({"available_minor": True, "currency": "TST"})
        with self.assertRaisesRegex(ValueError, "integer"):
            BalanceAdapter(client, "SYNTHETIC").read("fixture-account")
    def test_unhandled_missing_payload_key_propagates(self):
        with self.assertRaises(KeyError):
            BalanceAdapter(FakeClient({}), "SYNTHETIC").read("fixture-account")
    def test_unrelated_client_error_is_not_relabelled(self):
        with self.assertRaisesRegex(TimeoutError, "fixture timeout"):
            BalanceAdapter(FakeClient(error=TimeoutError("fixture timeout")), "SYNTHETIC").read("fixture-account")
    def test_invalid_account_does_not_call_client(self):
        client = FakeClient()
        for account in ("", "a/b"):
            with self.assertRaises(ValueError):
                BalanceAdapter(client, "SYNTHETIC").read(account)
        self.assertEqual([], client.calls)
    def test_timeout_override_is_only_forwarded(self):
        client = FakeClient()
        BalanceAdapter(client, "SYNTHETIC", timeout=0.25).read("fixture-account")
        self.assertEqual(0.25, client.calls[0][2])
    def test_currency_validation_is_length_not_iso_or_uppercase(self):
        client = FakeClient({"available_minor": 7, "currency": "abc"})
        self.assertEqual("abc", BalanceAdapter(client, "SYNTHETIC").read("fixture-account").currency)
