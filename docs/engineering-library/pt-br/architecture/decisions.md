# Decisões arquiteturais e compromissos

[Índice de arquitetura](index.md) · [Implementação atual](current-implementation.md)

Explicação do desenho atual derivada do código, revisada em 26/11/2026. Não afirma retroativamente que alternativas foram comparadas em benchmark ou aprovadas formalmente em ADRs históricos.

| Limite implementado | Mecanismo e justificativa prática | Compromisso / limite |
| --- | --- | --- |
| Corpos Markdown e metadados relacionais | Next lê capítulos delimitados; Rails sincroniza catálogo/bios validados e armazena anotações. Arquivos seguem editáveis/revisáveis, enquanto identidades e anotações usam restrições relacionais. | Arquivos e banco são domínios de consistência distintos; startup/acesso ao catálogo pode sincronizar metadados. |
| Processos Rails e Next separados | HTTP separa persistência/operação da renderização do leitor e layout do navegador. | Dois conjuntos de dependências, targets e caminhos de diagnóstico; não comprova Clean Architecture. |
| Anotações da instalação | Chaves lógicas de documento/localização sobrevivem à repaginação física. | Sem identidade pessoal ou notas privadas por usuário; acesso à instalação deve ser restrito. |
| Cadastro explícito e identidade de linhagem | Referências relativas, commits raiz Git e verificações físicas evitam descoberta cega de vizinhos e duplicatas/relocações ambíguas. | Repositórios da mesma linhagem exigem desambiguação; identidade não comprova árvores de trabalho iguais. |
| Adapter do usuário comum no host | Requisições limitadas por arquivos privados evitam montar árvores externas arbitrárias na aplicação. Descritores/no-follow limitam aquisição/publicação. | Exige Python POSIX e processo supervisionado adicional; Docker isoladamente não basta. |
| Mesmo comando padrão de geração | Coordenador da UI e CLI reutilizam `Documentation::Command`, sem lógicas independentes de geração. | Orquestração/entrega do frontend ainda diferem da CLI direta; fluxo optativo de projeto é separado. |
| Saídas gerenciadas e propriedade por hash | Resumos/blocos navegacionais podem atualizar enquanto conflitos com conteúdo manual são recusados. | Edição manual em saída própria exige conciliação explícita; não é merge geral de Markdown. |
| Journals e entrega recuperável | Versões anteriores, manifestos, hashes e entrega pendente permitem conclusão/rollback após interrupção. | Atomicidade por arquivo não é transação distribuída; evidências precisam permanecer disponíveis. |
| Recursos locais aprovados do Ollama | Manifesto e hashes de tags/skills delimitam modelo/contexto efetivos sem fallback de nuvem. | Localidade não comprova privacidade do rascunho publicado, correção, latência ou fine-tuning concluído. |
| Fatos de código limitados | Declarações, trechos exatos e fatos vinculados por schema limitam geração e preservam proveniência. | Cobertura parcial e validação heurística exigem revisão humana factual/de tradução. |

<!-- reading-section: decisions-1 -->
## Consequências de segurança e portabilidade

Acesso privado ao repositório, portas loopback, chave de gerenciamento e verificações de origem protegem limites diferentes. Não criam conjuntamente um sistema público de contas. Notas compartilhadas e evidências privadas de código/execução precisam de instalação restrita. Nunca incorpore caminhos específicos da máquina, chaves, URLs com credenciais ou envelopes confidenciais brutos à documentação.

Aliases de caixa são confirmados por identidade física, sem converter todos os caminhos para minúsculas. Isso preserva separação em filesystem sensível a caixa e acomoda aliases do macOS. Referências relativas são portáveis somente se a relação esperada entre checkouts e a identidade existirem no novo host; não tornam caminhos automaticamente portáveis. WSL2 é o ambiente necessário no Windows para o adapter POSIX, sem afirmação de aceitação Windows nesta revisão.

<!-- reading-section: decisions-2 -->
## Trabalho ainda futuro

Qualidade desejada da documentação por IA, cobertura útil mais ampla, avaliação semântica mais forte e qualquer campanha de treinamento/fine-tuning são trabalhos separados. Não se estabelece novo deployment público, arquitetura de identidade multiusuário ou recuperação universal. Relatórios datados permanecem históricos; esta explicação não apaga evidências nem autoriza mudanças de implementação.

Referências: [mapa de código da arquitetura](current-implementation.md#mapa-de-código), `backend/lib/documentation/command.rb`, `backend/lib/documentation/catalog_management.rb`, `tools/host_filesystem.py`, `frontend/lib/reading-position.ts` e `frontend/lib/note-location.ts`.
