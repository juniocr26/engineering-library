# Direção futura e questões de projeto

[Índice de arquitetura](index.md) · [Implementação atual](current-implementation.md)

<!-- reading-section: future-direction-1 -->
## Base implementada

Já existem catálogo, leitor bilíngue, busca, anotações compartilhadas, rascunhos Ollama locais, acesso ao filesystem do host, ciclo explícito de projetos e publicação recuperável. Propostas anteriores de introduzir inferência local são históricas. O gerador normal produz resumos limitados, não todos os capítulos de um livro revisado.

<!-- reading-section: future-direction-2 -->
## Qualidade e avaliação

A próxima campanha de qualidade deve ser delimitada separadamente pelo proprietário. Verificações atuais de evidência/schema/propriedade não estabelecem verdade semântica, tradução equivalente, cobertura útil ou qualidade editorial final. Alterações propostas em prompts, skills, datasets, modelos ou fine-tuning precisam de evidência e autorização próprias. Preserve pesquisa, checkpoints e aprendizado existentes; não se afirma fine-tuning neural concluído.

<!-- reading-section: future-direction-3 -->
## Acesso e portabilidade

A instalação tem anotações compartilhadas e gerenciamento local de desenvolvimento, não identidade pública. Política de produção, exposição externa e propriedade individual exigiriam desenho explícito. Adapter Windows nativo não está implementado; o ambiente documentado é WSL2. Cobertura mais ampla, integração de recuperação e garantias de desempenho são questões para validar, não aceitações atuais.

Veja [decisões e compromissos](decisions.md) e [limitações do MakeDocs](../training/local-documentation-command.md). Preserve relatórios datados como histórico, sem transformar resultados antigos em verificações atuais.
