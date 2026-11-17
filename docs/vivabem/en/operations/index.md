# Operations and review

## Deployment status — 2026-11-16

SQL readiness uses authenticated `SELECT 1`; crypto, private health storage and HTTP/FPM checks remain separate. The Compose environment defaults `VIVABEM_RUN_MIGRATIONS` to `0`, although direct entrypoint execution defaults to `1`; migration and health-install behavior depend on this existing selector. Do not infer startup writes from an omitted command-line `--migrate` alone.

**Implemented:** configuration present in source. **Previously validated:** the preceding Docker task reported merged Compose and deployment-contract checks, four Linux ARM64 builds on Docker Desktop/macOS, and isolated client checks with synthetic settings and no network. Those checks were not rerun here and do not establish external connectivity or native-server acceptance. **Pending:** infrastructure settings, connectivity, migrated-data verification, backup/rollback, authorized activation and production acceptance. Existing data remains retained until a separately controlled decommissioning. No production deployment, restart or migration was performed by this documentation task.

[Index / Índice](../index.md)

- [Source review](source-review.md)

- [Backend](backend-testing.md)

- [Technical Cockpit](technical-cockpit.md)
