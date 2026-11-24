# SQLX: binding nomeado antes da execução da consulta

Este capítulo cobre fontes públicas selecionadas de `jmoiron/sqlx` na revisão `41dac167fdad5e3fd81d66cafba0951dc6823a30`. O tema é o binding nomeado ad hoc, dependências de mapeamento e placeholders e os invólucros de execução direta. Ciclo de vida de instruções preparadas, leitura de resultados, transações e comportamento de drivers concretos ficam fora do escopo. O módulo declara `github.com/jmoiron/sqlx` e uma diretiva Go 1.10 em `go.mod`; essa diretiva não demonstra compilador ou runtime instalado. A família tem dezesseis registros históricos de desenvolvimento, portanto não é uma avaliação de família independente.

O aviso MIT fixado em `LICENSE` foi preservado. Este candidato de pesquisa escrito manualmente está isolado do catálogo ativo, não é alvo de treinamento aprovado pelo proprietário e não autoriza publicação ou treinamento. Nenhum banco, credencial ou registro privado de aplicação foi acessado.

## Entradas públicas e limite da execução

A função de pacote `Named` chama `bindNamedMapper` usando `QUESTION` e o mapper do pacote (`named.go:417-435`). Retorna uma string de consulta, argumentos posicionais e um erro; não recebe um identificador de banco do qual possa selecionar o formato do driver. A função de pacote `BindNamed` recebe um tipo de binding explícito e está marcada como obsoleta na fonte selecionada. Evidência: `named.go:408-412`. Já o método de nome semelhante `DB.BindNamed` usa o nome do driver e o mapper do objeto de banco (`sqlx.go:300-303`). Essas entradas não devem ser confundidas.

Os métodos de conveniência `DB.NamedExec` e `DB.NamedQuery` encaminham para os invólucros do pacote (`sqlx.go:305-315`). Esses invólucros usam `BindType(e.DriverName())` e `mapperFor(e)`, retornam um erro de binding antes da chamada selecionada ao executor e então delegam a `e.Exec` ou `e.Queryx` (`named.go:441-458`). São APIs de execução, não apenas auxiliares de formatação. A interface `Ext` combina capacidades de binding, consulta e execução (`sqlx.go:89-101`); essa fonte não determina efeitos ou resultados do driver concreto.

Essa afirmação trata das chamadas explícitas no caminho selecionado da biblioteca, não de uma garantia global de ausência de entrada/saída ou de pureza. Métodos de interfaces personalizadas e callbacks de mapeamento continuam sendo limites comportamentais separados.

## Formato do driver e compilação dos nomes

O registro de binding começa com padrões de drivers e pode ser alterado por `BindDriver`; um nome de driver não registrado resulta em `UNKNOWN` (`bind.go:15-54`). No compilador de nomes selecionado, esse caso desconhecido usa a forma com interrogação, sem demonstrar suporte ao driver ou rejeitar todo nome não registrado. O auxiliar público de binding do pacote também seleciona deliberadamente essa forma. Um invólucro específico de banco seleciona a partir do registro, mas execução válida ainda depende do driver e da consulta.

O compilador percorre bytes, coleta cada ocorrência de nome de parâmetro em ordem e emite um placeholder conforme o tipo selecionado (`named.go:331-405`). Ocorrências repetidas não são deduplicadas. Existem caminhos específicos para dois-pontos duplicados e dois-pontos seguido de igual, mas isso não é um analisador léxico ou validador SQL completo. Os comentários selecionados alertam para o tratamento Unicode por bytes. A rotina separada `Rebind` procura interrogações e as reescreve para formatos selecionados; seus comentários também apontam limites de escape (`bind.go:56-89`). Nenhum auxiliar demonstra a semântica de strings entre aspas, comentários ou instruções SQL arbitrárias.

## Formato do argumento, busca de campos e erros

O despachante distingue mapas com chave string conversíveis, arrays/slices e o caminho padrão de binding de struct (`named.go:152-168,421-435`). Um mapa com chave string ainda precisa ser conversível para a representação esperada. Falha de conversão tem erro retornado; isso não significa que toda outra entrada não suportada ou nula seja protegida uniformemente.

O binding de mapa busca valores na ordem dos nomes compilados. Acrescenta cada ocorrência, inclusive repetições, e retorna erro quando um nome está ausente (`named.go:197-207`). O auxiliar de baixo nível pode retornar os argumentos coletados antes desse nome ausente. O invólucro de binding de mapa retorna a consulta compilada, essa lista e o erro; já o invólucro de struct descarta sua consulta/lista quando recebe erro da busca (`named.go:213-225,304-312`). Um componente de resultado não vazio não deve ser confundido com binding bem-sucedido quando há erro. Os erros selecionados de nome ausente formatam o valor do argumento fornecido; este capítulo registra apenas o comportamento da fonte e usa dados inventados.

O binding de struct desreferencia ponteiros, obtém percursos do mapper e lê os campos correspondentes (`named.go:173-194`). O percurso de reflexão selecionado exige uma struct e pode gerar panic por `mustBe`; o auxiliar de leitura de campos não aloca ponteiros aninhados nulos (`reflectx/reflect.go:181-200,223-227,246-250`). Este capítulo não promete que toda entrada inválida retorne um erro comum nem enumera toda falha de reflexão.

## Estado do mapper e callbacks

O mapper padrão do pacote usa nomes de campos em minúsculas e a tag `db`. A configuração pode variar, e `mapperFor` usa o mapper selecionado do banco/transação quando o argumento é um tipo concreto de banco ou transação suportado; outros tipos seguem o mapper do pacote (`sqlx.go:22-49,146-159`). A configuração do mapeamento é, portanto, uma dependência, não uma propriedade fixa de todo chamador.

