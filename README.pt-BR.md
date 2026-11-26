# Engineering Library

> Projeto de software privado da Viva Bem, mantido em repositório privado para uso interno autorizado. Não divulgue publicamente código, documentação interna ou informações específicas dos projetos sem autorização.

[Documentação em português](docs/engineering-library/pt-br/index.md) · [English](README.md)

## Implementação atual

Engineering Library reúne leitor de livros Markdown bilíngues, catálogo, anotações compartilhadas PostgreSQL e elaboração local de documentação com Ollama. Next.js lê capítulos e consulta Rails para metadados, notas, destaques, marcadores e gerenciamento protegido em desenvolvimento. Um adapter POSIX supervisionado no host resolve referências relativas cadastradas e publica rascunhos aceitos na biblioteca e na documentação original.

MakeDocs está operacional. Seus resumos limitados continuam como rascunhos sujeitos a revisão factual e bilíngue; publicação bem-sucedida não comprova qualidade desejada, aceitação integral do projeto ou fine-tuning neural. Uma futura campanha de qualidade é separada da operação normal.

## Instalação e ciclo operacional

Use Docker com Compose e Python 3.10+ no host POSIX. Node.js, Ruby, Rails e clientes de banco executam nos containers. No Windows use WSL2 integrado ao Docker; PowerShell nativo não executa o adapter atual. Execute na raiz deste checkout:

```sh
# Preserva .env existente; gera credenciais privadas somente se ausente.
# Inicia o supervisor obrigatório no host e os serviços Compose existentes.
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
# Frontend: http://127.0.0.1:3099
# Health do backend: http://127.0.0.1:3098/up
python3 -B tools/init_dev_env.py status
python3 -B tools/init_dev_env.py stop
python3 -B tools/init_dev_env.py up -d
python3 -B tools/init_dev_env.py restart
python3 -B tools/init_dev_env.py down
```

O startup executa preparação do banco e sincronização do catálogo Rails. Revise migrations antes de upgrades. Compose sozinho não inicializa o supervisor. O desligamento preserva `.dockerized-postgres/`, `ollama/`, recursos do agente e recuperação privada MakeDocs; prune, resets e exclusão de estado não são limpeza rotineira. Editar `.env` não troca credenciais de inicialização de banco existente.

O stack padrão contém frontend, backend, PostgreSQL 18 e Ollama fixado. Portas padrão 3099/3098/5499 são loopback; Ollama não publica porta no host. `/up` verifica Rails e adapter obrigatório, não qualidade semântica ou disponibilidade integral de banco/modelo. Anotações são compartilhadas na instalação; não existem contas pessoais.

## Ciclo dos projetos

Cadastre no frontend uma referência como `../example-project`, relativa ao checkout da biblioteca no host. O cadastro verifica identidade e inicializa metadados sem inferência; repetição equivalente é idempotente. Relocação exige identidade correspondente, origem anterior ausente e ausência de ambiguidades. Remoção preserva código/documentação manual originais e arquiva conteúdo elegível da biblioteca para recuperação/recadastro.

Sequência esperada: cadastrar → gerar → atualizar → remover cadastro → cadastrar novamente → gerar novamente. Ausência de `docs/` original é suportada; a publicação cria diretórios. UI e CLI padrão usam `Documentation::Command`. Geração escreve dados: execute apenas para projeto cadastrado especificamente autorizado, por exemplo `docker compose exec -T backend make docs DOCS_ARGS='--project example-project'`. Entrega pendente, conflitos e journals devem ser tratados pelo fluxo documentado, não excluídos.

## Documentação técnica

- [Arquitetura, integração e mapa de código](docs/engineering-library/pt-br/architecture/current-implementation.md)
- [Decisões arquiteturais e limites atuais](docs/engineering-library/pt-br/architecture/decisions.md)
- [Desenvolvimento, Docker e comandos](docs/engineering-library/pt-br/guides/application-development.md)
- [Filesystem do host, publicação e recuperação](docs/engineering-library/pt-br/operations/runtime-and-recovery.md)
- [Variáveis de ambiente e configuração](docs/engineering-library/pt-br/env/index.md)
- [MakeDocs, recursos do agente e avaliação](docs/engineering-library/pt-br/training/local-documentation-command.md)
- [FAQ técnica](docs/engineering-library/pt-br/faq/index.md)
- [Leitor e referências aprovadas de código](docs/engineering-library/pt-br/guides/book-frontend.md)

Revisão atual: 26/11/2026, referência de implementação `246f58be`. Auditorias e relatórios datados permanecem históricos. Esta consolidação não executou geração, treinamento, preparação de banco ou novo teste de aceitação do ciclo. Identidade privada do repositório e artefatos existentes de agente/recuperação são preservados.
