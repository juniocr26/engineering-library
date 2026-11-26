# Environment utility: synchronization and explicit proposal application

Source inspection: 2026-11-04. Implemented behavior is distinguished from executed verification and provider homologation.

Python 3 CLI using the standard library. `audit-envs.py` delegates to `env_sync.py`; `env_apply.py` owns explicit proposal application. Discovery is rooted at the parent of the utility repository unless an explicit root is supplied; it does not climb to arbitrary ancestors.

## Domain boundaries and detailed implementation

The maintained private source chapter covers workflows, persistence, authorization, failure handling and current limitations. Centralization keeps this concept summary separate from operational detail.

- [Environment utility: synchronization and explicit proposal application](../../../../../script-auditoria-envs/docs/en/architecture/current-implementation.md)
- [Implemented contracts](contracts.md)
