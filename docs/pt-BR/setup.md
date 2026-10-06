# Leitura e recuperação dos guias

Este repositório contém guias Markdown de entrevista sobre ENV Auditor, Go Image Optimizer e URL Shortener. Não há aplicação executável, Dockerfile, serviços Compose, manifest, lockfile, script de startup ou configuração gerada. Leia no GitHub ou em leitor Markdown; não é necessário instalar pacotes.

Comandos e referências de fonte pertencem à raiz do projeto estudado, não a este repositório. Use a documentação de instalação/testes desse projeto para configuração de runtime. Startup Docker, persistência de dependências, aplicação/banco, conflitos de porta e parada não se aplicam aqui. Nenhum container foi iniciado.

Para guia versionado ausente, confirme a ausência antes de restaurar somente esse caminho:

```sh
# Execute em tecnical-interview; substitua pelo caminho versionado ausente.
git restore --source=HEAD -- docs/pt-BR/exact-missing-guide.md
```

Git não recupera notas não commitadas excluídas; use backups. Containers/instaladores não reconstroem conteúdo personalizado. Os documentos Word anteriores foram convertidos em Markdown com pares de idiomas, preservando perguntas, exemplos técnicos e tabelas, com consolidação de explicações repetidas em inglês. O layout de páginas Word não é formato mantido. Veja [validação](verification.md).
