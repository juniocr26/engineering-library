# Ferramentas de servidor: deploy protegido e custódia runtime

## Arquitetura de servidor — 16/11/2026

A orquestração mantém limpeza protegida de artefatos regeneráveis e preserva armazenamento MongoDB, MySQL e Redis em ambas as respostas à pergunta existente. Verificações de pais, entradas aninhadas e caminhos resolvidos impedem alvos indiretos; a ação antiga de remoção MongoDB é rejeitada. Retirar comportamento destrutivo do script não excluiu diretórios existentes. Overlays de servidor selecionam bancos gerenciados externamente; desenvolvimento mantém infraestrutura local.

[Estado operacional e limites](../operations/index.md) · [Interface de conexão](../env/index.md)

Inspeção do código: 04/11/2026. Comportamento implementado é distinto de verificação executada e homologação no provedor.

Orquestração Bash com guardas Python para quatro aplicações de servidor: Hub, Portal, Carteira e Cofre. O atualizador valida raízes/estado Git, coordena o bloqueio de auditoria, atualiza branches selecionadas, provisiona entradas runtime existentes, faz builds sequenciais, verifica prontidão e executa limpeza restrita. Não existe rollback automático de todos os projetos.

## Fronteiras e implementação detalhada

O capítulo privado de origem mantém fluxos, persistência, autorização, falhas e limitações atuais. A centralização separa este resumo conceitual dos detalhes operacionais.

- [Ferramentas de servidor: deploy protegido e custódia runtime](../../../../../acesso-servidor/docs/pt-br/architecture/current-implementation.md)
- [Contratos implementados](contracts.md)
