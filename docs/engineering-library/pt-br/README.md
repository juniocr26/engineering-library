# Engineering Library

> Aplicação privada da Viva Bem para uso interno autorizado. Preserve a confidencialidade do código e da documentação interna.

[Índice do projeto](index.md) · [English](../en/README.md) · [Visão do repositório](../../../README.pt-BR.md)

A aplicação fornece catálogo Rails/PostgreSQL e anotações compartilhadas, leitor bilíngue Next.js e rascunhos Ollama locais. Markdown contém os capítulos; o banco contém metadados e notas/destaques/marcadores compartilhados. O adapter adquire código cadastrado e verifica a publicação na documentação original.

<!-- reading-section: README-1 -->
## Ordem de leitura

1. [Arquitetura e mapa de código](architecture/current-implementation.md)
2. [Desenvolvimento e Docker](guides/application-development.md)
3. [Configuração](env/index.md)
4. [MakeDocs e avaliação](training/local-documentation-command.md)
5. [Operação e recuperação](operations/runtime-and-recovery.md)
6. [Decisões e limites](architecture/decisions.md)
7. [FAQ técnica](faq/index.md)

MakeDocs está operacional, mas o conteúdo continua como rascunho. Não se estabelece qualidade factual/de tradução desejada nem fine-tuning neural concluído. Startup exige Python POSIX no host e Docker Compose; use os comandos gerenciados do guia. Relatórios datados conservam o escopo original, sem equivaler à aceitação integral atual.

[Bio do projeto](bio.md)
