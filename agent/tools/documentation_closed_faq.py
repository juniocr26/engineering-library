"""One mechanical bilingual FAQ from a fresh, guarded closed-source observation."""
import hashlib
import json
import re

import documentation_python_dependencies as dependencies

VERSION = "0.1.0"
SUPPORTED_PRODUCER_VERSION = "0.1.2"
QUESTION_KIND = "conditional-static-integer-return-v1"
QUESTION_ID = re.compile(r"[a-z][a-z0-9_.:-]{0,95}\Z")


class ClosedFaqRefused(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def prepare_closed_return_pair(observer, question_id, entry_module, entry_symbol):
    """Prepare memory-only text; no lifecycle action or document write is chosen."""
    if not isinstance(question_id, str) or not QUESTION_ID.fullmatch(question_id):
        raise ClosedFaqRefused("explicit stable question ID required")
    if type(observer) is not dependencies.ClosedDependencyObserver:
        raise ClosedFaqRefused("trusted operator-created observer required, not a persisted JSON fact")
    result = {"version": VERSION, "status": "INCONCLUSIVE", "question_id": question_id,
              "question_kind": QUESTION_KIND, "faq_pair": None, "model_calls": 0,
              "writes": 0, "owner_approved": False, "publication_authorized": False,
              "training_gold": False, "source_executed": False,
              "runtime_bindings_verified": False}
    fact = observer.observe(entry_module, entry_symbol)
    result["source_observation"] = fact
    if fact.get("status") != "STATIC_INTEGER_RETURN_UNDER_CLOSED_PROFILE":
        result["reason"] = fact.get("reason", "closed source observation is inconclusive")
        return result
    if (fact.get("version") != SUPPORTED_PRODUCER_VERSION
            or fact.get("extractor_sha256") != dependencies.OWN_SHA
            or fact.get("entry_module") != entry_module
            or fact.get("entry_symbol") != entry_symbol
            or type(fact.get("value")) is not int
            or abs(fact["value"]) > 2**53 - 1
            or any(fact.get(key) is not False for key in ("source_executed", "runtime_bindings_verified", "owner_approved"))):
        result["reason"] = "producer contract, entry identity or authority boundary differs"
        return result
    qualified = entry_module + "." + entry_symbol
    value = str(fact["value"])
    pair = {
        "en": {
            "question": f"What integer does `{qualified}` return under the registered closed profile?",
            "answer": f"Under the registered closed source profile, `{qualified}` returns `{value}`. Runtime name bindings are unverified.",
        },
        "pt-br": {
            "question": f"Qual valor inteiro `{qualified}` retorna sob o perfil fechado registrado?",
            "answer": f"Sob o perfil fechado de fontes registrado, `{qualified}` retorna `{value}`. A resolução dos nomes em execução não foi verificada.",
        },
    }
    result.update(status="PREPARED_CONDITIONAL_FAQ_PAIR", faq_pair=pair,
                  pair_sha256=hashlib.sha256(canonical(pair)).hexdigest(),
                  source_observation_sha256=hashlib.sha256(canonical(fact)).hexdigest(),
                  evidence_key=fact["evidence_key"],
                  reason="Fresh admitted conditional integer fact rendered without inference; owner review remains required.")
    return result
