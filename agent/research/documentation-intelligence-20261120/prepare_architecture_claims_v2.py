"""Derive narrowly worded claim values from syntax fields before prose."""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def derive(pack):
    units = pack["units"]
    if pack.get("classes", {}).get("client.py:JsonClient", {}).get("bases") != ["Protocol"]:
        raise ValueError("client protocol base not established")
    imports = pack["files"]["client.py"]["imports"]
    if imports.get("Protocol", {}).get("module") != "typing":
        raise ValueError("protocol import identity changed")
    expected_imports = {"GatewayUnavailable": ("client", "GatewayUnavailable"), "BalanceUnavailable": ("domain", "BalanceUnavailable"), "balance_from_payload": ("mapping", "balance_from_payload")}
    for local, (module, symbol) in expected_imports.items():
        ref = pack["files"]["adapter.py"]["imports"].get(local, {})
        if ref.get("module") != module or ref.get("symbol") != symbol:
            raise ValueError("adapter import registry identity changed")
    adapter = units["adapter.py:BalanceAdapter.read"]
    constructor = units["adapter.py:BalanceAdapter.__init__"]
    service = units["service.py:BalanceService.summary"]
    mapper = units["mapping.py:balance_from_payload"]
    client_calls = [c for c in adapter["calls"] if c["callee_expression"] == "self._client.get"]
    mapper_calls = [c for c in adapter["calls"] if c["callee_expression"] == "balance_from_payload"]
    port_calls = [c for c in service["calls"] if c["callee_expression"] == "self._port.read"]
    stored = {a["targets"][0]: a["value"] for a in constructor["assignments"] if len(a["targets"]) == 1}
    if len(client_calls) != 1 or len(mapper_calls) != 1 or len(port_calls) != 1:
        raise ValueError("closed call shape not established")
    client, mapping, port = client_calls[0], mapper_calls[0], port_calls[0]
    if stored.get("self._timeout") != "timeout" or client["keywords"].get("timeout") != "self._timeout":
        raise ValueError("timeout forwarding ownership not established")
    if adapter["top_level_statement_kinds"] != ["If", "Try", "Return"]:
        raise ValueError("closed exception boundary shape changed")
    if mapping["arguments"] != ["account_id", "payload"]:
        raise ValueError("mapper argument identity changed")
    if len(adapter["handlers"]) != 1 or adapter["handlers"][0]["type_expression"] != "GatewayUnavailable":
        raise ValueError("exception selection changed")
    handler = adapter["handlers"][0]
    if handler["binding"] != "error":
        raise ValueError("caught exception and chained cause are not the same binding")
    if adapter.get("top_level_returns") != ["balance_from_payload(account_id, payload)"]:
        raise ValueError("mapper call is not the top-level return after try")
    tries = adapter.get("try_blocks", [])
    if len(tries) != 1 or tries[0]["body_statement_kinds"] != ["Assign"] or tries[0]["else_count"] or tries[0]["finally_count"]:
        raise ValueError("client-only try scope changed")
    if handler["raises"] != [{"exception_expression": "BalanceUnavailable('gateway unavailable')", "cause_expression": "error"}]:
        raise ValueError("exception translation changed")
    if mapper["handlers"] or service["handlers"]:
        raise ValueError("new catches require source review")
    claims = [
        {"id": "F1", "kind": "written_call", "caller": "BalanceService.summary", "callee_expression": "self._port.read", "arguments": port["arguments"], "evidence": ["service.py:BalanceService.summary"]},
        {"id": "F2", "kind": "constructor_default_and_forwarded_keyword", "owner": "BalanceAdapter", "parameter": "timeout", "default_expression": constructor["declared_defaults"]["timeout"], "callee_expression": client["callee_expression"], "keyword": "timeout", "enforced_deadline": "UNKNOWN", "evidence": ["adapter.py:BalanceAdapter.__init__", "adapter.py:BalanceAdapter.read"]},
        {"id": "F3", "kind": "written_exception_translation", "owner": "BalanceAdapter.read", "caught_type_expression": handler["type_expression"], "raises": handler["raises"], "covers_mapper_call": False, "evidence": ["adapter.py:BalanceAdapter.read"]},
        {"id": "F4", "kind": "written_mapper_call_after_try", "caller": "BalanceAdapter.read", "callee_expression": mapping["callee_expression"], "arguments": mapping["arguments"], "evidence": ["adapter.py:BalanceAdapter.read"]},
        {"id": "F5", "kind": "declared_protocol_only", "interface": "JsonClient.get", "concrete_transport": "UNKNOWN", "internal_retries": "UNKNOWN", "server_authorization": "UNKNOWN", "evidence": ["client.py:JsonClient.get"]},
        {"id": "F6", "kind": "no_written_exception_handler_in_selected_body", "owners": ["BalanceService.summary", "balance_from_payload"], "evidence": ["service.py:BalanceService.summary", "mapping.py:balance_from_payload"]},
    ]
    # Include only exact addressed units; citations are source-backed, not proof
    # that arbitrary generated prose will preserve the bounded predicates.
    evidence = {key: units[key] for c in claims for key in c["evidence"]}
    return {"claims": claims, "evidence": evidence, "runtime_binding_verified": False,
            "scope": "Owned fixed syntax shape with manual source review; not a general architecture resolver."}


def run():
    raw = (HERE / "architecture-facts-v2.json").read_bytes()
    claims = derive(json.loads(raw))
    claims.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  pack_sha256=hashlib.sha256(raw).hexdigest(), owner_approved=False,
                  training_gold=False, status="SOURCE_REVIEWED_BOUNDED_CLAIM_VALUES")
    with (HERE / "architecture-claims-v2.json").open("x") as stream:
        stream.write(json.dumps(claims, ensure_ascii=False, indent=2) + "\n")
    print("Six bounded claims assembled before prose; no model call.")


if __name__ == "__main__":
    run()
