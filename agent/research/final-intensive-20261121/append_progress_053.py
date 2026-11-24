import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 053 — alvo DuckDB e inventário temporário explícito

O par original completo DuckDB BOOLEAN factory passou G1–G9 no escopo estático declarado após o checkpoint 037. Cinco arquivos públicos fixados por Git e seis trechos originais foram conferidos. A declaração do cabeçalho estabelece static Value BOOLEAN(bool); Value(LogicalType) é um construtor separado que move o tipo e inicia is_null como true. A factory escreve o payload bool e depois is_null=false, retornando Value. A tabela true/false apresenta duas derivações de fonte, não testes de banco. O construtor de conversão LogicalTypeId consulta informações internas; não foi inferida ausência de exceções/alocação nem desempenho de elisão. Não houve parser, compilação ou execução DuckDB.

A resposta histórica real contém cinco itens, mas dois fatos bilíngues distintos: o fato do construtor LogicalType se repete quatro vezes. O primeiro chama a factory de construtor nas duas línguas; suas observações sobre armazenamento e nulidade continuam corretas. A repetição foi preservada, sem contar cinco fatos independentes ou alterar a pontuação histórica.

O checkpoint 037 restaurou 4.346 arquivos regulares, arquivo compactado de 112.632.389 bytes e 38 grupos finitos de consumidores. O consumidor DuckDB verificou os dois documentos, seis trechos, resposta histórica e tabela conceitual. As quatro notas dos relatórios foram reconstruídas. A auditoria v15 registra 31 versões relacionadas: 27 aceitas tecnicamente, uma lacuna de citação e três falhas históricas de atribuição. O lote v15 reúne 20 pares públicos, três prioritários e 17 suplementares; o helper interno permanece separado. Publicação, Gold e treinamento seguem sem aprovação. A reconciliação v14 cobre as 16 métricas sem criar taxa neural para zero novas chamadas locais.

O inventário temporário v1 leu somente 36 raízes declaradas pelos checkpoints bem-sucedidos, sem varrer /tmp genericamente ou modificar os arquivos. Encontrou 82.858 entradas restauradas com hashes atuais iguais aos manifestos e 6.027 saídas adicionais dos consumidores; nenhuma entrada declarada estava ausente. O fluxo JSONL preserva caminho, tamanho, hash e finalidade por arquivo. Isso é observação atual de recuperação local, não imagem da máquina, backup remoto ou certificação de crash/Windows/modelo/otimizador.

O inventário principal corte015 contém 4.000 arquivos, sendo 3.857 de pesquisa, com caches/binários ignorados incluídos. Classifica explicitamente o arquivo, manifesto e sidecar do checkpoint031 como falha antes da extração, sem consumidores ou recuperação bem-sucedida. O corte exclui seu próprio arquivo e acréscimos posteriores por construção finita. Os dados originais e fontes externas continuam preservados. A campanha permanece ativa antes de aproximadamente12horas reais.
'''
j=p/'root-report-bundle-progress-053';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v53.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
