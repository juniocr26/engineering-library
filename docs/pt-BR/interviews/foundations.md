# Entrevista de fundamentos transversais

Comparações conceituais não implicam integração runtime. Fatos implementados, teoria e alternativas hipotéticas são separados explicitamente.

### Q001 — Intermediária: Como atomicidade, durabilidade e idempotência diferem nestes projetos?

**Resposta:** Teoria: atomicidade é visibilidade tudo-ou-nada numa fronteira; durabilidade é sobreviver após confirmação sob falhas definidas; idempotência trata efeitos repetidos. São independentes. ENV Auditor substitui alvo atomicamente, mas não transaciona vários alvos ou sincroniza diretório; plano estável pode estar semanticamente errado. INCR aloca ID atomicamente, mas não commita mapeamento Cassandra junto. Produtor futuro Rust precisa acoplar alteração/outbox na mesma transação local, enquanto broker permanece externo; worker não existe. São fronteiras diferentes, não alegações contraditórias.

Aprofundamento: Retry após timeout é seguro? Só conhecendo efeitos possíveis e contrato de idempotência/reconciliação. Escrita Cassandra pode existir após resposta perdida; RabbitMQ pode aceitar após timeout de confirm. Tratar timeout como rollback duplica efeitos. Aprofundamento: Volume persistente prova durabilidade/backup? Não. Sobrevive recriação comum, mas pode falhar com host ou propagar corrupção; backup precisa de evidência independente de recuperação. Projeto hipotético deve nomear fronteira e falhas em vez de declarar “confiável” sem qualificação.

### Q002 — Intermediária: O que arquitetura em camadas realmente protege?

**Resposta:** Teoria: fronteira localiza responsabilidades/representações; seu valor depende de direção de dependências e comportamento reais. Go separa HTTP, validação/contexto e codec com interfaces pequenas. Shortener separa rotas/controllers/serviço/adapters, mas serviço importa tipos concretos; não se pode presumir interfaces. Payment Lab mapeia entidades JPA a DTOs na transação, com repositório concreto no serviço. Rust mantém SQLx/Lapin na infraestrutura e define contratos focados de leitura/publicação/autoridade. Nenhum exige camadas vazias para reivindicar padrão.

Aprofundamento: DTO é segurança? Evita exposição acidental, mas não substitui autorização, validação ou logs. Aprofundamento: Quando adicionar port? Quando requisito estável não deve depender de protocolo ou testes/adapters precisam da fronteira. Abstração acrescenta tipos/mapeamento e pode esconder consistência. Compare custos: CRUD genérico esconderia snapshot versus autoridade Rust; contrato focado torna distinção revisável. Comparações são conceituais; projetos não chamam camadas uns dos outros.

### Q003 — Desafiadora: Como estimar desempenho sem inventar resultados de benchmark?

**Resposta:** Teoria: conte trabalho e crescimento de recursos, rotulando como análise. ENV Auditor percorre entradas, ordena diretórios e trata blocos; busca em lista pode ficar quadrática com muitas chaves ausentes. Go cresce com pixels/frames; alocações nativas e resultados do proxy excedem bytes codificados. Shortener inclui rede síncrona e contador serializado; Payment Lab materializa todas as entidades/DTOs visíveis; Rust materializa lote limitado por linhas e serializa admissão do publisher. Mecanismos indicam o que medir, não operações por segundo, capacidade ou superioridade de linguagem.

Aprofundamento: O que benchmark útil exige? Distribuição representativa, versões/topologia, hardware, concorrência, warmup, método, unidades/incerteza e observações separadas de latência/vazão/pico/correção. Benchmark não é autorizado nesta tarefa. Aprofundamento: Por que Big-O não basta? Parâmetros nativos, payload, caudas de rede e alocações simultâneas dominam constantes. Limite de 32 milhões permite estimar RGBA, mas não RSS total. Constraints, contagem de testes e réplicas Docker não geram gráficos de desempenho.

### Q004 — Introdutória: Quais mecanismos de segurança resolvem problemas diferentes?

**Resposta:** Teoria: validação verifica representação/invariantes; autenticação verifica identidade/origem; autorização permite ações; cifra protege sigilo; integridade detecta alterações indevidas. Sintaxe URL não previne abuso; Basic autentica credenciais e precisa de transporte protegido; ofuscação afim não é cifra. CORS controla navegador e não autoriza outros clientes. Negação fora de GETs do Payment Lab protege superfície atual, não pagamento futuro. Token de lease Rust protege autoridade futura no banco, não envio/sigilo. Backups privados em texto puro e limites Go reduzem riscos específicos sem sandbox.

Aprofundamento: Resposta sanitizada implica log sanitizado? Não. Payment Lab registra exceção; Rust mantém fontes; chaves/caminhos revelam metadados. Aprofundamento: Webhook assinado difere de TLS? TLS protege conexão; assinatura autentica payload definido por chave/protocolo, com requisitos de replay/corpo bruto. Não há webhook Stripe aqui. Controles hipotéticos são requisitos novos; verifique contratos antes de implementar, sem inferir criptografia da presença de hash no código.

### Q005 — Intermediária: Como fakes, integração e liveness limitam alegações?

**Resposta:** Teoria: evidência comprova assertivas na fronteira exercitada sob suas fixtures. Fakes provam ordem/tradução de erros excluindo bancos, locks ou codecs reais. PostgreSQL real verifica constraints e algumas sequências isoladas, não todo crash/queda. Resultado histórico pertence ao checkout/ambiente registrado; inventário e workflow não são nova execução aprovada. Navegador Go e corridas nativas exigem evidência diferente de unitários. Leases puros Rust não demonstram SQL ausente.

Aprofundamento: Health verde é readiness? Não sozinho. Health fixo Rust testa liveness; OpenAPI Shortener testa serviço HTTP; readiness Payment inclui banco, mas não conciliação/provedor. Aprofundamento: Como escolher próximo teste? Parta de invariante material e injete falha na fronteira: backup antes do replace, escrita remota incerta, owner antigo após espera ou DTO na transação. Teste deve falhar para o requisito, não espelhar implementação. Testes de aplicação não foram executados nesta revisão documental.

### Q006 — Desafiadora: Como implantação, rollback e recuperação diferem entre componentes stateless e stateful?

**Resposta:** Teoria: rollback de código troca artefatos; recuperação restaura estado operacional/dados válido. Go tem processamento efêmero e dependências nativas, exigindo builds antigos compatíveis sem banco de uploads. ENV Auditor grava arquivos/backups reais; recuperar pode exigir originais exatos preservando edições posteriores. Shortener coordena contador Redis, mapeamentos Cassandra e ofuscação. Payment preserva Flyway e volume inicializado. Rust preserva eventos/migrações/broker e ainda precisa do worker ausente antes de alegar recuperação de entrega.

Aprofundamento: Down desfaz tudo? Pode remover schema/dados em vez de recuperar estado original. Reaplicar schema não restaura linhas. Aprofundamento: O que procedimento produtivo revisável especifica? Compatibilidade de artefatos/schema, identidade de backup, restore testado, gatilhos de falha, rollback/correção e checks observáveis limitados. Reload/caches/health locais são fatos dev; não há rollout TLS/HA, restore ou RTO/RPO medido. Nomear projeto/volume não migra dados. São projetos independentes, não plataforma produtiva compartilhada.

