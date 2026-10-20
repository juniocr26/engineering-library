# Entrevista sobre aplicação e catálogo

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
