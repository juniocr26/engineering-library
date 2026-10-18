# URL Shortener — Guia de Estudo para Entrevista Técnica


[English](../../en/technical-interview/study-guide.md) | [Português brasileiro](study-guide.md)

Paths e comandos citados são relativos ao projeto url-shortener. O contador é inicializado de forma lazy na primeira geração de ID, não no lifespan. O lifespan cria tabela Cassandra com CREATE TABLE IF NOT EXISTS; o bootstrap Compose também pode criar/alterar roles e keyspace. Startup é operação de escrita e não deve ser usado como verificação inofensiva sobre dados existentes. O schema não define TTL; não há deduplicação nem LWT de proteção contra ID reutilizado. Erros de configuração podem gerar 500, distintos de falhas de infraestrutura 503; payload inválido gera 422. Não há nível QUORUM explicitamente configurado no perfil atual; a discussão abaixo sobre QUORUM é hipotética.

### Objetivo deste documento

Este documento é um material de estudo para explicar e defender tecnicamente as decisões do projeto url-shortener.

Ele não deve ser decorado palavra por palavra.

O objetivo é entender suficientemente bem cada decisão para conseguir explicar:

- 		qual problema precisava ser resolvido;

- 		por que determinada tecnologia foi escolhida;

- 		quais alternativas existiam;

- 		quais trade-offs foram aceitos;

- 		quais limitações continuam existindo;

- 		o que mudaria em um ambiente de produção real.

## 1. VISÃO GERAL

### Pergunta: Explique o projeto para mim.

Resposta possível:

O projeto é um serviço de encurtamento de URLs que eu desenvolvi principalmente como projeto de Backend Engineering e System Design.

Ele tem dois fluxos principais.

O primeiro é a criação de uma URL curta. O cliente envia uma URL original para um endpoint autenticado. A aplicação valida a URL, usa Redis para gerar um ID inteiro único de forma atômica, converte esse ID para Base62, aplica uma camada reversível de obfuscação para gerar um código público de sete caracteres e persiste a associação entre o ID e a URL original no Cassandra.

O segundo fluxo é a resolução. O cliente acessa publicamente o código curto. A aplicação desfaz a obfuscação, decodifica o Base62 para recuperar o ID inteiro, consulta o Cassandra por esse ID e retorna um 301 Moved Permanently apontando para a URL original.

A aplicação foi desenvolvida com Python e FastAPI e o ambiente é Docker-first. A infraestrutura local possui Redis e um cluster Cassandra com três nós.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** O caminho separa responsabilidades testáveis: HTTP valida/autentica, serviço coordena alocação/gravação e adapters encapsulam protocolos. Resolução reverte representação em vez de buscar texto público. Evita chave de código armazenada, mas acopla links ao alfabeto/chave. Aprofundamento: É ecossistema de microsserviços? Não; Redis/Cassandra são dependências desta aplicação independente, sem parceiro de portfólio verificado.

## 2. POR QUE UM URL SHORTENER?

### Pergunta: Por que você escolheu implementar um URL shortener?

Resposta possível:

Porque é um problema aparentemente simples na interface, mas que permite explorar vários problemas interessantes de backend e sistemas distribuídos.

A API em si pode ser pequena, mas rapidamente surgem decisões sobre geração de identificadores únicos, concorrência, persistência, representação compacta de IDs, distribuição dos dados, durabilidade, disponibilidade, caching HTTP e comportamento de redirects.

Eu queria justamente um projeto pequeno o suficiente para conseguir explicar o fluxo inteiro, mas que tivesse decisões de arquitetura reais para estudar.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Contrato externo pequeno ainda expõe falha distribuída: alocação pode funcionar sem mapeamento, e timeout pode esconder escrita bem-sucedida. Isso permite explicar fronteiras sem inventar escala. Banco SQL único reduziria complexidade operacional/transacional em produto pequeno. Aprofundamento: O que foi demonstrado e não apenas pretendido? Caminhos de código e assertivas fake demonstram mecanismos locais; volume produtivo, HA e recuperação não foram comprovados.

## 3. ARQUITETURA EM ALTO NÍVEL

### Pergunta: Quais são os principais componentes?

Resposta possível:

Os principais componentes são:

- 		FastAPI como aplicação HTTP;

- 		Redis como gerador atômico de IDs;

- 		Cassandra como armazenamento persistente das URLs;

- 		Base62 para representar IDs de forma compacta;

- 		uma transformação reversível para não expor diretamente a sequência Base62;

- 		Docker e Docker Compose para reproduzir o ambiente;

- 		Pytest para testes automatizados.

No Cassandra eu uso três nós locais. É importante dizer que Cassandra é peer-to-peer. O cassandra-1 é configurado como seed para descoberta do cluster, mas ele não é leader ou master.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Cada componente fornece garantia diferente: Pydantic valida sintaxe, Redis serializa incremento, Cassandra armazena consulta por chave e função afim fornece reversibilidade. Nenhum autoriza redirects ou transaciona bancos juntos. Banco único poderia combinar identidade/mapeamento atomicamente. Aprofundamento: Componentes distribuídos provam resiliência distribuída? Não; três peers locais compartilham host e alocador não tem failover.

## 4. POR QUE PYTHON?

### Pergunta: Por que Python?

Resposta possível:

Python foi uma escolha deliberada de aprendizado.

Minha experiência principal de backend não depende de Python, então eu queria desenvolver o mesmo raciocínio de engenharia em outro ecossistema e aprender a linguagem através de um projeto real.

Para esse serviço, Python também funciona bem porque a aplicação HTTP não precisa executar processamento computacional pesado. Grande parte do trabalho é coordenar validação, Redis, Cassandra e respostas HTTP.

Eu também queria separar duas coisas: aprender a sintaxe e o framework de uma linguagem nova e, ao mesmo tempo, aplicar conceitos de engenharia que são transferíveis entre stacks.

### Pergunta: Por que FastAPI?

Resposta possível:

FastAPI fornece uma base relativamente enxuta para APIs, integração com validação de dados e documentação OpenAPI.

Eu queria que o framework resolvesse a camada HTTP sem esconder o fluxo principal da aplicação.

Por isso, mesmo usando FastAPI, organizei o código para que a route não concentrasse toda a lógica.

O projeto usa uma separação como:

```text
route
→ controller
→ service
→ infrastructure
```

A ideia é deixar cada responsabilidade identificável sem criar um número desnecessário de abstrações.

### Pergunta: Isso é Clean Architecture?

Resposta possível:

Eu não apresentaria o projeto como uma implementação completa e rígida de Clean Architecture.

Existem princípios semelhantes, principalmente separação de responsabilidades e isolamento de infraestrutura, mas o objetivo não foi implementar todas as camadas formais de Clean Architecture.

Eu preferi manter uma arquitetura pequena e explicável.

Se eu criasse interfaces, repositories, use cases e várias outras abstrações sem uma necessidade concreta, poderia aumentar a complexidade sem melhorar o projeto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Rotas/clientes atuais são síncronos; chamadas bloqueantes ocupam capacidade de workers apesar do suporte async FastAPI. Camadas não invertem dependências automaticamente: serviço importa adapters concretos. Ports/drivers async seriam mudanças hipotéticas com custos de contrato/lifecycle. Aprofundamento: Apenas trocar def por async def melhora? Não; I/O síncrono em handler async pode bloquear event loop sem offload deliberado.

## 5. FLUXO DO POST

### Pergunta: O que acontece quando alguém cria uma URL?

Resposta possível:

O fluxo é:

```text
POST /urls
→ Basic Authentication
→ validação da URL
→ Redis INCR
→ ID inteiro
→ Base62
→ obfuscação reversível
→ código público de 7 caracteres
→ persistência no Cassandra
→ 201 Created
```

O endpoint de criação é protegido porque criar dados modifica o estado do sistema.

Cada POST válido gera um novo ID. O projeto não implementa deduplicação da URL original e também não utiliza TTL para expirar mappings.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Resposta é construída após store_url; não há transação com incremento anterior. Requisições repetidas criam códigos distintos e recuperação de timeout não tem identidade durável da solicitação. Registro chave/resultado implementaria idempotência com regras concorrentes/conflito/expiração. Aprofundamento: Criação 503 pode deixar mapeamento? Sim, se Cassandra aceitou antes de perder resposta; falha não prova ausência de efeito.

## 6. POR QUE REDIS?

### Pergunta: Qual é a responsabilidade do Redis?

Resposta possível:

No projeto, Redis não é o banco das URLs e também não é simplesmente um cache.

A principal responsabilidade dele é gerar IDs inteiros únicos por meio do comando atômico INCR.

Isso é importante porque duas requisições concorrentes não podem receber o mesmo ID.

### Pergunta: Por que não fazer SELECT MAX(id) + 1 no Cassandra?

Resposta possível:

Porque isso introduziria uma condição de corrida.

Duas requisições poderiam observar o mesmo valor máximo antes de qualquer uma persistir o próximo registro.

Além disso, Cassandra não foi escolhido para funcionar como um contador global transacional.

Com Redis INCR, a operação de incremento é atômica e o problema de concorrência fica concentrado em uma primitiva apropriada.

### Pergunta: Redis está funcionando como uma fila?

Resposta possível:

Não.

Esse é um ponto importante.

Redis possui estruturas que podem ser usadas para outros casos, inclusive mensageria, mas neste projeto não existe uma fila para geração de IDs.

O que garante a geração concorrente é a atomicidade do comando INCR.

Eu não preciso enfileirar manualmente as requisições para obter essa propriedade.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** INCR serializa uma chave Redis, não garante unicidade durável em toda recuperação. Gerador conserva inicialização em cache; apagar chave pode fazer INCR reiniciar sem piso configurado. Identidade gerada pelo banco evitaria recuperação separada, mudando exercício. Aprofundamento: Lock Python garante entre processos? Não; NX/INCR no servidor coordenam operações saudáveis.

## 7. INICIALIZAÇÃO DO CONTADOR

### Pergunta: Como o contador Redis é inicializado?

Resposta possível:

O primeiro ID pretendido é:

```text
62^4 = 14.776.336
```

Então o contador inicialmente recebe:

```text
14.776.335
```

O primeiro INCR retorna:

```text
14.776.336
```

A inicialização utiliza SET ... NX.

Isso é importante porque NX significa que o valor só será definido se a chave ainda não existir.

Assim, se o Redis já possui um contador persistido, uma reinicialização da aplicação não volta o contador para o início.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Lock local evita inicialização duplicada no gerador; NX impede processos de sobrescrever contador existente. Inicialização lazy significa que constructor/lifespan não provam primeiro incremento. Check no startup falharia antes, mas acrescentaria dependência e não coordenaria restauração. Aprofundamento: Novo URL_ID_START eleva contador existente? Não; NX mantém estado existente.

## 8. POR QUE COMEÇAR EM 62^4?

