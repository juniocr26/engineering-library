"""Optional, checksum-pinned Go lexical binding experiment; no default routing.

The operator supplies the native executable and frozen package census. Source
and import paths in the request are data, never host filesystem selectors.
Positive evidence is conditional on complete source and a valid package build.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

from documentation_lifecycle import Unsupported

MAX_INPUT = 16 * 1024 * 1024
MAX_OUTPUT = 1024 * 1024
POSITIVE = "LEXICALLY_UNSHADOWED_UNDER_PROFILE"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stable_binary(path, expected):
    """Pin the exact operator executable, refusing links and mutable reads."""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        first = os.fstat(descriptor)
        if not stat.S_ISREG(first.st_mode) or not 0 < first.st_size <= 32 * 1024 * 1024:
            raise Unsupported("invalid native executable")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        last = os.fstat(descriptor)
        if (first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns, first.st_ctime_ns) != (
            last.st_dev, last.st_ino, last.st_size, last.st_mtime_ns, last.st_ctime_ns
        ) or digest.hexdigest() != expected:
            raise Unsupported("native executable checksum or stability mismatch")
    finally:
        os.close(descriptor)


def closed_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate response field")
            result[key] = value
        return result
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


class GoBindingObserver:
    def __init__(self, executable, *, binary_sha256, go_version, timeout=20):
        if not isinstance(executable, (str, Path)) or not Path(executable).is_absolute():
            raise ValueError("operator must supply an absolute native executable")
        if not isinstance(binary_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", binary_sha256):
            raise ValueError("verified native executable checksum required")
        if not isinstance(go_version, str) or not re.fullmatch(r"go1\.\d+(?:\.\d+)?", go_version):
            raise ValueError("verified compiler version required")
        if type(timeout) not in (int, float) or not 0 < timeout <= 60:
            raise ValueError("bounded observer deadline required")
        self.executable = str(executable)
        self.binary_sha256 = binary_sha256
        self.go_version = go_version
        self.timeout = timeout
        stable_binary(self.executable, self.binary_sha256)

    def __call__(self, request):
        if not isinstance(request, dict):
            raise Unsupported("frozen request must be an object")
        try:
            raw = json.dumps(request, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        except (ValueError, TypeError, UnicodeError) as error:
            raise Unsupported("request is not lossless UTF-8 JSON") from error
        if len(raw) > MAX_INPUT:
            raise Unsupported("request exceeds source-census budget")
        stable_binary(self.executable, self.binary_sha256)
        # The checksum-pinned native producer bounds its own input and output.
        # This is an operator-trusted executable, not a request-selected command.
        try:
            result = subprocess.run(
                [self.executable], input=raw, capture_output=True, timeout=self.timeout,
                shell=False, env={"PATH": "/usr/bin:/bin", "GOENV": "off", "GOTOOLCHAIN": "local",
                                  "GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off"},
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            raise Unsupported("native observer deadline or launch failure; no automatic retry") from error
        stable_binary(self.executable, self.binary_sha256)
        if len(result.stdout) > MAX_OUTPUT or len(result.stderr) > 65536:
            raise Unsupported("native response exceeds byte budget")
        try:
            packet = closed_json(result.stdout)
        except (ValueError, UnicodeError, RecursionError) as error:
            raise Unsupported("invalid native response JSON") from error
        self.validate(packet, request, raw, result.returncode)
        return packet

    def validate(self, packet, request, raw, returncode=0):
        if not isinstance(packet, dict) or packet.get("producer") != {
            "version": "0.1.0", "go_version": self.go_version, "binary_sha256": self.binary_sha256
        } or packet.get("input_sha256") != sha(raw):
            raise Unsupported("native producer or exact request identity mismatch")
        status = packet.get("status")
        if status not in {POSITIVE, "INCONCLUSIVE", "REFUSED"}:
            raise Unsupported("invalid native decision status")
        if returncode != (2 if status == "REFUSED" else 0):
            raise Unsupported("native status and exit code differ")
        if packet.get("source_executed") is not False or packet.get("owner_approved") is not False:
            raise Unsupported("native authority boundary differs")
        if status == "REFUSED":
            return
        if any(packet.get(key) is not False for key in (
            "runtime_bindings_verified", "type_checked", "publication_authorized"
        )) or packet.get("conditional_on_supplied_complete_census") is not True:
            raise Unsupported("native source-only limitations differ")
        if packet.get("build_profile") != request.get("profile"):
            raise Unsupported("native build profile differs")
        if status != POSITIVE:
            return
        if packet.get("profile") != "go-build-filtered-predeclared-binding-v1" or packet.get("version") != "0.1.0":
            raise Unsupported("native binding profile differs")
        if packet.get("function") != request.get("function") or packet.get("builtin") != request.get("builtin"):
            raise Unsupported("native selected function or name differs")
        try:
            package = next(item for item in request["packages"] if item["import_path"] == request["package_import_path"])
            selected = next(item for item in package["files"] if item["name"] == request["file"])
            source = selected["source"].encode("utf-8")
            quote = packet["quote"].encode("utf-8")
            first, last = packet["quote_byte_start"], packet["quote_byte_end"]
            if type(first) is not int or type(last) is not int or not 0 <= first < last <= len(source):
                raise ValueError("quote offsets")
            if len(quote) > 6144 or source[first:last] != quote or packet["source_sha256"] != sha(source) or selected["sha256"] != sha(source) or packet["quote_sha256"] != sha(quote):
                raise ValueError("source/quote identity")
            if packet["first_line"] != source[:first].count(b"\n")+1 or packet["last_line"] != source[:last].count(b"\n")+1:
                raise ValueError("physical line positions")
            censuses = packet["package_censuses"]
            registered = {item["import_path"]: item for item in request["packages"]}
            if not isinstance(censuses, dict) or request["package_import_path"] not in censuses:
                raise ValueError("missing selected census")
            for name, census in censuses.items():
                item = registered[name]
                expected = sha("\n".join(sorted(file["name"]+":"+file["sha256"] for file in item["files"])).encode())
                names = {file["name"] for file in item["files"]}
                if census["source_set_sha256"] != expected or not set(census["active_files"]) <= names:
                    raise ValueError("census source identity")
            if request["file"] not in censuses[request["package_import_path"]]["active_files"]:
                raise ValueError("selected source is inactive")
            if not re.fullmatch(r"[0-9a-f]{64}", packet["proof_fingerprint"]):
                raise ValueError("invalid proof identity")
        except (KeyError, StopIteration, TypeError, ValueError, UnicodeError) as error:
            raise Unsupported("native source evidence differs") from error
