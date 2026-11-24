# Modernização documental VivaBem — 04/11/2026

## Escopo e evidência

Os nove repositórios imediatos foram inspecionados e atualizados: `vivabem`, `carteira-digital`, `cofre-paciente`, `hub-vivabem`, `vivabem-android`, `engineering-library`, `acesso-servidor`, `criptografia-lib`, `script-auditoria-envs`. Metadados de ferramentas da raiz foram classificados sem inventar outra aplicação. Dependências, assinatura, diretórios secretos e dados runtime gerados foram excluídos. Não foram lidos conteúdos dotenv/credenciais/dados runtime.

Quatro raízes externas de portfólio foram resolvidas pelo manifesto existente. Seus repositórios não foram alterados; somente referências no catálogo privado foram reparadas.

## Documentação resultante

Cada projeto tem capítulo atual sustentado no código e contrato de configuração, ligados à navegação/README existentes. Cadastro/perfil/atendimento do Portal, fábricas/enum/Orders/reconciliação da Carteira, coleções/exclusão/limpeza do Cofre, autenticação/roteamento/prontidão Hub, TWA/build/assinatura Android, envelopes criptográficos, guardas de deploy e sincronização de ambiente possuem fronteiras e limitações explícitas.

A tabela antiga de boleto/12 casos foi substituída pelo mapeamento real de 11 casos. Processamento atual de compra/webhook substitui a descrição obsoleta de placeholder. Simulador Pix local é distinto de aprovação do provedor. O histórico Elo não é homologação ativa ou inelegibilidade permanente. ADRs/revisões históricas foram preservados e afirmações superadas sinalizadas; classes removidas viraram caminhos históricos, não links ativos quebrados. Nenhum documento preexistente foi excluído.

O catálogo mantém a organização real `docs/<slug>/{en,pt-br}`, separação privado/público, bios, IDs canônicos e assets compartilhados. Detalhe operacional de origem e síntese conceitual central são vinculados, sem espelhamento indiscriminado. Projetos privados mantêm referências de testes backend em Operações, respeitando a política existente do validador; capítulos de origem usam a categoria convencional Testes.

## Cartões, idiomas e diagramas

As quatro linhas de cartões fornecidas coincidem com o guia oficial Orders consultado em 04/11/2026. Estão marcadas TEST DATA ONLY — NEVER USE IN PRODUCTION. Cenários oficiais por titular estão separados de Pix. As quatro novas capturas não foram anexadas: não se afirma comparação visual ou novo asset dessas imagens. Imagens existentes anonimizadas de webhook foram reaproveitadas.

Capítulos novos/atuais têm equivalentes inglês/português brasileiro; a versão inglesa ausente do histórico de dashboards foi criada e ligada. Caminhos canônicos/identificadores técnicos foram preservados. É paridade técnica redigida, não certificação independente de tradução. Dois blocos Mermaid localizados descrevem o mesmo fluxo financeiro implementado; não houve nova imagem raster ou asset de UI.

## Verificação

Executado em 04/11/2026 sem iniciar aplicações:

| Check / Verificação | Result / Resultado |
| --- | --- |
| Portal PHPUnit | 23 cases / casos, 77 assertions / asserções: PASS |
| Wallet PHPUnit | 55 cases / casos, 157 assertions / asserções: PASS |
| Cofre PHPUnit | 21 cases / casos, 52 assertions / asserções: PASS |
| Crypto standalone | 292 security assertions / asserções de segurança: PASS |
| Documentation-tool unittest | 28 tests / testes: PASS |
| Hub Node suite | Not executed / Não executada: host Node unavailable / ausente |

O Portal reutilizou PHPUnit existente na Carteira porque seu runner local está ausente. Nenhum teste/dependência foi alterado. Percentual não foi medido; Xdebug/PCOV indisponível. Fronteiras simuladas verificam contratos selecionados, não aceite do provedor ou produção.

O validador estático do catálogo passa sem erros, incluindo links/imagens locais, âncoras, alcance e paridade de caminhos. Foram reparadas 711 referências centrais após a separação dos workspaces. A validação dos documentos de origem não tem erros nos nove repositórios locais; restam 37 referências quebradas anteriores em repositórios externos (11 go-image-optimizer, 17 payment-reconciliation-lab, 9 url-shortener). Estão fora do escopo de escrita/tarefa e não foram ocultadas por mudança de regras do validador. Avisos de caminhos restritos são verificações de metadados; URLs externas não foram rastreadas exaustivamente.

```sh
python3 -B tools/check_docs.py --discover-only
python3 -B tools/check_docs.py
python3 -B tools/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Execute na Engineering Library. `check_docs.py` retorna erro enquanto persistirem falhas nas origens externas; `check_catalog.py` é o resultado central sem erros. Nenhum deles altera fontes ou exige Docker.


Contagens estáticas finais: 730 Markdown no catálogo, 4533 links locais, zero erros e 26 avisos de referências restritas; validador de origem: 798 documentos em 13 mapeamentos, zero erros nos nove repositórios locais, 37 erros externos e 28 avisos de caminhos restritos. `git diff --check` passou nos nove repositórios. A varredura das adições não encontrou padrões de chave privada/token do provedor/chave AWS; padrões não comprovam sigilo universal. Inventário completo: 60 criados, 340 modificados, zero removidos; nenhuma alteração não documental.

## Limitações restantes

Não houve homologação completa do provedor, aceite débito real, filas/bancos/notificações reais, integração HTTP completa, dispositivo/build/assinatura Android, runtime Rails/Next ou deploy. A omissão conhecida de claims temporais JWT no Portal continua defeito de produção fora deste escopo documental. Relatos históricos não foram promovidos a resultados atuais. Nenhum comportamento de aplicação/esquema/configuração/teste/infraestrutura, segredo, histórico Git, stage, commit ou publicação foi alterado.

## Inventário completo de arquivos

[Created, modified and removed files by repository / Arquivos criados, alterados e removidos por repositório](../../en/operations/documentation-modernization-2026-11-04.json).
