# Role identity and personal-data minimization

Authorized private-source review on 2026-11-12. This public explanation generalizes observed patterns without reproducing proprietary code, internal contracts or production records. [Index](../index.md).

## Account, profile and participation are related identities

An account authenticates a person; a profile describes a role; participation defines that role in a particular consultation. A professional buying a consultation acts as a patient in that appointment. Resolving recipient, name and image from the global account flag gives incorrect results when both roles exist. Start with appointment participants, then select the corresponding profile.

In inspected behavior, the patient recipient sees the counterpart's professional identity, including CRP when available. The professional sees patient identity without adding any CRP that patient may also hold. Missing region/registration number has textual fallback; missing contextual photos can fall back to the global image and then a default avatar. Fallback preserves usability but can lose role specificity. [Notifications](../architecture/contextual-notifications.md).

## CPF and CNPJ have different contracts

CPF identifies an individual and is required by inspected patient/professional registration. Input normalizes to digits, checks length, repetition and both check digits; uniqueness is declared per profile table. This detects formatting errors without proving ownership, official existence or uniqueness across all roles. Display masking is not protection.

The current professional flow also has optional CNPJ, with normalization, numeric validation and persistence/editing. Omission during editing preserves the value; empty input can remove it after normalization. CNPJ does not replace CPF and observed implementation establishes neither external tax validation nor alphanumeric-format support. Do not extrapolate local rules into legal or tax obligations.

## Message exclusion is not API exclusion

Reviewed consultation notification producers use names and professional identity without CPF in messages. The persisted bell projection contains no CPF field. This reduces channel exposure without creating a universal redactor: arbitrary publisher input strings can contain personal data. Message producers remain responsible for content.

Authenticated application reads can still carry personal documents into authorized screens/actions. Do not conclude that all CPF data were removed from APIs. Nor should field encryption or automatic serialization hiding be claimed without model evidence. Authentication, object authorization and field minimization need separate assessment.

Synthetic example: “Your consultation with the professional was confirmed” needs neither party's tax identifier. Authenticated details may need more context, but every field needs a verifiable purpose and authorization. Do not use personal identifiers in cache keys, logs, push tags or public examples.

## Surfaces and trade-offs

A publicly URL-accessible photo is not protected merely by an unpredictable filename. Push can appear outside the authenticated session; even names and appointment relationships require necessity review. Exports, backups and administrative access are personal-data surfaces too. Notification TTL does not define persistent-profile retention.

The architecture separates technical recovery from business transitions to avoid repeating personal/financial operations while retrying alerts. Real protection still depends on effective privileges, query scope and per-item controls. A read/mark action should check item association with the user rather than identifier existence alone.

## Evidence and limits

Inspection found existing tests for CPF-free messages, professional identification and role photos, alongside registration atomicity. These cover defined scenarios without constituting a complete API audit or privacy certification. No application tests or personal-data queries were executed during this update.

Future verification should use synthetic data, inspect response projections and check cross-account authorization in an authorized isolated environment. Documentation does not establish legal compliance, anonymization, encryption at rest or production-device validation. Implementation details, specific findings and operational procedures remain internal.
