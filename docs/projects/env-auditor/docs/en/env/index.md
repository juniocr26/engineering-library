# ENV — env-auditor

[Project index](../index.md)

Source review: 2026-10-19. The CLI has no application-specific environment settings and no Compose interpolation contract. Only source/test definitions were inspected; no real environment values were read.

The CLI consumes no application-specific environment configuration. It reads literal assignments from files selected by arguments; it does not expand `${NAME}` or interpolate the process environment, and preserves empty values. A missing key can be added from the example; an existing empty key is preserved rather than replaced by the example default. There is no universal required-name list: each project defines its authoritative template. Backups may contain secrets and must remain private.

[Implementation](../../../../../../../env-auditor/scripts/audit-envs.py) · [Tests](../../../../../../../env-auditor/tests/test_audit_envs.py)