### Pergunta: Por que o contador não começa em zero?

Resposta possível:

Foi uma decisão relacionada à representação Base62.

62^4 é representado como 10000 em Base62 com o alfabeto utilizado pelo projeto.

Eu queria trabalhar desde o início com uma faixa que já produzisse uma representação com determinado comprimento antes da transformação para o código público.

Mas isso não é uma exigência fundamental de um URL shortener. É uma decisão do projeto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Piso configurado escolhe faixa de representação; sete caracteres vêm da ofuscação/padding, não do início. Começar alto consome domínio finito e não aumenta aleatoriedade/segurança. Contador desde zero ou código aleatório teriam outros custos de leitura/colisão. Aprofundamento: E em 62**7? Ofuscação rejeita entrada fora do domínio após alocar; não há expansão/versão automática.

## 9. REDIS E DURABILIDADE

### Pergunta: O que acontece se Redis reiniciar?

Resposta possível:

No ambiente local eu habilitei AOF, ou Append Only File.

O AOF registra operações de escrita para que Redis consiga reconstruir seu estado após uma reinicialização.

A configuração usa appendfsync everysec.

Mas é importante não confundir isso com alta disponibilidade.

AOF melhora durabilidade. Ele não fornece failover.

### Pergunta: Então o Redis é altamente disponível?

Resposta possível:

Não.

A implementação atual possui um Redis e não implementa Redis Sentinel, Redis Cluster ou outro mecanismo de failover.

Portanto, se o Redis estiver indisponível, a criação de novas URLs fica indisponível e a aplicação retorna uma falha de infraestrutura.

Isso é uma limitação conhecida do projeto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Everysec troca custo de flush por janela potencial de perda recente. Linha Cassandra preservada com contador regressivo é pior que lacuna porque INSERT sobrescreve ID reutilizado. Replicação/Sentinel melhoraria disponibilidade, mas consistência de recuperação ainda exige projeto. Aprofundamento: Fsync mais forte resolve tudo? Não evita reset manual, restore incoerente ou perda total de storage.

## 10. UM DOS PRINCIPAIS TRADE-OFFS DO PROJETO

### Pergunta: Existe risco de inconsistência entre Redis e Cassandra?

Resposta possível:

Sim, e esse é um dos trade-offs mais importantes.

O Redis gera o ID antes da persistência no Cassandra.

Imagine:

```text
Redis INCR → ID 100
Cassandra → grava ID 100
```

Agora imagine que Redis reconheça determinados incrementos, mas depois perca parte desse estado persistido, enquanto Cassandra mantém as URLs correspondentes.

Redis poderia eventualmente reutilizar um ID que Cassandra já possui.

Isso seria um problema de correctness, não apenas uma lacuna estética na sequência.

AOF reduz o risco de perda de estado, mas não elimina todas as possibilidades e não substitui uma arquitetura de alta disponibilidade.

Em uma implementação de produção eu precisaria revisar a estratégia de geração de IDs e suas garantias de recuperação.

### Pergunta: E se Redis gerar um ID e Cassandra falhar antes de persistir?

Resposta possível:

Nesse caso pode existir um gap na sequência.

Por exemplo:

```text
Redis gera 100
Cassandra falha
próxima requisição:
Redis gera 101
```

O ID 100 pode nunca ser utilizado.

Isso é aceitável para esse projeto porque os IDs precisam ser únicos, mas não precisam formar uma sequência sem buracos.

Duplicidade é um problema. Gap não é.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Serviço encapsula falhas sem compensação, commit distribuído ou reconciliação. Recuperar IDs falhos é inseguro com aceitação incerta; tolerar lacunas é mais simples que adivinhar. Transação em banco único simplificaria correção. Aprofundamento: Por que timeout não é rollback? Servidor pode concluir e perder confirmação. Retry seguro considera efeito original possível, não o infere apenas do 503.

## 11. POR QUE BASE62?

### Pergunta: Por que Base62?

Resposta possível:

Porque Base62 permite representar um número inteiro utilizando 62 símbolos:

```text
0-9
A-Z
a-z
```

Isso produz representações mais compactas que a representação decimal e utiliza caracteres adequados para URLs sem precisar de símbolos adicionais.

No projeto o alfabeto é:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

### Pergunta: Base62 é criptografia?

Resposta possível:

Não.

Base62 é encoding, ou uma representação numérica em outra base.

É reversível por definição:

```text
integer
→ Base62 encode
→ Base62 decode
→ mesmo integer
```

Ele não oferece confidencialidade.

### Pergunta: É Base64?

Resposta possível:

Não. É Base62.

Base64 utiliza 64 símbolos e normalmente inclui caracteres adicionais. Para esse código público, eu utilizo 62 símbolos alfanuméricos.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Encoding divide por 62 repetidamente; decoding acumula valor*62+dígito. Comprimento cresce logaritmicamente; formato público fixa largura por outra transformação. Alfabeto exige 62 caracteres únicos. Mapa substituiria alphabet.index, mas códigos são curtos e não há gargalo medido. Aprofundamento: Qualquer alfabeto é seguro ponta a ponta? Não comprovado: padding usa 0 literal em vez do zero configurado.

## 12. POR QUE OBFUSCAÇÃO?

### Pergunta: Se você já tem Base62, por que existe outra transformação?

Resposta possível:

Porque Base62 sozinho preservaria a natureza sequencial dos IDs.

Se os IDs fossem:

```text
14.776.336
14.776.337
14.776.338
```

as representações Base62 também seguiriam uma progressão previsível.

Eu queria evitar expor diretamente essa sequência nos códigos públicos.

Por isso existe uma transformação reversível antes de publicar o código.

### Pergunta: Essa obfuscação é criptograficamente segura?

Resposta possível:

Não.

Eu deliberadamente chamo isso de obfuscação, e não de encryption.

Ela serve para esconder a sequência óbvia dos IDs e produzir códigos públicos de sete caracteres, mas não deve ser tratada como uma proteção criptográfica forte.

Se o requisito fosse segurança criptográfica real, eu escolheria uma construção criptográfica apropriada e revisada para esse domínio, em vez de uma transformação própria.

### Pergunta: Qual é o tamanho do espaço de códigos?

Resposta possível:

Como o código público possui sete posições e cada posição pode assumir 62 valores:

```text
62^7 = 3.521.614.606.208
```

Então o domínio possui aproximadamente 3,52 trilhões de combinações possíveis.

Isso representa o tamanho matemático do espaço de códigos, não significa que o sistema atual foi testado ou dimensionado para armazenar trilhões de URLs.

Essa distinção é importante.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Mapa é (a*x+b) módulo 62**7. gcd(a,módulo)=1 permite inversa e correspondência única no domínio com configuração fixa. SHA-256 deriva a/b, mas função afim não vira cifra autenticada. Códigos aleatórios evitam acoplamento reversível, exigindo colisões. Aprofundamento: Links sobrevivem rotação arbitrária? Não; inversa nova produz outros IDs sem versão/migração.

## 13. POR QUE CASSANDRA?

### Pergunta: Por que você escolheu Cassandra?

Resposta possível:

Eu escolhi Cassandra principalmente porque o projeto também possui um objetivo explícito de estudo de sistemas distribuídos.

O padrão principal de acesso é muito simples:

```text
ID conhecido
→ lookup por primary key
→ URL original
```

Isso combina com modelagem orientada à consulta.

Cassandra também me permitiu estudar replicação, arquitetura peer-to-peer, seed nodes, coordinator nodes e outros conceitos de armazenamento distribuído.

Mas eu não diria que Cassandra é obrigatório para um URL shortener pequeno.

Para uma aplicação pequena real, PostgreSQL provavelmente seria operacionalmente muito mais simples.

### Pergunta: Então Cassandra não é overengineering?

Resposta possível:

Se eu alegasse que uma aplicação pequena precisa obrigatoriamente de Cassandra, provavelmente seria.

Mas o projeto tem um objetivo explícito de System Design e aprendizado de persistência distribuída.

Por isso eu separo duas perguntas:

```text
Qual seria a solução mais simples para uma aplicação pequena?
vs.
Que tecnologia permite explorar os problemas de engenharia que quero estudar?
```

Cassandra foi escolhido principalmente pela segunda pergunta.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Tabela atende ID conhecido, mas Cassandra acrescenta nós, replicação/autenticação e tuning além do HTTP. Stack mostra projeto de estudo, não exigência por carga medida. SQL com ID gerado combinaria alocação/mapeamento. Aprofundamento: Que acesso exige outra tabela? Busca/deduplicação por URL original não usa eficientemente schema por ID sem modelo próprio.

## 14. MODELAGEM NO CASSANDRA

### Pergunta: Como os dados são modelados?

Resposta possível:

O modelo principal é intencionalmente simples:

```text
CREATE TABLE urls_by_id (
    id bigint PRIMARY KEY,
    original_url text
);
```

O acesso é:

```text
ID inteiro
→ original_url
```

O sistema não precisa executar joins para resolver uma URL.

### Pergunta: Por que o código público não é a primary key?

Resposta possível:

Porque o código público pode ser revertido deterministicamente.

O fluxo é:

```text
short_code
→ desfaz obfuscação
→ Base62 decode
→ integer ID
→ Cassandra lookup
```

Assim, o ID inteiro permanece como chave do modelo persistente e o código público funciona como uma representação transformada desse identificador.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Partition key bigint atende igualdade; parâmetros transportam ID/URL sem interpolar valores do usuário. INSERT é upsert, não check condicional, sem TTL ou versão do código. Simplicidade perde busca por URL/histórico. Aprofundamento: Por que upsert ameaça após perder alocador? ID reutilizado muda destino de código antigo apesar de não existir rota de edição.

## 15. CASSANDRA É LEADER/FOLLOWER?

### Pergunta: Qual nó Cassandra é o leader?

Resposta possível:

Nenhum deles é um leader permanente.

Cassandra possui arquitetura peer-to-peer.

No ambiente local existem:

```text
cassandra-1
cassandra-2
cassandra-3
```

O cassandra-1 é um seed node, mas seed não significa leader.

O seed ajuda os nós a descobrirem o cluster durante bootstrap.

Um nó que recebe uma operação pode atuar como coordinator daquela requisição, mas coordinator também não significa leader permanente.

### Pergunta: Então o que é um coordinator?

Resposta possível:

É o nó que recebe determinada requisição e coordena a operação com as réplicas necessárias.

Outra requisição pode ser coordenada por outro nó.

Por isso eu separaria:

```text
seed → descoberta do cluster
coordinator → coordenação de uma requisição específica
replica → nó que possui uma cópia daquele dado
leader → conceito que não descreve a arquitetura Cassandra desse projeto
```

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Driver escolhe coordenadores pela política; replicação define donos de partição. cassandra-1 seed muda descoberta, não liderança ou roteamento universal. Analogia primary/replica SQL pode enganar. Aprofundamento: Seed saudável prova dados de réplicas acessíveis? Não; consistência, alcance e topologia definem fronteira. Sequências reais de outage não foram testadas nesta revisão.

