"""Deterministic review candidate from the bounded V2 claim values."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def render(fact):
    id = fact["id"]
    if id == "F1" and fact["arguments"] == ["account_id"]:
        return ("`BalanceService.summary` contains the written call `self._port.read(account_id)`.",
                "`BalanceService.summary` contém a chamada escrita `self._port.read(account_id)`.")
    if id == "F2" and fact["default_expression"] == "2.0" and fact["enforced_deadline"] == "UNKNOWN":
        return ("`BalanceAdapter` declares `timeout=2.0` and forwards `timeout` to `self._client.get`; units and an enforced deadline are not established.",
                "`BalanceAdapter` declara `timeout=2.0` e encaminha `timeout` a `self._client.get`; unidades e um deadline efetivo não estão estabelecidos.")
    if id == "F3" and fact["caught_type_expression"] == "GatewayUnavailable" and fact["covers_mapper_call"] is False:
        return ("`BalanceAdapter.read` catches `GatewayUnavailable` from the client call and raises `BalanceUnavailable` from `error`; this handler does not cover the mapper call.",
                "`BalanceAdapter.read` captura `GatewayUnavailable` da chamada ao cliente e lança `BalanceUnavailable` a partir de `error`; esse handler não abrange a chamada ao mapeador.")
    if id == "F4" and fact["arguments"] == ["account_id", "payload"]:
        return ("After the `try`, `BalanceAdapter.read` returns `balance_from_payload(account_id, payload)`.",
                "Após o `try`, `BalanceAdapter.read` retorna `balance_from_payload(account_id, payload)`.")
    if id == "F5" and fact["interface"] == "JsonClient.get" and all(fact[k] == "UNKNOWN" for k in ("concrete_transport", "internal_retries", "server_authorization")):
        return ("`JsonClient.get` is declared on a protocol; concrete transport, internal retries and server authorization remain unknown.",
                "`JsonClient.get` é declarado em um protocolo; transporte concreto, tentativas internas e autorização do servidor permanecem desconhecidos.")
    if id == "F6" and fact["owners"] == ["BalanceService.summary", "balance_from_payload"]:
        return ("The selected bodies of `BalanceService.summary` and `balance_from_payload` contain no written exception handler; this statement does not describe `BalanceAdapter.read`.",
                "Os corpos selecionados de `BalanceService.summary` e `balance_from_payload` não contêm handler de exceção escrito; essa afirmação não descreve `BalanceAdapter.read`.")
    raise ValueError("claim outside the reviewed renderer profile")


def run():
    raw = (HERE / "architecture-claims-v2.json").read_bytes()
    pack = json.loads(raw)
    modules = []
    for filename, name in (("assemble_architecture_facts_v2.py", "render_observer"),
                           ("prepare_architecture_claims_v2.py", "render_compiler")):
        spec = importlib.util.spec_from_file_location(name, HERE / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    observer, compiler = modules
    sources = {name: (observer.SOURCE / name).read_bytes() for name in observer.FILES}
    derived = compiler.derive(observer.extract(sources))
    if derived["claims"] != pack["claims"] or derived["evidence"] != pack["evidence"]:
        raise ValueError("claim pack differs from re-derived physical source facts")
    if [f["id"] for f in pack["claims"]] != ["F1", "F2", "F3", "F4", "F5", "F6"]:
        raise ValueError("exact unique claim set required")
    rows = []
    for fact in pack["claims"]:
        en, pt = render(fact)
        rows.append({"claim_id": fact["id"], "en": en, "pt-br": pt,
                     "evidence_units": fact["evidence"], "status": "VERIFIED_WITH_LIMITATIONS",
                     "limitation": "Reviewed fixed owned syntax profile; no runtime receiver or external transport proof."})
    result = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "claims": rows,
              "claim_pack_sha256": hashlib.sha256(raw).hexdigest(),
              "rederived_from_physical_sources_before_render": True,
              "model_calls": 0, "neural_improvement": False, "training_use_approved": False,
              "scope": "Fixed six-fact renderer, not arbitrary chapter generation or automatic source approval.",
              "review_author": "Codex; no independent human review"}
    with (HERE / "architecture-deterministic-bilingual-v2.json").open("x") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("Six EN/PT pairs rendered without a model; fixed-profile review only.")


if __name__ == "__main__":
    run()
