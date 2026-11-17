# Ruff — Input selection

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: ruff. Generation: 1.9.12; model: llama3.2:3b; evidence SHA-256: fc2a1ddf4d25ac96af48d7677a7eb041fd6c279e7f33fd3fbf4ec2db08c0b33f.

Coverage: 1/1 candidate files; explicit project section; counts apply only to staged files, not whole repository coverage; 0 omitted.

Explicit source-unit scope for the files listed below; their unselected content was not provided:

    {}

Selected units: 0; cited units: 0.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

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


