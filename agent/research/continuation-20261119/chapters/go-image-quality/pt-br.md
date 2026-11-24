# Qualidade JPEG: uma alternativa antecipada não é um limite inferior

Correção experimental revisada na fonte pelo Codex; não é dado de treinamento aprovado pelo proprietário nem documentação publicada da aplicação. Fonte congelada: go-image-optimizer na revisão `48476de6e4450294b7769ab7af90805100bb21b5`, `backend/internal/infrastructure/imaging/compress/compressor.go`. Os braços originais do modelo, `gio-quality-caller` e `gio-quality-helpers`, foram mantidos sem alterações. Seus pacotes de fonte omitiam a constante numérica; este capítulo acrescenta explicitamente essa declaração do mesmo arquivo congelado.

## O wrapper fornece dois argumentos

O método de receptor `Compressor.jpegQuality` não tem parâmetros explícitos além do receptor e retorna um inteiro. Seu corpo inteiro retorna `clampQuality(c.JPEGQuality, DefaultJPEGQuality)`. O campo configurado no receptor é o primeiro argumento; a constante nomeada é o segundo. A expressão de chamada isolada não estabelece o que o auxiliar faz com esses argumentos. Não justifica descrever o segundo como limite inferior nem inventar um número para a constante.

A fonte ampliada fornece `DefaultJPEGQuality = 82`. Também mostra o construtor inicializando o campo de qualidade JPEG a partir dessa constante. Essa evidência sustenta o padrão numérico aqui. Ela não torna retroativamente correta uma resposta do modelo com um número sem suporte no pacote original menor. A resposta com auxiliar inventou 80, embora o número estivesse ausente das declarações selecionadas e o arquivo congelado use outro valor.

## O primeiro ramo ignora os limites posteriores

A declaração do auxiliar é `clampQuality(value, fallback int) int`. Sua primeira condição é `value == 0`, que retorna `fallback` imediatamente. Nenhuma condição posterior é avaliada nesse caminho. Portanto, o parâmetro de alternativa é um resultado substituto para uma entrada sentinela específica. O auxiliar não o valida recursivamente, não o compara com o limite superior e não o reescreve por meio dos ramos seguintes.

Essa ordem invalida um resumo tentador: todo resultado possível do auxiliar genérico estaria entre 1 e 100. Um primeiro argumento zero retorna o segundo mesmo quando ele está fora dessa faixa. Essa é uma consequência do retorno antecipado derivada da fonte, não uma observação de execução de codec. O wrapper JPEG fornece uma constante conhecida dentro da faixa, mas esse fato específico do chamador deve permanecer separado do contrato do auxiliar para argumentos arbitrários.

## As comparações restantes preservam os extremos

Depois do caso zero, `value < 1` retorna `1`. Como zero já retornou, esse ramo cobre entradas inteiras negativas no caminho restante. Em seguida, `value > 100` retorna `100`. A instrução final retorna `value` sem alteração. Entradas nos dois extremos não satisfazem nenhuma desigualdade estrita e chegam ao retorno do valor inalterado. Dizer que a alternativa é a qualidade mínima permitida perderia tanto o comportamento de sentinela exclusivo de zero quanto o ramo de limite inferior.

A resposta com auxiliar continha um subfato correto sobre os casos zero, inferior, superior e inalterado. Outros fatos da mesma resposta inventavam o padrão e generalizavam incorretamente a faixa. O gravador estrutural também recusou uma citação pertencente ao auxiliar que descrevia o chamador. É possível preservar um subfato correto como candidato sem aprovar a resposta inteira nem presumir que a validação do esquema estabeleça exatidão factual.

## O escopo termina antes do comportamento de codificação

Os métodos relacionados `Compressor.webpQuality`, `Compressor.avifQuality` e `Compressor.heifQuality` usam o mesmo auxiliar com seus próprios campos e padrões nomeados. O arquivo declara padrões de 82 para WebP e 60 para AVIF e HEIF. Essa estrutura paralela de chamadas sustenta uma observação sobre a família na fonte; não estabelece que os codificadores interpretem os números de forma idêntica ou produzam a mesma qualidade visual.

O auxiliar de qualidade inspecionado não tem entrada de imagem, resultado de erro, chamada de codec ou comparação de tamanhos em bytes. Não prova taxa de compressão, saída menor, preservação de metadados ou decodificação bem-sucedida. Um comentário próximo declara a intenção de semelhança visual e redução de tamanho para JPEG, mas intenção não é resultado medido em execução. A aplicação não foi executada. Este capítulo corrige papéis de argumentos, proveniência da constante e limites dos ramos, mantendo o comportamento dos codificadores e auxiliares importados fora de sua prova. A revisão EN/PT permanece separada da aprovação do proprietário e de uma futura decisão de criar dados de treinamento.
