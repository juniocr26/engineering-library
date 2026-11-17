# Operations and review

## Deployment status — 2026-11-16

Node `/health` is liveness; `/ready` requires both Redis clients, required subscription acknowledgements and no shutdown. Existing reconnection and offline-publish behavior remain unchanged. Publisher and subscriber credentials have distinct responsibilities; Pub/Sub is not durable replay. RabbitMQ is a separate retained broker: service, image, users/vhosts, node identity and persistence configuration were not changed. The earlier RabbitMQ host-directory migration remains separate pending work; do not activate an empty replacement or infer migration completion from this Redis change.

**Implemented:** configuration present in source. **Previously validated:** the preceding Docker task reported merged Compose and deployment-contract checks, four Linux ARM64 builds on Docker Desktop/macOS, and isolated client checks with synthetic settings and no network. Those checks were not rerun here and do not establish external connectivity or native-server acceptance. **Pending:** infrastructure settings, connectivity, migrated-data verification, backup/rollback, authorized activation and production acceptance. Existing data remains retained until a separately controlled decommissioning. No production deployment, restart or migration was performed by this documentation task.

[Index / Índice](../index.md)

- [Source review](source-review.md)

- [Backend](backend-testing.md)
