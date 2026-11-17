# Requisições cifradas com escopo e titularidade de cartões

2026-11-04. Todas as rotas de domínio declaradas são POST com JWT de serviço e vínculo exato de método/caminho/corpo. Links expõem insert/get/update; cartões possuem famílias separadas de crédito/débito; avaliações expõem inserção/IDs avaliados/médias. Rotas bancárias foram retiradas. Débito acrescenta validação de sub delegado contra titular que falta no Use Case base de crédito. Exclusão manual de débito em produção confirma remoção no provedor; crédito não faz a mesma chamada. Essas diferenças são limitações da implementação.

O repositório de origem mantém detalhes e evidências de código; a revisão foi estática, sem acesso a banco ou provedor.

- [HTTP](../../../../../cofre-paciente/docs/pt-br/api/http-contracts.md)
- [Lifecycle / Ciclo de vida](../../../../../cofre-paciente/docs/pt-br/architecture/current-implementation.md)

[Index / Índice](../index.md)