## 16. REPLICATION FACTOR

### Pergunta: Qual replication factor você usa?

Resposta possível:

O keyspace utiliza NetworkTopologyStrategy com replication factor 3 em datacenter1.

Como o ambiente possui três nós Cassandra locais, cada row é replicada para os três nós desse datacenter.

### Pergunta: Ter três réplicas significa que o sistema é automaticamente altamente disponível?

Resposta possível:

Não necessariamente.

Replicação é uma parte da arquitetura de disponibilidade, mas não é sinônimo de uma solução completa de alta disponibilidade.

Ainda existem decisões sobre consistency level, disponibilidade dos clientes, topology, deployment, failure detection e operação do cluster.

Além disso, esse projeto executa três containers Cassandra na mesma máquina durante desenvolvimento. Isso é excelente para estudar comportamento de cluster, mas não representa isolamento físico real de falhas.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Cópias seguem estratégia do datacenter; consistência define acknowledgements. Réplicas melhoram algumas tolerâncias, mas acrescentam storage/repair/operação. Mesmo host não prova resiliência entre zonas. Aprofundamento: RF=3 garante leitura após escrita? Não; perfil deixa consistência implícita e RF sozinho não define promessa ao cliente.

## 17. CONSISTENCY LEVEL

### Pergunta: Qual consistency level você escolheria em produção?

Resposta possível:

Eu não daria uma resposta automática sem definir os requisitos.

Com replication factor 3, uma possibilidade seria trabalhar com QUORUM, mas isso tem custo de disponibilidade e latência.

O ponto importante é que consistency level é uma decisão por operação no Cassandra.

Eu primeiro definiria qual garantia de leitura e escrita o produto precisa e quais falhas precisa tolerar.

Depois escolheria o nível apropriado.

Eu evitaria dizer simplesmente que "QUORUM é melhor", porque ele otimiza determinadas garantias aceitando outros custos.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Sobreposição quorum é teoria útil, exigindo conjuntos/políticas precisos, sem eliminar automaticamente conflitos concorrentes. Mais acknowledgements reduzem disponibilidade se faltam réplicas. Código escolhe roteamento DC sem contrato explícito de consistência. Aprofundamento: O que documentar hoje? RF/topologia e política ausente, não QUORUM inventado ou latência medida.

## 18. FLUXO DO GET

### Pergunta: O que acontece quando alguém acessa uma URL curta?

Resposta possível:

O fluxo é:

```text
GET /{short_code}
→ validação
→ desfaz obfuscação
→ Base62 decode
→ ID inteiro
→ Cassandra lookup
→ URL original
→ 301 Moved Permanently
```

Diferentemente da criação, o endpoint GET é público.

Isso faz sentido porque a finalidade de um short link é poder ser compartilhado e resolvido sem exigir credenciais do usuário final.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Tamanho/caracteres são validados na transformação inversa; Cassandra fornece destino. Redis não participa, mas mudar ofuscação quebra consultas antigas. Código armazenado moveria compatibilidade aos dados. Aprofundamento: Código válido mas ausente? Compartilha 404 com malformado; configuração/adapter continuam 500/503.

## 19. POR QUE 301?

### Pergunta: Por que você escolheu 301 Moved Permanently?

Resposta possível:

Porque o modelo do projeto considera o mapping permanente.

Um 301 comunica ao cliente que o redirecionamento é permanente e pode ser cacheado por browsers, proxies e outros componentes.

Isso também pode reduzir requisições futuras ao backend quando o cliente reutiliza o redirect armazenado em cache.

### Pergunta: Qual é o trade-off do 301?

Resposta possível:

A possibilidade de caching é ao mesmo tempo benefício e custo.

Depois que um cliente armazena:

```text
abc1234 → example.com
```

alterar esse mapping no servidor não garante que aquele cliente volte a consultar o backend.

Por isso o projeto trata os mappings como efetivamente imutáveis.

Se edição frequente do destino fosse requisito, eu reconsideraria o uso de 301.

### Pergunta: Por que não 302?

Resposta possível:

302 representa um redirect temporário e tende a manter o servidor mais envolvido nas resoluções futuras.

Isso poderia ser interessante se o destino pudesse mudar ou se eu precisasse observar cada acesso no backend para analytics, por exemplo.

No projeto eu priorizei a semântica de mapping permanente.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Resposta expressa permanência HTTP; clientes guardam Location e pulam consultas futuras. Ajuda resolução repetida, mas reduz visibilidade e torna mudança futura surpreendente. Política 302/307 teria outros efeitos de cache/método e exigiria contrato. Aprofundamento: Logs contam todo clique? Não; redirect cacheado pode não chegar ao servidor, exigindo limites analíticos explícitos.

## 20. POR QUE NÃO EXISTE REDIS CACHE NO GET?

### Pergunta: Já que você usa Redis, por que não guardar URLs populares nele?

Resposta possível:

Porque Redis tem uma responsabilidade específica no projeto atual: geração atômica de IDs.

Eu poderia adicionar caching das resoluções, mas isso criaria novas decisões sobre cache invalidation, eviction, memória, cache miss, consistência e comportamento quando Redis falha.

Como o objetivo era manter o projeto pequeno e cada tecnologia com responsabilidade clara, eu não adicionei cache apenas para dizer que existe cache.

Se medições mostrassem que Cassandra se tornou um gargalo de leitura, aí caching seria uma evolução justificável.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Cache de mapeamento imutável poderia consultar por código/ID, mas misses usam Cassandra e 404 cacheado exige frescor após criação. Limite de memória, eviction e fallback importam mesmo sem editar destino. Não existe. Aprofundamento: Redis alocador justifica guardar mapeamentos também? É outra responsabilidade/dependência de recuperação; exige requisito, não cliente disponível.

## 21. POR QUE NÃO KAFKA OU RABBITMQ?

### Pergunta: Por que não usar uma fila para criação das URLs?

Resposta possível:

Porque a criação atual precisa retornar o código imediatamente e o fluxo é pequeno.

Adicionar um broker criaria producer, consumer, retries, entrega de mensagens, idempotência, observabilidade e consistência eventual sem resolver uma necessidade atual.

Eu usaria mensageria se surgisse uma responsabilidade assíncrona real, como analytics, auditoria, processamento posterior ou integração desacoplada.

Não adicionaria Kafka ou RabbitMQ apenas para tornar o diagrama mais complexo.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Enfileirar persistência mudaria 201: responder antes do mapeamento cria link não resolvível sem outro contrato durável. Broker exige duplicatas/recuperação de consumidor. Aprofundamento: Analytics pode ser desacoplado? Hipoteticamente, com latência/loss/replay definidos. Seria fluxo novo; Rust Relay independente não é parceiro produtor/consumidor atual.

## 22. POR QUE NÃO MICROSERVICES?

### Pergunta: Por que você fez um único serviço?

Resposta possível:

Porque o domínio atual é pequeno e não existem bounded contexts ou necessidades operacionais que justifiquem separar deployment e comunicação entre múltiplos serviços.

Um monólito pequeno e modular é mais fácil de executar, testar e explicar.

Microservices introduziriam comunicação distribuída, observabilidade, deployment independente, retries e falhas parciais sem uma necessidade concreta.

Eu prefiro introduzir complexidade quando existe um problema que justifica essa complexidade.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Uma fronteira de processo facilita criação síncrona/erros. Separar serviços HTTP de alocação/storage acrescentaria timeout/deploy sem corrigir atomicidade Redis/Cassandra. Código modular testa sem deploy independente. Aprofundamento: O que justificaria separar? Requisito verificado de escala, responsabilidade ou isolamento com contrato/medições; não há tal integração runtime do portfólio.

## 23. BASIC AUTH

### Pergunta: Por que Basic Authentication?

Resposta possível:

Porque o objetivo da autenticação nesse projeto é simples: proteger o endpoint de criação sem transformar autenticação em outro domínio de estudo.

O endpoint GET continua público.

Basic Auth é simples para demonstrar essa separação.

Em um produto real multiusuário eu provavelmente avaliaria uma solução diferente, como tokens ou integração com um provedor de identidade, dependendo dos requisitos.

### Pergunta: Basic Auth é seguro?

Resposta possível:

As credenciais em Basic Auth são apenas codificadas para transporte; isso não substitui TLS.

Em produção eu exigiria HTTPS.

No projeto também existe cuidado para não versionar as credenciais reais e a comparação utiliza secrets.compare_digest.

Mas eu não apresentaria Basic Auth como a arquitetura de identidade completa de um produto real.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Implementação compara bytes UTF-8 com secrets.compare_digest e desafia Basic inválido. Credenciais ausentes produzem erro de configuração. Evita igualdade direta comum, mas não limita tentativas ou gerencia usuários. Aprofundamento: GET autentica dono do destino? Não; resolve mapeamento compartilhável. Autorização de produto/moderação são futuros requisitos separados.

## 24. GERENCIAMENTO DE SEGREDOS

### Pergunta: Onde ficam as senhas?

Resposta possível:

O repositório possui .env.example como contrato público de configuração.

Os valores reais ficam no .env local, que é ignorado pelo Git.

Segredos como senha Redis, senha Cassandra, credenciais Basic Auth e a chave de obfuscação não devem ser commitados.

Em produção eu substituiria o .env local por um mecanismo adequado de secret management da infraestrutura utilizada.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Arquivos ignorados evitam inclusão comum, não são storage cifrado ou rotação. Chave também define compatibilidade: perdê-la/mudá-la quebra decoding. Secret manager exigiria controle/versionamento, não apenas mover valores. Aprofundamento: Segredos reais foram inspecionados? Não. Apenas código/metadados/documentação seguros; valores e dados não foram lidos.

## 25. CONNECTION LIFECYCLE

### Pergunta: Você abre uma conexão com Redis e Cassandra a cada request?

Resposta possível:

Não.

Os recursos de infraestrutura são criados durante o lifespan da aplicação FastAPI e reutilizados.

Isso inclui Redis, o gerador de IDs e a sessão/cluster Cassandra.

No shutdown, esses recursos são fechados.

Criar uma nova sessão Cassandra para cada requisição, por exemplo, seria desnecessariamente caro.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Cluster/sessão Cassandra precedem serviço; falha de conexão encerra cluster. finally fecha Cassandra e Redis inicializados. Reuso reduz setup, mas acopla lifecycle à disponibilidade de startup. Contador Redis segue lazy. Aprofundamento: Startup health é somente leitura? Não; tabela recebe DDL. Privilégio mínimo produtivo poderia mover schema para migrações; é hipotético.

## 26. POR QUE DOCKER-FIRST?

### Pergunta: Por que Docker?

