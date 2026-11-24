"""Memory-only counterexamples for campaign claim derivation, not a test suite."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(phase):
    observer = load("assemble_architecture_facts_v2.py" if phase == "candidate" else "assemble_architecture_facts_v1.py", "claim_observer")
    compiler = load("prepare_architecture_claims_v2.py" if phase == "candidate" else "prepare_architecture_claims_v1.py", "claim_compiler")
    base = {name: (observer.SOURCE / name).read_bytes() for name in observer.FILES}
    definitions = [
        ("unchanged-owned-source", None, None, None, "DERIVED"),
        ("protocol-base-removed", "client.py", b"class JsonClient(Protocol):", b"class JsonClient:", "REFUSED"),
        ("exception-binding-changed", "adapter.py", b"except GatewayUnavailable as error:", b"except GatewayUnavailable as another:", "REFUSED"),
        ("mapper-moved-into-try", "adapter.py", b'                timeout=self._timeout,\n            )', b'                timeout=self._timeout,\n            )\n            balance_from_payload(account_id, payload)', "REFUSED"),
        ("timeout-storage-changed", "adapter.py", b"self._timeout = timeout", b"self._timeout = 99.0", "REFUSED"),
        ("mapper-argument-changed", "adapter.py", b"return balance_from_payload(account_id, payload)", b"return balance_from_payload(payload, account_id)", "REFUSED"),
    ]
    oracle = HERE / "architecture-counterexample-oracle-v1.json"
    if phase == "baseline":
        with oracle.open("x") as stream:
            stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                    "definitions": [dict(zip(("id", "file", "old", "new", "expected"),
                                        (id, file, old.decode() if old else None, new.decode() if new else None, expected)))
                                        for id,file,old,new,expected in definitions],
                                    "scope": "Deliberate source mutations; development only; no source or fixture file changed."}, indent=2) + "\n")
    else:
        if not oracle.is_file():
            raise ValueError("frozen oracle missing")
    rows = []
    for id, file, old, new, expected in definitions:
        source = dict(base)
        if file:
            if source[file].count(old) != 1:
                raise ValueError("unique mutation target required")
            source[file] = source[file].replace(old, new)
        try:
            result = compiler.derive(observer.extract(source))
            actual, reason = "DERIVED", "Six bounded claim values assembled"
        except (ValueError, KeyError) as error:
            actual, reason = "REFUSED", str(error)
        rows.append({"id": id, "expected": expected, "actual": actual, "matches": actual == expected, "reason": reason})
    with (HERE / ("architecture-counterexamples-" + phase + "-v1.json")).open("x") as stream:
        stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "rows": rows, "correct": sum(r["matches"] for r in rows),
                                "source_files_written": 0, "model_calls": 0}, indent=2) + "\n")
    print([(r["id"], r["actual"]) for r in rows])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("baseline", "candidate"))
    run(parser.parse_args().phase)
