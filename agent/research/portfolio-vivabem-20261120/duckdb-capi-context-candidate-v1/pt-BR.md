# API C do DuckDB: propriedade de resultados e limites dos erros

Candidato de desenvolvimento limitado à fonte, sem aprovação do proprietário. A revisão pública fixada é `e41515de6f7efb19b43293ab49cb967cd64ab9f9`, com aviso MIT preservado. Este capítulo trata do header e da implementação C++ selecionados da API C v1, sem abranger a superfície v2 ou uma execução completa do banco. A família já aparece em oito registros históricos do dataset e não constitui holdout independente. Nenhuma consulta, banco, teste do projeto ou programa de exemplo foi executado.

## A fronteira e seu estado

O header público declara as funções voltadas a C e envolve as declarações em `extern "C"` quando incluído por C++. Suas macros padrão de versão da API selecionam 1.5.6; são as macros-alvo do header inspecionado, não uma versão instalada ou lançada verificada. `duckdb_result` contém campos antigos de metadados e um ponteiro `internal_data`; os chamadores recebem a orientação de destruir o resultado com `duckdb_destroy_result`. [H1,H2]

O wrapper de consulta selecionado converte a conexão para `Connection *`, chama `conn->Query(query)` dentro de um bloco try e move o objeto retornado para `DuckDBTranslateResult`. Seu ramo catch-all retorna `DuckDBError`. Esse ramo, por si só, não inicializa a saída do chamador nem atribui uma mensagem de erro. O código selecionado não estabelece uso seguro de conexões ou ponteiros de consulta arbitrariamente inválidos. [Q1]

`DuckDBTranslateResult` pressupõe um objeto de resultado utilizável: desreferencia o ponteiro recebido antes de sua asserção escrita. Se `out` for nulo, o ramo retorna o status a partir de `result.HasError()` sem criar um objeto C de saída. Caso contrário, zera a saída, aloca `DuckDBResultData`, move o resultado para esse objeto, define o marcador do conjunto de resultados e guarda seu ponteiro em `out->internal_data`. Um resultado com erro então fornece `deprecated_error_message` a partir da string do resultado e retorna `DuckDBError`; o caminho normal registra metadados de colunas e retorna `DuckDBSuccess`. Essa é a ordem escrita, não uma garantia geral contra falhas de alocação ou callbacks. [R1]

A declaração interna mantém `result` e `stream` como membros `unique_ptr`. `HasError()`, `GetError()` e `GetErrorType()` delegam ao stream quando presente e, caso contrário, ao resultado. Isso liga o campo C opaco ao proprietário de estado C++ selecionado; não comprova toda transição de streaming nem todo efeito da destruição. [I1]

## Mensagens de erro e limpeza

O contrato público de consulta exige `duckdb_destroy_result` para o objeto de resultado mesmo quando a consulta falha, pois as informações de erro armazenadas também precisam de limpeza. Essa obrigação nominal sobre o objeto de resultado não deve ser ampliada para prometer que toda exceção arbitrária preencheu todos os bytes de saída. O ramo de resultado traduzido com erro e o catch genérico são evidências diferentes. [H3,Q1,R1]

`duckdb_result_error` retorna `nullptr` quando seu ponteiro de resultado ou `internal_data` é nulo. Com dados internos, retorna ausência de mensagem quando `HasError()` é falso; caso contrário, retorna o `c_str()` obtido por `GetError()`. O header afirma explicitamente que essa mensagem retornada não deve ser liberada separadamente e é limpa com o resultado. Trate-a como emprestada e não a retenha como armazenamento próprio após a destruição. `duckdb_result_error_type` possui suas próprias condições de nulo/sem erro, que retornam `DUCKDB_ERROR_INVALID`. Essas condições não estabelecem segurança universal para nulos em outras funções da API. [H4,R3,I1]

A implementação selecionada de `duckdb_destroy_result` primeiro acessa campos do resultado sem uma condição de proteção para ponteiro nulo. Destrói o armazenamento antigo de colunas se presente, deleta o objeto por trás de `internal_data` se presente e depois zera a struct de resultado. Portanto, passar um ponteiro de resultado nulo não é uma conclusão de segurança sustentada por esse código. Zerar a struct não preserva a duração de ponteiros emprestados anteriormente. O header público também documenta efeitos de cancelamento de streaming e transações, mas esses efeitos mais amplos não foram verificados nesta revisão da implementação selecionada. [R2,H5]

## Um fragmento C próprio