A preparação usa mapeamentos em cache mutáveis e locks. O `TypeMap` selecionado consulta seu cache, pode chamar `getMapping` e armazena o mapeamento (`reflectx/reflect.go:104-113`). O mapeamento pode invocar callbacks configurados. Em particular, `parseName` chama o mapper de nome de campo antes de inspecionar a tag (`reflectx/reflect.go:282-319`); uma tag isoladamente não prova que esse callback seja ignorado. Isso explica por que “não chama explicitamente um executor de banco” é uma afirmação mais restrita do que “globalmente livre de efeitos colaterais”.

O desbloqueio do método de cache está escrito depois do mapeamento, sem defer. Não se afirma aqui uma garantia de recuperação do lock após panic de callback recuperado. A campanha não executou uma observação de falha no método original. Comportamento dos callbacks, alterações concorrentes de configuração e sincronização completa do cache ficam fora desta revisão baseada apenas nas fontes.

## Reescrita de arrays e encaminhamento de contexto

O binding de array/slice primeiro compila placeholders com interrogação, rejeita comprimento zero, obtém argumentos de cada elemento e concatena essas listas (`named.go:273-300`). Para vários elementos, tenta repetir um fragmento de valores entre parênteses e então refaz o binding se necessário. O localizador do fragmento e o contador de parênteses podem deixar o SQL inalterado quando não encontram o padrão selecionado ou o fechamento (`named.go:227-268`). É reescrita textual condicional, sem garantir que toda combinação de array e consulta produza SQL válido ou uma operação em lote bem-sucedida.

As variantes com contexto fazem o binding antes de chamar `e.QueryxContext` ou `e.ExecContext` com o contexto (`named_context.go:116-133`). Sua dependência `ExtContext` combina as interfaces de binding e execução com contexto (`sqlx_context.go:26-48`). Não há verificação do contexto mostrada dentro desse caminho de binding. Encaminhar um contexto não prova que o cancelamento impeça todo o trabalho de binding anterior nem estabelece o tempo de cancelamento do driver concreto.

## Exemplo inventado somente de binding

Este fragmento usa um registro genérico inventado e chama a API de binding do pacote se sua função for invocada. Não passa um identificador de banco nem chama um executor. A campanha verificou a sintaxe, mas não invocou o fragmento, resolveu suas importações, verificou seus tipos ou observou um resultado de binding. O comportamento de um mapper personalizado não é testado por esse exemplo.

```go
package examples

import "github.com/jmoiron/sqlx"

func BindWidget() (string, []interface{}, error) {
    return sqlx.Named("SELECT code FROM widgets WHERE id=:id", map[string]interface{}{"id": 7})
}
```

O fragmento exato foi preservado com o registro de sintaxe Go nativo. O produtor identifica Go 1.27.4 e informa explicitamente análise somente de sintaxe, sem execução da fonte; isso não demonstra um compilador correspondente instalado. Uma busca no PATH do host não encontrou compilador Go. Não houve instalação nem tentativa de compilar o projeto upstream.

## Testes escritos e limites das observações

A tabela selecionada de `TestCompileQuery` contém expectativas de placeholders e ordem das ocorrências, e `TestFixBounds` contém casos de reescrita de fragmentos de valores em `named_test.go`. O caso Unicode das linhas 56-65 está comentado. `TestEscapedColons` chama skip explicitamente na linha 125. Descrever esses casos como cobertura ativa aprovada seria falso. O arquivo também contém testes de consultas nomeadas que usam banco; nenhum foi executado nesta campanha.

A campanha usou o parser nativo existente e sem estado para 37 declarações selecionadas nos arquivos de dependência. Isso valida sintaxe/seleção delimitada e preserva citações de fonte, não tipagem do pacote, validade do SQL, efeitos de callbacks ou comportamento do banco. Não houve instalação de SQLX, importação/execução de programa original, conexão/consulta/migração de banco ou execução de suíte upstream.

## FAQ

**O binding do pacote escolhe automaticamente os placeholders do meu driver?** Não. Ele seleciona a forma com interrogação; o método de binding específico do banco usa o registro do driver do objeto e seu mapper.

**O invólucro de execução apenas prepara uma consulta?** Não. Após binding bem-sucedido, o invólucro selecionado chama seu executor. Um erro de binding retorna antes dessa chamada explícita; callbacks e interfaces personalizados arbitrários não são caracterizados globalmente.

**Todo formato de argumento inválido resulta em erro comum retornado?** Não. Alguns caminhos selecionados retornam erros de binding, enquanto caminhos de reflexão podem gerar panic. Entradas nulas e formatos não suportados não têm contrato universal de erro seguro.

**Uma tag de campo evita o callback personalizado de nomes?** Não por si só. O parser de nomes selecionado invoca esse callback antes de tratar a tag.

**Qualquer array não vazio se torna uma consulta em lote válida?** Não. A concatenação de argumentos e a reescrita condicional do fragmento de valores não validam SQL arbitrário nem demonstram aceitação pelo driver.

**Um contexto cancelado necessariamente evita todo o trabalho de binding?** Essa garantia não decorre daqui. Os invólucros selecionados fazem o binding primeiro e passam o contexto à chamada seguinte ao executor; o comportamento do driver e dos callbacks exige mais evidências.

## Preservação e estado

Os snapshots reais de fonte, comentários/testes existentes, registros nativos e os dois arquivos completos de idioma foram preservados. Nenhuma documentação ativa, teste permanente, esquema de aplicação ou repositório externo foi alterado. Revisão completa das fontes e dos dois idiomas é necessária antes de ficar pronto para revisão do proprietário. Aprovação do proprietário, Gold de treinamento, aprendizagem neural, generalização para família independente e integração completa da aplicação não são inferidas deste candidato.
