# engineering-library: Checklist de conclusão do repositório

Revisão estática em 2026-10-10; sem execução runtime. Itens marcados indicam documentação concluída, não funcionalidades entregues ou lacunas encerradas.

- [x] Inventário: documentação e código/configuração/testes inspecionados; inventário original no manifest da biblioteca.
- [x] Reestruturação: categorias equivalentes por idioma; IDs/histórico ADR preservados; arquivos exigidos por ferramentas mantidos.
- [x] Revisão de conteúdo: mecanismos, contratos, alternativas, falhas e limites de evidência explicados.
- [x] Cobertura bilíngue: páginas mantidas equivalentes en/pt-BR; históricos identificados explicitamente.
- [x] Navegação: README e catálogo por idioma alcançam cada documento mantido.
- [x] Cobertura Engineering Library: explicações completas e respostas substanciais preservadas/ampliadas.
- [x] Validação de links/anchors/numeração: verificação final sem erros; 18 warnings de links restritos de fixtures registrados no relatório da biblioteca.

## Evidência inspecionada

- [tools/check_docs.py](../../../tools/check_docs.py)
- [tools/test_check_docs.py](../../../tools/test_check_docs.py)
- [tools/docs_manifest.json](../../../tools/docs_manifest.json)

## Cobertura de entrevista e contraparte na biblioteca

Propósito da coleção; dossiês/entrevistas com evidência; fluxos independentes; trade-offs; validação somente leitura/parser/segurança/testes.

[Collection interview / Entrevista da coleção](../interviews/engineering-library.md) | [Foundations / Fundamentos](../interviews/foundations.md)

## Aplicabilidade das categorias

| Categoria | Tratamento / justificativa |
| --- | --- |
| api | Não aplicável: sem API runtime; contrato CLI/JSON no guia do validador. |
| database | Não aplicável: sem armazenamento persistente. |
| docker | Não aplicável: sem topologia de contêineres. |
| payments | Não aplicável: pagamentos ausentes. No Payment Lab, conciliação/Stripe são apenas direção futura. |
| deployment | Distribuição de arquivos/ferramenta; sem serviço implantado ou publicação neste escopo. |
| security | Política de segurança do validador documentada no guia e entrevista. |
| observability | Findings JSON estruturados, sem métricas runtime. |
| integrations | Apenas links de evidência; fluxos das aplicações documentados separadamente. |
| adr | Sem série ADR histórica; escolhas/trade-offs observados ficam junto à arquitetura ou explicações do validador, sem inventar histórico. |
| benchmarks | Não aplicável: sem medições de desempenho verificadas adequadas a gráficos; nenhuma executada. |

Categorias presentes no índice contêm conteúdo mantido; categorias tratadas em outros locais não recebem pastas vazias. ADR/comparações conservam histórico; nenhuma motivação ou data histórica nova foi inventada.

## Lacunas restantes dependentes de evidência

Equivalência semântica/completude exigem revisão humana; Markdown complexo/corridas adversariais são limites; links externos não verificados.

## Integração durável — Marco 3.3

[Decisões contextuais, jitter sem viés, pausas separadas, manutenção finita e cancelamento](../architecture/durable-failure-policy.md). Integração implementada e testada em infraestrutura isolada; rollout compartilhado permanece pendente. Descrições anteriores mantêm escopo histórico. Scanning geral fica em 3.4, replay em 3.5 e fechamento em 3.6.
