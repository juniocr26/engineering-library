import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 056 — SQLx aceito, reconstrução tardia e falha de atribuição SDK

Os dois pares originais SQLx In e bindMapArgs concluíram G1–G9 após o checkpoint040. Foram restaurados4.573arquivos regulares, arquivo compactado121.906.400bytes e41grupos finitos de consumidores com resultados esperados. A primeira aplicação da nota posterior foi recusada antes da escrita: progresso055 havia sido acrescentado depois do corte do checkpoint. O preimage do bundle055 coincidiu byte a byte com o prefixo arquivado, e o estado atual coincidiu com seu afterhash. Os dez arquivos do bundle055 foram preservados como sidecar adicional dentro da pasta do checkpoint. Os quatro relatórios finais foram reconstruídos exatamente como prefixo arquivado + payload055 + nota posterior, com hashes e bytes conferidos.

Portanto, a reconstrução final específica do checkpoint040 requer esse sidecar adicional, além do arquivo e do recibo. Não foi declarada recuperação a partir de archive+receipt apenas. A recusa inicial e um SyntaxError do primeiro produtor suplementar, anterior a sua execução, foram preservados. A segunda versão usa os mesmos preimages/payloads e aplicador de acréscimo com recibo. Nenhum histórico foi reescrito.

A auditoria v18 contém37versões relacionadas:32aceitas,1lacuna de citação e4falhas históricas de atribuição já contabilizadas; helper interno separado. O lote v18 reúne25pares públicos,3prioritários+22suplementares. A correspondência v8 mede128referências diretas exatas a64hashes aceitos,68diferentes,101sem referência nos campos selecionados e8registros privados excluídos. Sete arquivos originais seguem idênticos. Esses números não aprovam registros, FAQs, publicação ou Gold. A reconciliação v17 mantém16métricas e zero denominador de novas chamadas locais.

A revisão do alvo original Temporal SDK detectou uma quinta falha de atribuição, ainda fora da auditoria v18: os três baselines reais descrevem criação/retorno da política, sem afirmar explicitamente execução de retries. A frase do original dizendo que misturaram configuração e execução é mais forte que os bytes. O original permanece FAIL_HISTORICAL_ATTRIBUTION, sem apagar as rejeições históricas por guardas omitidas ou aritmética/deadline incorretos. Uma cópia completa EN/PT corrige uma frase por língua e, em v2, ajusta dois links relativos de proveniência por língua para o novo local; v1 com links herdados inválidos permanece não aceita. Código, FAQs e contrato técnico não mudaram. A correção ainda aguarda revisão final e recuperação.

O censo histórico de vínculo de max teve207arquivos conferidos:206Go maisgo.mod. Quatro recibos nativo/consumidor representam dois perfis declarados Darwin/arm64 eLinux/arm64, não quatro ambientes independentes. O SDK tinha157arquivos Go imediatos e78ativos nos perfis. Não houve novo experimento de build/typecheck ou execução SDK. Cinco arquivos Go do alvo passaram gofmt sintático e um controle malformado foi recusado; nove testes foram lidos como fonte, sem execução. O caminho presumido internal_retry_test.go falhou e foi preservado, sem conclusão de ausência global de testes.

A fonte mantém200ms inicial,60s padrão,coeficiente2, guarda de contexto não nulo e deadline estritamente futuro. max(timeout/10,200ms) é piso condicional à resolução predeclarada, não teto20ms nem mínimo com60s. A configuração armazena campos; ComputeNextDelay calcula limites/jitter e outros consumidores invocam operação/espera/cancelamento. O preflight inicial mencionouPython por engano; correção de linguagem Go foi registrada sem mudar critérios ou executar fonte. A campanha permanece ativa antes de12horas reais.
'''
j=p/'root-report-bundle-progress-056';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v56.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
