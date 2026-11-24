"""H95: bounded owned-script replay; FastAPI text is parsed, never executed."""
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace


def digest(value):
    return hashlib.sha256(value).hexdigest()


payload = json.load(sys.stdin)
archive = base64.b64decode(payload["archive_base64"], validate=True)
assert digest(archive) == payload["archive_sha256"]
root = Path(tempfile.mkdtemp(prefix="el-h95-replay-"))
root.chmod(0o700)
members = {}
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as capsule:
    for member in capsule.getmembers():
        path = PurePosixPath(member.name)
        assert member.isfile() and not path.is_absolute() and ".." not in path.parts
        assert member.name not in members
        members[member.name] = capsule.extractfile(member).read()
assert digest(members["manifest.json"]) == payload["manifest_sha256"]
manifest = json.loads(members["manifest.json"])
assert set(members) == {r["path"] for r in manifest["files"]} | {"manifest.json"}
for row in manifest["files"]:
    data = members[row["path"]]
    assert len(data) == row["bytes"] and digest(data) == row["sha256"]
for name, data in members.items():
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    target.chmod(0o600)

contract = json.loads(members["contract.json"])
expected = json.loads(members["expectations.json"])
sources = {r["path"]: members["source/" + r["path"]].decode() for r in expected["source_identities"]}
for row in expected["source_identities"]:
    assert digest(sources[row["path"]].encode()) == row["sha256"]
assert digest(members["scripts/" + contract["renderer_file"]]) == contract["renderer_sha256"]
assert digest(members["scripts/" + contract["source_verifier_file"]]) == contract["source_verifier_sha256"]


def load_owned(name):
    namespace = {"__name__": "recovered_owned_" + name, "__file__": str(root / "scripts" / name)}
    exec(compile(members["scripts/" + name], namespace["__file__"], "exec"), namespace)
    return namespace


observer = load_owned("python_cache_flow_profile_v2.py")
reviewer = load_owned("verify_python_cache_flow_v4.py")
renderer = load_owned("render_python_cache_flow_v2.py")
binder = load_owned("verify_python_cache_document_v4.py")
blocked_attempts = []


def forbidden(*args, **kwargs):
    blocked_attempts.append("Unexpected file/subprocess or acquisition route")
    raise RuntimeError(blocked_attempts[-1])


# Instrumentation for these selected, source-reviewed function paths, not a security sandbox.
reviewer["reacquire"] = forbidden
binder["fresh_sources"] = forbidden
binder["owned_module"] = forbidden
saved_path = {name: getattr(Path, name) for name in ("open", "read_bytes", "read_text")}
saved_process = {name: getattr(subprocess, name) for name in ("Popen", "run", "check_output")}
for name in saved_path:
    setattr(Path, name, forbidden)
for name in saved_process:
    setattr(subprocess, name, forbidden)
try:
    observation = observer["observe"](sources["fastapi/dependencies/models.py"], sources["fastapi/dependencies/utils.py"])
    observation_bytes = (json.dumps(observation, indent=2) + "\n").encode()
    assert digest(observation_bytes) == expected["expected_observation_sha256"]
    source_proof = reviewer["verify_observation"](observation, sources, expected["source_identities"])
    documents = renderer["render"](observation)
    for language, data in documents.items():
        assert digest(data) == expected["documents"][language]["sha256"]
        assert len(data) == expected["documents"][language]["bytes"]
    context = (contract, SimpleNamespace(**reviewer), SimpleNamespace(**renderer), sources, expected["source_identities"])
    binding_proof = binder["verify_pair"](documents, observation, context)
    mutants = []
    for name in ("unsupported-extra-prose", "translated-identifier"):
        changed = dict(documents)
        if name == "unsupported-extra-prose":
            changed["en"] += b"\nDependencies always execute exactly once globally.\n"
        else:
            changed["pt-BR"] = changed["pt-BR"].replace(b"dependency_cache", b"cache_de_dependencias", 1)
        assert changed != documents
        try:
            binder["verify_pair"](changed, observation, context)
        except binder["DocumentRefused"] as error:
            mutants.append({"id": name, "rejected": True, "reason": str(error), "scope": "finite-profile mismatch, not general semantic diagnosis"})
        else:
            mutants.append({"id": name, "rejected": False})
finally:
    for name, value in saved_path.items():
        setattr(Path, name, value)
    for name, value in saved_process.items():
        setattr(subprocess, name, value)

output = {
    "python": platform.python_version(),
    "platform": platform.platform(),
    "restored_root": str(root),
    "archive_sha256": payload["archive_sha256"],
    "restored_members_verified": len(members),
    "observation_sha256": digest(observation_bytes),
    "source_rule_groups": len(source_proof["checks"]),
    "binding_proof": binding_proof,
    "documents": {language: {"sha256": digest(data), "bytes": len(data), "base64": base64.b64encode(data).decode()} for language, data in documents.items()},
    "finite_profile_mutants": mutants,
    "blocked_unexpected_IO_attempts": blocked_attempts,
    "application_source_imported_or_executed": False,
    "neural_calls": 0,
    "owner_approved": False,
    "training_gold": False,
    "not_application_coldboot_or_trainedstate": True,
}
print(json.dumps(output, sort_keys=True))
