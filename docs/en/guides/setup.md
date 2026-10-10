# Study guide setup and recovery

This repository contains Markdown interview guides about ENV Auditor, Go Image Optimizer, URL Shortener, Rust Event Relay and Payment Reconciliation Lab. It has no runtime application, Dockerfile, Compose services, application dependency manifest/lockfile or service startup configuration. It now includes standard-library Python documentation tooling and a safe metadata manifest under tools/. Read the guides on GitHub or in any Markdown reader; no package installation is required.

Commands and source references inside each guide belong to its subject project's root, not this repository. Use that project's setup and testing documentation for runtime configuration. Docker startup, dependency persistence, application/database checks, port conflicts and shutdown are not applicable here. No containers were started.

For a missing tracked guide, confirm the exact file is absent before restoring that path:

```sh
# Run in engineering-library; substitute the exact missing tracked path.
git restore --source=HEAD -- docs/en/interviews/exact-missing-guide.md
```

Git cannot restore deleted uncommitted notes; use backups. No container or dependency installer can reconstruct custom interview content. The former Word study documents were converted to language-paired Markdown, preserving questions, technical examples and tables while consolidating repeated English explanations. Original Word page layout is not a maintained output format. See [validation](../testing/verification.md).

For documentation checks, Python 3.10+ is required; no third-party packages are needed. See the [validator guide](documentation-validator.md). Validator commands belong to this repository; application commands inside project interviews belong to the subject project.
