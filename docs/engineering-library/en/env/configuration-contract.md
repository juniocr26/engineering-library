# Configuration contract without private values

[Environment reference](index.md) · [Runtime and recovery](../operations/runtime-and-recovery.md)

The current configuration has three consumers: Compose interpolation, container application processes and the POSIX host adapter. They do not share every environment variable automatically. A declaration in source does not make an input globally required.

- Compose requires PostgreSQL user/password/database and Rails secret, and binds default ports to loopback. The existing `.env` is preserved by the managed launcher.
- Container paths identify the mounted library/agent and internal service endpoints. They are not user-facing host source paths.
- Host references are relative to the library checkout. The adapter validates identity and bounds acquisition/publication; changing container mounts is not the normal registration flow.
- Approved model and skill identities constrain generation. Request limits, coverage and publication state do not establish editorial acceptance or completed fine-tuning.
- Startup runs database preparation and catalog synchronization. Use read-only source analysis when database mutations are outside the authorized scope.

[Environment tables](index.md) record current defaults, validation ranges and consumers. No private effective values, credentials or machine-specific source paths belong in this documentation. Dated configuration reviews remain historical evidence; current source contracts take precedence.
