# Integration boundaries — VivaBem Android

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

VivaBemFirebaseMessagingService distinguishes display from cancel, correlates notification tags/IDs, checks posting permission and builds immutable PendingIntents through trustedUri. onNewToken saves last_token in private preferences; that write does not prove server registration. The web entry and Portal OfficialAppRequestDetector determine app authentication. Portal RedisAuthenticationSession uses rolling 60-day inactivity, separate from cookie transport duration and passive presence/push.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
