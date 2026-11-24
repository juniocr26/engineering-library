# Bounded helper cache validation: maintenance candidate

Research-only change note for engineering-library from b586e484a56ef7e868c7257b2ea11ad9f71b606b to 7dbc3b696ddafb6a302ae47ea412e85b587bc308. Audience: operators of the optional source-retrieval API. This is selected static control flow, not exhaustive helper architecture or observed runtime behavior.

R01: The selected helper version is 0.1.5.

Source: agent/tools/documentation_retrieval.py:[21, 21] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R02: Python unit validation reconstructs the selected lexical callable and compares canonical evidence units.

Source: agent/tools/documentation_retrieval.py:[98, 102] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R03: Go unit validation invokes extraction and compares the resulting canonical unit.

Source: agent/tools/documentation_retrieval.py:[109, 113] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R04: A cached FOUND result calls validate_unit during cached-result validation.

Source: agent/tools/documentation_retrieval.py:[145, 148] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R05: The fresh-extraction path also calls validate_unit and catches subprocess.SubprocessError in its inner extraction handler.

Source: agent/tools/documentation_retrieval.py:[425, 439] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R06: The selected Go extraction subprocess uses timeout=20; a timeout is not successful source retrieval.

Source: agent/tools/documentation_retrieval.py:[267, 269] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R07: The duplicate path calls validate_cached outside the fresh-extraction inner handler.

Source: agent/tools/documentation_retrieval.py:[399, 413] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R08: The shown JobBoundRetrieval wrapper returns UNKNOWN_COMPLETION when helper.request raises an Exception.

Source: agent/tools/documentation_job_budget.py:[306, 310] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

The prior helper source version was 0.1.3; the existing guide still identifies that version and describes physical-quote checks. The source revision adds whole lexical-unit reconstruction and comparison. The existing guide therefore needs MODIFY within this declared scope.

The outer helper exception tuple does not include subprocess.SubprocessError, while the fresh-extraction inner tuple does. In the shown duplicate path, a Go subprocess exception may escape to the job wrapper. Do not promise that every cached revalidation returns a normal status or that a failed subprocess retrieved valid evidence. The caller must retain uncertainty and the reserved-job evidence. No automatic replay is justified here.

No external source, helper request, subprocess fault or application test was executed for this candidate. Historical defect receipts remain separate. Lexical evidence is not runtime binding, source semantics, publication permission or training Gold. Examples and operational commands are outside this bounded change-note scope. This candidate was manually authored; no neural improvement is claimed.
