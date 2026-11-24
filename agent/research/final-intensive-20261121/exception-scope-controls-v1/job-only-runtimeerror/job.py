"""Opt-in durable POSIX helper budgets; no automatic retry or model routing."""
from contextlib import contextmanager
import copy
import datetime
try:
    import fcntl
except ImportError:
    fcntl = None
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from documentation_workspace import directory, read, same_root, write_new, WorkspaceRefused

VERSION = "0.1.0"
IMPLEMENTATION_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORKSPACE_SHA256 = hashlib.sha256(Path(__file__).with_name("documentation_workspace.py").read_bytes()).hexdigest()
KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
REQUEST_FIELDS = {"request_id", "source_id", "revision", "path", "qualified_symbol", "expected_sha256"}
RESERVE_FIELDS = {"schema", "config_sha256", "sequence", "request", "request_sha256", "reserved_at", "quote_reserved", "previous_reservation_sha256"}
COMPLETE_FIELDS = {"schema", "config_sha256", "sequence", "reservation_sha256", "completed_at", "result_sha256", "result_status", "quote_bytes", "late"}
COMPLETED_STATUSES = {"FOUND", "INCONCLUSIVE", "REFUSED", "DUPLICATE", "LEGACY_RESULT_REVIEW_REQUIRED", "STALE_SOURCE", "REQUEST_ID_CONFLICT", "BUDGET_EXHAUSTED"}


class JobRefused(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise JobRefused("duplicate journal field")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(JobRefused("nonfinite journal value")))


def utc(value):
    if not isinstance(value, str):
        raise JobRefused("UTC timestamp required")
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo != datetime.timezone.utc:
        raise JobRefused("explicit UTC offset required")
    return parsed


def request_identity(request):
    if not isinstance(request, dict) or set(request) != REQUEST_FIELDS or any(not isinstance(value, str) for value in request.values()):
        raise JobRefused("closed helper request required")
    if not KEY.fullmatch(request["request_id"]) or len(canonical(request)) > 4096:
        raise JobRefused("request identity or byte bound")
    return sha(canonical(request))


