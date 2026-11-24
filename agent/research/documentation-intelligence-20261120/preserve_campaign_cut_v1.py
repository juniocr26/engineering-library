"""Content-pinned local cut and isolated code restoration; no model copies."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run():
    out = ROOT / ".local-backups/documentation-intelligence-20261120/recovery-cut-v1"
    out.mkdir(parents=True, exist_ok=False)
    inventory = {}
    roots = [ROOT / name for name in (
        "agent/tools", "agent/test", "agent/research/documentation-intelligence-20261120",
        "agent/research/documentation-intelligence-20261119/owned-adapter",
        ".local-backups/documentation-intelligence-20261120/reference-workspaces-v1",
        ".local-backups/documentation-intelligence-20261120/batch-candidates-v1",
        ".local-backups/documentation-intelligence-20261120/public-rotate-v1",
        ".local-backups/documentation-intelligence-20261119/lifecycle-matrix-v3")]
    files = set()
    for directory in roots:
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError("symlink not admitted into cut")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files.add(path)
    files.add(ROOT / ".local-backups/documentation-intelligence-20261119/http_over_existing_ollama.py")
    for path in sorted(files):
        if path.name == ".env" or path.name.startswith(".env."):
            raise ValueError("credentials not admitted")
        relative = str(path.relative_to(ROOT))
        inventory[relative] = {"sha256": sha_file(path), "bytes": path.stat().st_size,
                               "mode": path.stat().st_mode & 0o777}
    archive = out / "code-and-research.tar.gz"
    with tarfile.open(archive, "x:gz") as bundle:
        for relative in inventory:
            bundle.add(ROOT / relative, arcname=relative, recursive=False)
    (out / "file-manifest.json").write_text(json.dumps(inventory, indent=2) + "\n")
    restored = Path(tempfile.mkdtemp(prefix="el-doc-intel-20261120-restored-", dir="/private/tmp"))
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if set(m.name for m in members) != set(inventory):
            raise ValueError("archive inventory differs")
        for member in members:
            path = Path(member.name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts:
                raise ValueError("unsafe archive member")
        bundle.extractall(restored, filter="data")
    for relative, record in inventory.items():
        if sha_file(restored / relative) != record["sha256"]:
            raise ValueError("restored checksum differs")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-m", "unittest", "discover", "-s", "agent/test", "-p", "*_test.py"]
    started = time.monotonic()
    result = subprocess.run(command, cwd=restored, env=env, capture_output=True, timeout=120)
    (out / "restored-tests.stdout").write_bytes(result.stdout)
    (out / "restored-tests.stderr").write_bytes(result.stderr)
    receipt = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha_file(archive),
               "archive_bytes": archive.stat().st_size, "files": len(inventory),
               "manifest_sha256": sha_file(out / "file-manifest.json"),
               "restored_root": str(restored), "restored_hashes_verified": len(inventory),
               "test_command": command, "test_exit_code": result.returncode,
               "test_seconds": time.monotonic()-started,
               "model_weights_copied": False, "remote_recovery": False,
               "cold_boot": False, "model_runtime_consumption_in_restored_copy": False,
               "limits": ["Same-host local restoration only; prior retained datasets/model/source recovery chains remain separate prerequisites.",
                          "Later metadata and reports are not inside this cut; retain following checkpoint/supplement.",
                          "No filesystem-crash durability or remote disaster recovery is claimed."]}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    with (HERE / "local-recovery-cut-v1.json").open("x") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if result.returncode:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    run()
