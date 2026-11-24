# Retomada local — corte V6 de fontes e evidências

Este roteiro registra o corte restaurado às 09:59 UTC de 20/11/2026. Consulte o
relatório final da campanha e o checkpoint mais recente para metadados posteriores.
A restauração foi exercitada em outro diretório da mesma máquina. Ela não comprova
backup remoto, recuperação após perda do disco, cold boot do modelo ou treino.

## O que preservar

Preserve os seis arquivos abaixo, os respectivos `creation-receipt.json` e
`file-manifest.json`, a receita `restore_source_evidence_delta_v6.py` e os
checkpoints posteriores. Os deltas dependem dos componentes anteriores na ordem;
o V6 isolado não contém todas as fontes. Nunca limpe os arquivos antigos para
reduzir o backup: eles preservam versões, falhas e proveniência.

| Ordem | Arquivo a partir da raiz da biblioteca | Bytes | SHA-256 |
|---|---|---:|---|
| 1 | `.local-backups/documentation-intelligence-20261119/source-evidence-recovery-v1/source-evidence.tar.gz` | 315908501 | `4ca675a73f24d18d39d9cab257c9d26860476e871f3d900ef86844c8860e1e95` |
| 2 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v2/evidence-delta.tar.gz` | 64502095 | `30adabed7c9614454dec0ec81ad520bdfc96344c41d25f18a84bd1f1e80ea8aa` |
| 3 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v3/evidence-delta.tar.gz` | 7082627 | `d303cf268fdc6016df0f19ee0b1a77892bd37661b2f70285c97f53e3ca32de24` |
| 4 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v4/evidence-delta.tar.gz` | 7859580 | `3616d18531ee58d136ce8635ec1312e7b8ce837a594f52a5a590fc5445046e4d` |
| 5 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v5/evidence-delta.tar.gz` | 11767034 | `ca1da97490b7f1a46f523bdb115d2048bc8fcd86f57e6876e906c3974f8379f0` |
| 6 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v6/evidence-delta.tar.gz` | 3315397 | `96054ee2abb8af21c5cf943ae86c558287d5e8a934f0422344aece649c8256d8` |

Os caminhos estão sob `.local-backups/documentation-intelligence-20261119/`.
Arquivos ignorados pelo Git não estão automaticamente protegidos por um clone ou
por um futuro commit. Neste trabalho não houve upload nem sincronização remota.
Os hashes detectam alteração contra recibos confiados; não são assinaturas nem
protegem contra adulteração consistente de artefato e recibo juntos.

## Como foi verificado

A partir da raiz `engineering-library`, a receita executada foi:

```sh
python3 .local-backups/documentation-intelligence-20261119/restore_source_evidence_delta_v6.py
```

Este comando é uma receita de verificação, não uma ação automática de retomada.
Ele cria uma nova pasta em `/private/tmp`, lê os arquivos selados na ordem e grava
recibos locais; cada execução consome novo espaço. Não o execute com `python -O`:
as verificações desta receita de pesquisa usam `assert`. Não extraia sobre o
checkout, sobre um store de modelo ou sobre uma recuperação anterior. O ensaio
concluído está em `/private/tmp/el-source-evidence-base-delta-v6-1oz1fzl1`.

O resultado conferiu 8.920 arquivos, 77 versões sobrepostas preservadas por conteúdo,
1.951 itens de conhecimento, 305 registros e 1.271 referências diretas, 77 pares FAQ,
279 intervalos físicos de fonte/588 trechos documentais e 192 documentos do leitor
com 392 arestas. Os 83 arquivos de código/testes coincidem com o corte operacional
V7 que passou 278 testes em macOS e Linux; a receita não repetiu esses testes.
Os caminhos absolutos históricos dos fixtures foram relocados lexicalmente para
a cópia recuperada. Os originais desses fixtures não foram usados como evidência.

## Componentes separados

A cápsula operacional V7 (`operational-recovery-v7/operational-code.tar.gz`) tem
25.293.922 bytes e SHA-256
`ab6fd71e975b0a83c0485f0a816972f7ee19117e0b55ae6d8d8b0d5e914a8678`.
Ela preserva o corte de código testado; os nomes de alguns recibos públicos foram
corrigidos depois. A cadeia V6 sobrepõe os recibos corretos sem reescrever a cápsula.

Pesos, imagem Ollama e runtimes extraídos são componentes separados. O índice das
14 partes do modelo está em `agent/recovery/model-bundle.json`; os caminhos locais
estão em `agent/recovery/manifest.json`. Preservar o JSON sem as partes não permite
reconstruir o modelo. O GGUF tem SHA-256
`dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff`.
Esse hash difere do digest de runtime
`a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
O wrapper legado de metadados também possui identidade própria; não o substitua
pelo namespace nativo apenas porque ambos apontam para os mesmos pesos.

A imagem preservada tem 2.872.640.512 bytes e SHA-256
`18da54da82a8fb31195048d6664559cf582c84bc531f96d8db95a21257bf6f6e`.
Contém as quatro camadas Linux ARM64 verificadas, sem payload amd64. Não houve
`image load` nem serving do store recuperado. Os catálogos V3 e do complemento das
sete árvores restauradas descrevem arquivos separados; não são seus payloads.

## Se uma operação foi interrompida

Uma raiz parcial de candidato é evidência. Preserve-a e o recibo bruto do processo.
Não trate `result.json` existente como conclusão: um dos três ensaios terminou
após essa gravação e antes da resposta do CLI. Não repita uma inferência de estado
incerto. O CLI recusou três tentativas no mesmo caminho; somente novos pedidos
explícitos em novas raízes prepararam candidatos sem apagar as anteriores.
Esses ensaios mataram três processos próprios após gravações sincronizadas, sem
simular perda física de energia ou durabilidade de crash do sistema de arquivos.

Mantenha o backend parado e todas as alterações fora do staging. Esta recuperação
não autoriza publicar, fazer commit, promover dados a gold, treinar, iniciar
serviços ou substituir stores. Fontes e documentação permanecem sujeitas à revisão
do proprietário. O recibo de restauração e o relatório final são posteriores ao
selo V6; a camada final de metadados/checkpoint os preserva separadamente.