Resposta possível:

Eu queria que o ambiente fosse reproduzível e que o projeto não dependesse de configurar manualmente Python, Redis e três instâncias Cassandra na máquina do desenvolvedor.

Por isso o fluxo de desenvolvimento é Docker-first.

O host precisa basicamente do Docker, Docker Compose, editor e Git.

A aplicação e as dependências de runtime executam nos containers.

### Pergunta: Por que três Cassandra containers se todos estão na mesma máquina?

Resposta possível:

Porque o objetivo local é estudar a topologia lógica do Cassandra: descoberta, seed, peers, replicação e comportamento de cluster.

Isso não simula independência física de falhas.

Se a máquina host falhar, os três nós falham juntos.

Então eu não apresentaria esses três containers como uma implantação de produção altamente disponível.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Compose controla nomes, dependências, binds e rede bridge. Aplicação usa DNS de contêiner; portas loopback servem host. Reload/binds ajudam desenvolvimento, não rollout imutável. Aprofundamento: Rebuild muda credenciais inicializadas? Não automaticamente; identidade retida exige cuidado. Produção precisa de artefatos, TLS, recuperação/readiness além do local.

## 27. HEALTH CHECKS E STARTUP

### Pergunta: Como você garante que os serviços estejam prontos?

Resposta possível:

O Docker Compose utiliza health checks e dependências entre os serviços.

Eu preferi isso a adicionar sleeps arbitrários, como "espere 30 segundos e tente conectar".

Tempo não é uma garantia de readiness.

Um serviço pode iniciar em cinco segundos hoje e cinquenta segundos em outra máquina.

Health checks tornam essa dependência mais explícita.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Checks condicionam startup, não congelam saúde posterior. Probe app busca OpenAPI, sem novo incremento/lookup. Readiness melhor incluiria probes limitadas sem alocar ID para testar saúde. Aprofundamento: Redis é opcional no startup Compose porque GET não usa? Não; dependências de startup e caminho de requisição são contratos distintos.

## 28. TESTES

### Pergunta: Como o projeto é testado?

Resposta possível:

A suíte cobre diferentes partes do comportamento da aplicação, incluindo autenticação HTTP, redirects, pipeline de criação e resolução, geração de IDs Redis, comportamento do store Cassandra, Base62 e obfuscação reversível.

A suíte padrão usa fakes para Redis e Cassandra em vários testes.

Isso deixa os testes determinísticos e rápidos.

### Pergunta: Então seus testes provam que o cluster Cassandra funciona?

Resposta possível:

Não.

Esse seria um exagero.

Os testes com fakes validam o contrato da aplicação contra aquelas interfaces e comportamentos simulados.

O comportamento real da infraestrutura é validado separadamente através do ambiente Docker e verificações de integração.

Eu não chamaria um teste com fake de teste de integração real com Cassandra.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Fakes modelam respostas/erros para status, round-trip e ordem com baixo custo. Não reproduzem retries/defaults/replicação. Testes reais exigem bancos descartáveis/falhas controladas. Aprofundamento: Suíte no código é aprovação nova? Não; nenhum teste de aplicação executou aqui. Separe histórico datado, inventário atual e lacunas.

## 29. POR QUE FAKES?

### Pergunta: Por que não subir Cassandra para cada teste?

Resposta possível:

Porque nem todo teste precisa pagar o custo de infraestrutura real.

Para testar encoding, validação, autenticação ou determinadas regras de service, subir três Cassandra nodes não acrescenta valor proporcional.

Eu separo a pergunta:

```text
Quero validar minha lógica?
ou
Quero validar a integração real com a infraestrutura?
```

Os dois tipos de teste têm valor, mas resolvem problemas diferentes.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Injeção em lifecycle/rotas permite geradores/stores determinísticos. Prova ausência de gravação após input inválido ou simula falha, não autenticação de rede/atomicidade real. Aprofundamento: O que torna integração relevante? Assertiva de contrato em infraestrutura isolada com limpeza controlada, sem apagar fixtures em banco existente.

## 30. TRATAMENTO DE FALHAS

### Pergunta: O que acontece se Cassandra estiver indisponível?

Resposta possível:

Falhas de persistência ou lookup são traduzidas para 503 Service Unavailable.

Eu não quero retornar detalhes internos como hostname, stack trace ou credenciais para o cliente.

### Pergunta: E se Redis estiver indisponível?

Resposta possível:

A criação de URLs depende da geração de ID pelo Redis, então o POST não pode continuar corretamente e retorna uma falha de serviço.

O GET, por outro lado, não depende do Redis na arquitetura atual. Ele resolve o código e consulta Cassandra.

Isso mostra que os dois caminhos possuem dependências diferentes.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Tradução esconde dependências do cliente e conserva causas. Nem toda categoria pede retry: configuração precisa reparo; efeitos incertos precisam reconciliação. Sanitizar resposta não sanitiza logs. Aprofundamento: 404 em outage Cassandra seria adequado? Não; descreveria evidência indisponível como ausência. 503 distingue impossibilidade de consulta de não encontrado.

## 31. DISPONIBILIDADE DO READ PATH E WRITE PATH

### Pergunta: Uma falha no Redis derruba o serviço inteiro?

Resposta possível:

Não necessariamente.

Ela derruba o caminho de criação:

```text
POST
→ Redis necessário
```

Mas o caminho de resolução é:

```text
GET
→ Cassandra
```

Portanto, se Redis falhar mas Cassandra e a aplicação continuarem disponíveis, links existentes ainda podem ser resolvidos.

É importante analisar disponibilidade por operação, e não apenas dizer que "o sistema está disponível" ou "indisponível".

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Disponibilidade depende da operação/fase. GET não incrementa Redis; ambas usam Cassandra; cold start inicializa schema e Compose espera dependências. Um rótulo uptime esconde diferenças. Aprofundamento: 301 cacheado funciona sem app? Alguns clientes reutilizam destino, mas é comportamento cliente, não failover garantido ou disponibilidade medida.

## 32. O QUE ACONTECE COM URL INVÁLIDA?

### Pergunta: Como a entrada é validada?

Resposta possível:

A aplicação utiliza a validação do FastAPI/Pydantic para o contrato HTTP.

Entradas inválidas são rejeitadas antes de seguir pelo fluxo de geração de ID e persistência.

Isso impede gastar recursos de infraestrutura com uma entrada que já sabemos ser inválida.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** HttpUrl aceita HTTP/HTTPS sintaticamente válido, mesmo inacessível/abusivo. Aplicação grava/redireciona sem buscar. Reputação/allowlist acrescentaria falsos positivos/frescor/operação; futuro fetch preview criaria fronteira SSRF. Aprofundamento: Rejeitar URL malformada impede link malicioso? Não; sintaxe não prova reputação, posse ou conteúdo seguro.

## 33. CÓDIGO CURTO INVÁLIDO

### Pergunta: O que acontece com um short code inválido?

Resposta possível:

Códigos malformados ou que não correspondem a um registro conhecido resultam em 404 Not Found.

Eu não exponho detalhes sobre se a falha ocorreu durante Base62, obfuscação ou lookup.

Para o consumidor da API, o recurso solicitado não existe.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Serviço reverte sete caracteres/valida alfabeto antes do lookup. Identidade inválida/ausente compartilha contrato público. Configuração não é erro do usuário; outage não é ausência. Aprofundamento: Esconder motivo do 404 impede enumeração? Reduz detalhe, mas mapeamentos públicos continuam descobríveis; sem rate limit/sigilo e função afim não é cifra segura.

## 34. DEDUPLICAÇÃO

### Pergunta: O que acontece se eu enviar a mesma URL duas vezes?

Resposta possível:

O projeto gera dois IDs diferentes.

Não existe deduplicação por URL original.

Isso foi uma decisão deliberada para manter o write path simples.

Implementar deduplicação criaria outro padrão de acesso, porque eu precisaria consultar por URL original ou manter algum índice/mapping adicional.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Deduplicar exige normalização: grafias diferentes podem ter semântica diferente e query params importam. Criações concorrentes precisam de política atômica, não check-then-insert. Aprofundamento: Índice secundário sozinho daria idempotência? Não define arbitragem, conflito ou replay estável. POST repetido atual continua alocação distinta.

## 35. TTL E EXPIRAÇÃO

### Pergunta: As URLs expiram?

Resposta possível:

Não.

A implementação atual não possui TTL.

Os mappings são considerados permanentes.

Adicionar expiração exigiria novas decisões sobre armazenamento, limpeza, comportamento HTTP depois da expiração e possivelmente caching.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** TTL removeria linhas sem invalidar redirects permanentes cacheados. Introduz resposta expirado/ausente, relógio/retenção/limpeza. Redirect temporário poderia combinar melhor. Aprofundamento: Contador deveria expirar junto? Não; reutilizar IDs é perigoso com códigos/caches sobreviventes. Lifecycle de identidade é separado de retenção.

## 36. ESCALABILIDADE

### Pergunta: Esse projeto suporta bilhões de requests?

Resposta possível:

Eu não afirmaria isso porque não existe benchmark que demonstre essa escala.

O projeto utiliza componentes e padrões que permitem discutir escalabilidade, como geração atômica de IDs e Cassandra, mas arquitetura potencialmente escalável e capacidade medida são coisas diferentes.

Para afirmar determinada quantidade de requests por segundo eu precisaria realizar testes de carga, definir hardware, topologia, consistency levels e observar latência e throughput.

### Pergunta: Então por que o README menciona high-throughput?

Resposta possível:

Porque o projeto explora decisões relacionadas a padrões de acesso de alto volume, especialmente armazenamento distribuído e geração concorrente de IDs.

Mas eu faria questão de distinguir objetivo arquitetural de benchmark comprovado.

Eu não tenho uma métrica de throughput de produção para alegar.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Espaço de códigos, capacidade de storage e vazão são grandezas distintas. Primeiro é aritmética; outros dependem de dados/topologia/consistência/carga. Chamadas síncronas/contador indicam o que medir. Aprofundamento: Como relatar carga futura? Versões/hardware/input/concorrência, distribuição de latência/vazão/erros/limites, sem escala universal ou testes unitários como capacidade.

## 37. GARGALOS

### Pergunta: Qual é um possível gargalo da arquitetura?

Resposta possível:

Um ponto evidente é o Redis único usado para geração global dos IDs.

Ele centraliza a sequência.

Embora INCR seja eficiente, o desenho cria uma dependência central para todos os writes e também um ponto único de indisponibilidade na implementação atual.

Se o volume ou requisito de disponibilidade exigisse outra solução, eu avaliaria uma estratégia distribuída de geração de IDs.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Alocador acrescenta rede síncrona por criação/estado central. Cassandra e threads também podem dominar; ranking não foi medido. Blocos de IDs reduziriam calls, mas desperdiçam faixas em crash/complicam ownership. Aprofundamento: GET compartilha gargalo? Não usa Redis; criação/resolução exigem medições separadas.

