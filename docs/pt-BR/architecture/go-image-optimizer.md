# go-image-optimizer: dossiê de implementação

[English](../../en/architecture/go-image-optimizer.md) | [Português brasileiro](go-image-optimizer.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

## API de imagens e contrato do proxy

O router Go expõe `GET /health` e POSTs multipart `/images/compress`, `/images/resize/info`, `/images/resize`, `/images/convert/info`, `/images/convert` e `/images/preview`. O campo de arquivo é `image`. Rotas de inspeção retornam metadados da operação; rotas de processamento retornam bytes com tipo de mídia e metadados de download. Compressão conserva família e dimensões orientadas; resize altera dimensões nas famílias suportadas; conversão muda a família; preview fornece bytes de exibição separados do download. Variante não suportada não equivale a família não suportada.

As rotas Next.js em `/api/images` usam uma função compartilhada de encaminhamento. O navegador envia multipart à mesma origem; o servidor reconstrói `FormData`, encaminha a `BACKEND_URL`, propaga o sinal de abortamento, lê o resultado bem-sucedido em `ArrayBuffer` e encaminha cabeçalhos de formato/dimensões/disposição com `Cache-Control: no-store`. Status/texto de erro do backend são devolvidos; exceções de encaminhamento viram JSON 502. Content-Type ausente assume octet-stream. O navegador não precisa do hostname do serviço Compose. Nenhum token de identidade é inserido; não é um gateway público com autorização ou controle de admissão.

O handler de compressão Go limita o corpo inteiro a 50 MiB e usa 8 MiB como limiar multipart em memória antes de temporários. O proxy verifica `File.size` depois de interpretar multipart, portanto seu limite de arquivo de 50 MiB não é admissão por streaming nem equivale exatamente ao limite total do Go: o overhead multipart pode fazer um arquivo aparentemente permitido exceder o limite do backend. O processamento usa bytes reais, não o nome ou MIME do cliente. Erros compartilhados mapeiam entrada vazia/corrompida para 400, família não suportada para 415, excesso de recursos para 413, variante não suportada para 422 e falhas de codec/inesperadas para 500. Compressão tem mapeamento próprio; não se deve presumir que todos os handlers são idênticos com base em um helper.

O resultado pode crescer. Redução de bytes é observação da UI, não contrato. JSON de inspeção e resultados binários compartilham o encaminhamento, então consumidores precisam respeitar Content-Type. Retry repete processamento caro; não há ID de job, histórico, chave de idempotência, resultado durável ou API de conclusão assíncrona.

## Limites de recursos e código nativo

Bytes codificados não equivalem à memória decodificada. A camada de imagens limita dimensões estáticas a 32.000.000 pixels e trabalho de canvas animado a 64.000.000 pixels de frames. A validação usa divisão para evitar overflow de multiplicação. Um buffer RGBA no limite estático já representa cerca de 128 milhões de bytes; original, destino, frames, buffers do proxy e alocações do codec se somam. Limites são por operação, com verificações por variante; não são cota global de memória ou limite de concorrência. Parte da decodificação nativa pode preceder verificações posteriores.

`UseCase.Execute` verifica contexto antes e depois da compressão. Não passa um contexto cancelável ao compressor. Propagar abortamento e definir timeouts HTTP, portanto, não prova interrupção de um codec nativo síncrono. O servidor Go configura 5 s para cabeçalhos, 2 min para leitura/gravação e 60 s de ociosidade. Prazos HTTP limitam transporte; o encoder pode continuar consumindo CPU até retornar. Um semáforo ou processo de worker separado poderia oferecer admissão e isolamento, com custo de complexidade e comunicação; nenhum existe.

CGO e codecs nativos ampliam suporte HEIF/AVIF e acrescentam manutenção de ABI, build e segurança. Temporários multipart são removidos após interpretação bem-sucedida; handles são fechados; helpers HEIF limpam seus temporários. Resultados por requisição não são armazenamento durável. Recuperação de panic no handler não isola biblioteca nativa nem recupera toda falha nativa do processo. Não há login, terminação TLS ou rate limit por usuário implementados na aplicação revisada. Exposição pública exige projeto separado; validação do conteúdo sozinha não torna seguros uploads hostis.

## Implantação, diagnóstico e evidência

Compose descreve backend Go e frontend Next.js, além de perfis de teste/desenvolvimento. O runtime do backend exige bibliotecas nativas fornecidas pelo Dockerfile. Bind mounts e caches de dependências de desenvolvimento ajudam a edição; não são procedimento de rollout em produção. `BACKEND_URL` do servidor frontend precisa resolver a partir do próprio runtime, geralmente `backend:8080` no Compose. `localhost` ali significa aquele contêiner, não o host do desenvolvedor ou outro serviço.

Diagnostique separadamente: 502 do proxy sugere falha de encaminhamento/abortamento/conectividade; 4xx do backend identifica entrada inválida ou não suportada; 500 de codec sugere falha de implantação ou encoder; `/health` é liveness, não autoteste de todos os codecs. Analise warnings/erros estruturados de `slog` sem registrar conteúdo da imagem. Preserve um reproducer mínimo não sensível e seu formato/variante real. Testes HTTP, fakes de aplicação e fixtures de imagens comprovam fronteiras diferentes; builds/testes históricos registrados não são nova validação. Nenhum navegador, carga, teste de corrida ou aplicação foi executado nesta revisão.

Não há banco persistente de uploads para backup nem migrações. Atualizar o backend exige manter dependências de codec compatíveis e os metadados de resposta do frontend/backend precisam continuar compatíveis. Rollback de imagens é conceitualmente possível com artefatos retidos, mas não há evidência de registro de releases, pipeline produtivo, topologia TLS, ensaio de rollback ou SLO de produção. Benchmarks não se aplicam sem medições: limites de pixels e bytes mostrados na UI não medem vazão. Lacunas incluem picos de memória concorrente, interrupção de trabalho nativo, fidelidade visual em variantes representativas e compatibilidade de navegador. A documentação de testes conserva a limitação histórica de race/checkptr nativo.

## Evidência de apoio

- [api/contracts](../../../../go-image-optimizer/docs/pt-BR/api/contracts.md)
- [security/resource-boundaries](../../../../go-image-optimizer/docs/pt-BR/security/resource-boundaries.md)
- [operations/deployment-and-diagnosis](../../../../go-image-optimizer/docs/pt-BR/operations/deployment-and-diagnosis.md)
- [Interview / Entrevista](../interviews/go-image-optimizer.md)
