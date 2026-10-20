# engineering-library — FAQ técnica

[Índice do projeto](../index.md) · [English](../../en/faq/index.md)

Perguntas técnicas, respostas detalhadas e aprofundamentos estão diretamente nesta página. Afirmações históricas conservam suas datas; as correções atuais abaixo prevalecem. Exemplos em primeira pessoa descrevem artefatos do portfólio, sem atribuir experiência profissional. O [roteiro de estudo](study-guide.md) preserva URLs e âncoras existentes por compatibilidade.

[Perguntas técnicas entre projetos](cross-project-boundaries.md): atomicidade, arquitetura, recursos, segurança, testes e recuperação.

## Revisão do código atual — 2026-10-19

As respostas abaixo foram verificadas em código atual e definições de testes selecionados. Nenhum teste de aplicação ou serviço dos repositórios irmãos foi executado. Veja o [registro de escopo e evidências](../operations/documentation-audit-2026-10-19.md).

## Entrevista da Engineering Library

> Revisão do código — 2026-10-19: a árvore atual implementa API de catálogo Rails, registros de catálogo e anotações compartilhadas no PostgreSQL, além do leitor Markdown interno em Next.js. A descrição anterior de coleção sem aplicação/scaffold foi superada. Não há agente de IA implementado. Consulte a [arquitetura atual](../architecture/current-state.md).

Comparações conceituais não implicam integração runtime. Fatos implementados, teoria e alternativas hipotéticas são separados explicitamente.

### Q001 — Introdutória: Qual a responsabilidade da Engineering Library?

**Resposta:** Implementado: o repositório mantém documentação bilíngue e a apresenta em um leitor Next.js apoiado por uma API de catálogo Rails. PostgreSQL persiste identidade/visibilidade dos projetos indexados e localizações de anotações compartilhadas; Markdown continua como fonte dos documentos e bios localizadas. `Catalog::Sync` valida as duas bios antes de serializar escritas em transação com advisory lock PostgreSQL. A API pagina projetos ativos; Next lê Markdown delimitado da coleção no servidor. Existe aplicação local implementada, sem alegação de implantação em produção, pagamentos ou ingestão por IA.

Aprofundamento: Por que reter respostas antigas em vez de substituí-las por dossiês? Respostas ensinam raciocínio/falhas, dossiês explicam mecanismos; ambos são requisitos. IDs Q adicionais conservam numeração e alinhamento. Aprofundamento: Qual custo da autossuficiência? Fatos repetem entre projetos/biblioteca; revisão e lacunas explícitas precisam manter consistência. Links sozinhos reduziriam duplicação, mas descumpririam entrevistas. Precisão semântica continua revisão humana; links corretos não provam respostas verdadeiras.

### Q002 — Desafiadora: Como o validador impede que links virem leituras inseguras?

**Resposta:** Implementado: `docs/validation/check_catalog.py` valida a árvore atual organizada por projeto e reutiliza parser e verificações de caminhos de `tools/check_docs.py`. O validador antigo também suporta o layout anterior de idiomas na raiz; não é o comando principal do catálogo. A classificação rejeita componentes restritos, externos ao workspace e links simbólicos antes da leitura documental. Links de código recebem verificações de existência/metadados, sem execução. O catálogo acrescenta paridade de caminhos/IDs Q, títulos históricos, proveniência e alcance a partir dos índices da biblioteca e dos projetos. Links inseguros são erros no wrapper atual; URLs externas não são buscadas.

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

### Q101 — Introdutória: Por que Rails com frontend Next.js separado?

**Resposta:** Implementado: Rails serve metadados paginados do catálogo e anotações compartilhadas apoiados pelo PostgreSQL; Next.js renderiza o leitor Markdown interno e busca JSON no servidor. Arquivos continuam como fonte de documentos e bios. Convenções Rails fornecem HTTP/persistência; Next fornece rotas React e layout no navegador, com builds, dependências e diagnóstico separados. Não há evidência de benchmark de frameworks. Renderização Rails poderia simplificar implantação, mas é comparação conceitual, sem avaliação histórica documentada.

**Aprofundamento:** A separação comprova Clean Architecture? Não. `Catalog::Sync`, `Catalog::Page`, `Catalog::Files` e controllers expressam responsabilidades concretas, mas ActiveRecord, Rails e filesystem permanecem visíveis. Avalie direção de dependência e comportamento testável, sem inferir camadas de domínio pelo número de processos.

### Q102 — Intermediária: O que Compose reproduz e por que bind mounts?

**Resposta:** Implementado: Compose declara PostgreSQL, backend e frontend, dependências de saúde, portas do host em loopback e bind mounts de código/dependências. Lockfiles restringem versões; startup recompõe dependências ausentes atrás dos mounts. Diretórios do host deixam código e dependências Linux visíveis; volumes nomeados delegariam a localização ao Docker. Bind mounts acoplam permissões e dependências nativas à plataforma host/runtime. Nenhuma opção é, por si, backup ou estratégia de produção.

