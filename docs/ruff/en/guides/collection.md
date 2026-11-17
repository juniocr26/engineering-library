# ruff

Evaluation draft assembled from bounded, independent source-only local-model passes. Explanations require factual and bilingual review. Selected files do not establish complete project documentation.

Revision: `0222c19dd8e0c9a927f2e47bf3774a108431da25`.

## Contents

- [CLI outcomes](#cli-outcomes)
- [Input selection](#input-selection)
- [Verification and technical limitations](#verification-and-technical-limitations)

<!-- reading-section: project-section-exit-status -->

## CLI outcomes

### 1

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




<!-- reading-section: project-section-stdin -->

## Input selection

### 1

The `is_stdin` function supports the condition that if the user provided a `--stdin-filename`, the program always reads from standard input.

Source: `crates/ruff/src/lib.rs:96`; SHA-256: `0ef764772b4d62ea35232b09f2fe7a578dc5211451bf59fabd4e653251c276c6`.

    fn is_stdin(files: &[PathBuf], stdin_filename: Option<&Path>) -> bool {
        // If the user provided a `--stdin-filename`, always read from standard input.
        if stdin_filename.is_some() {
            if let Some(file) = files.iter().find(|file| file.as_path() != Path::new("-")) {
                warn_user_once!(
                    "Ignoring file {} in favor of standard input.",
                    file.display()
                );
            }
            return true;
        }
    
        let [file] = files else {
            return false;
        };
        // If the user provided exactly `-`, read from standard input.
        file == Path::new("-")
    }
    
    /// Returns the default set of files if none are provided, otherwise returns provided files.
    fn resolve_default_files(files: Vec<PathBuf>, is_stdin: bool) -> Vec<PathBuf> {
        if files.is_empty() {
            if is_stdin {
                vec![Path::new("-").to_path_buf()]
            } else {
                vec![Path::new(".").to_path_buf()]
            }
        } else {
            files
        }
    }




<!-- reading-section: project-verification -->

## Verification and technical limitations

Runtime/build evidence is recorded separately in the campaign report. This generation command executes no discovered source code and does not certify GUI/GPU/device behavior.