## 38. ALTERNATIVAS PARA GERAÇÃO DE ID

### Pergunta: O que poderia substituir Redis INCR?

Resposta possível:

Existem várias possibilidades dependendo dos requisitos:

- 		UUID;

- 		UUIDv7;

- 		Snowflake-like IDs;

- 		blocos de IDs pré-alocados;

- 		um serviço dedicado de geração de IDs;

- 		identificadores aleatórios com tratamento de colisão.

Eu escolhi Redis INCR porque queria uma solução simples, determinística e fácil de raciocinar sobre concorrência.

Mas a escolha possui o custo de centralizar a geração dos IDs.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Compare colisão, tamanho, estado central, ordem/recuperação. UUID/aleatório muda pressupostos; Snowflake exige nó/relógio; blocos reduzem tráfego com lacunas. Aprofundamento: ID alternativo resolve retries HTTP? Não; idempotência exige identidade lógica estável/resultados/conflitos, distinta de ID novo único.

## 39. POR QUE NÃO UUID?

### Pergunta: Por que não simplesmente usar UUID?

Resposta possível:

UUID resolveria parte do problema de geração distribuída sem um contador global.

Por outro lado, eu queria estudar explicitamente a transformação:

```text
integer
→ Base62
→ código público
```

e o comportamento de um gerador atômico centralizado.

Então Redis INCR foi uma escolha ligada ao objetivo do projeto.

Se os requisitos fossem outros, UUID poderia ser uma solução perfeitamente válida.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** UUID ocupa mais bits que domínio de sete dígitos; formato exige redesenho. Truncar cria colisão; hash não garante unicidade. Código aleatório armazenado manteria tamanho com insert condicional/retry. Aprofundamento: UUIDv7 ordena exatamente? Ajuda representação temporal, não garante ordem global de negócio/aceitação.

## 40. OBSERVABILIDADE

### Pergunta: O projeto possui observabilidade de produção?

Resposta possível:

Não em nível de produção.

Eu não afirmaria que existe uma stack completa de métricas, tracing e alerting porque isso não está implementado.

Uma evolução de produção poderia incluir métricas de latência, taxa de erro, disponibilidade de Redis/Cassandra, tracing distribuído e alertas.

Isso é uma limitação conhecida, não algo que eu esconderia em uma entrevista.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Telemetria útil separaria criação/resolução, validação/configuração/storage, timeouts/risco do contador. Labels não devem ter cardinalidade ilimitada de código/URL ou credenciais. Trace ID não prova commit. Aprofundamento: Probe OpenAPI é sistema de métricas? Não; sinal de serving limitado. Dashboards/alertas/tracing/retenção são hipotéticos.

## 41. CI/CD

### Pergunta: O projeto possui uma pipeline completa de deployment?

Resposta possível:

Eu responderia apenas com o que estiver efetivamente presente no repositório naquele momento.

O ambiente local e os testes são reproduzíveis via Docker, mas eu não apresentaria isso automaticamente como uma estratégia completa de CI/CD ou deployment em produção.

Dockerização e CI/CD são problemas relacionados, mas diferentes.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Compose local usa reload/binds, lifecycle dev. Release precisaria artefatos imutáveis/configuração compatível, schema/bootstrap e recuperação. Aprofundamento: Configuração automatizada de teste é deploy aprovado? Não; workflow descreve intenção, resultados exigem execução datada. Não houve CI remoto/release/rede e nomes/URLs GitHub do proprietário não foram presumidos.

## 42. POR QUE NÃO KUBERNETES?

### Pergunta: Por que não Kubernetes?

Resposta possível:

Porque não existe atualmente um problema de orquestração que justifique introduzi-lo.

Docker Compose atende o objetivo de desenvolvimento local e estudo da arquitetura.

Adicionar Kubernetes apenas para ter Kubernetes no currículo aumentaria muito a superfície operacional do projeto sem resolver uma necessidade concreta.

Se eu quisesse estudar deployment distribuído e Kubernetes como um objetivo separado, poderia fazer isso como uma evolução explícita.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Orquestrador agenda/reinicia, não repara contador regressivo ou consistência Cassandra. Stateful exige storage/domínios/backup/credenciais/recuperação. Kubernetes poderia esconder correção sob complexidade. Aprofundamento: O que justificaria? Objetivo explícito de orquestração/requisitos testados, não três contêineres ou rótulo production-ready.

## 43. POR QUE NÃO POSTGRESQL?

### Pergunta: Se você começasse uma startup hoje com esse produto, usaria Cassandra?

Resposta possível:

Não necessariamente.

Para um produto pequeno começando do zero, PostgreSQL provavelmente seria uma opção muito forte por simplicidade operacional, maturidade e flexibilidade.

Eu começaria pelos requisitos reais e pela escala observada.

Cassandra fez sentido neste projeto porque eu queria estudar armazenamento distribuído e porque o padrão de acesso é compatível com lookup por chave.

Isso não significa que Cassandra seja automaticamente melhor que PostgreSQL.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Transação relacional única inseriria mapeamento/ID gerado, evitando dual write. Índices dão lookup/unicidade e deploy simples. Troca estudo de peers/alocador separado; sem benchmark comparativo. Aprofundamento: Reescrever portfólio agora? Não no escopo documental; explique alternativa/requisitos antes de autorizar código.

## 44. SQL VS NOSQL

### Pergunta: Então NoSQL é melhor para URL shortener?

Resposta possível:

Eu evitaria essa generalização.

O modelo de um URL shortener pode ser muito simples e funcionar muito bem tanto em bancos relacionais quanto em diferentes bancos NoSQL.

A escolha depende de escala, padrão de acesso, consistência, operação, equipe e infraestrutura.

Neste projeto Cassandra é uma decisão de arquitetura e aprendizado, não uma afirmação de que SQL seria incapaz de resolver o problema.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Constraints/transações relacionais e tabelas distribuídas por consulta têm custos distintos, sem vencedor universal. Mapeamento atual é chave/valor; deduplicação/analytics mudaria acesso. Aprofundamento: NoSQL é mais rápido automaticamente? Não; hardware/replicação/consistência/carga/implementação determinam medições. Explique chave primária/falhas entre bancos, não capacidade por tecnologia.

## 45. O QUE VOCÊ MUDARIA PARA PRODUÇÃO?

### Pergunta: O que você mudaria antes de colocar isso em produção?

Resposta possível:

Eu começaria pelos requisitos reais de produção em vez de simplesmente adicionar tecnologias.

Alguns pontos que eu avaliaria seriam:

- 		estratégia de alta disponibilidade do gerador de IDs;

- 		risco de recuperação do contador Redis;

- 		consistency levels do Cassandra;

- 		deployment dos Cassandra nodes em domínios de falha independentes;

- 		TLS;

- 		autenticação apropriada ao produto;

- 		secret management;

- 		rate limiting;

- 		observabilidade;

- 		métricas e alertas;

- 		testes de carga;

- 		testes reais de integração;

- 		estratégia de backup e recuperação;

- 		CI/CD;

- 		comportamento de abuse prevention para URLs maliciosas.

Mas eu não diria que todos são obrigatoriamente necessários sem conhecer os requisitos do produto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Comece por nunca reutilizar ID mapeado, preservar decoding e distinguir indisponível/ausente. Defina durabilidade/disponibilidade/abuso. Caches/nós antes disso complicam recuperar. Aprofundamento: Quais checks completos? Comportamento código/fakes e topologia local documentada; perda/restore/failover independente/TLS/rollback são lacunas.

## 46. MAIOR DECISÃO DE ARQUITETURA

### Pergunta: Qual decisão do projeto você considera mais interessante?

Resposta possível:

Uma das mais interessantes é separar geração de identidade e persistência.

Redis possui a responsabilidade de gerar IDs atômicos.

Cassandra possui a responsabilidade de armazenar o mapping persistente.

Isso torna as responsabilidades claras, mas também cria um problema distribuído: não existe uma transação única envolvendo Redis e Cassandra.

Essa separação me obrigou a pensar sobre falha parcial, gaps na sequência, perda de estado e possível reutilização de IDs.

Esse tipo de trade-off foi justamente uma das razões de eu construir o projeto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Ordem mostra trade-off: Redis aloca, Cassandra mapeia, sem transação local comum. É interpretação de estudo, não avaliação histórica inventada. Aprofundamento: Qual invariante principal? ID não pode sobrescrever outro mapeamento após recuperação. Lacuna é aceitável; reutilização não. Estado perdido viola isso apesar de incrementos atômicos saudáveis.

## 47. MAIOR LIMITAÇÃO

### Pergunta: Qual é a maior limitação que você reconhece?

Resposta possível:

Uma das mais importantes é a dependência de um Redis único para geração de IDs.

AOF melhora durabilidade local, mas não fornece alta disponibilidade.

Além disso, existe um risco de correctness se Redis perder estado confirmado enquanto Cassandra preservar mappings associados a IDs maiores.

Eu prefiro reconhecer explicitamente essa limitação a dizer que o problema está resolvido apenas porque existe persistência AOF.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Risco operacional é integridade: contador regressivo alcança IDs preservados. Upserts comuns não têm guarda de recuperação. Persistência forte, gravação condicional ou banco único são alternativas com custos. Aprofundamento: Três réplicas protegem alocador? Não; preservam mapeamentos, não Redis, inclusive linhas que alocador perdido sobrescreve.

## 48. O QUE VOCÊ APRENDEU?

### Pergunta: Qual foi o principal aprendizado?

Resposta possível:

Um dos maiores aprendizados foi separar conceitos que parecem semelhantes.

Por exemplo:

```text
persistência ≠ alta disponibilidade
replicação ≠ backup
seed node ≠ leader
coordinator ≠ leader
Base62 ≠ criptografia
obfuscação ≠ criptografia
atomicidade ≠ fila
Docker containers ≠ infraestrutura de produção
testes com fake ≠ teste real de integração
arquitetura escalável ≠ throughput comprovado
```

O projeto me ajudou muito mais a entender os limites de cada mecanismo do que simplesmente aprender a configurar Redis ou Cassandra.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Defenda distinções seguindo requisição e alterando uma hipótese: perda Redis, Cassandra indisponível, chave mudada ou cache. Conceitos ganham sentido no código. Aprofundamento: O que é limite e não lição produtiva? Capacidade sem medição/recuperação não executada são limites de estudo; não invente incidentes/resultado profissional.

## 49. PERGUNTA COMPORTAMENTAL: POR QUE UMA STACK NOVA?

### Pergunta: Você já dominava Python e Cassandra antes desse projeto?

Resposta possível:

Eu evitaria fingir experiência que não tenho.

Eu desenvolvi esse projeto justamente para ampliar minha experiência prática nessas tecnologias e estudar os conceitos por trás delas.

