# Study guide setup and recovery

This repository contains Markdown interview guides about ENV Auditor, Go Image Optimizer, URL Shortener, Rust Event Relay and Payment Reconciliation Lab. It has no executable application, Dockerfile, Compose services, dependency manifest, lockfile, startup script or generated configuration. Read the guides on GitHub or in any Markdown reader; no package installation is required.

Commands and source references inside each guide belong to its subject project's root, not this repository. Use that project's setup and testing documentation for runtime configuration. Docker startup, dependency persistence, application/database checks, port conflicts and shutdown are not applicable here. No containers were started.

For a missing tracked guide, confirm the exact file is absent before restoring that path:

```sh
# Run in tecnical-interview; substitute the exact missing tracked path.
git restore --source=HEAD -- docs/en/exact-missing-guide.md
```

Git cannot restore deleted uncommitted notes; use backups. No container or dependency installer can reconstruct custom interview content. The former Word study documents were converted to language-paired Markdown, preserving questions, technical examples and tables while consolidating repeated English explanations. Original Word page layout is not a maintained output format. See [validation](verification.md).
