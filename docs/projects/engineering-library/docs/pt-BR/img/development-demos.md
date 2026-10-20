# Demonstrações de desenvolvimento

O startup Docker (`docker compose up -d --build`) inicializa metadados do catálogo, sem criar demonstrações de anotações. Um leitor anônimo novo tem coleções vazias. Os seeds são opcionais, manuais e exclusivos de desenvolvimento; a limpeza nunca é automática. Não reinicialize o PostgreSQL nem remova seu volume.

## Fluxo A — leitor de demonstração do CLI

O CLI usa um perfil persistente separado, por padrão `/tmp/engineering-note-demo-browser` (configurável com `DEMO_BROWSER_PROFILE`). O Rails cria seu cookie aleatório assinado HttpOnly `engineering_reader` pela API normal de marcações. O PostgreSQL guarda somente seu SHA-256. Os registros pertencem a esse perfil: executar a verificação ou abrir links do manifesto em outro navegador não transfere a propriedade. `demo_key` identifica demonstrações para limpeza, não concede visibilidade pública. Nunca copie cookies nem publique digests.

Com Node.js e Playwright instalados no host:

```sh
cd frontend
npm install --prefix /tmp/engineering-library-browser playwright
export PLAYWRIGHT_MODULE=/tmp/engineering-library-browser/node_modules/playwright
/tmp/engineering-library-browser/node_modules/.bin/playwright install chromium
export BROWSER_BASE_URL=http://localhost:3099
npm run notes:demos
npm run notes:demos:verify
npm run notes:demos:manifest
```

Use `PLAYWRIGHT_EXECUTABLE_PATH` para um navegador instalado. Não execute comandos simultâneos no mesmo perfil. `notes:demos` cria ou reconcilia somente as demonstrações desse perfil. `notes:demos:verify` lê os registros persistidos e abre indicadores e prévias reais. `notes:demos:manifest` faz diagnóstico atualizado de âncoras somente leitura, sem criar ou excluir registros. Ele grava `/tmp/engineering-note-demo-manifest.json` com IDs, documento/idioma, âncoras lógicas, indicadores `valid` e totais válidos/inválidos, sem cookies ou digests. Após editar documentos, confira âncoras inválidas e execute explicitamente o seed para reconciliar demonstrações. Os registros pessoais são preservados.

## Fluxo B — demonstrações no navegador atual

Use o navegador onde deseja ver as anotações, sempre em `localhost:3099`. Outro navegador, janela privada, perfil ou hostname `127.0.0.1` pode ter identidade diferente.

1. Abra cada um dos quatro endereços:
   - [Arquitetura, inglês](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=en&noteDemos=1)
   - [Componentes visuais, inglês](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=en&noteDemos=1)
   - [Arquitetura, português](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=pt-BR&noteDemos=1)
   - [Componentes visuais, português](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=pt-BR&noteDemos=1)
2. Expanda **Development note demonstrations** abaixo do livro, rolando a página se necessário. Clique em **Seed current reader** em cada endereço. A ação preenche somente o documento e idioma abertos, usando seu cookie protegido existente. Não adota a identidade do CLI. Outros documentos mostram links de orientação e o botão de seed fica desabilitado.
3. Aguarde a mensagem de contagem salva. Notas, destaques, painéis de marcações e fitas se atualizam imediatamente. Abra **Destaques e notas** e **Minhas marcações** na barra normal. Use filtros ou links dos trechos gerados e clique no indicador sobrescrito da nota. **Download manifest** exporta os trechos criados neste documento; o manifesto somente leitura do CLI valida o perfil separado dele.
4. Remova `noteDemos=1` ou recarregue normalmente. O mesmo navegador mantém os dados. Troque o idioma para ver sua coleção independente. Não é necessário reiniciar o Docker.

Repetir a ação reconcilia demonstrações sem duplicatas. Uma nota ou marcação pessoal no trecho provoca conflito, sem sobrescrita. Uma execução interrompida pode deixar demonstrações parciais; o erro é exibido e o estado salvo é atualizado. Resolva o conflito ou use um perfil de desenvolvimento vazio antes de tentar novamente. Dados pessoais nunca são removidos para liberar espaço.

## Contagens e inspeção do banco

Por documento e idioma: 15 notas, 15 destaques ativos (14 com notas e um independente), 3 marcações. Dois documentos e dois idiomas totalizam **60 notas, 60 destaques e 12 marcações por leitor populado**. Quatro notas não têm cor. Por idioma, o painel do projeto tem 32 anotações, incluindo 30 notas: amarelo 6; azul, rosa, laranja, roxo, vermelho e verde 4 cada. O painel carrega inicialmente 20 entradas; use o controle de carregar mais para as restantes. O manifesto de seed tem 76 cenários de criação; a validação atual confere 132 âncoras persistidas.

As identidades canônicas são `architecture/current-state.md` e `img/visual-components.md`, independentes do idioma. As âncoras derivam do DOM medido do leitor. A API normal de notas/destaques consulta o documento; `/api/annotations?project=engineering-library&language=pt-BR` e `/api/bookmarks?project_slug=engineering-library&language=pt-BR` consultam todo o projeto. Toda leitura continua limitada ao proprietário do cookie e ao idioma, com cache `no-store`.

O DBeaver acessa `localhost:5499`, banco `engineering_library`, com suas credenciais locais existentes. As consultas somente leitura abaixo agregam **todos** os leitores de demonstração. Duas identidades totalmente populadas dobram os totais. Contagens no banco não comprovam visibilidade no navegador aberto.

```sql
SELECT language, document, count(*), count(DISTINCT reader_digest) AS owners
FROM notes WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

## Limpeza explícita

Na interface de desenvolvimento, **Remove demonstration records** remove somente as demonstrações identificadas do navegador atual em todo o projeto, nos dois documentos e idiomas, e atualiza a interface. Preserva registros pessoais e outros leitores. A limpeza não se limita ao documento aberto.

Para remover somente as demonstrações do perfil CLI, execute separadamente quando desejar:

```sh
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:cleanup
```

Use o mesmo `DEMO_BROWSER_PROFILE` do seed. Isso não limpa seu navegador habitual. Cores legadas sem identificação explícita de demonstração podem permanecer para evitar excluir destaques pessoais.

## Validação em 20/10/2026 — correção de visibilidade

O leitor temporário novo no Edge começou vazio mesmo com os registros do perfil CLI presentes. A ação explícita passou nos dois documentos e idiomas: indicadores, fitas e listas de marcações imediatos, seed repetido, contagens dos sete filtros, filtro de notas, reload, isolamento de outro leitor novo e limpeza explícita do proprietário temporário. Execute `npm run test:demos:browser` com o ambiente Playwright acima. A regressão Rails verifica reconciliação de âncoras movidas, idempotência, isolamento e preservação na limpeza. Consulte o relatório da tarefa para os resultados efetivamente executados das suítes e das prévias; este guia não infere a identidade do navegador já aberto do usuário. Firefox e Safari exigem validação separada; mídia externa depende do provedor.
