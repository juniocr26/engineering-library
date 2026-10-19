# Perguntas de engenharia entre projetos

[FAQ técnica](index.md) · [English](../../en/faq/cross-project-boundaries.md)

Reavaliação em 2026-10-19 de `foundations.md` histórico em `5052a8515b30278abea5fb81b37647482c10ba18` e fontes atuais selecionadas. Os seis IDs estáveis pertencem a este documento. Comparam projetos independentes do portfólio, sem integração runtime ou atribuição de experiência profissional. Afirmações históricas de worker ausente foram superadas; nenhum teste de aplicação foi executado nesta revisão.

### Q001 — Como atomicidade, durabilidade e idempotência diferem?

**Resposta:** Cada garantia exige fronteira e modelo de falha. ENV Auditor substitui um arquivo atomicamente, sem transação do workspace ou fsync do diretório. INCR é atômico no Redis do URL Shortener, mas não confirma mapeamento Cassandra na mesma transação. O produtor atual do relay acopla fato e outbox no PostgreSQL; o consumidor acopla recibo e estoque, enquanto confirms e ACKs permanecem externos. Transporte repetido e um efeito local suportado coexistem porque o consumidor retém recibo de deduplicação. Persistência e transações SQL não comprovam por si só recuperação após perda de energia, backups ou entrega exactly-once entre sistemas.

Aprofundamento: Timeout significa rollback? Não. Escrita remota ou COMMIT podem ter ocorrido antes da resposta perdida. Retry precisa preservar identidade e reconciliar efeitos possíveis, sem presumir ausência de efeito.

### Q002 — O que uma arquitetura em camadas protege?

**Resposta:** Camadas localizam responsabilidades quando dependências seguem o contrato pretendido. Go separa handlers HTTP, casos de uso e codecs por interfaces focadas. Payment Lab mapeia entidades para DTOs explícitos dentro da transação, mas depende de repositório JPA concreto. O serviço URL Shortener também importa adaptadores concretos e helpers usam settings globais. Rust separa contratos de aplicação/persistência de SQLx e broker. Engineering Library separa metadados indexados de documentos em arquivos e layout do navegador. São graus e finalidades distintos, sem comprovação automática de inversão estrita de dependências.

Aprofundamento: Quando criar uma porta? Quando um caso concreto exige independência de protocolo, adaptadores alternativos ou testes controlados relevantes. CRUD genérico pode ocultar operações como aquisição de posse ou reconciliação de incerteza.

### Q003 — Como raciocinar sobre desempenho sem inventar benchmarks?

**Resposta:** Rastreie trabalho, alocação e bloqueio, identificando conclusões como análise. ENV Auditor ordena entradas e pode ter trabalho quadrático ao acrescentar muitas chaves ausentes. Go mantém buffers codificados/decodificados e codecs nativos; pixels não delimitam RSS total. Payment Lab materializa lista visível sem paginação. URL Shortener faz chamadas síncronas aos stores e alocação central de IDs. Engineering Library pagina metadados com tamanho fixo, mas processa e mede documentos separadamente. Isso indica alvos de medição, sem produzir throughput ou superioridade de linguagem.

Aprofundamento: O que registrar na medição? Tamanhos/distribuições de entradas, topologia, versões, hardware, concorrência, aquecimento, unidades, método, observações de correção e limites. Esta auditoria não mediu capacidade.

### Q004 — Quais mecanismos de segurança resolvem problemas diferentes?

**Resposta:** Validação verifica representação/invariantes; autenticação identifica; autorização permite ações; criptografia protege confidencialidade. Sintaxe de URL não impede destinos abusivos; Basic exige transporte protegido; ofuscação afim reversível não é criptografia. CORS do Payment Lab controla o navegador, enquanto regras explícitas negam rotas indisponíveis. Cookie assinado e token CSRF por leitor da Engineering Library isolam mutações de favoritos, sem controlar acesso a documentos privados. Permissões dos backups ENV Auditor reduzem acesso ordinário mantendo texto puro. Limites de pixels Go reduzem riscos específicos sem isolar código nativo.

Aprofundamento: Erro genérico ao cliente prova logs seguros? Não. O handler financeiro registra a exceção original. Examine cada fronteira de saída/armazenamento; valores secretos não foram inspecionados ou publicados aqui.

### Q005 — O que fakes, testes de integração e liveness estabelecem?

**Resposta:** Evidência vale para asserções e fixtures realmente exercitadas. Fakes verificam sequência e tradução HTTP/erros, excluindo stores/codecs reais. Testcontainers PostgreSQL verifica migrations e restrições selecionadas em banco isolado, sem provar restauração de volume existente. Health pode provar apenas serviço/boot; readiness do Payment Lab inclui banco, enquanto `/up` Rails não consulta catálogo. Definição de teste ou resultado histórico verde não constitui nova execução.

Aprofundamento: O que o próximo teste deve atingir? Invariante relevante ainda sem evidência em sua fronteira de falha, como confirmação de commit perdida ou posse vencida. Validação documental estrutural comprova links/navegação, sem verdade técnica, tradução ou layout real no navegador.

### Q006 — Como rollback e recuperação diferem?

**Resposta:** Rollback de artefato troca código; recuperação estabelece estado operacional e de dados válido. Go exige builds/codecs compatíveis. ENV Auditor precisa do backup original correto e comparação de edições posteriores. URL Shortener exige coerência entre contador, mapeamentos e configuração pública. Payment Lab precisa preservar Flyway e identidade do banco inicializado. Relay deve preservar eventos/recibos e reconciliar entrega incerta; worker e consumidor já existem. Favoritos da Library dependem de caminhos/âncoras lógicos, identidade do navegador e linhas PostgreSQL.

Aprofundamento: Migration down é backup? Não. Pode destruir dados/schema ou falhar quando restrições antigas já não valem. O down da nova migration de múltiplas ações do relay restaura unicidade por execução e recusa quando há várias ações retidas; descartar evidências para forçá-lo mudaria o problema de recuperação. Nenhum restore em produção, RTO ou RPO foi medido aqui.
