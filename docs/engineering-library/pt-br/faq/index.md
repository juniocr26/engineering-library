# engineering-library — FAQ técnica

[Índice do projeto](../index.md) · [English](../../en/faq/index.md)

Perguntas técnicas, respostas detalhadas e aprofundamentos estão diretamente nesta página. Afirmações históricas conservam suas datas; as correções atuais abaixo prevalecem. Exemplos em primeira pessoa descrevem artefatos do portfólio, sem atribuir experiência profissional. O [roteiro de estudo](study-guide.md) preserva URLs e âncoras existentes por compatibilidade.

[Perguntas técnicas entre projetos](cross-project-boundaries.md): atomicidade, arquitetura, recursos, segurança, testes e recuperação.

## Proveniência da revisão

Q001–Q005 conservam a revisão de 19/10/2026; Q101–Q106 foram atualizadas contra o código em 26/11/2026. Nenhum teste de aplicação ou serviço dos repositórios irmãos foi executado. Veja o [registro de escopo e evidências](../operations/documentation-audit-2026-10-19.md).

## Entrevista da Engineering Library

> Referência atual — 26/11/2026: MakeDocs/Ollama local e publicação gerenciada no host estão implementados. O conteúdo continua rascunho; qualidade desejada e fine-tuning neural não estão estabelecidos. Veja [arquitetura atual](../architecture/current-implementation.md).

Comparações conceituais não implicam integração runtime. Fatos implementados, teoria e alternativas hipotéticas são separados explicitamente.

### Q001 — Introdutória: Qual a responsabilidade da Engineering Library?

**Resposta:** Implementado: o repositório mantém documentação bilíngue e a apresenta em um leitor Next.js apoiado por uma API de catálogo Rails. PostgreSQL persiste identidade/visibilidade dos projetos indexados e localizações de anotações compartilhadas; Markdown continua como fonte dos documentos e bios localizadas. `Catalog::Sync` valida as duas bios antes de serializar escritas em transação com advisory lock PostgreSQL. A API pagina projetos ativos; Next lê Markdown delimitado da coleção no servidor. Existe aplicação local implementada, sem alegação de implantação em produção, pagamentos ou aceitação integral da geração por IA.

Aprofundamento: Por que reter respostas antigas em vez de substituí-las por dossiês? Respostas ensinam raciocínio/falhas, dossiês explicam mecanismos; ambos são requisitos. IDs Q adicionais conservam numeração e alinhamento. Aprofundamento: Qual custo da autossuficiência? Fatos repetem entre projetos/biblioteca; revisão e lacunas explícitas precisam manter consistência. Links sozinhos reduziriam duplicação, mas descumpririam entrevistas. Precisão semântica continua revisão humana; links corretos não provam respostas verdadeiras.

### Q002 — Desafiadora: Como o validador impede que links virem leituras inseguras?

**Resposta:** Implementado: `tools/check_catalog.py` valida a árvore atual organizada por projeto e reutiliza parser e verificações de caminhos de `tools/check_docs.py`. O validador antigo também suporta o layout anterior de idiomas na raiz; não é o comando principal do catálogo. A classificação rejeita componentes restritos, externos ao workspace e links simbólicos antes da leitura documental. Links de código recebem verificações de existência/metadados, sem execução. O catálogo acrescenta paridade de caminhos/IDs Q, títulos históricos, proveniência e alcance a partir dos índices da biblioteca e dos projetos. Links inseguros são erros no wrapper atual; URLs externas não são buscadas.

Aprofundamento: É sandbox livre de corrida? Não. lstat seguido de leitura tem janela TOCTOU em filesystem maliciosamente alterado; assume workspace cooperativo. Percurso por descritores no-follow fortaleceria com custo de portabilidade. Aprofundamento: Parser equivale ao GitHub completo? Não. Trata subconjunto documentado de links/referências, headings, fences e IDs. Sintaxe aninhada complexa exige revisão. Erros retornam não zero, JSON registra findings e fixtures isoladas exercitam falhas. Validador expõe lacunas, não decide verdade técnica ou qualidade de tradução.

