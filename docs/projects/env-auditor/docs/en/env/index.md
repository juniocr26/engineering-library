# ENV — env-auditor

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

The CLI consumes no application-specific environment configuration. It reads literal assignments from files selected by arguments; it does not expand `${NAME}` or interpolate the process environment, and preserves empty values. A missing key can be added from the example; an existing empty key is preserved rather than replaced by the example default. There is no universal required-name list: each project defines its authoritative template. Backups may contain secrets and must remain private.

[Implementation](../../../../../../../env-auditor/scripts/audit-envs.py) · [Tests](../../../../../../../env-auditor/tests/test_audit_envs.py)