Minha preocupação foi não apenas conseguir fazer o código funcionar, mas entender as decisões: lifecycle de conexões, concorrência, persistência, replicação, falhas e testes.

Em uma entrevista eu separaria claramente experiência profissional anterior de experiência hands-on adquirida neste projeto.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Boa resposta demonstra código sem alegar deploy profissional: localize INCR/NX, explique inversa, store/erros. Primeira pessoa sugerida é ensaio, não currículo comprovado. Aprofundamento: E tráfego/resultados de produção? Informe ausência de evidência/medições; discuta validação hipotética, não fabrique conquista.

## 50. COMO VOCÊ ABORDOU UMA TECNOLOGIA NOVA?

### Pergunta: Como você trabalha quando precisa aprender uma tecnologia nova?

Resposta possível:

Eu tento começar pelo problema, e não pela sintaxe.

Primeiro entendo qual responsabilidade aquela tecnologia precisa assumir e quais garantias eu espero dela.

Depois estudo como o ecossistema implementa isso.

Foi assim, por exemplo, com Cassandra. Mais importante que conseguir conectar o driver foi entender que ele é peer-to-peer, o que é um seed, o que é um coordinator, como replication factor funciona e quais garantias eu realmente tenho.

Isso ajuda a transferir conhecimento entre stacks diferentes.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Separe linguagem/invariantes. Sintaxe Python difere, mas ambiguidade, recursos e atomicidade permanecem. Use fixtures para representação/ordem antes de driver real. Aprofundamento: Ler framework prova domínio? Não; trace cleanup/falha e limites fake. Não alegue cronologia pessoal não registrada.

## 51. POR QUE A ORGANIZAÇÃO ROUTE → CONTROLLER → SERVICE?

### Pergunta: FastAPI permite colocar tudo na route. Por que você não fez isso?

Resposta possível:

Porque funcionar não é o único critério.

Eu queria separar a responsabilidade HTTP da orquestração e das regras do serviço.

A route define o contrato HTTP e dependências como autenticação.

O controller faz a ponte entre HTTP e aplicação.

O service concentra o fluxo de criação e resolução.

A infraestrutura encapsula Redis e Cassandra.

Ao mesmo tempo, eu evitei criar camadas adicionais que não tinham responsabilidade real.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Controller traduz categorias para HTTP; serviço mantém transformação/ordem. Adapters encapsulam protocolo sem escolher redirect. Isso separa resposta/persistência. Aprofundamento: Serviço é totalmente independente? Não; importa adapters/settings concretos. Port ajudaria, exigindo contrato estável de comportamento, não métodos genéricos sem garantias.

## 52. SOLID

### Pergunta: Você aplicou SOLID?

Resposta possível:

Eu diria que utilizei princípios de separação de responsabilidades e dependências de forma pragmática, mas evitaria afirmar que o projeto é uma demonstração formal de todos os cinco princípios SOLID.

Por exemplo, Redis ID generation e Cassandra persistence possuem responsabilidades diferentes e são mantidos separados.

Isso melhora testabilidade e compreensão.

Mas eu não criei interfaces e hierarquias apenas para poder dizer que apliquei SOLID.

Para mim, o princípio precisa resolver um problema de design, e não virar uma checklist.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Responsabilidade única aparece em alocação/mapeamento, mas separação cria falhas; nomes de princípios não provam melhoria. Substituição nos testes ajuda mesmo com imports concretos. Aprofundamento: O que seria excesso? CRUD/hierarquias/serviços/interfaces que apenas encaminham sem fronteira significativa. Explique invariante/erro antes da sigla.

## 53. POR QUE NÃO REPOSITORY PATTERN EM TUDO?

### Pergunta: Por que não usar Repository Pattern formal?

Resposta possível:

Porque eu não queria adicionar abstração sem necessidade.

O Cassandra URL store já encapsula a responsabilidade de persistência necessária para esse projeto.

Se existissem múltiplas implementações, domínio mais complexo ou necessidade real de desacoplamento adicional, uma abstração formal poderia fazer sentido.

Eu prefiro que a arquitetura cresça conforme surgem responsabilidades reais.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Store concreto possui inicialização/insert/lookup parametrizados. Abstração útil preservaria upsert/ausência/erro; save/find genérico pode esconder retry. Aprofundamento: SQL seria substituição direta? Só com identidade/falha/lifecycle equivalentes ou serviço alterado deliberadamente. Gerar identidade transacional redesenha orquestração, não troca cosmética.

## 54. DEPENDENCY INJECTION

### Pergunta: Como você torna o código testável?

Resposta possível:

Uma parte importante é evitar que a lógica crie infraestrutura arbitrariamente no meio da execução.

Os recursos são construídos no lifecycle da aplicação e as dependências podem ser substituídas nos testes.

Isso permite usar fakes para Redis e Cassandra e testar comportamento sem subir infraestrutura real para cada caso.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Estado guarda recursos do lifespan; dependências fornecem serviço sem novos clusters por request. Reuso reduz setup/exige cleanup/startup. Aprofundamento: Injeção exige container? Não; construção explícita/funções fornecem fronteira. Fakes devem refletir falhas, não apenas métodos iguais escondendo incerteza.

## 55. ERROS INTERNOS

### Pergunta: Por que não retornar a exceção do Cassandra para o cliente?

Resposta possível:

Porque detalhes de infraestrutura não pertencem ao contrato público e podem inclusive revelar informações sensíveis.

Para o cliente, o que importa é que uma dependência necessária está indisponível.

Internamente, em um sistema de produção, eu registraria os detalhes necessários para diagnóstico através de logs e observabilidade.

Externamente, retorno um erro controlado.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Exceções tipadas conservam causas; controllers retornam texto controlado. 500/503/404 implicam ações diferentes. Logger produtivo precisa redigir fontes/destinos. Aprofundamento: Por que não registrar toda cadeia? Pode conter hosts/credenciais/consultas; saída cliente segura não protege diagnóstico irrestrito.

## 56. URL SHORTENER E CACHE

### Pergunta: Um URL shortener normalmente é read-heavy. Como você escalaria os reads?

Resposta possível:

Eu começaria medindo.

Se Cassandra começasse a receber volume suficiente para justificar caching, eu poderia introduzir Redis ou outra camada de cache para mappings populares.

Também poderia explorar caching HTTP e infraestrutura de edge dependendo dos requisitos.

Mas adicionar cache cria novos problemas, principalmente invalidation e consistência.

Como os mappings atuais são imutáveis, esse caso seria particularmente favorável para caching.

Mesmo assim, eu adicionaria baseado em necessidade ou objetivo explícito de estudo, não automaticamente.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** GET usa lookup após inversa. Cache reduz chamadas, não garante correção com criação/expiração/edição. 301 já cacheia no cliente com controle diferente. Aprofundamento: O que medir antes de Redis cache? Latência/erros/hits representativos, memória/fallback explícitos. Não houve medições aqui.

## 57. 301 E ESCALABILIDADE

### Pergunta: O 301 pode ajudar na carga do backend?

Resposta possível:

Pode.

Como clientes podem armazenar permanentemente o redirect, acessos posteriores podem não chegar ao backend.

Isso potencialmente reduz carga.

Mas eu não contaria com isso como garantia de capacidade, porque comportamento de cache varia e caches podem ser limpos ou ignorados.

Eu trataria como uma propriedade útil da semântica HTTP, não como substituto de capacity planning.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Primeiro resolve exige serviço/Cassandra; posteriores podem usar cache. Isso desloca tráfego, não prova vazão máxima; varia por cliente. Aprofundamento: Como afeta teste de outage? Sucesso cacheado esconde falha; separe cliente sem cache de repetido. Nenhum experimento executou aqui.

## 58. E SE O DESTINO PRECISAR MUDAR?

### Pergunta: Como você implementaria URLs editáveis?

Resposta possível:

Primeiro eu reconsideraria a semântica de redirect.

Com 301, clientes podem manter o destino antigo em cache mesmo depois da alteração no servidor.

Se edição fosse requisito central, eu provavelmente avaliaria um redirect temporário apropriado e modelaria atualização do mapping explicitamente.

Isso mostra como uma mudança de requisito funcional pode alterar uma decisão HTTP e a arquitetura.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Sem API de edição, upsert ainda muda mapeamento com ID reutilizado. Edição futura exige ownership/autorização/consistência/cache, não só UPDATE. Aprofundamento: 302 invalida 301 já cacheado? Não garante para clientes sem contato; links antigos exigem migração/compatibilidade explícita.

## 59. ANALYTICS

### Pergunta: Como você adicionaria analytics de cliques?

Resposta possível:

Eu evitaria tornar o redirect síncrono dependente de um processamento pesado de analytics.

Uma possibilidade seria registrar ou publicar um evento e processá-lo assincronamente.

Nesse momento um broker poderia começar a fazer sentido.

Mas eu precisaria definir primeiro os requisitos: perda de eventos é aceitável? Precisamos de exactly-once? Qual volume? Qual latência?

Eu não escolheria Kafka ou RabbitMQ antes dessas respostas.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Log registra apenas requests recebidos, não 301 cacheado. Pipeline poderia persistir cliques observados com identidade/retry/deduplicação/loss. Aprofundamento: Rust já fornece isso? Não; independente sem worker/consumidor composto. Usá-lo exigiria integração nova verificada, não inferência por workspace.

## 60. RATE LIMITING

### Pergunta: Você adicionaria rate limiting?

Resposta possível:

Para uma API pública real, provavelmente avaliaria rate limiting principalmente no endpoint de criação, além de mecanismos contra abuso.

Mas isso não está implementado atualmente, então eu apresentaria como evolução de produção, não como capacidade existente.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Limites de criação/resolução têm propósitos distintos: escrita reduz abuso/storage; lookup não deve quebrar compartilhamento. Identidade/IP/contadores/fallback afetam justiça. Aprofundamento: Redis indisponível faria limiter abrir/fechar? Decisão nova com custo de segurança/disponibilidade; Redis é apenas alocador, sem limiter testado.

## 61. CAP

### Pergunta: Como CAP theorem se relaciona com Cassandra?

Resposta possível:

Eu teria cuidado para não reduzir CAP a "escolher duas letras".

Em presença de uma partição de rede, um sistema distribuído precisa tomar decisões entre disponibilidade e consistência das operações.

Cassandra oferece consistência configurável através de replication factor e consistency levels.

Então a discussão concreta seria sobre quais leituras e escritas precisam de quais garantias e como o sistema deve se comportar durante falhas.

Eu evitaria responder simplesmente "Cassandra é AP" sem explicar a configuração e o comportamento das operações.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** CAP trata partição sob definições precisas, não velocidade normal. Cassandra pode esperar réplicas/falhar; código não escolhe níveis explícitos. Aprofundamento: Por que rótulo AP permanente é insuficiente? Esconde política/operação/falhas. Redis impõe dependência separada; classificar Cassandra não descreve disponibilidade ponta a ponta.

