# Engineering Library

> Private Viva Bem application for authorized internal use. Preserve source and internal-document confidentiality.

[Project index](index.md) · [Português brasileiro](../pt-br/README.md) · [Repository overview](../../../README.md)

The application provides a Rails/PostgreSQL catalog and shared annotations, a Next.js bilingual book reader and local Ollama draft generation. Markdown owns chapter bodies; database records own metadata and shared notes/highlights/bookmarks. The host adapter handles registered source acquisition and verified publication to original project documentation.

<!-- reading-section: README-1 -->
## Reading order

1. [Current architecture and source map](architecture/current-implementation.md)
2. [Development and Docker](guides/application-development.md)
3. [Configuration](env/index.md)
4. [MakeDocs and evaluation](training/local-documentation-command.md)
5. [Runtime and recovery](operations/runtime-and-recovery.md)
6. [Decisions and limits](architecture/decisions.md)
7. [Technical FAQ](faq/index.md)

MakeDocs is operational but generated content remains a draft. Desired factual/translation quality and completed neural fine-tuning are not established. Startup requires POSIX host Python and Docker Compose; use the managed commands in the development guide. Dated reports remain evidence of their original review scope, not current full acceptance.

[Project bio](bio.md)
