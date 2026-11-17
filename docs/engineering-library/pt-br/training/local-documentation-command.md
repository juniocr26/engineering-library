# Comando local de documentação

Engineering Library é privada. Entre no backend existente com `docker compose exec backend sh` e execute `make docs`. O caller atual é a versão 1.9.12, usa o bundle Rails e chama explicitamente o Ollama no Docker. O padrão configurado é `llama3.2:3b`; não há substituição silenciosa. A saída é um rascunho bilíngue do código, sem aprovação factual autônoma.

## Preparação inteiramente em Docker

Execute estes comandos Docker na raiz deste repositório. Não é necessário Python, Bash, Ruby, Node ou make no host. O helper temporário recebe a coleção irmã gravável apenas para criar `docs/` ausentes; preserva conteúdo existente e atribui às novas pastas o proprietário da pasta pai. Na geração normal, fontes são somente leitura e apenas os destinos documentais são graváveis.

```sh
docker compose run --rm --no-deps --user 0:0 --volume ..:/sources --entrypoint python3 backend /sources/engineering-library/tools/prepare_docs_mounts.py --bind-root /sources=.. --output /docs/.docs-state/setup
docker compose -f compose.yaml -f docs/.docs-state/setup/mounts.json config --quiet
docker compose -f compose.yaml -f docs/.docs-state/setup/mounts.json up -d --no-deps backend
docker compose exec backend sh
# Dentro do backend:
make docs
make docs DOCS_ARGS='--project project-slug'
```

`exec` não adiciona mounts: aplicar o overlay recria somente o backend. Preserve configurações, ambiente, volumes e dados existentes. Para fontes já preparadas, gerar não exige recriação. A invocação opcional do helper em Python no host continua sendo conveniência, não dependência.

A descoberta padrão visita somente repositórios Git irmãos diretos. Exclui esta biblioteca, symlinks e checkouts aninhados de ferramentas/dependências; não percorre ancestrais sem relação. Coleções adicionais são configuração explícita da instalação. Monte a segunda em `/extra-sources-1` durante a preparação e acrescente `--bind-root /extra-sources-1=RELATIVE_COMPOSE_SOURCE` (ou caminho absoluto do host); o overlay gerado mantém esse mount. Caminhos relativos usam o primeiro arquivo Compose como base. Caminhos com espaços precisam de aspas no shell utilizado. Não publique a seleção gerada como dataset portátil do agente.

Use `/docs/.docs-state/setup/projects.json` ou uma seleção JSON privada:

```sh
make docs DOCS_ARGS='--config /docs/.docs-state/setup/projects.json'
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug'
```

```json
{"projects":[{"slug":"project-slug","source":"/sources/project-slug","destination":"/project-docs/project-slug","files":["src/component.rb"],"question":"Explique o contrato declarado e seu limite de falha."}]}
```

`files` e `question` são opcionais. A pergunta é tarefa explícita, não evidência verificada. A amostragem padrão limita-se a quatro arquivos elegíveis completos e 6 KiB totais para inferência CPU. Seleções `files` explícitas mantêm até doze arquivos e 24 KiB; cada elegível tem no máximo 64 KiB. Candidatos automáticos grandes são omitidos e contabilizados, nunca truncados silenciosamente. O padrão menor decorre de timeouts de 300 segundos com a amostra automática anterior de 24 KiB; troca abrangência por rascunho limitado, não por cobertura arquitetural exaustiva. Arquivo explicitamente selecionado ausente faz o projeto falhar. Arquivos ocultos, dotenv, credenciais, dependências, dados gerados/runtime, testes e `docs_codex` são excluídos. Literais reconhecidos como credenciais causam omissão ou rejeição quando selecionados explicitamente. Esse controle é conservador, não detecção completa de segredos; revise a evidência antes de autorizar auditoria ou pesquisa.

## Evidência e skills

O caller lê bytes atuais exatos pelas fontes somente leitura. `DOCS_EVIDENCE_MODE=declarations` é o padrão: enums Rust simples e trechos limitados de métodos públicos inerentes recebem preparação determinística. Formas não suportadas usam trechos brutos; `DOCS_EVIDENCE_MODE=raw` seleciona explicitamente a representação anterior. A assistência é registrada e não deve ser creditada como descoberta autônoma do modelo. Amostragem parcial não comprova cobertura arquitetural completa.