## 62. QUORUM

### Pergunta: O que significa quorum com RF=3?

Resposta possível:

Para replication factor 3, quorum corresponde a:

```text
floor(RF / 2) + 1
= floor(3 / 2) + 1
= 2
```

Então um quorum envolve duas réplicas.

Mas saber essa conta não basta. Eu ainda preciso decidir os consistency levels das operações e entender o efeito em latência, disponibilidade e consistência.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Mesmo conjunto R=2/W=2 sobrepõe N=3. Ajuda raciocínio sem definir timestamps/conflitos/linearizabilidade. Mais réplicas trocam latência/disponibilidade por acknowledgements. Aprofundamento: Onde QUORUM está configurado? Não explicitamente no perfil; separe aritmética hipotética do comportamento/default implementado.

## 63. BACKUP VS REPLICATION

### Pergunta: Se Cassandra tem RF=3, você precisa de backup?

Resposta possível:

Sim, se os requisitos exigirem recuperação de dados.

Replicação protege contra determinadas falhas de nós.

Ela não protege automaticamente contra exclusão lógica, corrupção propagada, erro de aplicação ou outras situações em que todas as réplicas recebem o mesmo estado indesejado.

Replicação e backup resolvem problemas diferentes.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Backup útil recupera independentemente das réplicas e testa ponto de recuperação. Alocador/ofuscação precisam concordar com linhas restauradas. Replicar upsert ruim conserva erro. Aprofundamento: Copiar data dir vivo é backup seguro demonstrado? Não; exige procedimento consistente/restore. Revisão não leu dados, criou backup ou mediu RTO/RPO.

## 64. AOF VS BACKUP

### Pergunta: Redis AOF é backup?

Resposta possível:

Eu trataria AOF principalmente como mecanismo de persistência e recuperação do estado Redis, não como estratégia completa de backup ou disaster recovery.

Da mesma forma, AOF não fornece failover.

É importante dar a cada mecanismo exatamente a garantia que ele realmente oferece.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** AOF/everysec registra mutações com janela própria. Não reconstrói Cassandra nem infere IDs superiores ao contador restaurado. Coordenação temporal é lacuna. Aprofundamento: AOF antigo sozinho é perigoso? Sim com IDs novos preservados; criação reutiliza. Não há reconciliação automática do piso.

## 65. POR QUE DOCUMENTAÇÃO BILÍNGUE?

### Pergunta: Por que documentar o projeto em inglês e português?

Resposta possível:

O inglês é a documentação principal para apresentação internacional.

A documentação em português também funciona como material de estudo para eu conseguir explicar profundamente as decisões.

Eu queria que ambas descrevessem os mesmos fatos técnicos, sem inventar funcionalidades ou métricas.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Caminhos/números equivalentes permitem comparar contratos. Validação de links/anchors/paridade não julga significado. Aprofundamento: Como manter fatos? Revise fonte, propague mecanismos/limites a projeto/biblioteca e separe histórico. Idioma com respostas curtas apenas por links perderia substância apesar de validação aprovada.

## 66. POR QUE MERMAID?

### Pergunta: Por que criar diagramas se o projeto é pequeno?

Resposta possível:

Porque o diagrama ajuda a comunicar relações que seriam mais demoradas de compreender apenas lendo código.

No projeto eu uso diagramas tanto para componentes quanto para os fluxos de criação e resolução.

Mas eu não vejo diagrama como decoração.

Se um diagrama não acrescentasse compreensão, eu não adicionaria apenas para parecer mais sofisticado.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Sequência de criação mostra alocação antes de mapeamento/sem commit comum; resolução omite Redis. Omissões são fatos. Diagrama com broker seria falso sem código. Aprofundamento: Como reduzir drift? Junto ao mecanismo, poucos componentes reais e atualização quando contrato muda, sem alegações decorativas.

## 67. QUALIDADE DO PROJETO

### Pergunta: Você considera isso production-ready?

Resposta possível:

Não usaria essa expressão.

O projeto possui vários cuidados de engenharia, mas existem limitações conhecidas: Redis sem failover, ausência de uma estratégia completa de observabilidade e deployment, testes de infraestrutura limitados e decisões que precisariam ser revisitadas conforme requisitos reais de produção.

Eu prefiro dizer que é um projeto de Backend Engineering e System Design com decisões e limitações explicitamente documentadas.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Qualidade é contrato defensável/limites, não quantidade de tecnologias. API/erros/lifecycle vêm de código/fakes; recovery/HA exigem evidência. Aprofundamento: O que invalida production-ready? Perda não coordenada, sem restore/failover/TLS/abuso verificados e carga representativa. Documentação conserva lacunas.

## 68. SE TIVESSE MAIS UMA SEMANA

### Pergunta: O que você faria se tivesse mais tempo?

Resposta possível:

Eu escolheria uma evolução com objetivo claro, em vez de simplesmente adicionar mais tecnologias.

Uma área interessante seria aprofundar testes de integração e failure scenarios com Redis e Cassandra reais.

Outra seria medir o sistema com load testing para finalmente obter dados reais de throughput e latência.

A partir dessas medições eu poderia decidir se caching, mudanças na geração de IDs ou outras otimizações são justificadas.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Experimento útil mira invariante como não sobrescrever após perder contador isolado ou recuperar escrita ambígua. Define fixtures/limpeza antes de infraestrutura. Desempenho exige unidades/ambiente/correção. Aprofundamento: Sugestão significa concluído? Não; prioridades hipotéticas exigem autorização separada fora desta documentação.

## 69. COMO VOCÊ SABE QUE A ARQUITETURA É BOA?

### Pergunta: Como você avalia se sua arquitetura foi uma boa escolha?

Resposta possível:

Eu não avaliaria pelo número de tecnologias.

Eu verificaria se:

```text
cada componente possui uma responsabilidade clara;
as decisões resolvem requisitos reais ou objetivos explícitos de aprendizado;
os principais failure modes são conhecidos;
os trade-offs são compreendidos;
o código consegue ser testado;
a documentação corresponde ao comportamento;
e eu consigo explicar por que cada componente existe.
```

Uma arquitetura simples e bem compreendida é melhor que uma arquitetura sofisticada que eu não consigo defender.

**Mecanismo, trade-off e aprofundamento (revisão estática; alternativas hipotéticas):** Trace normal/falha/restore inconsistente. Se resposta depende de transação/consistência/integração inventada, explicação está errada. SQL menor pode ser razoável sem apagar estudo distribuído. Aprofundamento: Mais docs prova implementação? Não; código/assertivas/evidência datada estabelecem fatos distintos. Biblioteca marca fluxos ausentes/resultados não medidos.

## 70. RESUMO DE 60 SEGUNDOS

### Pergunta: Você pode resumir a arquitetura em um minuto?

Resposta possível:

O projeto é um URL shortener desenvolvido em Python com FastAPI.

Na criação, um endpoint protegido por Basic Auth valida a URL e utiliza Redis INCR para gerar atomicamente um ID inteiro. Esse ID é codificado em Base62 e passa por uma transformação reversível para produzir um código público de sete caracteres. O mapping entre ID e URL original é persistido em Cassandra.

Na resolução, o endpoint é público. A aplicação desfaz a transformação, decodifica Base62, recupera o ID, consulta Cassandra pela primary key e responde com 301 Moved Permanently.

O ambiente é Docker-first e possui Redis com AOF e três Cassandra nodes com replication factor 3. Cassandra é peer-to-peer; o primeiro nó é seed, não leader.

O projeto deliberadamente mantém algumas limitações, como Redis sem failover e ausência de benchmarks de produção, porque meu objetivo foi estudar e conseguir explicar os trade-offs em vez de esconder complexidade atrás de tecnologias adicionais.

## 71. RESUMO DE 30 SEGUNDOS

Resposta possível:

É um URL shortener que eu construí como projeto de Backend Engineering e System Design usando Python, FastAPI, Redis e Cassandra.

Redis gera IDs atomicamente, Base62 e uma obfuscação reversível produzem códigos públicos de sete caracteres, e Cassandra persiste os mappings em um cluster local de três nós.

Além da implementação, o foco do projeto foi estudar concorrência, persistência distribuída, replicação, failure modes, semântica HTTP e os trade-offs entre simplicidade, disponibilidade e consistência.

## 72. RESUMO DOS PRINCIPAIS TRADE-OFFS

| Decisão | Benefício | Custo / Limitação |
| --- | --- | --- |
| Python + FastAPI | Stack enxuta e oportunidade de aprendizado | Nova stack para dominar |
| Redis INCR | IDs atômicos sob concorrência | Dependência central no write path |
| Redis AOF | Melhor durabilidade local | Não fornece HA/failover |
| Cassandra | Persistência distribuída e aprendizado de System Design | Complexidade operacional maior que PostgreSQL |
| 3 Cassandra nodes | Permite estudar replicação e cluster | Mesma máquina não representa isolamento real |
| RF=3 | Três réplicas no datacenter local | Replicação não é backup |
| Base62 | Representação compacta e URL-friendly | Não oferece segurança |
| Obfuscação reversível | Esconde sequência óbvia | Não é criptografia forte |
| Código de 7 caracteres | Espaço de 62^7 | Espaço matemático não é capacidade comprovada |
| 301 | Semântica permanente e possibilidade de cache | Dificulta alteração posterior do destino |
| Basic Auth no POST | Autenticação simples | Não é identidade completa de produção |
| GET público | Links compartilháveis | Endpoint precisa considerar abuso em produção |
| Fakes nos testes | Testes rápidos e determinísticos | Não substituem integração real |
| Docker Compose | Ambiente local reproduzível | Não representa orquestração de produção |
| Monólito modular | Simplicidade e clareza | Não possui independência de deployment por domínio |
| Sem cache no GET | Menos complexidade | Cassandra atende todos os lookups atuais |
| Sem broker | Fluxo síncrono simples | Analytics assíncrono exigiria nova arquitetura |
| Sem deduplicação | Write path simples | Mesma URL pode gerar vários códigos |
| Sem TTL | Mapping simples e permanente | Não existe expiração automática |

## 73. FRASES QUE EU DEVO EVITAR NA ENTREVISTA

Evitar:

"Cassandra é melhor que PostgreSQL."

Preferir:

"Cassandra foi apropriado para os objetivos de aprendizado e para o padrão de lookup por chave deste projeto, mas PostgreSQL seria provavelmente mais simples operacionalmente para uma aplicação pequena."

Evitar:

"Redis garante que nunca vou perder IDs."

Preferir:

"Redis INCR garante atomicidade da geração concorrente; durabilidade e recuperação são problemas separados."

Evitar:

"AOF deixa Redis altamente disponível."

Preferir:

"AOF melhora durabilidade. A implementação atual não possui failover Redis."