Este fragmento pressupõe conexão e string de consulta já válidas. Inicializa seu resultado com zeros, observa uma mensagem emprestada somente antes da limpeza e retorna o status; não cria conexão, inicia servidor nem copia texto de erro para posse posterior.

```c
#include "duckdb.h"
duckdb_state query_with_cleanup(duckdb_connection connection, const char *query) {
    duckdb_result result = {0};
    duckdb_state state = duckdb_query(connection, query, &result);
    if (state == DuckDBError) {
        const char *borrowed = duckdb_result_error(&result);
        (void)borrowed;
    }
    duckdb_destroy_result(&result);
    return state;
}
```

O fragmento efetivo foi verificado com o Apple Clang 21.0.0 existente, contra o header público fixado e copiado, usando C11, `-fsyntax-only` e diagnósticos explícitos de declarações e ponteiros. Não foi linkado nem executado. Isso verifica o uso selecionado de tipos e declarações neste host; não valida banco, comportamento de ponteiros inválidos, segurança completa de exceções, compatibilidade binária ou builds Windows/Linux. [E1]

Quatro controles próprios do compilador tiveram os resultados esperados: o exemplo passou; o nível de ponteiro errado e um identificador traduzido falharam; uma liberação manual deliberadamente indevida do ponteiro emprestado de erro ainda passou no compilador. Esse último controle é rejeitado contra o contrato de propriedade do header. Aceitação pelo compilador não substitui revisão semântica da fonte. [E1,H4]

## Testes escritos e preservação

O teste básico selecionado da API C contém asserções explícitas com resultado nulo para o getter de erro e o getter do tipo de erro. O caso de regressão identificado com a issue #2058 executa SQL inválido em seu corpo escrito, espera `DuckDBError` e chama a limpeza do resultado. Sua redação histórica sobre segmentation fault não demonstra que a fonte atual tenha falhado nesta campanha. Outro teste selecionado contém consultas bem-sucedidas seguidas de limpeza e uma consulta com erro e ponteiro de saída nulo. São instruções de testes inspecionadas; os testes de banco não foram executados. [T1,T2,T3]

Nenhuma documentação, fonte, teste, schema ou catálogo ativo externo foi alterado. Este capítulo elaborado separadamente não substitui, corrige nem reavalia a FAQ neural rejeitada de H32. Snapshots históricos e saídas que falharam continuam preservados.

## FAQ

**Um resultado nominal de consulta com falha ainda precisa ser destruído?** O header diz que sim, incluindo a limpeza do erro armazenado. Isso não comprova que o catch genérico sempre inicializou memória de saída arbitrária. [H3,Q1]

**O chamador deve liberar separadamente o ponteiro da mensagem de erro?** Não. A mensagem é emprestada segundo o contrato do header e limpa com o resultado; limite seu uso à duração suportada. [H4,R3]

**O getter de erro seguro para nulos torna segura a destruição com ponteiro nulo?** Não. A condição de proteção do getter e o acesso inicial a campos no destruidor são caminhos diferentes. [R2,R3]

**O catch-all garante mensagem de erro preenchida?** Não. O ramo selecionado apenas retorna `DuckDBError`; não contém inicialização de saída nem atribuição de mensagem. [Q1]

**Compilar com sucesso comprova propriedade correta?** Não. O controle com liberação indevida compilou, mas contradiz o contrato inspecionado de mensagem emprestada. [E1,H4]

## Evidências e limites

Todos os caminhos são relativos ao repositório público fixado. H1: `src/include/duckdb.h`, linhas 14–20 e 68–85. H2: mesmo header, 832–845. H3: 6509–6525. H4: 6651–6663. H5: 6527–6543. Q1: `src/main/capi/v1/duckdb-c.cpp`, 194–202. R1: `src/main/capi/v1/result-c.cpp`, 350–376. R2: 494–506. R3: 611–627. I1: `src/include/duckdb/main/capi/capi_internal.hpp`, 102–151. T1: `test/api/capi/v1/test_capi.cpp`, 122–132. T2: 696–716. T3: 673–682. E1: `duckdb-capi-owned-c-example-observation-v1.json` isolado e seu protocolo congelado.

Hashes exatos da fonte e snapshots acompanham este candidato. As relações C++ foram revisadas a partir do texto da fonte; não se afirma um build C++ completo nem resultado de parser semântico geral. Os limites de escopo, plataforma e execução valem para o capítulo inteiro. Revisão de fonte, aceitação sintática e revisão bilíngue na mesma campanha não equivalem a aprovação humana independente, gold de treinamento ou autorização de publicação.