As skills de evidência, autoria e revisão são carregadas explicitamente de `agent/skills/`; seus hashes entram no fingerprint. O contexto inglês conciso orienta a geração, com instruções operacionais equivalentes em português preservadas. A atribuição MIT upstream é mantida; o checkout removido não é dependência de runtime. `DOCS_CONTEXT=baseline` omite skills para comparação controlada. `DOCS_TRANSPORT=generate` é alternativa experimental; chat é o normal. Inferências repetidas não treinam pesos. Cada requisição real usa `keep_alive=0` para liberar o runner após a conclusão, preservando o serviço Ollama. Isso acrescenta latência de recarga e não garante ausência de OOM. O contexto de 16k exige memória; não sobreponha inferência a browser/mídia ou builds quando houver restrição. Inspecione falhas e consumo real, sem deduzir a causa a partir de um indicador OOM histórico.

Uma resposta local fornece os dois idiomas. O caller verifica conclusão, JSON/schema, IDs de evidência, citações exatas, restrições de símbolos e formatação básica. Isso não comprova precisão factual, profundidade útil ou equivalência semântica da tradução. O modelo 3B já atribuiu responsabilidades erradas, inventou defaults e afirmou integrações sem suporte. Mantenha rascunhos claramente sem revisão até conferir ambos os idiomas contra código/runtime.

Em revisão explicitamente assistida, `feedback` opcional contém exatamente `kind` (`reviewer-feedback` ou `codex-reference`), `source_hashes` (mapa dos arquivos selecionados atuais para SHA-256) e `text` limitado. Hashes obsoletos bloqueiam antes da inferência. Documento e manifest identificam assistência. Avaliações iniciais independentes excluem referências e conclusões do revisor; revisões assistidas são resultados separados, sem crédito autônomo. `docs_codex` não é carregado automaticamente.

## Pesquisa pública opcional

Offline é o padrão. A inferência permanece local. SearXNG opcional é pesquisa auto-hospedada sob AGPL, sem API credentials obrigatórias; os mecanismos upstream podem limitar, desafiar ou falhar. Não é serviço ilimitado nem garantido.

```sh
docker compose -f compose.yaml -f compose.research.yaml --profile research up -d research
# No backend, com pesquisa pública explicitamente configurada:
DOCS_RESEARCH=search make docs DOCS_ARGS='--config /tmp/projects.json'
DOCS_RESEARCH=urls make docs DOCS_ARGS='--config /tmp/projects.json'
DOCS_RESEARCH=offline make docs DOCS_ARGS='--config /tmp/projects.json'
```

```json
{"research":{"technology":"Ruby","version":"3.4","query":"Ruby 3.4 Net HTTP ipaddr documentation","primary_hosts":["docs.ruby-lang.org"],"urls":[],"max_sources":1,"version_pattern":"3.4"}}
```

Insira `research` no objeto do projeto selecionado. URLs busca até dois endereços públicos explicitamente aprovados; search descobre candidatos e busca somente hosts primários aprovados. Consultas exigem palavras revisadas de tecnologia/versão/tópico público; nomes privados, código, dados pessoais, credenciais e identificadores arbitrários não podem ser enviados. Consultas são explícitas, nunca derivadas do código. Palavras desconhecidas são rejeitadas antes do envio.

A busca pública permite HTTP(S) somente em portas padrão. DNS e cada redirecionamento são verificados; endereços privados, loopback, link-local, metadata e reservados são rejeitados, e conexões fixam o IP validado preservando a verificação TLS do hostname. Há limites de tempo, bytes, tipo e redirecionamentos. Conteúdo recebido é texto não confiável, nunca executado. O filtro de versão por trecho textual não comprova compatibilidade semântica de versões.

A pesquisa registra URL, consulta, pequeno trecho citado e hash. Uma chamada local separada vê somente trechos públicos; a análise do código não vê o pacote web. Documentação pública explica contratos tecnológicos e não comprova a implementação local. Redação pública inválida é rejeitada; trechos exatos preservados continuam identificados. Falha de pesquisa/busca produz estado degradado explícito e preserva a geração local. Offline não faz consultas. `DOCS_RESEARCH_REFRESH=1` atualiza deliberadamente a consulta optativa; sem isso, entradas equivalentes podem reutilizar o resultado controlado. `DOCS_SEARCH_URL` aceita somente o limite local `http://research:8080/search`.

Provisionar o modelo é download separado e intencional, fora da geração:

```sh
docker compose exec ollama ollama list
# Somente quando o proprietário decidir provisionar esse modelo:
docker compose exec ollama ollama pull llama3.2:3b
```

## Dois destinos e navegação

| Biblioteca | Repositório analisado |
| --- | --- |
| `docs/<slug>/en/guides/generated-source-summary.md` | `docs/en/guides/generated-source-summary.md` |
| `docs/<slug>/pt-br/guides/generated-source-summary.md` | `docs/pt-br/guides/generated-source-summary.md` |
| `docs/<slug>/img/` | `docs/img/` |

As cópias de cada idioma são idênticas em bytes e vêm da mesma resposta. Cada índice localizado recebe link de rascunho em marcadores `make-docs:source-summary`. O comando controla esses blocos, resumos dedicados e metadados `.docs-state`, preservando texto humano fora deles. Não inventa bios/ícones, sincroniza catálogo no banco, gera imagens raster, executa aplicações ou consulta bancos dos projetos. Capturas/diagramas reais aceitos podem ser preparados separadamente e compartilhados nos destinos; inferência textual não gera pixels.

O journal cobre quatro resumos e quatro índices. Resumos preexistentes sem ownership, edição humana em conteúdo controlado, destino não gravável ou recuperação pendente bloqueiam aquele projeto. Adições humanas fora dos blocos dos índices são preservadas. Fonte/mount ausente nunca implica exclusão. Mudanças atuais regeneram o resultado controlado; confira manualmente remoção de afirmações obsoletas. Entradas relevantes e conteúdo controlado inalterados resultam em no-op sem inferência/regravação. Falhas por projeto são relatadas enquanto outros selecionados continuam.

## Recuperação e retenção

Um lock da biblioteca serializa execuções. Fontes/ownership são verificados antes da inferência e antes da aplicação. Candidatos e backups têm hashes; gravação usa rename/fsync atômico por arquivo e journal persistente. Não há transação atômica entre filesystems. Após interrupção, use a MESMA configuração dos destinos:

```sh
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug --recover rollback'
# Ou após revisar candidatos salvos:
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug --recover complete'
```

Rollback restaura bytes controlados e manifest anteriores; complete usa candidatos sem inferência e rejeita fontes alteradas. A recuperação verifica bytes atuais e preserva edições concorrentes; mantenha journal/backups quando bloqueada. Nunca apague dados, volumes ou documentação alheia para limpar um erro.

`DOCS_AUDIT=1` emite eventos com código, requisições e respostas exatos. Preserve resultados e falhas em armazenamento operacional privado; exemplos reutilizáveis exigem revisão separada antes de entrar na árvore ativa do agente. Preserve hashes históricos, backups de recuperação, licenças e atribuições. Não há certificação de anonimato ou publicação.

As evidências distinguem falhas simuladas, inferência local real, execução de componentes, builds completos e verificações reais de aplicação/browser. A execução usa host macOS com containers Linux; Android usa imagem AMD64 emulada. Windows/WSL2 e host Linux independente continuam sem validação. Consulte o relatório atual para cobertura por projeto, experiências rejeitadas e erros factuais restantes.

## Avaliações temporárias e isolamento da documentação original

Uma seleção pode declarar `"lifecycle":"temporary"`. As cópias na biblioteca ficam em `docs/.evaluations/<slug>/`, e o estado de ownership/recuperação em `docs/.docs-state/evaluations/`. O destino do projeto analisado continua sendo seu mount `docs/` configurado explicitamente. Essa opção não autoriza excluir documentação preexistente. A sincronização ignora a árvore oculta de avaliação; `docs/.catalog-policy.json` também lista slugs externos aposentados que a sincronização normal não deve ativar. A proveniência histórica permanece separada do catálogo atual.

O coletor exclui `docs_backup`, `docs_codex` e suas variantes com sufixos únicos, inclusive na seleção explícita. O modelo recebe cartões de código e os três contextos de skills ativos, sem relatórios de avaliação nem documentação preservada. Essas barreiras de diretório não identificam cópias não declaradas sob nomes arbitrários.

`tools/evaluation_lifecycle.py` oferece `capture`, `seal` e `restore`, com diretório privado explícito em `--session` e argumentos `--root` repetíveis na captura. A captura inventaria bytes e modos e preserva os arquivos originais. O selo registra o inventário final experimental revisado pelo operador. A restauração rejeita edições conflitantes e backups corrompidos antes de escrever, recupera originais e remove somente adições seladas. Uma restauração interrompida pode ser repetida. O operador precisa estabelecer a propriedade dos arquivos antes de selar; a ferramenta não deduz autoria. Links simbólicos são rejeitados, e os backups continuam disponíveis após a restauração. A ferramenta não restaura bancos ou serviços e não fornece transação entre filesystems.