class HelperJobBudget:
    def __init__(self, root, config, *, clock=None):
        if fcntl is None:
            raise JobRefused("POSIX process locking unavailable")
        fields = {"job_id", "registry_sha256", "max_steps", "max_quote_bytes", "deadline_utc"}
        if not isinstance(config, dict) or set(config) != fields:
            raise JobRefused("closed job configuration required")
        if not isinstance(config["job_id"], str) or not KEY.fullmatch(config["job_id"]):
            raise JobRefused("invalid job ID")
        if not isinstance(config["registry_sha256"], str) or not HASH.fullmatch(config["registry_sha256"]):
            raise JobRefused("invalid registry hash")
        if type(config["max_steps"]) is not int or not 1 <= config["max_steps"] <= 16 or type(config["max_quote_bytes"]) is not int or not 1 <= config["max_quote_bytes"] <= 98304:
            raise JobRefused("job budget bounds")
        utc(config["deadline_utc"])
        self.root, self.config = Path(root), copy.deepcopy(config)
        self.clock = clock or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self.config_record = {"version": VERSION, "config": self.config,
                              "implementation_sha256": IMPLEMENTATION_SHA256,
                              "workspace_sha256": WORKSPACE_SHA256}
        self.config_sha = sha(canonical(self.config_record))
        with directory(self.root) as fd:
            info = os.fstat(fd); self.root_identity = info.st_dev, info.st_ino
        with self.locked() as fd:
            try:
                raw, _ = read(fd, "job.json", 4096)
            except FileNotFoundError:
                # A directory containing pre-existing records without its config
                # is incomplete evidence, not a new resumable job.
                if set(os.listdir(fd)) != {"lock"}:
                    raise JobRefused("configuration missing from nonempty job journal")
                write_new(fd, "job.json", canonical(self.config_record))
            else:
                if raw != canonical(self.config_record):
                    raise JobRefused("existing job configuration differs")
            self.state(fd)

    @contextmanager
    def locked(self):
        with directory(self.root) as fd:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) != self.root_identity:
                raise JobRefused("job root identity changed")
            lock = os.open("lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=fd)
            try:
                info = os.fstat(lock)
                if not stat.S_ISREG(info.st_mode) or info.st_size != 0 or info.st_nlink != 1:
                    raise JobRefused("invalid job lock file")
                identity = info.st_dev, info.st_ino
                if hasattr(self, "lock_identity") and self.lock_identity != identity:
                    raise JobRefused("job lock identity changed")
                self.lock_identity = identity
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as error:
                    raise JobRefused("job journal busy; no automatic retry") from error
                if not same_root(self.root, fd):
                    raise JobRefused("job root changed during lock")
                yield fd
                if not same_root(self.root, fd):
                    raise JobRefused("job root changed during operation")
            finally:
                os.close(lock)

    def state(self, fd):
        if sha(Path(__file__).read_bytes()) != IMPLEMENTATION_SHA256 or sha(Path(__file__).with_name("documentation_workspace.py").read_bytes()) != WORKSPACE_SHA256:
            raise JobRefused("loaded implementation changed; operator review required")
        raw, _ = read(fd, "job.json", 4096)
        if raw != canonical(self.config_record):
            raise JobRefused("job configuration changed")
        names = set(os.listdir(fd))
        if len(names) > 34:
            raise JobRefused("job journal file bound")
        reserved, completed, ids, last_time = [], {}, set(), None
        previous = self.config_sha
        allowed = {"lock", "job.json"}
        for sequence in range(1, 17):
            reserve_name = f"step-{sequence:04d}-reserved.json"
            complete_name = f"step-{sequence:04d}-completed.json"
            if reserve_name not in names:
                continue
            if sequence != len(reserved) + 1:
                raise JobRefused("noncontiguous reservations")
            allowed.add(reserve_name)
            raw, _ = read(fd, reserve_name, 8192); reservation = decode(raw)
            if not isinstance(reservation, dict) or set(reservation) != RESERVE_FIELDS or canonical(reservation) != raw:
                raise JobRefused("invalid reservation schema")
            if reservation["schema"] != "helper-job-reservation-v1" or reservation["config_sha256"] != self.config_sha or type(reservation["sequence"]) is not int or reservation["sequence"] != sequence:
                raise JobRefused("reservation identity differs")
            if reservation["request_sha256"] != request_identity(reservation["request"]) or reservation["previous_reservation_sha256"] != previous or type(reservation["quote_reserved"]) is not int or reservation["quote_reserved"] != 6144:
                raise JobRefused("reservation integrity differs")
            request_id = reservation["request"]["request_id"]
            if request_id in ids:
                raise JobRefused("duplicate request reservation")
            ids.add(request_id); at = utc(reservation["reserved_at"])
            if at >= utc(self.config["deadline_utc"]):
                raise JobRefused("reservation was made after deadline")
            if reserved and at < utc(reserved[-1]["record"]["reserved_at"]):
                raise JobRefused("reservation clock order differs")
            previous = sha(raw)
            reserved.append({"record": reservation, "sha256": previous})
            last_time = max(last_time, at) if last_time else at
            if complete_name in names:
                allowed.add(complete_name)
                complete_raw, _ = read(fd, complete_name, 4096); record = decode(complete_raw)
                if not isinstance(record, dict) or set(record) != COMPLETE_FIELDS or canonical(record) != complete_raw:
                    raise JobRefused("invalid completion schema")
                if record["schema"] != "helper-job-completion-v1" or record["config_sha256"] != self.config_sha or type(record["sequence"]) is not int or record["sequence"] != sequence or record["reservation_sha256"] != previous:
                    raise JobRefused("completion identity differs")
                if not isinstance(record["result_sha256"], str) or not HASH.fullmatch(record["result_sha256"]) or not isinstance(record["result_status"], str) or record["result_status"] not in COMPLETED_STATUSES or type(record["quote_bytes"]) is not int or not 0 <= record["quote_bytes"] <= 6144:
                    raise JobRefused("completion result metadata differs")
                if record["result_status"] != "FOUND" and record["quote_bytes"]:
                    raise JobRefused("non-found completion has quote bytes")
                finished = utc(record["completed_at"])
                if finished < at or type(record["late"]) is not bool or record["late"] != (finished >= utc(self.config["deadline_utc"])):
                    raise JobRefused("completion clock metadata differs")
                last_time = max(last_time, finished);completed[sequence] = record
        if names != allowed:
            raise JobRefused("unrecognized or orphaned journal file")
        if len(reserved) > self.config["max_steps"] or len(reserved) * 6144 > self.config["max_quote_bytes"]:
            raise JobRefused("stored reservations exceed frozen budget")
        return reserved, completed, last_time

    def now(self, last_time):
        value = self.clock()
        if not isinstance(value, datetime.datetime) or value.tzinfo != datetime.timezone.utc:
            raise JobRefused("clock must supply explicit UTC")
        if last_time and value < last_time:
            raise JobRefused("clock moved backwards; reconciliation required")
        return value

    def reserve(self, request):
        result = {"version": VERSION, "status": "REFUSED", "owner_approved": False}
        try:
            request = copy.deepcopy(request); request_sha = request_identity(request)
            with self.locked() as fd:
                reserved, completed, last = self.state(fd)
                for row in reserved:
                    record = row["record"]
                    if record["request"]["request_id"] == request["request_id"]:
                        if record["request_sha256"] != request_sha:
                            raise JobRefused("request ID reused with different payload")
                        completion = completed.get(record["sequence"])
                        return {**result, "status": "DUPLICATE_COMPLETED" if completion else "UNKNOWN_COMPLETION",
                                "sequence": record["sequence"], "reservation_sha256": row["sha256"],
                                "completion": completion, "reason": "No helper dispatch or automatic replay."}
                now = self.now(last)
                if now >= utc(self.config["deadline_utc"]):
                    return {**result, "status": "DEADLINE_EXCEEDED"}
                if len(reserved) >= self.config["max_steps"] or (len(reserved)+1)*6144 > self.config["max_quote_bytes"]:
                    return {**result, "status": "BUDGET_EXHAUSTED"}
                record = {"schema": "helper-job-reservation-v1", "config_sha256": self.config_sha,
                          "sequence": len(reserved)+1, "request": request, "request_sha256": request_sha,
                          "reserved_at": now.isoformat(), "quote_reserved": 6144,
                          "previous_reservation_sha256": reserved[-1]["sha256"] if reserved else self.config_sha}
                encoded = canonical(record)
                write_new(fd, f"step-{record['sequence']:04d}-reserved.json", encoded)
                result.update(status="RESERVED", sequence=record["sequence"], reservation_sha256=sha(encoded),
                              config_sha256=self.config_sha)
        except (JobRefused, WorkspaceRefused, OSError, UnicodeError, ValueError, TypeError) as error:
            result.update(status="REFUSED", reason=str(error))
        return result

    def complete(self, ticket, helper_result):
        result = {"version": VERSION, "status": "UNKNOWN_COMPLETION", "owner_approved": False}
        try:
            if not isinstance(ticket, dict) or ticket.get("status") != "RESERVED" or ticket.get("config_sha256") != self.config_sha or type(ticket.get("sequence")) is not int:
                raise JobRefused("invalid reservation ticket")
            encoded = canonical(helper_result)
            if not isinstance(helper_result, dict) or len(encoded) > 16384 or helper_result.get("status") not in COMPLETED_STATUSES:
                raise JobRefused("helper completion is unknown or unsupported")
            if any(helper_result.get(key) is not False for key in ("source_executed", "runtime_bindings_verified", "owner_approved")):
                raise JobRefused("helper authority boundary differs")
            quote_bytes = helper_result.get("quote_bytes", 0)
            if type(quote_bytes) is not int or not 0 <= quote_bytes <= 6144:
                raise JobRefused("helper quote byte bound")
            if helper_result["status"] == "FOUND":
                evidence = helper_result.get("evidence")
                if not isinstance(evidence, dict) or not isinstance(evidence.get("quote"), str) or len(evidence["quote"].encode()) != quote_bytes:
                    raise JobRefused("helper quote size differs")
            elif "evidence" in helper_result or quote_bytes:
                raise JobRefused("non-found result contains quotation")
            with self.locked() as fd:
                reserved, completed, last = self.state(fd); sequence = ticket["sequence"]
                if not 1 <= sequence <= len(reserved) or reserved[sequence-1]["sha256"] != ticket.get("reservation_sha256"):
                    raise JobRefused("ticket differs from durable reservation")
                if sequence in completed:
                    if completed[sequence]["result_sha256"] != sha(encoded):
                        raise JobRefused("completed result differs; no overwrite")
                    return {**result, "status": "DUPLICATE_COMPLETED", "completion": completed[sequence]}
                now = self.now(last); late = now >= utc(self.config["deadline_utc"])
                record = {"schema": "helper-job-completion-v1", "config_sha256": self.config_sha,
                          "sequence": sequence, "reservation_sha256": ticket["reservation_sha256"],
                          "completed_at": now.isoformat(), "result_sha256": sha(encoded),
                          "result_status": helper_result["status"], "quote_bytes": quote_bytes, "late": late}
                write_new(fd, f"step-{sequence:04d}-completed.json", canonical(record))
                result.update(status="LATE_COMPLETION_REVIEW_REQUIRED" if late else "COMPLETED", completion=record)
        except (JobRefused, WorkspaceRefused, OSError, UnicodeError, ValueError, TypeError) as error:
            result.update(status="UNKNOWN_COMPLETION", reason=str(error))
        return result

    def authorize_dispatch(self, ticket):
        try:
            with self.locked() as fd:
                reserved, completed, last = self.state(fd)
                sequence = ticket.get("sequence")
                if type(sequence) is not int or not 1 <= sequence <= len(reserved) or reserved[sequence-1]["sha256"] != ticket.get("reservation_sha256") or ticket.get("config_sha256") != self.config_sha or sequence in completed:
                    raise JobRefused("dispatch ticket differs from pending reservation")
                if self.now(last) >= utc(self.config["deadline_utc"]):
                    raise JobRefused("deadline passed before dispatch")
            return True
        except (JobRefused, WorkspaceRefused, OSError, UnicodeError, ValueError, TypeError):
            return False


class JobBoundRetrieval:
    def __init__(self, helper, budget):
        if helper.registry_sha256 != budget.config["registry_sha256"]:
            raise JobRefused("helper registry differs from job configuration")
        job_root = budget.root
        for entry in helper.registry.values():
            source = Path(entry["root"])
            if source == job_root or source in job_root.parents or job_root in source.parents:
                raise JobRefused("job journal overlaps registered source")
        journal = Path(helper.journal_root)
        if journal == job_root or journal in job_root.parents or job_root in journal.parents:
            raise JobRefused("helper and job journals overlap")
        self.helper, self.budget = helper, budget

    def request(self, request):
        if sha(canonical(self.helper.registry)) != self.budget.config["registry_sha256"] or self.helper.registry_sha256 != self.budget.config["registry_sha256"]:
            return {"version": VERSION, "status": "REFUSED", "reason": "helper registry changed", "source_executed": False, "runtime_bindings_verified": False, "owner_approved": False}
        ticket = self.budget.reserve(request)
        if ticket["status"] != "RESERVED":
            return {**ticket, "source_executed": False, "runtime_bindings_verified": False}
        if not self.budget.authorize_dispatch(ticket):
            return {"version": VERSION, "status": "UNKNOWN_COMPLETION", "reason": "Dispatch not authorized; reservation retained without automatic replay.", "source_executed": False, "runtime_bindings_verified": False, "owner_approved": False}
        try:
            helper_result = self.helper.request(request)
        except RuntimeError as error:
            return {"version": VERSION, "status": "UNKNOWN_COMPLETION", "reason": type(error).__name__,
                    "source_executed": False, "runtime_bindings_verified": False, "owner_approved": False}
        completion = self.budget.complete(ticket, helper_result)
        if completion["status"] != "COMPLETED":
            return {**completion, "source_executed": False, "runtime_bindings_verified": False}
        return {"version": VERSION, "status": "COMPLETED", "job_completion": completion["completion"],
                "helper_result": helper_result, "source_executed": False,
                "runtime_bindings_verified": False, "owner_approved": False}
