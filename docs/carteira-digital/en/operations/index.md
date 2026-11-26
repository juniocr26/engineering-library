# Operations and review

## Deployment status — 2026-11-16

The bootstrap owner waits for authenticated SQL and automatically runs `php artisan migrate --force --no-interaction`. This behavior was preserved, not executed during the Docker change or this documentation task. Review schema compatibility and maintenance approval before starting against external MySQL. Financial processing, consumers and reconciliation were not changed.

**Implemented:** configuration present in source. **Previously validated:** the preceding Docker task reported merged Compose and deployment-contract checks, four Linux ARM64 builds on Docker Desktop/macOS, and isolated client checks with synthetic settings and no network. Those checks were not rerun here and do not establish external connectivity or native-server acceptance. **Pending:** infrastructure settings, connectivity, migrated-data verification, backup/rollback, authorized activation and production acceptance. Existing data remains retained until a separately controlled decommissioning. No production deployment, restart or migration was performed by this documentation task.

[Index / Índice](../index.md)

- [Source review](source-review.md)

- [Backend](backend-testing.md)
