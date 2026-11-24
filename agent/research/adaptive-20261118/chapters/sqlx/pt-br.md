# SQLx: invólucros, erros e destinos de dados

Capítulo experimental escrito pelo Codex após revisão da fonte. É um rascunho de correção, não saída inalterada do modelo local. Aprovação humana factual e bilíngue pendente; não é resposta positiva para treinamento.

Revisão da fonte: `41dac167fdad5e3fd81d66cafba0951dc6823a30`.

## 1. Um invólucro e a verificação da conexão

A declaração `DB` embute `*sql.DB` e acrescenta `driverName string`, `unsafe bool` e `Mapper *reflectx.Mapper`. Essa é a estrutura escrita do invólucro. Esses campos descrevem um ponteiro embutido e estado auxiliar; o sucesso de uma conexão de rede exige evidência própria. [sqlx.go:243–248](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L243-L248)

`NewDb` recebe um `db *sql.DB` existente e um `driverName string`. Sua expressão de retorno constrói `&DB{DB: db, driverName: driverName, Mapper: mapper()}`. O corpo fornecido não contém reescrita explícita de consulta nem verificação de conexão. O comportamento de `mapper()` exige sua própria fonte. [sqlx.go:254–256](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L254-L256)

`Open` declara `(*DB, error)` e primeiro chama `sql.Open(driverName, dataSourceName)`. Um erro não nulo retorna `nil, err`. Caso contrário, constrói o invólucro com o objeto retornado e `mapper()`, retornando esse invólucro junto com `err`. Esse invólucro não contém ping explícito; o comportamento da biblioteca chamada e do driver está fora deste trecho. [sqlx.go:264–270](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L264-L270)

`MustOpen` declara somente `*DB`. Chama `Open`, executa `panic(err)` quando o erro retornado não é nulo e, caso contrário, retorna `db`. Sua assinatura não é uma API com dois resultados que retorna erro. [sqlx.go:273–279](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L273-L279)

## 2. Verificação da conexão e liberação

`Connect` chama `Open(driverName, dataSourceName)` e retorna imediatamente `nil, err` se a abertura informar erro. Em seguida, atribui o resultado de `db.Ping()` a `err`. Um erro no ping leva a `db.Close()` antes de `nil, err`; o resultado do fechamento não é verificado aqui. O retorno restante é `db, nil`. Esse corpo não seleciona um fornecedor específico de banco. [sqlx.go:640–651](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L640-L651)

`MustConnect` declara `*DB`, chama `Connect`, entra em pânico com seu erro não nulo e retorna o objeto no outro caminho. Não acrescenta um resultado de erro à própria assinatura. A política de pânico é a diferença visível em relação ao invólucro com dois resultados. [sqlx.go:654–660](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L654-L660)

## 3. Auxiliares de consulta retornam estado e escrevem nos destinos

`Preparex` chama `p.Prepare(query)`. Um erro retorna `nil, err`; o outro caminho constrói `&Stmt{Stmt: s, unsafe: isUnsafe(p), Mapper: mapperFor(p)}` e o retorna com `err`. A definição fornecida mostra preparação e construção do invólucro, sem varredura de linhas ou execução da consulta. As duas chamadas auxiliares exigem evidência própria para seu comportamento interno. [sqlx.go:663–669](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L663-L669)

`Select` declara um resultado `error`. Chama `q.Queryx(query, args...)`, retorna imediatamente um erro de abertura e então registra `defer rows.Close()`. Sua expressão final é `scanAll(rows, dest, false)`. Os resultados são encaminhados a `dest`; essa assinatura não retorna um slice de resultados. A implementação do auxiliar de leitura não está incluída aqui. [sqlx.go:676–684](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L676-L684)

`Get` também declara `error`. Atribui `q.QueryRowx(query, args...)` a `r` e retorna `r.scanAny(dest, false)`. O corpo fornece um destino a um auxiliar; não retorna um valor de linha, não comprova unicidade dos dados do banco nem expõe a implementação do auxiliar. [sqlx.go:691–694](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L691-L694)

## 4. A execução de arquivo tem limites distintos de falha