## Evidência estrutural experimental

`DOCS_EVIDENCE_MODE=structural` habilita faixas completas de funções/métodos Python extraídas pelo parser AST da biblioteca padrão. Python precisa estar disponível dentro do container backend; o parser nunca importa os módulos da aplicação. Trechos literais e posições de linha são preservados. Funções acima do limite de 1.900 caracteres por citação são rejeitadas, sem divisão. A classe envolvente é uma indicação sintática, não prova de chamadas ou runtime. Outras linguagens mantêm a representação existente, inclusive Java; extensões de código e headers C/C++ passam a ser elegíveis nos mesmos limites de arquivo/contexto. O modo é experimental: não substitui o padrão `declarations` nem comprova qualidade factual/bilíngue superior.

A saída bruta de `DOCS_AUDIT=1` pode conter código privado autorizado. Guarde-a em diretório operacional com acesso controlado e ignorado pelo Git, como `.local-backups/`, fora do `agent/` reutilizável. Exemplos públicos exigem revisão própria de conteúdo e proveniência; nomes neutros não comprovam anonimato.

## Rejeição de alegações de unicidade

Uma barreira lexical estreita rejeita alegações afirmativas de unicidade quando o trecho citado não contém uma restrição explícita. Ela reconhece um conjunto limitado de negações EN/PT-BR e construções `UNIQUE`, `PRIMARY KEY` ou `unique()`. É auxílio à rejeição, não prova semântica: uma palavra/construção pode ter escopo inadequado, e muitos outros erros factuais continuam sem detecção. Alegações legítimas que exigem evidência mais ampla também podem ser rejeitadas. Uma resposta válida no esquema ainda exige revisão factual/bilíngue. A barreira foi introduzida em 1.9.3. Mudanças de versão do caller invalidam o fingerprint, evitando tratar um rascunho antigo em cache como validado pelo caller atual.

## Unidades completas explícitas

O mapa experimental `units` seleciona definições completas dentro de `files` explícitos. Por exemplo, `"files":["src/math.cpp"],"units":{"src/math.cpp":["Vector2Lerp"]}` envia somente a definição selecionada como evidência de código. O seletor pode usar um nome curto sem ambiguidade ou o nome qualificado pelo responsável. Definições ausentes, ambíguas ou não suportadas rejeitam antes da inferência. A pergunta continua sendo uma tarefa de redação, sem valor de prova.

Python usa intervalos da AST. C, C++, Java, PHP, Rust e funções livres Go suportadas usam um lexer conservador de disposição das definições, que mascara comentários/literais e acompanha os escopos envolventes. Não é compilador nem parser semântico: templates, expansão de macros, métodos gerados, algumas disposições da linguagem e definições condicionais exigem inspeção separada. Somente as definições explicitamente selecionadas entram; campos e dependências não são descobertos automaticamente. Uma indicação de classe/namespace não comprova comportamento em execução.

Nos arquivos com unidades selecionadas, o comando lê até 1 MiB por arquivo para hash integral, detecção de mudanças e triagem de credenciais, mas somente as citações selecionadas entram nos cartões enviados ao modelo. Cada unidade completa tem limite de 6.144 caracteres; são até doze unidades e 24 KiB de contexto de código selecionado. Os demais arquivos mantêm os limites anteriores. O hash integral identifica a revisão; não significa que o modelo recebeu todo o arquivo. A saída sinaliza esse escopo limitado. As exclusões de backups/referências ocorrem antes da seleção e não podem ser contornadas com `units`.

Nomes com menos de três caracteres exigem o nome qualificado em cada explicação; os demais métodos selecionados exigem o nome exato do método. O comando também rejeita padrões limitados que inventam um tipo ausente ou atribuem um método a outro responsável. Essas verificações lexicais podem rejeitar prosa legítima e deixar passar erros semânticos. Os ensaios controlados ainda encontraram limites inventados, confusão na posição de argumentos e traduções incorretas com unidades completas. A opção melhora o acesso ao código e os limites das citações, sem conceder aceite factual automático.


## Salvaguardas atuais e limites de instalação

