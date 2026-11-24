# Métodos de requisição Rails: responsabilidade dos getters, memoização e busca de símbolos

Correção escrita pelo Codex e revisada contra a fonte, pendente de aprovação do proprietário. Fonte: actionpack 8.1.4 instalado, com checksum exato do arquivo na [evidência de fonte](source-excerpts.json). Casos reais do agente local: rails-baseline e rails-hinted.

## Nomes parecidos não identificam o mesmo corpo

O arquivo inspecionado declara `ActionDispatch::Request`. Quatro métodos próximos têm expressões deliberadamente diferentes: `request_method`, `request_method_symbol`, method e `method_symbol`. O baseline real recebeu intervalos parciais dos corpos, e um braço posterior com metadados léxicos forneceu os nomes que os continham. Esse braço ainda atribuiu a busca do método original a `request_method`. Informação estrutural correta de responsabilidade não tornou a explicação fiel ao corpo selecionado.

Esta correção amplia a evidência para incluir cabeçalhos dos métodos, construção da tabela de busca e `check_method`. A identidade do pacote é a dependência instalada actionpack 8.1.4 junto do checksum exato da fonte. Não é uma revisão Git de aplicação. O experimento de inspeção de fonte não invocou esses métodos de requisição nem iniciou servidor Rails; o uso comum do framework pelos testes autorizados do backend é uma atividade separada.

## O método visível à aplicação delega por super

O corpo de `request_method` é `@request_method ||= check_method(super)`. Quando o valor armazenado é verdadeiro, a expressão o reutiliza. Caso contrário, avalia a delegação super e a chamada de validação mostradas antes de atribuir o resultado. O corpo selecionado não lê diretamente `rack.methodoverride.original_method` ou `REQUEST_METHOD`. Atribuir essa busca explícita de duas chaves a esse método transfere código de um método vizinho.

O comentário próximo descreve o método visível à aplicação, possivelmente sobrescrito. O próprio corpo delega a obtenção da entrada à cadeia superior. Sem a implementação ancestral e o despacho real do receptor, esta inspeção não estabelece qual método superior fornece o valor ou se ocorreu sobrescrita. A expressão de memoização também não comprova exatamente uma avaliação para todo valor armazenado possível: false e nil não satisfazem seu caminho de cache verdadeiro.

## O caminho de método original também tem uma alternativa reflexiva

A declaração de method aceita `*args`. Seu ramo sem argumentos é protegido por `args.empty?` e memoriza uma chamada `check_method` em `@method`. Dentro dela, a primeira expressão é `get_header("rack.methodoverride.original_method")`, com `get_header("REQUEST_METHOD")` escolhido pela alternativa escrita com ||. É uma escolha pelo valor lógico dos resultados, não um teste explícito de presença de chave. Uma String vazia é verdadeira no Ruby comum e, portanto, não seleciona automaticamente o segundo operando.

Quando há argumentos, esse corpo alcança super sem argumentos escritos explicitamente. O comentário associa o caminho a `Object#method` para depuração, mas a implementação seguinte efetiva depende da cadeia de ancestrais em execução. Preservar a delegação escrita é mais seguro que prometer um resultado reflexivo específico para todo receptor. Essas chaves da fonte pertencem ao acesso ao ambiente de requisição; seus nomes não estabelecem, por si só, cabeçalhos literais de rede. Os quatro corpos selecionados também não demonstram invalidação automática do cache após alterações arbitrárias no ambiente.

## Buscas de símbolos preservam o getter escolhido

O corpo de `request_method_symbol` avalia `HTTP_METHOD_LOOKUP[request_method]`. O corpo de `method_symbol` avalia `HTTP_METHOD_LOOKUP[method]`. Trocar essas expressões em português não é tradução equivalente: cada busca obtém sua chave por uma chamada escrita de método diferente. Nenhum dos métodos de símbolo tem atribuição própria com ||= no corpo mostrado, embora os getters subjacentes tenham seus campos separados de memoização.

O código fornecido de construção da tabela percorre `HTTP_METHODS`, converte cada String de método listado em minúsculas, substitui hífens por sublinhados e converte o resultado em símbolo antes de atribuí-lo sob a chave String original. Isso explica o mapeamento escrito de representação. Não estabelece uma tabela global imutável nem comprova que receptores arbitrários em execução não possam sobrescrever as operações participantes.

## A validação retorna o nome de entrada em vez do símbolo mapeado

O helper `check_method` recebe name. Para entrada verdadeira, avalia `HTTP_METHOD_LOOKUP[name] || raise(ActionController::UnknownHttpMethod, ...)`. Depois desse condicional, a expressão final é name. Assim, o caminho mostrado de validação bem-sucedida retorna seu nome de entrada; não retorna o símbolo da busca apenas porque ela foi usada como teste. Entrada falsa ignora esse condicional e alcança a mesma expressão final.

Essa distinção conecta getters e wrappers de símbolos sem juntar suas responsabilidades. O baseline parcial original omitiu esses detalhes de helper e tabela, e sua resposta em português também substituiu um getter pelo outro. O capítulo corrigido em EN/PT registra corpos separados, guardas de valor lógico, expressão de retorno e limites de execução não resolvidos. Continua sendo um candidato experimental revisado, sem integração de metadados em produção, treinamento neural ou aprovação automática como gold.