### Q003 — Intermediária: Como a coleção representa e valida navegação sem implantar aplicação?

**Resposta:** Implementado: caminhos Markdown estáveis formam o contrato de navegação. O validador atual carrega Markdown permitido, extrai âncoras/destinos e percorre o grafo desde a biblioteca e cada índice de projeto/idioma. Essas verificações Python dispensam Rails, PostgreSQL e Next. O leitor em execução tem comportamento separado: `documentationEntries` unifica IDs relativos entre idiomas, omite índices apenas navegacionais, mantém índices substanciais e constrói entradas por categoria/documento. Assim, índices FAQ com respostas tornam-se capítulos automaticamente. Validação estrutural não demonstra paginação no navegador nem disponibilidade da API.

Aprofundamento: Qual custo? Leitura/parser crescem com bytes; percurso com vértices/arestas, mais metadados filesystem; sem medições. Aprofundamento: Estrutura detecta fatos conflitantes/traduções ruins? Não. Detecta IDs/contrapartes/respostas ausentes, mas revisão do código julga significado. Testes isolados comprovam contratos selecionados, não operação livre de corrida sob mutação hostil ou alcance externo.

### Q004 — Por que conteúdo em arquivos e sincronização do catálogo têm fronteiras de consistência diferentes?

**Resposta:** `Catalog::Sync` valida as duas bios e IDs estáveis duplicados antes da transação PostgreSQL. Seu advisory lock serializa sincronizações cooperantes no banco, sem bloquear editores de arquivos. Arquivos podem mudar após a validação; presenters também leem bios do disco depois. Mantenha metadados estáveis durante sync e sincronize explicitamente alterações de bio/nome/slug. Editar o corpo de um capítulo dispensa ingestão no banco. Projetos ausentes ficam inativos; IDs estáveis preservam a identidade do catálogo em renomeações suportadas. Isso não migra favoritos, cuja associação usa o slug textual. Sync bem-sucedido estabelece a atualização indexada sob aquelas entradas, sem snapshot atômico de todos os capítulos ou reparação automática de URLs antigas de favoritos.

### Q005 — O que protege anotações compartilhadas e quais garantias permanecem ausentes?

**Resposta:** Todos os navegadores usam um conjunto local PostgreSQL, delimitado por projeto canônico, documento e idioma obrigatório. Tokens CSRF assinados com expiração e verificação de origem no proxy protegem mutações sem cookies ou perfis. IDs identificam anotações distintas; marcações legadas preservadas usam uma variante determinística de localização. O limite de admissão de 200 marcações não é quota exata sob concorrência. A existência do documento é validada, mas âncoras são conferidas na navegação; conteúdo alterado pode tornar uma posição indisponível. Consulte a [arquitetura atual](../architecture/current-state.md).


## Perguntas sobre aplicação e catálogo

O [caminho anterior da FAQ da aplicação](application-and-catalog.md) permanece disponível. As respostas completas também estão aqui; correções atuais superam a descrição anterior do scaffold.

Leia a [arquitetura atual](../architecture/current-state.md), a [direção futura](../architecture/future-direction.md) e as [perguntas preservadas](study-guide.md). Implementado significa código inspecionado, sem execução neste marco. Alternativas propostas abaixo são análises, não motivações originais sem evidência.

### Q101 — Por que Rails com frontend Next.js separado?

**Resposta:** Rails cuida da sincronização validada do catálogo, anotações relacionais e coordenação protegida de operações; Next renderiza Markdown e controla layout do livro. HTTP separa responsabilidades runtime. Markdown continua fonte dos capítulos; PostgreSQL armazena metadados/anotações. A separação acrescenta builds, dependências e diagnóstico; não prova superioridade em benchmark ou Clean Architecture.