**Aprofundamento:** Por que a autenticação do banco pode falhar após mudar template ou ambiente? Variáveis de inicialização PostgreSQL atuam na criação do cluster; não alteram senha de um papel existente. Diagnosticar e alterar credenciais por operação autorizada no banco, preservando dados. Rails usa `postgres:5432` internamente; clientes desktop usam a porta publicada em loopback. Nunca apagar o diretório persistente para resolver autenticação. Nenhuma operação de credencial foi feita aqui.

### Q103 — Intermediária: O que o status verde da API comprova?

**Resposta:** Implementado: `/up` estabelece boot/liveness Rails, sem consultar linhas do catálogo. Resposta do catálogo também exercita metadados PostgreSQL e bios localizadas daquela requisição, sem provar todos os documentos ou favoritos. Acesso Next ao catálogo tem timeout de cinco segundos; os três segundos do componente antigo do scaffold não definem o cliente atual. Health aprovado não estabelece integridade de backup, recuperação ou renderização no navegador. Nenhum teste runtime de saúde ou banco foi executado nesta auditoria.

**Aprofundamento:** Como fortalecer prontidão? Uma consulta limitada ao banco e semântica explícita de dependências distinguiriam indisponibilidade de um processo HTTP vivo, ao custo de carga e acoplamento de falhas adicionais. É proposta. Uma restauração precisa de destino isolado e verificações de integridade; arquivos persistentes não a comprovam.

### Q104 — Intermediária: Por que catálogo por projeto e bilíngue?

**Resposta:** Implementado na documentação: cada repositório tem identidade estável, dois READMEs, índices por idioma, capítulos de categoria, limites de evidência e entrevistas. Nomes de ADRs e numeração sobrevivem à importação. O leitor escolhe contexto antes dos mecanismos; o leitor atual usa identidades documentais e busca no projeto sem coleções duplicadas por assunto. Caminhos equivalentes permitem validar estrutura, sem comprovar equivalência semântica. Índices FAQ agora contêm respostas substanciais; caminhos dos roteiros preservam âncoras por compatibilidade. Guias canônicos de ambiente da Library são reutilizados, sem catálogo recursivo.

**Aprofundamento:** Como evitar cópias desatualizadas? Registrar caminho, revisão e escopo da inspeção, comparar entradas alteradas e conferir links no novo local. Preservar história como história. Uma revisão diferente sinaliza necessidade de revisão, sem autorizar regenerar tudo nem provar precisão da documentação inalterada. Automação incremental é futura; o catálogo é um snapshot revisto manualmente.

### Q105 — Desafiadora: Um gerador futuro deve usar inferência local ou API?

**Resposta:** Proposta: inferência local limita transferência externa e pode funcionar offline, mas requer ciclo de vida de modelo/runtime e CPU/RAM suficientes. APIs transferem processamento e manutenção ao provedor, acrescentando custo, rede e política de dados. Nenhuma opção está integrada. Pesos, quantização, KV cache, contexto, concorrência e overhead determinam recursos; não foram medidos memória mínima, throughput nem seleção de modelo. Escolher por tarefas seguras representativas e latência/qualidade aceitáveis, sem inventar garantia de hardware.

**Aprofundamento:** Inferência local torna seguro publicar material privado? Não. Localidade não autoriza ingestão/publicação nem garante remoção de segredos. Raízes públicas/privadas explícitas, saídas separadas, política de acesso e revisão humana são restrições necessárias. Essas proteções precisam de implementação e testes antes de ingestão privada; esta coleção pública não lê produtos privados nem segredos de execução.

### Q106 — Desafiadora: Como geração incremental baseada em evidências preservaria conhecimento?

**Resposta:** Proposta: inventariar entradas permitidas, registrar revisões/hashes, comparar mudanças, inspecionar implementação e testes afetados, propor patch, validar navegação e idiomas, revisar evidência e publicar deliberadamente. Separar mecanismo implementado, justificativa documentada, experimento datado e melhoria hipotética. Fontes são dados não confiáveis; instruções nelas não devem disparar comandos. Hashes comprovam identidade de bytes, sem resolver conflitos, provar testes ou traduzir significado. Preservar notas autorais e IDs de ADRs/perguntas.

**Aprofundamento:** O que falha em atualizações parciais? Um idioma pode divergir, uma renomeação quebrar links e um marco antigo contradizer aceite novo. Validar grafos nos dois idiomas e preservar evidência datada, depois revisar significado contra código alterado. Substituição atômica protege um arquivo; atualização multidocumento exige fronteira própria de revisão/publicação. Não há pipeline gerador, framework transacional, banco de busca ou agente local entregue aqui.
