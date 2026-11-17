# Operations and review

## Deployment status — 2026-11-16

The PHP MongoDB extension and application library remain runtime dependencies. Application readiness calls the existing MongoDB connection and a `ping` command; crypto, control storage, worker heartbeat and HTTP checks remain distinct. There is no local MongoDB health dependency in the server overlay; an unavailable external service must not be mistaken for successful readiness.

**Implemented:** configuration present in source. **Previously validated:** the preceding Docker task reported merged Compose and deployment-contract checks, four Linux ARM64 builds on Docker Desktop/macOS, and isolated client checks with synthetic settings and no network. Those checks were not rerun here and do not establish external connectivity or native-server acceptance. **Pending:** infrastructure settings, connectivity, migrated-data verification, backup/rollback, authorized activation and production acceptance. Existing data remains retained until a separately controlled decommissioning. No production deployment, restart or migration was performed by this documentation task.

[Index / Índice](../index.md)

- [Source review](source-review.md)

- [Backend](backend-testing.md)
