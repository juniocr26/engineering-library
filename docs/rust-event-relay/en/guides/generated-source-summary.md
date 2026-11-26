# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: rust-event-relay. Generation: 1.9.0; model: llama3.2:3b; evidence SHA-256: 94cd4afa4e35346e13016ec70660bd7d01c4adf255d69a831328230552d31a3a.

Coverage: 1/101 candidate files; explicit; 100 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The initial maximum acquisition budget is enforced by the `AcquisitionBudgetExhausted` terminal reason, which is represented by the `TerminalReason` enum. The retry delay is represented by the `RetryDelay` struct, which has a precision of microseconds. The retry delay is validated by the `from_micros` method, which checks if the provided microseconds value is within the allowed range of 1 to 86,400,000,000 microseconds. The retry delay is also validated by the `available_at` method, which checks if the provided timestamp is a multiple of 1000 nanoseconds. The `FailureEvidence` struct represents the failure evidence, which includes the phase, validator, and reference. The `FailureEvidence` struct is validated by the `new` method, which checks if the reference is not nil.

Source: `backend/src/domain/retry.rs:1`; SHA-256: `108edcc00edda09a8f3becd83053ca5cceb01143283e52f5d354159e95567744`.

    //! Durable retry data and invariants; no policy selection, storage or randomness.
    use chrono::{DateTime, Duration, Utc};
    use serde_json::{Value, json};
    use std::{error::Error, fmt};
    use uuid::Uuid;
    