Evitar:

"Cassandra-1 é o leader."

Preferir:

"Cassandra é peer-to-peer. Cassandra-1 é seed para descoberta; o coordinator depende da requisição."

Evitar:

"Base62 criptografa o ID."

Preferir:

"Base62 codifica o número. A camada seguinte faz obfuscação reversível, que também não deve ser tratada como criptografia forte."

Evitar:

"O projeto suporta trilhões de URLs."

Preferir:

"O espaço matemático dos códigos possui 62^7 combinações; isso não equivale a capacidade operacional comprovada."

Evitar:

"Tenho alta disponibilidade porque existem três Cassandra containers."

Preferir:

"Os três nós permitem estudar replicação e comportamento do cluster localmente; executar os três na mesma máquina não representa isolamento de falhas de produção."

Evitar:

"Os testes provam que Cassandra e Redis funcionam em qualquer cenário."

Preferir:

"A suíte padrão usa fakes para testar o contrato da aplicação; a infraestrutura real exige validações de integração separadas."

Evitar:

"Usei microservices best practices."

Preferir:

"Mantive um serviço modular porque o domínio atual não justificava a complexidade operacional de microservices."

## 74. MAPA MENTAL PARA A ENTREVISTA

Se eu esquecer uma resposta, voltar para este raciocínio:

```text
Qual era o problema?
        ↓
Qual requisito eu precisava atender?
        ↓
Quais alternativas existiam?
        ↓
Por que escolhi esta?
        ↓
O que ela me oferece?
        ↓
O que ela me custa?
        ↓
Como ela pode falhar?
        ↓
Como o projeto trata essa falha hoje?
        ↓
Qual limitação continua existindo?
        ↓
O que eu mudaria em produção?
```

Isso é mais importante do que decorar respostas.

## 75. PRINCÍPIO FINAL

Eu não preciso convencer o entrevistador de que cada decisão do projeto é a única decisão correta.

Preciso demonstrar que consigo raciocinar sobre engenharia.

Uma resposta tecnicamente madura pode ser:

"Essa foi a escolha que fiz para os requisitos e objetivos deste projeto. Ela resolve estes problemas, mas introduz estes custos. Se os requisitos mudassem desta forma, eu reconsideraria a decisão e avaliaria estas alternativas."

O objetivo da entrevista não é defender a arquitetura como perfeita.

O objetivo é demonstrar que eu:

- 		entendo o sistema que construí;

- 		conheço as responsabilidades de cada componente;

- 		consigo explicar os trade-offs;

- 		reconheço limitações;

- 		não confundo conceitos de sistemas distribuídos;

- 		não invento capacidade que não medi;

- 		consigo propor evoluções baseadas em requisitos;

- 		consigo transferir os aprendizados para outros sistemas.

Esse é o nível de entendimento que torna o projeto defensável em uma entrevista técnica.

## Aprofundamentos e ordem de estudo — 2026-10-09

A [arquitetura autoritativa](../architecture/overview.md) registra dois limites: preenchimento `0` assume alfabeto iniciado em zero, e o gerador Redis não reinicializa após perder a chave num processo já inicializado. Helpers usam settings globais mesmo com settings injetados no serviço. São achados estáticos, não regressões executadas; nenhum teste da aplicação rodou aqui.

**Pergunta: Qualquer alfabeto customizado funciona?** Resposta modelo: “Validação aceita 62 caracteres únicos, mas `0` fixo pode representar dígito não zero ou caractere inválido. Manteria o padrão e trataria padding/versão geral em tarefa de código separada com round-trips.”

**Pergunta: Lacuna e reutilização de ID são iguais?** Resposta modelo: “Falha na persistência após alocação consome ID e deixa lacuna. Perder estado do contador com mappings preservados pode reutilizar ID e sobrescrever Cassandra. É problema de correção; AOF e lock local não implementam recuperação entre stores.”

**Aprofundamento:** E se a chave desaparecer após `_initialized=true`? Por que Settings injetado diverge de helpers? Como rotacionar configuração preservando links? O que fake prova sobre concorrência Redis real?

Ordem: HTTP/auth/payload → serviço → Base62/inverso modular padrão → inicialização Redis/janelas de falha → lookup/replicação/consistência Cassandra → lifespan/configuração → fakes versus evidência real → alternativas de recuperação/cache HTTP. Sugestão, sem marcar progresso. Alternativas de estudo não são necessariamente avaliações históricas.


## Aprofundamentos adicionais de entrevista fundamentados no código

Perguntas e respostas originais acima foram preservadas. IDs abaixo identificam a sequência adicional; não renumeram material retido. Níveis orientam estudo, não status implementado. Aprofundamentos incluem respostas para manter a sequência autossuficiente.

### Q001 — Intermediária: Por que o lock local de inicialização não garante IDs globalmente únicos?

**Resposta:** Implementado: Lock protege `_initialized` com dupla verificação em um gerador. Entre processos, Redis SET NX protege inicialização e INCR serializa alocação no servidor compartilhado. Lock sozinho não coordena processos; operações no servidor fornecem essa fronteira. Mesmo alocação atômica depende de contador preservado: AOF everysec pode perder incrementos recentes sob falha, e contador reiniciado pode reutilizar IDs com mapeamentos Cassandra existentes. INSERT Cassandra é upsert, então reutilizar ID pode sobrescrever destino em vez de indicar colisão.

Aprofundamento: NX repara contador apagado após inicialização? A flag em cache pode pular inicialização e INCR em chave ausente recomeça. Não há verificação coordenada de recuperação. Aprofundamento: Que alternativa reduz acoplamento? Banco SQL único com identidade gerada e mapeamento na mesma transação simplificaria atomicidade; códigos aleatórios precisam resolver colisão; IDs distribuídos exigem disciplina de relógio/nó. São alternativas, não migrações entregues. Geração única saudável e recuperação segura após perda de estado são alegações diferentes.

### Q002 — Desafiadora: Como classificar falha após alocação ou escrita Cassandra com timeout?

**Resposta:** Implementado: criação aloca, codifica/ofusca e depois grava. Falha posterior consome inteiro. Se Cassandra definitivamente não gravou, sobra lacuna; se aceitou e a resposta se perdeu, mapeamento pode existir apesar do 503. O serviço não reconcilia ambiguidade nem reutiliza ID para HTTP repetido. Retry aloca outro ID e pode duplicar solicitação lógica. Teoria: resultado da operação e entrega da resposta são eventos separados; timeout não prova rollback. Redis e Cassandra não compartilham transação.

Aprofundamento: Repetir upsert com mesmo ID seria seguro? Apenas garantindo ownership do ID e destino idêntico; a API HTTP não retém esse contexto. Aprofundamento: O que exige chave de idempotência? Registro durável chave/resultado, política de conflito de payload, arbitragem concorrente, expiração e replay, não apenas cabeçalho. Transação em banco único é alternativa mais simples nessa escala. São projetos hipotéticos; não há criação exactly-once ou deduplicação de consumidor implementada.

### Q003 — Desafiadora: Por que derivação com SHA-256 não torna o código cifrado?

**Resposta:** Implementado: código transforma inteiro por `(a*x+b) mod 62**7`, com multiplicador coprimo e parâmetros derivados de SHA-256. Coprimalidade fornece reversibilidade e ausência de colisão no espaço suportado com configuração fixa; hash de parâmetros não transforma função afim em cifra autenticada segura. Código não carrega tag de integridade ou política de acesso. Resolução é pública. Teoria: encoding muda representação, ofuscação esconde sequência óbvia e cifra exige construção de segurança e ciclo de chave definidos. Basic protege criação, não sigilo do código, e precisa de transporte protegido em exposição pública.

Aprofundamento: Chave pode rotacionar transparentemente? Código/mapeamento não armazena versão; nova chave muda consulta. Aprofundamento: E alfabeto personalizado? Base62 aceita 62 caracteres únicos, mas padding é `0` literal, que pode não ser zero ou nem existir no alfabeto. Compatibilidade além do padrão é lacuna explícita. Código armazenado versionado permitiria migração com custo de armazenamento/consulta. É hipotético; código não deve ser credencial de acesso a recursos privados.

### Q004 — Intermediária: O que RF=3 e raciocínio quorum dizem sobre esta implantação?

**Resposta:** Implementado: bootstrap local configura três peers Cassandra e RF=3; o perfil escolhe roteamento atento ao DC local, mas não define consistência explícita de leitura/gravação. Fator de replicação descreve cópias desejadas, não quantos acknowledgements cada operação espera; nós compartilham host local. Seed serve descoberta, não liderança. Teoria geral: com conjuntos consistentes de réplicas, R+W>N oferece sobreposição quorum, mas resolução de conflitos, escritas concorrentes, detecção de falhas e política exata ainda importam. Não é linearizabilidade universal nem substitui conhecer defaults do driver travado.

Aprofundamento: RF sozinho permite prometer resolução imediata após criar? Não estabelece garantia própria de leitura após escrita. Aprofundamento: Réplicas são backups? Não; deleção/corrupção pode propagar e perda do host afeta todos os nós locais. Testes reais de falha/replicação e restore continuam lacunas. Quorum explícito tornaria contrato deliberado com custo de latência/disponibilidade; nenhuma configuração ou execução do cluster ocorreu nesta tarefa.

### Q005 — Introdutória: Como status da API, health e testes diferem como evidência?

**Resposta:** Implementado: POST válido autenticado retorna 201; GET público retorna 301, código inválido/ausente 404, falha de configuração 500 e de adapter 503. Redirect permanente pode ser cacheado, então logs não medem todas as visitas posteriores. Probe Compose busca OpenAPI após startup; startup inicializa Cassandra e alocação Redis é lazy. Logo health verde não prova novo incremento Redis ou consulta de mapeamento. GET não usa Redis, mas reinício da app ainda depende de inicialização Cassandra.

Aprofundamento: Testes fake HTTP/serviço provam cluster real? Não; verificam validação, mapeamento e ordem sob resultados modelados. Defaults do driver, autenticação, escritas parciais e failover exigem infraestrutura isolada. Aprofundamento: O que observabilidade produtiva acrescentaria? Latência/categorias por operação, readiness das dependências e alarmes de recuperação do contador sem vazar credenciais/destinos. São hipotéticos. Reload, bind mounts e health locais não são estratégia de implantação produtiva; retenção, restauração consistente e rollback seguem lacunas dependentes de evidência.

## Conciliação com o código — 2026-10-18

`40e4ea05d6e4d2d5ae81d2020ec6ea7936330d44`. Código, entradas API/CLI, limites de persistência/recursos e definições de testes foram revisados estaticamente. Explicações e respostas existentes continuam aplicáveis nos limites registrados. Não foram produzidos resultados de runtime. Consulte o [roteiro autossuficiente de implementação e entrevista](../guides/implementation-study.md).