A versão 1.9.7 mantém o filtro anterior de unicidade e acrescenta uma verificação limitada de paridade de literais entre aspas: tokens curtos selecionados da fonte, quando citados em qualquer idioma, devem permanecer exatos nas duas explicações. Literais traduzidos sem aspas e diferenças semânticas mais amplas ainda podem escapar. A cobertura de unidades completas conta definições completas citadas sem duplicação, lista as não citadas e não conta cartões de arquivo bruto como definições completas. Cinco unidades selecionadas com quatro fatos podem deixar cobertura incompleta. Esses contadores não são notas de qualidade.

A extração Go aceita layouts conservadores de funções livres, tipos de parâmetros qualificados e strings brutas mascaradas. Receivers, generics e retornos com tipos anônimos não são suportados. O lexer nativo não expande macros nem resolve dependências. Selecione helpers explicitamente quando a afirmação depender de seus corpos; a campanha ainda encontrou atribuições erradas e omissão de argumentos alterados mesmo com contexto da cadeia de chamadas. O candidato de pareamento de parâmetros Rust permaneceu privado: reduziu um erro posicional, mas gerou texto vago que não descreveu a mudança controlada.

O preparador de mounts exclui os dez slugs temporários da política validada do catálogo. A geração normal rejeita esses projetos sem `lifecycle` explicitamente `temporary`. É permitido reverter um journal temporário legado; concluí-lo pelo ciclo permanente é rejeitado. Políticas inválidas ou symlinks interrompem a operação.

Renomear `docs/` no host enquanto o container está ativo pode deixar o bind mount estreito preso ao inode do backup renomeado. Antes de escrever, inclusive na recuperação, o caller rejeita um destino estreito que não seja idêntico ao `docs/` atual da fonte. Termine os jobs, arquive evidências necessárias do tmpfs do backend, gere novamente o overlay da instalação e recrie somente o backend com os comandos de preparação acima. Isso reconecta o diretório atual; não restaura arquivos nem bancos. Confira a identidade do destino após a recriação. Não aponte o destino de geração para `docs_backup/` para contornar essa verificação.

## Perfil de inferência em host compartilhado e extração de métodos (1.9.11)

`DOCS_CONTEXT_TOKENS` seleciona de 4.096 a 16.384 tokens de contexto; o padrão continua em 16.384. `DOCS_MODEL_THREADS` seleciona opcionalmente de 1 a 16 threads de inferência; a ausência preserva o padrão do servidor. `DOCS_REQUEST_TIMEOUT` seleciona um timeout de leitura de 60 a 1.800 segundos; o padrão continua em 300 segundos. Contexto e threads entram no fingerprint da geração. Alterar somente o timeout de transporte não invalida um no-op que continua válido. O manifesto registra o timeout efetivamente usado em sua geração.

Para uma configuração de avaliação explicitamente autorizada, um exemplo em host limitado, dentro do backend, é:

```sh
DOCS_CONTEXT_TOKENS=4096 DOCS_MODEL_THREADS=1 DOCS_REQUEST_TIMEOUT=900 \
  make docs DOCS_ARGS='--config /path/to/authorized-evaluation.json'
```

Este é um exemplo de configuração, sem garantia universal de memória ou latência. Ajuste as threads à quota de CPU e registre memória real, tokens de entrada/saída, duração e falhas. Abaixo do contexto padrão, o comando rejeita um prompt cujo conteúdo UTF-8 ultrapasse o contexto selecionado menos uma margem de 256 tokens, usando bytes como limite superior deliberadamente conservador de tokens. Assim, alguns prompts que caberiam segundo um tokenizer serão rejeitados. Selecione menos unidades completas; nenhuma fonte é encurtada silenciosamente para caber nesse perfil. Não é necessário editar arquivos de ambiente existentes.

A descoberta de fontes reconhece `.cs` e `.gd`. A seleção explícita de unidades completas também aceita métodos comuns de C# e uma forma limitada de método de classe template C++, com um parâmetro `class`/`typename` e um argumento template que seja um único identificador. A citação inclui a declaração template; o responsável canônico remove esse argumento, por exemplo `Vector3::Normalize`. Trata-se de seleção lexical, não de análise semântica Roslyn/C++. Templates de funções livres, especializações, parâmetros template aninhados ou múltiplos, requires-expressions, propriedades, expansão de macros e definições ambíguas continuam fora desse suporte limitado a métodos. Reconhecer GDScript não acrescenta um seletor AST de GDScript.

