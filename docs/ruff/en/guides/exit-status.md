# Ruff — CLI outcomes

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: ruff. Generation: 1.9.12; model: llama3.2:3b; evidence SHA-256: fc2a1ddf4d25ac96af48d7677a7eb041fd6c279e7f33fd3fbf4ec2db08c0b33f.

Coverage: 1/1 candidate files; explicit project section; counts apply only to staged files, not whole repository coverage; 0 omitted.

Explicit source-unit scope for the files listed below; their unselected content was not provided:

    {}

Selected units: 0; cited units: 0.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The ExitStatus enum is used to represent the outcome of linting, with Success indicating no errors, Failure indicating one or more errors, and Error indicating a linting failure. The From trait is implemented to convert ExitStatus to ExitCode, mapping Success to 0, Failure to 1, and Error to 2.

Source: `crates/ruff/src/lib.rs:37`; SHA-256: `0ef764772b4d62ea35232b09f2fe7a578dc5211451bf59fabd4e653251c276c6`.

    #[derive(Copy, Clone)]
    pub enum ExitStatus {
        /// Linting was successful and there were no linting errors.
        Success,
        /// Linting was successful but there were linting errors.
        Failure,
        /// Linting failed.
        Error,
    }
    
    impl From<ExitStatus> for ExitCode {
        fn from(status: ExitStatus) -> Self {
            match status {
                ExitStatus::Success => ExitCode::from(0),
                ExitStatus::Failure => ExitCode::from(1),
                ExitStatus::Error => ExitCode::from(2),
            }
        }
    }


