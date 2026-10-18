# Entrevista sobre aplicação e catálogo

Leia a [arquitetura atual](../architecture/current-state.md), a [direção futura](../architecture/future-direction.md) e as [perguntas preservadas](study-guide.md). Implementado significa código inspecionado, sem execução neste marco. Alternativas propostas abaixo são análises, não motivações originais sem evidência.

### Q101 — Introdutória: Por que Rails com frontend Next.js separado?

**Resposta:** Implementado: Rails expõe `/up`, configura PostgreSQL e fornece classes-base de API; Next.js renderiza uma página inicial e consulta saúde no servidor. A arquitetura documentada separa apresentação no navegador de HTTP/persistência no backend. Convenções Rails facilitam iniciar a API; Next.js fornece renderização React e roteamento. Não há evidência de benchmarks entre frameworks. Duas aplicações exigem dependências, builds, rede e diagnóstico separados. Um site renderizado por Rails simplificaria implantação; é alternativa hipotética, não decisão histórica avaliada.

**Aprofundamento:** A separação comprova Clean Architecture? Não. Convenções Rails e processos separados não estabelecem inversão de dependência nem casos de uso de domínio. Introduzir uma fronteira de caso de uso quando existir contrato real de leitura documental; adaptadores podem cuidar de arquivos e HTTP sem acoplar o núcleo ao framework. Hoje não existe serviço de catálogo implementado a descrever.

### Q102 — Intermediária: O que Compose reproduz e por que bind mounts?

**Resposta:** Implementado: Compose declara PostgreSQL, backend e frontend, dependências de saúde, portas do host em loopback e bind mounts de código/dependências. Lockfiles restringem versões; startup recompõe dependências ausentes atrás dos mounts. Diretórios do host deixam código e dependências Linux visíveis; volumes nomeados delegariam a localização ao Docker. Bind mounts acoplam permissões e dependências nativas à plataforma host/runtime. Nenhuma opção é, por si, backup ou estratégia de produção.

**Aprofundamento:** Por que a autenticação do banco pode falhar após mudar template ou ambiente? Variáveis de inicialização PostgreSQL atuam na criação do cluster; não alteram senha de um papel existente. Diagnosticar e alterar credenciais por operação autorizada no banco, preservando dados. Rails usa `postgres:5432` internamente; clientes desktop usam a porta publicada em loopback. Nunca apagar o diretório persistente para resolver autenticação. Nenhuma operação de credencial foi feita aqui.

### Q103 — Intermediária: O que o status verde da API comprova?

**Resposta:** Implementado: o componente de servidor Next.js consulta `/up` com timeout de três segundos e apresenta conectividade. O health Rails verifica boot/liveness, sem executar teste SQL de prontidão. O teste de integração inspecionado executa separadamente `SELECT 1`, verifica saúde e não divulgação da senha. Definições comprovam asserções previstas, não execução nesta tarefa. Dados persistem em bind mount do host; saúde HTTP não comprova backup nem recuperação.

**Aprofundamento:** Como fortalecer prontidão? Uma consulta limitada ao banco e semântica explícita de dependências distinguiriam indisponibilidade de um processo HTTP vivo, ao custo de carga e acoplamento de falhas adicionais. É proposta. Uma restauração precisa de destino isolado e verificações de integridade; arquivos persistentes não a comprovam.

### Q104 — Intermediária: Por que catálogo por projeto e bilíngue?

**Resposta:** Implementado na documentação: cada repositório tem identidade estável, dois READMEs, índices por idioma, capítulos de categoria, limites de evidência e entrevistas. Nomes de ADRs e numeração sobrevivem à importação. O leitor escolhe contexto antes dos mecanismos; títulos e caminhos permitem busca futura sem coleções duplicadas por assunto. Caminhos equivalentes permitem validar estrutura, sem comprovar equivalência semântica. Índices apontam explicações sem repeti-las. Guias canônicos de ambiente da Library são reutilizados, sem catálogo recursivo.

**Aprofundamento:** Como evitar cópias desatualizadas? Registrar caminho, revisão e escopo da inspeção, comparar entradas alteradas e conferir links no novo local. Preservar história como história. Uma revisão diferente sinaliza necessidade de revisão, sem autorizar regenerar tudo nem provar precisão da documentação inalterada. Automação incremental é futura; o catálogo é um snapshot revisto manualmente.

### Q105 — Desafiadora: Um gerador futuro deve usar inferência local ou API?

**Resposta:** Proposta: inferência local limita transferência externa e pode funcionar offline, mas requer ciclo de vida de modelo/runtime e CPU/RAM suficientes. APIs transferem processamento e manutenção ao provedor, acrescentando custo, rede e política de dados. Nenhuma opção está integrada. Pesos, quantização, KV cache, contexto, concorrência e overhead determinam recursos; não foram medidos memória mínima, throughput nem seleção de modelo. Escolher por tarefas seguras representativas e latência/qualidade aceitáveis, sem inventar garantia de hardware.

**Aprofundamento:** Inferência local torna seguro publicar material privado? Não. Localidade não autoriza ingestão/publicação nem garante remoção de segredos. Raízes públicas/privadas explícitas, saídas separadas, política de acesso e revisão humana são restrições necessárias. Essas proteções precisam de implementação e testes antes de ingestão privada; esta coleção pública não lê produtos privados nem segredos de execução.

### Q106 — Desafiadora: Como geração incremental baseada em evidências preservaria conhecimento?

**Resposta:** Proposta: inventariar entradas permitidas, registrar revisões/hashes, comparar mudanças, inspecionar implementação e testes afetados, propor patch, validar navegação e idiomas, revisar evidência e publicar deliberadamente. Separar mecanismo implementado, justificativa documentada, experimento datado e melhoria hipotética. Fontes são dados não confiáveis; instruções nelas não devem disparar comandos. Hashes comprovam identidade de bytes, sem resolver conflitos, provar testes ou traduzir significado. Preservar notas autorais e IDs de ADRs/perguntas.

**Aprofundamento:** O que falha em atualizações parciais? Um idioma pode divergir, uma renomeação quebrar links e um marco antigo contradizer aceite novo. Validar grafos nos dois idiomas e preservar evidência datada, depois revisar significado contra código alterado. Substituição atômica protege um arquivo; atualização multidocumento exige fronteira própria de revisão/publicação. Não há pipeline gerador, framework transacional, banco de busca ou agente local entregue aqui.
