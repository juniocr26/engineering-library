import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 047 — alvo Rails aceito tecnicamente; tokenizer ainda inconclusivo

O checkpoint 033 restaurou 4.039 arquivos regulares com hashes e modos conferidos e reproduziu 34 grupos finitos. O consumidor Rails verificou o arquivo público inteiro, quatro trechos, cinco propriedades lexicais de método, duas respostas históricas e dois links documentais. A pós-nota dos quatro relatórios foi reconstruída pelo script arquivado e seus recibos laterais. A revisão v2 fecha G9 e aceita tecnicamente o par Rails original, sem alterar seus bytes e sem validar execução do actionpack em Ruby 2.6 ou binding real dos métodos.

O inventário v11 registra 24 pares relacionados de versões documentais: 21 aceitos tecnicamente, um inconclusivo por citação e dois com falha de atribuição histórica. A manutenção interna continua separada. O lote v11 mantém três pares públicos principais e onze complementares, 14 no total. A nova identidade Rails é pacote instalado actionpack 8.1.4 mais checksum de fonte; não foi inventado um commit Git. Publicação, treinamento e Gold continuam sem aprovação. O registro v10 contempla as 16 métricas solicitadas e conserva denominador zero para novos ensaios neurais locais.

Uma verificação adicional examinou a possibilidade de comparar vocabulário e merges completos do tokenizer candidato com os metadados GGUF já preservados. O candidato continua não selecionado e não aprovado. O manifesto público previamente fixado declara tokenizer.json com 17.209.920 bytes e SHA-256 6b9e4e7fb171f92fd137b777cc2714bf87d11576700a1dcd7a399e7bbe39537b. Foi congelado um protocolo de leitura de metadados, com limite de 20 MiB, uma tentativa e nenhuma instalação, execução de tokenizer, inferência ou download de tensores.

A tentativa falhou na resolução de DNS antes de obter resposta ou conteúdo. A exceção URLError, o endereço público fixado e o resultado foram preservados. Os dois caminhos de cache examinados não estavam disponíveis, e os metadados locais selecionados não incluem esse JSON completo. Portanto, vocabulário e merges do candidato não foram comparados; não houve promoção de critério de fine-tuning. A igualdade anterior de template e tokens especiais continua um resultado estático limitado, sem comprovar tokenização efetiva, normalização, padding, stop, base treinável ou autorização de piloto. A mesma tentativa não será repetida sem mudança de estado.

A campanha permanece ativa e ainda não atingiu aproximadamente 12 horas. Novas chamadas do modelo local e atualizações de otimizador seguem em zero; o uso de GPT/Codex é distinto e não nulo, com custo monetário total desconhecido. A próxima etapa útil continua a revisão de alvos originais e a consolidação de evidência, sem alterar produção, UI, testes permanentes, repositórios externos ou Git.
'''
j=p/'root-report-bundle-progress-047';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v47.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
