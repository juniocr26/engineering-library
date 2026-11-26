# FAQ de aplicação, catálogo e MakeDocs

[Índice da FAQ](index.md) · [Arquitetura atual](../architecture/current-implementation.md)

Revisão atual: 26/11/2026. As respostas descrevem mecanismos inspecionados, não teste adicional de aceitação runtime. IDs existentes foram preservados por compatibilidade.

### Q101 — Por que Rails com frontend Next.js separado?

**Resposta:** Rails cuida da sincronização validada do catálogo, anotações relacionais e coordenação protegida de operações; Next renderiza Markdown e controla layout do livro. HTTP separa responsabilidades runtime. Markdown continua fonte dos capítulos; PostgreSQL armazena metadados/anotações. A separação acrescenta builds, dependências e diagnóstico; não prova superioridade em benchmark ou Clean Architecture.

**Aprofundamento:** O frontend pode dispensar Rails em tudo? Lê capítulos no servidor, mas catálogo/anotações/operações usam Rails. Notas compartilhadas exigem persistência e localizações lógicas, não páginas físicas.

### Q102 — O que Compose reproduz e por que Python no host?

**Resposta:** Compose define frontend, backend, PostgreSQL e Ollama, dependências de health, portas loopback e armazenamento explícito. Supervisor/adapter no host é processo POSIX adicional necessário, gerenciado por `tools/init_dev_env.py`. Adquire código externo e publica docs aceitos sem novos mounts arbitrários. Frontend e backend atualmente montam a biblioteca gravável; código/agente têm restrições próprias.

**Aprofundamento:** Parar containers apaga estado? Stop/down gerenciados preservam armazenamento. Persistência ou startup bem-sucedido não comprova backup/restauração. Não exclua banco, modelos ou recuperação para reparar startup.

### Q103 — O que health verde comprova?

**Resposta:** `/up` comprova resposta Rails e heartbeat obrigatório do adapter naquele instante. Não consulta todos os registros nem valida modelo aprovado, qualidade, dois destinos ou restauração. Health checks PostgreSQL/Ollama/Next também têm escopos limitados. A API do catálogo pode sincronizar metadados, não sendo consulta estritamente somente leitura ao banco.

**Aprofundamento:** Inferência bem-sucedida basta? Não. Evidências devem passar avaliação/propriedade, escritas na biblioteca/workspace devem funcionar e entrega ao host deve concluir. O rascunho publicado ainda exige revisão humana.

### Q104 — Como cadastro, duplicatas e relocação funcionam?

**Resposta:** Referências relativas resolvem a partir do checkout da biblioteca no host. O cadastro verifica identidade e cria metadados/bios sem inferência. Identidade estável, caminhos normalizados, aliases físicos e request IDs evitam duplicatas em retries. Commits raiz identificam linhagem; hashes atuais identificam conteúdo. Relocação exige mesma identidade no novo caminho, origem anterior comprovadamente ausente e ausência de cópias ambíguas.

**Aprofundamento:** Renomear repositório distinto migra anotações? Não. Relocação verificada preserva relações suportadas de identidade/referência; não é renomeação genérica de slug, reescrita de marcadores ou migração arbitrária.

### Q105 — Como inferência local e avaliação funcionam hoje?

**Resposta:** O chamador normal usa `llama3.2:3b` aprovado no Ollama local e três skills verificadas por integridade. Seleciona evidências limitadas, solicita fatos bilíngues estruturados, verifica envelopes/proveniência/literais/alegações e renderiza resumos próprios. Requisições automáticas por declaração Python dividem prazo limitado. UI e CLI padrão usam `Documentation::Command`; fluxo optativo de projeto é separado.

**Aprofundamento:** O agente foi treinado até a qualidade desejada? Isso não está demonstrado. Contexto de skills não é fine-tuning neural. Aceitação mecânica pode deixar passar erros semânticos e traduções ruins; qualidade desejada é trabalho futuro com campanha autorizada separadamente. Não há fallback de nuvem ou substituição automática de modelo.

### Q106 — O ciclo completo suporta ausência de docs?

**Resposta:** O desenho suporta cadastrar → gerar → atualizar → remover cadastro → cadastrar novamente → gerar novamente. A primeira publicação cria `docs/` original com segurança. Remoção arquiva a árvore da biblioteca e preserva código/docs manuais originais; recadastro elegível restaura identidade/arquivo. Origem ausente ou falha do adapter não justificam apagar evidências ou excluir automaticamente cadastro gerenciado.

**Aprofundamento:** E se entrega ou remoção for interrompida? Entrega pendente pode retomar configuração salva sem inferência; journals e arquivos verificados governam recuperação do comando/remoção. Concorrência ou ambiguidade são recusadas. Veja [operação e recuperação](../operations/runtime-and-recovery.md). Esta revisão não afirma execução de novo teste completo do ciclo.