**Aprofundamento:** O frontend pode dispensar Rails em tudo? Lê capítulos no servidor, mas catálogo/anotações/operações usam Rails. Notas compartilhadas exigem persistência e localizações lógicas, não páginas físicas.

### Q102 — O que Compose reproduz e por que Python no host?

**Resposta:** Compose define frontend, backend, PostgreSQL e Ollama, dependências de health, portas loopback e armazenamento explícito. Supervisor/adapter no host é processo POSIX adicional necessário, gerenciado por `tools/init_dev_env.py`. Adquire código externo e publica docs aceitos sem novos mounts arbitrários. Frontend e backend atualmente montam a biblioteca gravável; código/agente têm restrições próprias.

**Aprofundamento:** Parar containers apaga estado? Stop/down gerenciados preservam armazenamento. Persistência ou startup bem-sucedido não comprova backup/restauração. Não exclua banco, modelos ou recuperação para reparar startup.

### Q103 — O que health verde comprova?

**Resposta:** `/up` comprova resposta Rails e heartbeat obrigatório do adapter naquele instante. Não consulta todos os registros nem valida modelo aprovado, qualidade, dois destinos ou restauração. Health checks PostgreSQL/Ollama/Next também têm escopos limitados. A API do catálogo pode sincronizar metadados, não sendo consulta estritamente somente leitura ao banco.

**Aprofundamento:** Inferência bem-sucedida basta? Não. Evidências devem passar avaliação/propriedade, escritas na biblioteca/workspace devem funcionar e entrega ao host deve concluir. O rascunho publicado ainda exige revisão humana.

### Q104 — Como cadastro, duplicatas e relocação funcionam?

**Resposta:** Referências relativas resolvem a partir do checkout da biblioteca no host. O cadastro verifica identidade e cria metadados/bios sem inferência. Identidade estável, caminhos normalizados, aliases físicos e request IDs evitam duplicatas em retries. Commits raiz identificam linhagem; hashes atuais identificam conteúdo. Relocação exige mesma identidade no novo caminho, origem anterior comprovadamente ausente e ausência de cópias ambíguas.

**Aprofundamento:** Renomear repositório distinto migra anotações? Não. Relocação verificada preserva relações suportadas de identidade/referência; não é renomeação genérica de slug, reescrita de marcadores ou migração arbitrária.

### Q105 — Como inferência local e avaliação funcionam hoje?

**Resposta:** O chamador normal usa `llama3.2:3b` aprovado no Ollama local e três skills verificadas por integridade. Seleciona evidências limitadas, solicita fatos bilíngues estruturados, verifica envelopes/proveniência/literais/alegações e renderiza resumos próprios. Requisições automáticas por declaração Python dividem prazo limitado. UI e CLI padrão usam `Documentation::Command`; fluxo optativo de projeto é separado.

**Aprofundamento:** O agente foi treinado até a qualidade desejada? Isso não está demonstrado. Contexto de skills não é fine-tuning neural. Aceitação mecânica pode deixar passar erros semânticos e traduções ruins; qualidade desejada é trabalho futuro com campanha autorizada separadamente. Não há fallback de nuvem ou substituição automática de modelo.

### Q106 — O ciclo completo suporta ausência de docs?

**Resposta:** O desenho suporta cadastrar → gerar → atualizar → remover cadastro → cadastrar novamente → gerar novamente. A primeira publicação cria `docs/` original com segurança. Remoção arquiva a árvore da biblioteca e preserva código/docs manuais originais; recadastro elegível restaura identidade/arquivo. Origem ausente ou falha do adapter não justificam apagar evidências ou excluir automaticamente cadastro gerenciado.

**Aprofundamento:** E se entrega ou remoção for interrompida? Entrega pendente pode retomar configuração salva sem inferência; journals e arquivos verificados governam recuperação do comando/remoção. Concorrência ou ambiguidade são recusadas. Veja [operação e recuperação](../operations/runtime-and-recovery.md). Esta revisão não afirma execução de novo teste completo do ciclo.
