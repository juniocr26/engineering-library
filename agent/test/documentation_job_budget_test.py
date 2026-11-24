import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import documentation_job_budget as jobs
import documentation_retrieval as retrieval


class JobBudgetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "source"; self.source.mkdir()
        self.helper_root = self.root / "helper"; self.helper_root.mkdir()
        self.job_root = self.root / "job"; self.job_root.mkdir()
        self.raw = b"def value():\n    return 7\n"
        (self.source / "value.py").write_bytes(self.raw)
        self.registry = {"owned": {"root": str(self.source), "revision": "1"*40,
            "files": {"value.py": {"sha256": jobs.sha(self.raw), "language": "python", "selectors": ["value"]}}}}
        self.current = datetime.datetime.now(datetime.timezone.utc)
        self.config = {"job_id": "test-job", "registry_sha256": jobs.sha(retrieval.canonical(self.registry)),
                       "max_steps": 2, "max_quote_bytes": 12288,
                       "deadline_utc": (self.current+datetime.timedelta(hours=1)).isoformat()}

    def budget(self, **changes):
        config = {**self.config, **changes}
        return jobs.HelperJobBudget(self.job_root, config, clock=lambda: self.current)

    def request(self, identifier="one"):
        return {"request_id": identifier, "source_id": "owned", "revision": "1"*40,
                "path": "value.py", "qualified_symbol": "value", "expected_sha256": jobs.sha(self.raw)}

    def result(self, status="INCONCLUSIVE"):
        return {"status": status, "source_executed": False, "runtime_bindings_verified": False, "owner_approved": False}

    def coordinator(self):
        helper = retrieval.HelperRetrieval(self.registry, self.helper_root)
        return jobs.JobBoundRetrieval(helper, self.budget())

    def test_restart_cannot_reset_global_step_budget(self):
        first = self.coordinator().request(self.request("one"))
        second = self.coordinator().request(self.request("two"))
        third = self.coordinator().request(self.request("three"))
        self.assertEqual([first["status"], second["status"], third["status"]], ["COMPLETED", "COMPLETED", "BUDGET_EXHAUSTED"])
        self.assertEqual(first["helper_result"]["status"], "FOUND")
        self.assertFalse((self.helper_root / "three.request.json").exists())

    def test_global_quote_allowance_is_conservatively_reserved(self):
        budget = self.budget(max_steps=10, max_quote_bytes=6144)
        self.assertEqual(budget.reserve(self.request())["status"], "RESERVED")
        self.assertEqual(budget.reserve(self.request("two"))["status"], "BUDGET_EXHAUSTED")
        reopened = jobs.HelperJobBudget(self.job_root, {**self.config, "max_steps": 10, "max_quote_bytes": 6144}, clock=lambda: self.current)
        self.assertEqual(reopened.reserve(self.request("two"))["status"], "BUDGET_EXHAUSTED")

    def test_completed_duplicate_has_no_quote_and_never_dispatches(self):
        first = self.coordinator().request(self.request())
        coordinator = self.coordinator()
        with mock.patch.object(coordinator.helper, "request", side_effect=AssertionError("must not call")):
            duplicate = coordinator.request(self.request())
        self.assertEqual(duplicate["status"], "DUPLICATE_COMPLETED")
        self.assertNotIn("helper_result", duplicate)
        self.assertNotIn("evidence", duplicate)
        self.assertEqual(duplicate["completion"]["result_sha256"], jobs.sha(jobs.canonical(first["helper_result"])))

    def test_interrupted_reservation_is_not_replayed(self):
        first = self.budget().reserve(self.request())
        self.assertEqual(first["status"], "RESERVED")
        coordinator = self.coordinator()
        with mock.patch.object(coordinator.helper, "request", side_effect=AssertionError("must not retry")):
            second = coordinator.request(self.request())
        self.assertEqual(second["status"], "UNKNOWN_COMPLETION")
        self.assertEqual(coordinator.request(self.request("independent"))["status"], "COMPLETED")
        self.assertEqual(self.coordinator().request(self.request("third"))["status"], "BUDGET_EXHAUSTED")

    def test_same_id_different_payload_refuses(self):
        self.budget().reserve(self.request())
        changed = self.request(); changed["qualified_symbol"] = "other"
        self.assertEqual(self.budget().reserve(changed)["status"], "REFUSED")

    def test_configuration_change_and_missing_configuration_refuse(self):
        self.budget().reserve(self.request())
        with self.assertRaises(jobs.JobRefused):self.budget(max_steps=3)
        (self.job_root / "job.json").unlink()
        with self.assertRaises(jobs.JobRefused):self.budget()

    def test_malformed_and_orphaned_records_refuse(self):
        budget = self.budget(); budget.reserve(self.request())
        path = self.job_root / "step-0001-reserved.json"; raw = path.read_bytes()
        path.write_bytes(raw[:-1])
        self.assertEqual(budget.reserve(self.request("two"))["status"], "REFUSED")
        path.write_bytes(raw); (self.job_root / "step-0002-completed.json").write_text("{}")
        self.assertEqual(budget.reserve(self.request("two"))["status"], "REFUSED")

    def test_hash_chain_corruption_refuses(self):
        budget = self.budget(); budget.reserve(self.request()); budget.reserve(self.request("two"))
        path = self.job_root / "step-0001-reserved.json"; record = json.loads(path.read_text())
        record["request"]["source_id"] = "different"; record["request_sha256"] = jobs.request_identity(record["request"])
        path.write_bytes(jobs.canonical(record))
        self.assertEqual(budget.reserve(self.request("third"))["status"], "REFUSED")

    def test_pinned_root_and_symlink_refuse(self):
        budget = self.budget(); moved = self.root / "moved"; self.job_root.rename(moved); self.job_root.mkdir()
        self.assertEqual(budget.reserve(self.request())["status"], "REFUSED")
        self.job_root.rmdir(); self.job_root.symlink_to(moved, target_is_directory=True)
        self.assertEqual(budget.reserve(self.request())["status"], "REFUSED")

    def test_fifo_lock_does_not_block(self):
        os.mkfifo(self.job_root / "lock")
        with self.assertRaises((jobs.JobRefused, OSError)):self.budget()

    def test_nonblocking_lock_reports_busy(self):
        budget = self.budget()
        with (self.job_root / "lock").open("rb") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = budget.reserve(self.request())
        self.assertEqual(result["status"], "REFUSED")
        self.assertIn("busy", result["reason"])

    def test_clock_rollback_and_deadline(self):
        budget = self.budget(); budget.reserve(self.request())
        self.current -= datetime.timedelta(seconds=1)
        self.assertEqual(budget.reserve(self.request("two"))["status"], "REFUSED")
        self.current += datetime.timedelta(hours=2)
        self.assertEqual(budget.reserve(self.request("two"))["status"], "DEADLINE_EXCEEDED")

    def test_late_completion_keeps_audit_but_suppresses_quote(self):
        coordinator = self.coordinator(); original = coordinator.helper.request
        def delayed(request):
            result = original(request); self.current += datetime.timedelta(hours=2); return result
        with mock.patch.object(coordinator.helper, "request", side_effect=delayed):result = coordinator.request(self.request())
        self.assertEqual(result["status"], "LATE_COMPLETION_REVIEW_REQUIRED")
        self.assertNotIn("helper_result", result)
        self.assertTrue(json.loads((self.job_root / "step-0001-completed.json").read_text())["late"])

    def test_completion_write_failure_suppresses_quote(self):
        coordinator = self.coordinator(); original = jobs.write_new
        def fail_completion(fd, name, raw, *args, **kwargs):
            if name.endswith("-completed.json"):raise OSError("synthetic fsync/write failure")
            return original(fd, name, raw, *args, **kwargs)
        with mock.patch.object(jobs, "write_new", side_effect=fail_completion):result = coordinator.request(self.request())
        self.assertEqual(result["status"], "UNKNOWN_COMPLETION")
        self.assertNotIn("helper_result", result)
        self.assertEqual(self.coordinator().request(self.request())["status"], "UNKNOWN_COMPLETION")

    def test_helper_exception_and_unknown_outcome_never_replay(self):
        for exception in [True, False]:
            coordinator = self.coordinator(); request = self.request("one" if exception else "two")
            options = {"side_effect": RuntimeError("unknown")} if exception else {"return_value": self.result("IN_PROGRESS_OR_INTERRUPTED")}
            with mock.patch.object(coordinator.helper, "request", **options):result = coordinator.request(request)
            self.assertEqual(result["status"], "UNKNOWN_COMPLETION")
            self.assertEqual(self.coordinator().request(request)["status"], "UNKNOWN_COMPLETION")

    def test_registry_mismatch_or_mutation_refuses(self):
        coordinator = self.coordinator(); coordinator.helper.registry["owned"]["revision"] = "2"*40
        self.assertEqual(coordinator.request(self.request())["status"], "REFUSED")
        self.assertFalse((self.job_root / "step-0001-reserved.json").exists())
        helper = retrieval.HelperRetrieval(self.registry, self.helper_root)
        helper.registry_sha256 = "0"*64
        with self.assertRaises(jobs.JobRefused):jobs.JobBoundRetrieval(helper, self.budget())

    def test_complete_is_idempotent_but_different_result_refuses(self):
        budget = self.budget(); ticket = budget.reserve(self.request()); result = self.result()
        self.assertEqual(budget.complete(ticket, result)["status"], "COMPLETED")
        self.assertEqual(budget.complete(ticket, result)["status"], "DUPLICATE_COMPLETED")
        self.assertEqual(budget.complete(ticket, self.result("REFUSED"))["status"], "UNKNOWN_COMPLETION")

    def test_quote_size_and_authority_flags_are_enforced(self):
        budget = self.budget(); ticket = budget.reserve(self.request())
        wrong = {**self.result("FOUND"), "quote_bytes": 1, "evidence": {"quote": "too long"}}
        self.assertEqual(budget.complete(ticket, wrong)["status"], "UNKNOWN_COMPLETION")
        self.assertEqual(budget.complete(ticket, {**self.result(), "owner_approved": True})["status"], "UNKNOWN_COMPLETION")
        self.assertEqual(budget.complete(ticket, {**self.result(), "evidence": {"quote": "x"}})["status"], "UNKNOWN_COMPLETION")

    def test_out_of_order_completions_are_recoverable(self):
        budget = self.budget(); first = budget.reserve(self.request())
        self.current += datetime.timedelta(seconds=1); second = budget.reserve(self.request("two"))
        self.current += datetime.timedelta(seconds=1); budget.complete(second, self.result())
        self.current += datetime.timedelta(seconds=1); budget.complete(first, self.result())
        reopened = self.budget()
        self.assertEqual(reopened.reserve(self.request())["status"], "DUPLICATE_COMPLETED")
        self.assertEqual(reopened.reserve(self.request("two"))["status"], "DUPLICATE_COMPLETED")

    def test_source_bytes_and_metadata_preserved(self):
        path = self.source / "value.py"; before = path.stat()
        result = self.coordinator().request(self.request()); after = path.stat()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(path.read_bytes(), self.raw)
        self.assertEqual((before.st_ino, before.st_mtime_ns, before.st_ctime_ns), (after.st_ino, after.st_mtime_ns, after.st_ctime_ns))

    def test_separate_process_resumes_and_does_not_reset_budget(self):
        config = {**self.config, "max_steps": 1}
        jobs.HelperJobBudget(self.job_root, config, clock=lambda: self.current).reserve(self.request())
        program = "import sys,json;sys.path.insert(0,sys.argv[1]);from documentation_job_budget import HelperJobBudget;b=HelperJobBudget(sys.argv[2],json.loads(sys.argv[3]));print(json.dumps(b.reserve(json.loads(sys.argv[4]))))"
        completed = subprocess.run([sys.executable, "-c", program, str(Path(jobs.__file__).parent), str(self.job_root), json.dumps(config), json.dumps(self.request("two"))], capture_output=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["status"], "BUDGET_EXHAUSTED")

    def test_concurrent_process_duplicate_is_reserved_once(self):
        self.budget()
        program = "import sys,json;sys.path.insert(0,sys.argv[1]);from documentation_job_budget import HelperJobBudget\ntry:\n b=HelperJobBudget(sys.argv[2],json.loads(sys.argv[3]));print(json.dumps(b.reserve(json.loads(sys.argv[4]))))\nexcept Exception as e:print(json.dumps({'status':'REFUSED','reason':str(e)}))"
        args = [sys.executable, "-c", program, str(Path(jobs.__file__).parent), str(self.job_root), json.dumps(self.config), json.dumps(self.request())]
        processes = [subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(4)]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr); results.append(json.loads(stdout))
        self.assertEqual(sum(row["status"] == "RESERVED" for row in results), 1)
        self.assertTrue(all(row["status"] in ("RESERVED", "UNKNOWN_COMPLETION", "REFUSED") for row in results))
        self.assertEqual(len(list(self.job_root.glob("*-reserved.json"))), 1)

    def test_lock_replacement_is_detected_by_existing_instance(self):
        budget = self.budget()
        (self.job_root / "lock").rename(self.root / "old-lock")
        (self.job_root / "lock").touch()
        result = budget.reserve(self.request())
        self.assertEqual(result["status"], "REFUSED")
        self.assertIn("lock identity", result["reason"])

    def test_deadline_rechecked_between_reservation_and_dispatch(self):
        coordinator = self.coordinator(); original = coordinator.budget.reserve
        def advance(request):
            result = original(request); self.current += datetime.timedelta(hours=2); return result
        with mock.patch.object(coordinator.budget, "reserve", side_effect=advance), mock.patch.object(coordinator.helper, "request", side_effect=AssertionError("must not dispatch")):
            result = coordinator.request(self.request())
        self.assertEqual(result["status"], "UNKNOWN_COMPLETION")
        self.assertFalse((self.helper_root / "one.request.json").exists())

    def test_changed_implementation_and_unavailable_process_lock_refuse(self):
        budget = self.budget()
        with mock.patch.object(jobs, "IMPLEMENTATION_SHA256", "0"*64):
            self.assertEqual(budget.reserve(self.request())["status"], "REFUSED")
        with mock.patch.object(jobs, "fcntl", None), self.assertRaises(jobs.JobRefused):
            self.budget()

    def test_separate_concurrent_coordinators_cannot_exceed_job_budget(self):
        self.budget()
        program = "import sys,json;sys.path.insert(0,sys.argv[1]);from documentation_job_budget import HelperJobBudget,JobBoundRetrieval;from documentation_retrieval import HelperRetrieval\ntry:\n h=HelperRetrieval(json.loads(sys.argv[3]),sys.argv[4]);b=HelperJobBudget(sys.argv[2],json.loads(sys.argv[5]));print(json.dumps(JobBoundRetrieval(h,b).request(json.loads(sys.argv[6]))))\nexcept Exception as e:print(json.dumps({'status':'REFUSED','reason':str(e)}))"
        processes = []
        for n in range(6):
            args = [sys.executable, "-c", program, str(Path(jobs.__file__).parent), str(self.job_root), json.dumps(self.registry), str(self.helper_root), json.dumps(self.config), json.dumps(self.request("request%d" % n))]
            processes.append(subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr);results.append(json.loads(stdout))
        reservations = list(self.job_root.glob("*-reserved.json"))
        self.assertGreaterEqual(len(reservations), 1)
        self.assertLessEqual(len(reservations), 2)
        self.assertLessEqual(len(list(self.helper_root.glob("*.request.json"))), 2)
        self.assertTrue(all(row["status"] in ("COMPLETED", "UNKNOWN_COMPLETION", "REFUSED", "BUDGET_EXHAUSTED") for row in results))


if __name__ == "__main__":unittest.main()
