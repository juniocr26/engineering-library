# Contrato de configuração sem valores privados

[Referência de ambiente](index.md) · [Operação e recuperação](../operations/runtime-and-recovery.md)

A configuração atual tem três consumidores: interpolação Compose, processos nos containers e adapter POSIX no host. Eles não compartilham automaticamente todas as variáveis. Uma declaração no código não torna uma entrada globalmente obrigatória.

- Compose exige usuário/senha/banco PostgreSQL e segredo Rails, com portas padrão loopback. O launcher preserva `.env` existente.
- Caminhos nos containers identificam biblioteca/agente montados e endpoints internos. Não são caminhos de origem do host apresentados ao usuário.
- Referências do host são relativas ao checkout da biblioteca. O adapter verifica identidade e limita aquisição/publicação; mudar mounts não é o fluxo normal de cadastro.
- Identidades aprovadas de modelo/skills limitam a geração. Limites, cobertura e publicação não comprovam aceitação editorial ou fine-tuning concluído.
- Startup executa preparação do banco e sincronização do catálogo. Use análise somente leitura quando mutações no banco estiverem fora do escopo.

As [tabelas de ambiente](index.md) registram defaults, faixas e consumidores atuais. Valores efetivos privados, credenciais e caminhos particulares da máquina não pertencem à documentação. Revisões datadas permanecem históricas; os contratos atuais do código prevalecem.
