# Cockpit técnico: capacidades e limites públicos

[Index](../index.md)

## Estado verificado e limites públicos — 11/11/2026

Portal Laravel com Cockpit técnico separado do painel de auditoria. A navegação atual tem Visão Geral, Infraestrutura, RabbitMQ, Bancos de dados, Reconciliações e TracePaw; não há destinos separados de Execuções e Integrações. Observabilidade consulta arquivos retidos sob demanda, com autorização por projeto, filtros, paginação limitada e indicadores de consulta incompleta. O gerador SQL MySQL oferece INSERT/UPDATE/SELECT/DELETE de linhas selecionadas, incluindo chaves compostas verificadas; produz texto para revisão/cópia, sem execução automática.

Os três consumidores declaram e fixam `parceiro-vivabem/tracepaw-lib 0.2.0`; metadados locais também registram essa versão. Canal `tracepaw`, namespace `TracePaw` e arquivos `tracepaw-YYYY-MM-DD.log` são os contratos atuais. Monolog controla formato/rotação/retenção; o gravador JSONL interno é outro adaptador. Logs históricos permanecem intactos.

Inspeção de fonte e metadados locais não confirma imagem Docker, implantação, montagens ou homologação externa. Esta síntese pública omite endpoints internos, topologia, identificadores e regras privadas; contratos operacionais completos permanecem nos repositórios de origem. Não houve sincronização do catálogo no banco.

O acesso técnico é separado do login do produto. Ações administrativas exigem autorização e salvaguardas específicas; geração de SQL não concede privilégios de execução. Consultas de logs usam HTTP sob demanda, sem streaming contínuo. Métricas de severidade, códigos frequentes e evolução diária representam apenas a consulta completa dos arquivos retidos. Consultas parciais não devem produzir totais aparentando completude. A disponibilidade real de cada fonte permanece não verificada. Não há evidência de módulo separado que observe todos os comandos, jobs e eventos Node ao vivo; não confundir operações administrativas auditadas com histórico genérico de saída de execução.

## Query Plan — 12/11/2026

O Database Explorer inclui plano estimado MySQL, execução medida restrita ao ambiente local autorizado e explain MongoDB 7.0 com modos de planejamento/estatísticas separados. Redis não possui equivalente SQL. [Diagnóstico e fronteiras de execução](../database/query-plan.md) explica autorização, read-only por caminho, limites, interpretação e ausência de certificação de runtime.
