# Compatibilidade das dimensões finais inclui canais

Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.

Repository: opencv; revision: 5d0660acfed08650cafec4876b4792a369a20601; baseline: opencv-shape-contract. [Exact source excerpts](source-excerpts.json).

## O baseline e o limite

A resposta real do agente local identificou a comparação da direita para a esquerda e a regra que permite dimensão de tamanho um. Essas observações eram úteis, mas incompletas. Omitiu as entradas de canais acrescentadas, os contadores de dimensões incrementados e a condição de parada do laço. Em português, traduzir broadcasting como transmissão comum também obscureceu o conceito de dimensões de arrays. Este capítulo mantém broadcasting como termo técnico e descreve o helper selecionado, em vez de uma operação aritmética inteira.

A declaração é `static bool shapesBroadcastCompat(InputArray a, int acn, InputArray b, int bcn)`. Ela retorna uma decisão booleana de compatibilidade. Isso não demonstra alocação da saída expandida, cópia de dados da imagem, escolha de tipo numérico ou execução aritmética. Essas afirmações exigiriam evidências separadas dos chamadores e helpers.

## Os canais entram nas dimensões comparadas

Dois arrays locais de inteiros têm espaço para `MatShape::MAX_DIMS + 1` entradas. As chamadas `a.sizend(asz)` e `b.sizend(bsz)` fornecem os contadores iniciais e arrays usados por este corpo. As instruções seguintes são `asz[ad++] = acn` e `bsz[bd++] = bcn`. Cada uma escreve o número de canais recebido após as dimensões existentes e então aumenta seu contador.

Assim, o primeiro par visitado pelo laço reverso é o par de canais acrescentado. Uma descrição limitada às dimensões espaciais perde uma entrada efetiva da decisão. A fonte não mostra uma guarda separada de igualdade de canais: essas entradas passam pela mesma regra de divergência das demais entradas visitadas. Essa observação não estabelece todos os intervalos válidos de `InputArray` nem a implementação de `sizend`.

## Uma conjunção controla rejeição e percurso

Os índices começam em `ad - 1` e `bd - 1`. Cada iteração decrementa ambos, e o laço continua apenas enquanto os dois permanecem não negativos. Um par visitado rejeita a compatibilidade somente quando suas entradas diferem e nenhuma delas é igual a um. A igualdade permite continuar; um par desigual contendo um também permite continuar. Não há ramo que retorne verdadeiro imediatamente ao encontrar um: pares posteriores ainda podem rejeitar.

Para listas conceituais de dimensões [2, 3] com quatro canais e [3] com quatro canais, as entradas visitadas são os canais iguais e as dimensões espaciais finais iguais. O dois inicial sem correspondente não é visitado por este laço. Trata-se de um percurso derivado da fonte, não de teste OpenCV executado. Ele mostra por que dizer que toda dimensão deve ser comparada exageraria o corpo selecionado.

## O que o retorno final estabelece

Se nenhum par visitado segue o ramo de rejeição, a execução alcança `return true`. Esgotar qualquer um dos índices basta para terminar o laço. Esse fato é mais restrito que uma prova geral de todas as regras de broadcasting em outros pontos do OpenCV. O helper verifica esse alinhamento final e as entradas de canais recebidas sob suas próprias premissas de entrada.

Nenhum benchmark foi executado. Descrições próximas que chamem a verificação de barata não estabelecem tempo constante ou ganho de velocidade medido. O capítulo corrige a resposta preservada do modelo por revisão da fonte; não demonstra modelo modificado, adaptador treinado ou transferência independente em reserva. As identidades exatas da fonte e do baseline permanecem anexadas, e a correção bilíngue continua pendente de revisão do proprietário.

