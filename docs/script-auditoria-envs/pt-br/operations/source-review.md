> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — script-auditoria-envs

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `script-auditoria-envs/audit-envs.py`
- `script-auditoria-envs/env_sync.py`
- `script-auditoria-envs/env_apply.py`
- `script-auditoria-envs/tests/test_selected_directory.py`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

O mapa e a entrevista antigos fornecem explicações de preservação literal, backup e escrita parcial. Não foram adotadas afirmações antigas de análise de uso no código ou de auditoria do portal apenas futura. A CLI atual inclui aplicação de proposta no diretório selecionado; a integração com o Portal exige inspeção do executor como autoridade separada.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/script-auditoria-envs.md`
- `engineering-library_old/docs/pt-BR/interviews/script-auditoria-envs-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Recuperação após crash, corridas com editores não cooperantes, ACLs nomeadas em cada filesystem e ativação completa dos consumidores permanecem sem validação. A CLI não foi executada sobre configuração real.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)