`LoadFile` declara `(*sql.Result, error)`. Chama `filepath.Abs(path)` e depois `ioutil.ReadFile(realpath)`; qualquer um desses erros retorna `nil, err` antes da execução. Fornece `string(contents)` a `e.Exec` uma vez, sem argumentos adicionais nessa chamada, e retorna `&res, err` mesmo quando essa execução informa erro. O código não contém um laço para dividir instruções SQL. A análise ou execução de múltiplas instruções depende da implementação invocada. [sqlx.go:707–718](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L707-L718)

`MustExec` passa `query, args...` a `e.Exec`. Executa `panic(err)` para um erro não nulo e, caso contrário, retorna `res`, cujo tipo declarado é `sql.Result`. Esse contrato pertence a esta definição; não deve ser atribuído à citação do carregador de arquivo. [sqlx.go:722–728](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L722-L728)

## 5. A leitura separa alocação, chamadas e desreferência

`SliceScan` primeiro solicita `r.Columns()`. Esse caminho de erro retorna `[]interface{}{}` com o erro. Aloca um slice `values` com o tamanho da quantidade de colunas e preenche suas entradas com `new(interface{})` antes de chamar `r.Scan(values...)`. Um erro nessa leitura retorna o contêiner atual antes que esta função execute seu laço explícito de desreferência. No caminho restante, substitui cada entrada pelo valor apontado e retorna `values, r.Err()`. A chamada de leitura é atribuída a `err`; ela própria não retorna o slice de resultados. [sqlx.go:805–828](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L805-L828)

`MapScan` obtém os nomes das colunas, aloca destinos com ponteiros e chama `r.Scan(values...)`, retornando qualquer erro anterior antes de seu laço de atribuição. O laço escreve `dest[column] = *(values[i].(*interface{}))` na ordem das colunas; depois a função retorna `r.Err()`. Nomes repetidos de coluna atribuem novamente à mesma chave do mapa; esse laço não contém rejeição de nomes duplicados. Ele também não inicializa o mapa do chamador nem verifica se é gravável. [sqlx.go:837–859](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L837-L859)

## 6. Auxiliares de reflexão expõem um contrato limitado

`baseType` atribui `reflectx.Deref(t)` novamente a `t` e compara `t.Kind()` com `expected`. Uma diferença retorna `nil` e um erro formatado; o outro retorno é `t, nil`. O auxiliar de desreferência é chamado, mas não definido neste trecho. Não há tratamento local de entrada nula nem recuperação de pânico do auxiliar. [sqlx.go:1012–1018](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1012-L1018)

`fieldsByTraversal` aplica `reflect.Indirect(v)` e rejeita um tipo que não seja struct com `argument not a struct`. Para um percurso vazio, armazena `new(interface{})` e continua. No outro caminho, obtém `f` por `reflectx.FieldByIndexes(v, traversal)` e armazena `f.Addr().Interface()` quando `ptrs` é verdadeiro ou `f.Interface()` no outro caso. Retorna `nil` após o laço. Comprimento do slice de destino, possibilidade de obter endereço e comportamento do auxiliar não são validados por essas guardas explícitas. [sqlx.go:1026–1045](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1026-L1045)

`missingFields` percorre `transversals` na ordem de entrada. Sua primeira entrada com `len(t) == 0` retorna esse índice e `missing field`; concluir o laço retorna `0, nil`. Um índice zero acompanhado de erro nulo é a forma visível de sucesso, sem indicar ausência no primeiro campo. Nenhuma propriedade de unicidade é verificada. [sqlx.go:1047–1054](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1047-L1054)

## Evidência e limites

As definições citadas foram inspecionadas estaticamente. Nenhuma aplicação, banco, servidor ou suíte de testes do projeto externo foi executada para estabelecer comportamento em execução. Auxiliares externos exigem sua própria fonte e suas premissas. Estes capítulos ampliam e corrigem rascunhos de pesquisa; não foram colocados no catálogo público. Licenças das fontes e citações/hashes exatos estão preservados na evidência da campanha.

Licença do projeto fonte: [LICENSE](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/LICENSE). O texto exato da licença e seu checksum estão preservados com a evidência da fonte.