Arquivos e diretórios nomeados como feedback de revisão, saídas esperadas, resumos de comparação e referências Codex são excluídos antes da seleção explícita. Essa convenção não detecta respostas renomeadas arbitrariamente. Inspecione as requisições capturadas para verificar a fronteira real da evidência. Citações exatas, JSON válido e gravações bem-sucedidas continuam separados do aceite factual e bilíngue; uma tradução ainda pode substituir uma diferença com sinal por um valor absoluto incorreto.

O avaliador separado `tools/documentation_similarity.py` recebe artefatos bilíngues congelados e julgamentos de afirmações revisados contra fontes. Ele confere hashes dos arquivos e dos trechos citados, apresenta separadamente as cinco dimensões ponderadas e mantém incompletas as dimensões ausentes. Citações copiadas do código não contribuem para a similaridade textual. Suas heurísticas reproduzíveis não comprovam verdade semântica, cobertura integral do projeto, aceite do proprietário ou prontidão para remover backups recuperáveis. Os resultados operacionais pertencem ao relatório datado da avaliação.

## Rascunhos explícitos de projeto com múltiplas seções

A versão 1.9.12 corrige demonstrativos como “Essa classe” que eram tratados como tipos inventados; tipos externos explicitamente nomeados continuam rejeitados. O coordenador opcional de projeto está na versão 1.0.1. A campanha com quatro seções produziu rascunhos bilíngues reais, mas erros factuais e contratos omitidos impediram a aprovação de projetos completos. Escrita bem-sucedida ou citação literal correta não equivale a aprovação factual.

Dentro do backend existente, forneça um plano privado explícito e diretórios persistentes, distintos e graváveis para biblioteca e workspace:

```sh
DOCS_LIBRARY=/docs/.evaluations/my-run DOCS_WORKSPACE=/docs/.docs-state/workspaces/my-run DOCS_CONTEXT_TOKENS=4096 DOCS_MODEL_THREADS=2 DOCS_REQUEST_TIMEOUT=600 DOCS_RESEARCH=offline make docs DOCS_WORKFLOW=project DOCS_ARGS='--config /docs/.docs-state/my-plan.json --project sample'
```

O plano contém `schema: 1` e `projects`. Cada projeto exige `slug` validado, `name`, `source` somente leitura, revisão Git congelada `source_revision` e `sections`. Cada seção exige `id`, `titles` bilíngues (`en`, `pt-br`), `files`, `question` e `ranges` inclusivos do arquivo original (caminho associado a listas de `[início, fim]`) ou `units` completas suportadas (caminho associado a identificadores exatos). Intervalos selecionam a disposição do código; não comprovam semântica por AST. Os trechos enviados ao modelo são limitados; contexto excessivo é rejeitado, sem truncamento silencioso. Exclua documentação gerada, referências independentes, credenciais e arquivos de ambiente do proprietário das fontes selecionadas.

O coordenador copia os arquivos originais selecionados para o workspace sob seu controle, registra hashes completos, confere a revisão congelada, usa as transações existentes por seção e mantém auditorias persistentes em `audits/SLUG/SECTION.ndjson`. Um bloqueio não bloqueante da biblioteca impede outro coordenador de escrever na mesma raiz. Falhas de transporte interrompem o agendamento antes da próxima seção. Seções rejeitadas permanecem identificadas; uma revisão malsucedida preserva o rascunho anteriormente montado. A montagem bilíngue verifica os dois destinos antes da escrita e mantém um diário pendente em caso de interrupção. Inspecione e recupere esse diário antes de escrever novamente; não há promessa de recuperação automática após reinício.

Os rascunhos montados ficam em `DOCS_LIBRARY/projects/SLUG/{en,pt-br}.md`; saídas das seções, manifestos de propriedade e auditorias ficam separados. Os `docs/` originais permanecem intactos quando os destinos são cópias isoladas de preparação. Para retomadas, use caminhos persistidos no host: `/tmp` e os workspaces `tmp` do backend podem ser efêmeros. Preserve um arquivo privado com respostas brutas, fontes selecionadas e avisos de licença antes de retirar árvores de avaliação pelo ciclo capture/seal/restore. Não exclua árvores inteiras de documentação nem pare serviços normais da Library ou do Viva Bem durante a limpeza.

Os candidatos de contexto sem metadados e de proposições revisadas no código continuam como experimentos privados. Este fluxo não os ativa. Diferencie geração independente, variantes assistidas por revisão e aprovação de projetos completos.
