# url-shortener: dossiê de implementação

[English](../../en/architecture/url-shortener.md) | [Português brasileiro](url-shortener.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

## Contrato de criação e redirecionamento

`POST /urls` exige credenciais HTTP Basic e o campo JSON `url` como `HttpUrl` do Pydantic; sucesso retorna 201 com `short_code` e `short_url`. A rota chama um controller que delega a `UrlShortenerService`. O serviço aloca inteiro, codifica Base62, aplica ofuscação reversível, armazena `(id, original_url)` no Cassandra e constrói a URL pública com `SHORT_URL_BASE`. A validação verifica sintaxe HTTP/HTTPS; não busca o destino, não prova disponibilidade nem classifica abuso. URLs repetidas geram IDs diferentes, sem deduplicação.

`GET /{short_code}` é público. A desofuscação exige exatamente sete caracteres, recupera o inteiro, consulta Cassandra e retorna 301 com Location. Código inválido e mapeamento ausente viram 404. Erros de configuração viram 500; erros de adapters Redis/Cassandra viram 503 sanitizado. Redis não participa da resolução, portanto uma aplicação inicializada pode resolver enquanto Redis está indisponível. Cassandra é necessário nos dois caminhos. O startup cria sessão Cassandra e assegura a tabela; health contra OpenAPI não testa uma nova consulta de mapeamento ou incremento do contador.

A API e clientes são síncronos; declarar rota async não tornaria essas chamadas não bloqueantes. Redirecionamentos permanentes podem ser armazenados por navegadores/intermediários, desviando acessos posteriores da aplicação; uma futura análise de cliques não necessariamente veria todas as visitas. Não há expiração, destino editável, moderação de abuso, rate limit, chave de idempotência ou endpoint analítico. Alterar esses contratos exige projeto e testes, não inferências a partir do nome do domínio.

## Identidade, mapeamentos e consistência

Redis `SET NX` inicializa o contador compartilhado em início menos um; `INCR` aloca inteiro atomicamente no servidor. O lock do processo e `_initialized` evitam inicialização redundante no mesmo gerador; NX trata inicializadores concorrentes entre processos. Nem lock nem INCR criam transação com Cassandra. `urls_by_id` usa `id bigint PRIMARY KEY` e `original_url text`; inserts e consultas usam valores vinculados. A tabela corresponde à consulta por chave única, não a joins ou busca por destino.

Se alocação funciona e gravação falha, o ID é consumido. Timeout após Cassandra aceitar a escrita pode deixar mapeamento embora o cliente veja falha. Retry da criação aloca outro ID. Lacunas são inofensivas se IDs existentes nunca forem reutilizados, mas perder/reiniciar o contador com mapeamentos preservados pode sobrescrever uma linha, pois INSERT é upsert. AOF Redis `everysec` está configurado localmente; não é durabilidade sem perda nem backup coordenado dos dois bancos. Restauração exige piso do contador consistente com mapeamentos preservados e compatibilidade de alfabeto/chave. Não há coordenador automático de reparo/recuperação.

Compose/bootstrap tem três peers Cassandra e NetworkTopologyStrategy RF=3. São locais, não três domínios de falha de hosts independentes. Seeds auxiliam descoberta, não eleição de líder. `DCAwareRoundRobinPolicy` define preferência pelo DC local, mas o perfil não seleciona explicitamente consistência de leitura/gravação. RF sozinho não garante leitura após escrita. Leituras/gravações quorum são alternativa hipotética que troca acknowledgements e disponibilidade por maior sobreposição; gravações condicionais tratariam outra invariante e acrescentariam coordenação.

Codificar inteiro usa divmod sucessivo por 62; a ofuscação de sete caracteres opera módulo `62**7`. SHA-256 deriva parâmetros afins, `gcd(a, módulo)=1` permite inversa modular e padding dá largura fixa no alfabeto padrão. O contador pode exceder esse espaço; o serviço então retorna erro de configuração após consumir um ID. Alfabetos personalizados têm uma preocupação adicional de compatibilidade não resolvida: o padding é `0` literal, que pode não representar o dígito zero. Mudanças arbitrárias de alfabeto são não verificadas, não migrações transparentes suportadas.

## Autenticação, ofuscação e transporte

HTTP Basic verifica usuário e senha configurados com `secrets.compare_digest`. Credenciais inválidas retornam 401 com desafio Basic; configuração ausente retorna 500. Credenciais Basic são codificação, não cifra de transporte. A aplicação local não configura terminação TLS. A rota pública de redirect é intencionalmente não autenticada e possuir código curto não é verificação de autorização. CORS ou rede Compose privada não substituiriam autenticação da API.

A transformação afim é ofuscação reversível, mesmo usando SHA-256 para derivar parâmetros. Não é cifra autenticada, hash de senha ou fronteira de sigilo. Pares conhecidos de entrada/saída e sua estrutura algébrica tornam inadequadas alegações de segurança criptográfica. Alterar chave ou alfabeto muda a decodificação de links existentes; não há prefixo de versão ou consulta de migração. Código aleatório armazenado evitaria acoplamento a uma chave global, mas exigiria colisões e outra chave de consulta; cifra autenticada introduziria outros requisitos de tamanho e gestão de chaves. Nenhuma está implementada.

A sintaxe do destino é validada, mas não há allowlist ou reputação. A aplicação redireciona em vez de buscar URLs, portanto a criação atual não é fetch de URL no servidor; um futuro preview/fetch criaria novas preocupações de SSRF. Evite logs de credenciais e destinos sensíveis completos. Arquivos reais de ambiente e conteúdo dos bancos não foram lidos. Lacunas incluem implantação TLS, controle de abuso, rotação de credenciais e migração testada de código/chave.

## Implantação e recuperação coordenada

Lifespan cria recursos Redis/Cassandra, assegura a tabela e expõe adapters no estado da aplicação. Cassandra é inicializado antes de servir; o contador Redis é inicializado sob demanda. `finally` fecha Cassandra e Redis; falha ao criar conexão Cassandra encerra o cluster. O comando Compose padrão usa Uvicorn com reload para desenvolvimento local. Três nós Cassandra, armazenamento AOF Redis e bind mounts são topologia de estudo, não release HA produtivo verificado.

A revisão de atualização/rollback precisa preservar dados e contrato do espaço de códigos. Nunca reinicie Redis independentemente dos mapeamentos Cassandra nem presuma que recriar contêineres recria credenciais em volumes inicializados. Backup/restauração precisam coordenar ambos os bancos e conservar a configuração de ofuscação; persistência de volume não é backup. São requisitos de procedimento, não ensaio de restore realizado aqui. Não há ferramenta de recuperação coordenada, pipeline de releases ou RTO/RPO medido. Não há ciclo versionado de edição de destino.

Testes fake isolam codificação, alocação, ordem do serviço e mapeamento de erros HTTP sem provar consistência, autenticação ou failover reais do cluster. Instruções Docker/Postman existentes não foram executadas nesta revisão. OpenAPI acessível prova startup HTTP, não prontidão das dependências na requisição. Custos potenciais são chamadas de rede síncronas, serialização Redis, trabalho de rede/réplicas Cassandra e capacidade de threads do cliente; topologia não fornece gráfico de vazão. Lacunas incluem injeção real de falhas, recuperação de perda do contador, carga concorrente, escolha de política quorum e ensaios de implantação/rollback.

## Evidência de apoio

- [api/contracts](../../../../url-shortener/docs/pt-BR/api/contracts.md)
- [database/identity-and-consistency](../../../../url-shortener/docs/pt-BR/database/identity-and-consistency.md)
- [security/identity-and-transport](../../../../url-shortener/docs/pt-BR/security/identity-and-transport.md)
- [operations/deployment-and-recovery](../../../../url-shortener/docs/pt-BR/operations/deployment-and-recovery.md)
- [Interview / Entrevista](../interviews/url-shortener.md)
