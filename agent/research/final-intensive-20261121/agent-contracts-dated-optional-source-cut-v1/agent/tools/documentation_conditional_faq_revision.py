"""Optional memory-only lifecycle for one deterministic conditional FAQ record."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import time

import documentation_closed_faq as closed_faq
import documentation_python_dependencies as dependencies
from documentation_workspace import directory, read, same_root, WorkspaceRefused

VERSION = "0.1.0"
MAX_PAIR_BYTES = 16384
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
FAQ_SHA = hashlib.sha256(Path(closed_faq.__file__).read_bytes()).hexdigest()
HASH = re.compile(r"[a-f0-9]{64}\Z")


class ConditionalFaqRefused(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def implementation():
    files = [(Path(__file__), OWN_SHA), (Path(closed_faq.__file__), FAQ_SHA),
             (Path(dependencies.__file__), dependencies.OWN_SHA),
             (Path(dependencies.__file__).with_name("documentation_workspace.py"), dependencies.WORKSPACE_SHA)]
    for path, expected in files:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ConditionalFaqRefused("loaded producer implementation changed; explicit reload required")
    return {"version": VERSION, "implementation_sha256": OWN_SHA,
            "faq_sha256": FAQ_SHA, "observer_sha256": dependencies.OWN_SHA,
            "workspace_sha256": dependencies.WORKSPACE_SHA}


def observer_state(observer):
    if type(observer) is not dependencies.ClosedDependencyObserver:
        raise ConditionalFaqRefused("trusted exact closed observer required")
    registry = observer.configuration()
    return {"root": str(observer.root), "root_identity": observer.root_identity,
            "timeout": observer.timeout, "registry": registry}


def recheck(observer, state):
    if observer_state(observer) != state:
        raise ConditionalFaqRefused("observer configuration changed during planning")
    with directory(state["root"]) as descriptor:
        info = os.fstat(descriptor)
        if (info.st_dev, info.st_ino) != state["root_identity"]:
            raise ConditionalFaqRefused("registered root identity changed")
        for entry in state["registry"]["modules"].values():
            _, metadata = read(descriptor, entry["path"], dependencies.MAX_FILE)
            if metadata["sha256"] != entry["sha256"]:
                raise ConditionalFaqRefused("registered source changed during planning")
        if not same_root(state["root"], descriptor):
            raise ConditionalFaqRefused("registered source root changed")
    if observer_state(observer) != state:
        raise ConditionalFaqRefused("observer configuration changed during source recheck")


def validate_pair(pair, expected):
    if pair is None:
        if expected is not None:
            raise ConditionalFaqRefused("missing pair cannot carry an expected existing hash")
        return
    if type(pair) is not dict or set(pair) != {"en", "pt-br"}:
        raise ConditionalFaqRefused("strict paired FAQ record required")
    for item in pair.values():
        if type(item) is not dict or set(item) != {"question", "answer"} or any(
            type(text) is not str or not text or "\0" in text for text in item.values()
        ):
            raise ConditionalFaqRefused("strict question and answer strings required")
    raw = canonical(pair)
    if len(raw) > MAX_PAIR_BYTES or type(expected) is not str or not HASH.fullmatch(expected) or digest(pair) != expected:
        raise ConditionalFaqRefused("FAQ record exceeds bound or expected checksum differs")


def plan_revision(previous_observer, current_observer, question_id, entry_module, entry_symbol,
                  *, existing_pair, expected_pair_sha256, question_registered,
                  complete_inventory, managed_ownership, human_authored):
    """Recommend a paired-record delta only; never edit files or recommend REMOVE.

    Inventory completeness and ownership are trusted operator declarations for
    this one canonical question, not discovered paraphrases or repository proof.
    """
    result = {"version": VERSION, "action": "INCONCLUSIVE", "changed": False,
              "candidate_pair": None, "history": None,
              "question_id": question_id, "question_kind": closed_faq.QUESTION_KIND,
              "owner_approved": False, "publication_authorized": False,
              "training_gold": False, "source_executed": False,
              "runtime_bindings_verified": False, "model_calls": 0,
              "original_files_written": 0,
              "limitations": [
                  "One exact conditional integer-return FAQ record; no arbitrary Markdown or paraphrase deduplication.",
                  "Runtime name bindings remain unverified; all proposed answers retain that condition.",
                  "Both registered snapshots must be admitted; missing or unknown source never establishes retirement.",
                  "Sequential source rechecks are not an atomic multi-root filesystem snapshot.",
                  "Recommendation only; caller must separately preserve complete documents/history before any application.",
              ]}
    started = time.monotonic()
    try:
        # Preserve the input record before invoking either observer or validating
        # replacement claims. Caller edits are a separate, explicit new request.
        existing_pair = copy.deepcopy(existing_pair)
        result["candidate_pair"] = copy.deepcopy(existing_pair)
        identity = implementation()
        validate_pair(existing_pair, expected_pair_sha256)
        if (type(question_registered) is not bool or complete_inventory is not True
                or managed_ownership is not True or human_authored is not False):
            raise ConditionalFaqRefused("complete explicit owned inventory without human conflict required")
        if question_registered != (existing_pair is not None):
            raise ConditionalFaqRefused("question inventory and existing pair disagree")
        if type(question_id) is not str or not closed_faq.QUESTION_ID.fullmatch(question_id):
            raise ConditionalFaqRefused("stable canonical question identity required")
        states = [observer_state(observer) for observer in (previous_observer, current_observer)]
        observations = [closed_faq.prepare_closed_return_pair(observer, question_id, entry_module, entry_symbol)
                        for observer in (previous_observer, current_observer)]
        result["observation_statuses"] = [row["status"] for row in observations]
        if any(row["status"] != "PREPARED_CONDITIONAL_FAQ_PAIR" for row in observations):
            raise ConditionalFaqRefused("previous or current registered conditional source is inconclusive")
        before, after = [row["faq_pair"] for row in observations]
        if existing_pair is None:
            action, candidate = "ADD", after
        elif existing_pair == after:
            action, candidate = "NO-OP", existing_pair
        elif existing_pair == before:
            action, candidate = "MODIFY", after
        else:
            raise ConditionalFaqRefused("existing FAQ is not either trusted exact conditional rendering")
        if time.monotonic() - started > 8:
            raise ConditionalFaqRefused("planning deadline exceeded")
        for observer, state in zip((previous_observer, current_observer), states):
            recheck(observer, state)
        if time.monotonic() - started > 8 or implementation() != identity:
            raise ConditionalFaqRefused("deadline or implementation consistency check failed")
        changed = candidate != existing_pair
        result.update(action=action, changed=changed, candidate_pair=copy.deepcopy(candidate),
                      history=copy.deepcopy(existing_pair) if changed else None,
                      before_pair_sha256=None if existing_pair is None else digest(existing_pair),
                      candidate_pair_sha256=digest(candidate),
                      source_value_changed=observations[0]["source_observation"]["value"] != observations[1]["source_observation"]["value"],
                      source_evidence_changed=observations[0]["evidence_key"] != observations[1]["evidence_key"],
                      implementation=identity, source_rechecks_passed=True,
                      source_observations={"previous": observations[0], "current": observations[1]},
                      reason="Fresh source-bound conditional FAQ record recommendation; owner review remains required.")
    except (ConditionalFaqRefused, closed_faq.ClosedFaqRefused, dependencies.DependencyRefused,
            WorkspaceRefused, ValueError, TypeError, KeyError, OSError, UnicodeError,
            RecursionError, RuntimeError) as error:
        result["reason"] = str(error)
    return result
