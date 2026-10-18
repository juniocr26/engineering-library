# Go Image Optimizer Guia de Estudo para Entrevista Técnica

[English](../../en/interviews/go-image-optimizer.md) | [Português brasileiro](go-image-optimizer.md)

As verificações de 2026-10-04 são históricas. A configuração de desenvolvimento atual usa o override Compose e binds do host, não volumes nomeados de node_modules/.next. Paths citados são relativos ao projeto go-image-optimizer, não a este repositório.

Este guia ajuda a explicar o problema, os fluxos e as decisões do projeto com base na implementação atual. O escopo funcional está concluído: compressão, redimensionamento, conversão de formatos e fallback de prévia. Concluído não significa compatibilidade universal, capacidade de produção medida ou ausência de limitações.

Minha experiência profissional principal de backend é PHP/Laravel. Uso este projeto de portfólio como experiência prática deliberada de aprendizado em Go. As respostas possíveis estão na primeira pessoa para facilitar o estudo, mas devem ser adaptadas ao meu entendimento. O objetivo é compreender e raciocinar, não decorar um roteiro ou atribuir ao projeto usuários e resultados de produção que não foram demonstrados.

Base de estudo: checkout do projeto e verificações locais de 04 de outubro de 2026. Referências de arquivos são relativas à raiz do repositório. O guia de URL Shortener serviu como modelo de perguntas, respostas, aprofundamentos e discussão de custos; fatos e tecnologias daquele projeto não descrevem este sistema.

## 1 Propósito e escolhas

### 1 Qual problema o projeto resolve

Resposta possível: Eu ofereço um fluxo simples para enviar uma imagem, comprimir, redimensionar ou converter seu formato e baixar o resultado. Mostro dimensões e tamanhos medidos, inclusive quando o arquivo fica maior. Também trato a situação em que o navegador não consegue abrir uma imagem que o backend suporta: tento uma prévia gerada no servidor, sem trocar os bytes do download.

Explicação técnica: O frontend mantém uma imagem original selecionada e resultados temporários. Compression conserva a família e as dimensões orientadas; Resize altera dimensões na família original; Convert altera a família conservando dimensões orientadas. A prévia é um recurso interno de exibição. Resize atende ao caso básico de criar imagens menores, sem recorte, composição avançada ou editor.

Aprofundamento: Por que encerrar o escopo? Eu consigo explicar e verificar o fluxo inteiro de um portfólio Go e Next.js sem adicionar funcionalidades que trazem outras responsabilidades. Manutenção e correções continuam possíveis; novas funcionalidades não estão planejadas.

Referências: README.pt-BR.md; frontend/app/components/image-upload/image-upload-form.tsx.

**Aprofundamento:** Por que saída maior satisfaz contrato? Operação retorna bytes válidos da família escolhida; economia é observação. Rejeitar crescimento exigiria outra política de manter/rejeitar/ajustar.

### 2 Por que Go se minha experiência principal é PHP e Laravel

Resposta possível: Eu escolhi Go como aprendizado prático de outra linguagem de backend. Minha experiência em PHP/Laravel me ajuda a reconhecer responsabilidades de transporte, aplicação e infraestrutura, mas preciso aprender como Go expressa essas fronteiras: pacotes, interfaces pequenas, construtores explícitos, erros retornados e gerenciamento de recursos. Este projeto permite exercitar isso em processamento real de imagens e em uma API pequena.

Explicação técnica: O backend usa net/http, sem framework HTTP ou container de injeção de dependências. Em Laravel eu poderia usar controllers, serviços e bindings do container; aqui NewRouter constrói os casos de uso com suas dependências concretas. Isso facilita acompanhar a ligação entre interface e implementação. Não há Eloquent ou equivalente porque o produto não persiste entidades.

Aprofundamento: Go garante que seja mais rápido? Eu não afirmaria isso sem benchmark. O custo inclui decodificação, escala, encoding, upload e bibliotecas nativas. O projeto demonstra comportamento testado, não superioridade medida sobre PHP.

Referências: backend/internal/infrastructure/http/router.go; backend/internal/application/imagecompression/usecase.go.

**Aprofundamento:** Go sozinho explica velocidade? Não; upload/decode/transform/encode/nativo contribuem. Comparação exige medições representativas ausentes.

### 3 Por que Next.js e React

Resposta possível: Eu uso Next.js e React para organizar a interface e o estado de seleção, configuração e resultado. As rotas API do Next.js encaminham multipart para Go pela mesma origem do navegador. Assim, o navegador conversa com a aplicação web e os detalhes dos codecs ficam no backend.

Explicação técnica: app/page.tsx compõe a Home. ImageUploadForm controla o fluxo; ImageResizeModal e ImageConvertModal cuidam das opções; ImageSettingsDialog compartilha comportamento modal; ImageResultModal apresenta resultados. Tailwind CSS organiza estilos. O helper forward-image-request.ts preserva status e headers relevantes e encaminha o sinal de cancelamento.

Alternativa e custo: Uma interface mais simples ou um backend que servisse HTML também poderia resolver o problema. O arranjo atual separa interface e processamento, mas adiciona runtime Node e um salto HTTP. O proxy lê FormData e armazena a resposta em arrayBuffer; não é streaming ponta a ponta.

Referências: frontend/app/api/images/forward-image-request.ts; frontend/app/components/image-upload/.

**Aprofundamento:** Mesma origem elimina checks? Não; clientes arbitrários chamam direto. Proxy interpreta/materializa antes de checar tamanho e não autentica.

### 4 Isso é Clean Architecture ou microsserviços

Resposta possível: Eu descreveria como uma arquitetura pequena em camadas. O handler resolve HTTP; o caso de uso coordena regras da operação; a infraestrutura trata pixels e codecs. Não preciso afirmar que implementei todas as camadas formais de Clean Architecture. Os containers Next.js e Go separam necessidades de build e runtime; isso, sozinho, não torna o projeto um sistema de microsserviços.

Explicação técnica: As interfaces Compressor, Decoder/Source e Processor estão nas fronteiras em que ajudam a substituir infraestrutura nos testes. Não há entidades de domínio persistidas, repositories, banco ou framework de injeção. Os tipos comuns ficam em application/imageprocessing. Os pacotes tornam responsabilidades navegáveis sem criar uma abstração para cada função.

Aprofundamento: Quando separar outro serviço? Eu partiria de requisitos independentes de operação, isolamento ou escala e de medições. Não existe esse compromisso no escopo atual.

Referências: docs/pt-BR/architecture/overview.md; backend/internal/application/; backend/internal/infrastructure/.

**Aprofundamento:** Quando justificar outro serviço? Necessidade demonstrada de operação/isolamento/escala. Dois contêineres/interfaces não provam microsserviço ou desacoplamento útil.

## 2 Fluxos de ponta a ponta

### 5 Como acontece uma compressão

Resposta possível: Eu seleciono a imagem, escolho Compression e envio o arquivo ao proxy /api/images/compress. Ele encaminha para POST /images/compress. O handler valida multipart e tamanho, lê bytes e executa o caso de uso. O compressor detecta a família real pelos bytes, verifica limites, decodifica e reencoda com o codec correspondente. O resultado volta como bytes e headers de download, e a interface mede o Blob recebido.

Explicação técnica: O caso de uso rejeita entrada vazia e verifica contexto antes e depois de Compressor.Compress. A interface do compressor não recebe context.Context, portanto a compressão interna não é interrompida pelo contexto. JPEG aplica orientação EXIF; PNG usa melhor compressão sem alterar pixels; outros caminhos têm políticas próprias. O arquivo pode ficar maior.

Aprofundamento: Por que não salvar o upload? A resposta já contém o resultado para download. Persistência exigiria retenção, identificação e recuperação de arquivos que não são requisitos atuais.

Referências: backend/internal/infrastructure/http/handler/compress_image/handler.go; backend/internal/infrastructure/imaging/compress/compressor.go.

**Aprofundamento:** Cancelamento dentro do codec? Caso de uso percebe depois; interface não interrompe compressão nativa. Cancelar transporte difere de parar CPU.

### 6 Como funciona a inspeção e a configuração de Resize

Resposta possível: Eu abro o modal, envio o original para /api/images/resize/info e recebo dimensões orientadas, família, MIME e quantidade de frames. Em pixels posso manter a proporção ou definir largura e altura independentes. Em porcentagem escolho 25%, 50% ou 75% menores. O frontend mostra a previsão, mas o servidor recalcula a saída a partir dos bytes enviados.

Explicação técnica: A inspeção decodifica a origem. Não é apenas leitura de extensão ou consulta a um registro. O fechamento do modal aborta a requisição de inspeção. Pixels começa nas dimensões originais, com proporção preservada; a última dimensão editada determina axis. Os testes frontend verificam regras de cálculo, arredondamento e limites. Eles não exercitam o foco real de um navegador.

Aprofundamento: Qual é o custo das duas requisições? O original é enviado e decodificado novamente na execução. Isso evita IDs e cache de uploads no servidor, aceitando mais rede e processamento.

Referências: frontend/app/components/image-resize/image-resize-modal.tsx; resize-options.ts; backend/internal/application/imageresize/usecase.go.

**Aprofundamento:** Por que não reutilizar pixels? Evitar upload/decode exige estado servidor ou novo contrato. Trabalho extra mantém operação efêmera sem IDs persistentes.

### 7 O que acontece ao executar e baixar Resize

Resposta possível: Eu envio o original e as opções para /api/images/resize, que encaminha para /images/resize. O caso de uso valida opções e calcula dimensões. A origem decodificada aplica Catmull–Rom e codifica na mesma família. Recebo bytes, dimensões originais e finais e um nome com _resized. A interface substitui configuração por resultado, mas mantém o original para outra operação.

Explicação técnica: O download usa o Blob do resultado real. Se as dimensões efetivas forem iguais às dimensões orientadas da origem, o caso de uso devolve os bytes originais intactos. Nesse caso não há nova codificação nem remoção de metadados. Redimensionamentos efetivos podem alterar pixels, qualidade, paleta e metadados.

Aprofundamento: A operação usa um resultado anterior? O fluxo da interface envia o original selecionado. Isso evita acumular perdas de sucessivas recodificações no uso normal, embora uma pessoa possa reenviar um resultado como novo arquivo.

Referências: backend/internal/application/imageresize/usecase.go; backend/internal/infrastructure/imaging/resize/decoder.go; frontend/app/components/image-upload/image-result-modal.tsx.

**Aprofundamento:** Resize sem alteração prova metadados universais? Não. Só branch no-op conserva bytes; escala real recodifica/metadados/paleta.

### 8 Como acontece a conversão de formatos

Resposta possível: Eu inspeciono o original, escolho uma família diferente e envio image e targetFormat. O backend aceita os destinos canônicos jpeg, png, webp, avif, heif, gif, bmp e tiff. Converte uma imagem estática suportada mantendo dimensões orientadas, retorna MIME e extensão coerentes e deixa disponível o resultado mesmo se tiver mais bytes.

Explicação técnica: JPG/JPEG são aliases de família, mas a API exige jpeg, não jpg. HEIC/HEIF usa heif como destino canônico e HEVC como encoder, normalmente retornando image/heic e .heic. O caso de uso rejeita destino igual à origem, destino inválido e animação. APNG, sequências AVIF, TIFF multipágina e HEIF multi-imagem não suportado são rejeitados pelo decoder compartilhado.

Aprofundamento: Quantas decodificações existem? Há inspeção da interface e novo processamento. Além disso, Execute chama Inspect e Processor.Convert chama decode novamente dentro da execução. Não apresento esse caminho como otimizado para eliminar toda repetição.

Referências: backend/internal/application/imageconversion/usecase.go; backend/internal/infrastructure/imaging/convert/processor.go.

**Aprofundamento:** Por que rejeitar animação? Achatar silenciosamente perde significado. Rejeição expõe variante; suporte exigiria contratos de duração/loop/disposal/fixtures.

### 9 Como a prévia funciona quando o navegador não abre o formato

Resposta possível: Eu tento primeiro abrir bytes no navegador, inclusive corrigindo o MIME apenas para exibição de algumas assinaturas conhecidas. Se a carga falhar, envio o File ou Blob real para /api/images/preview. O backend produz uma imagem proporcional limitada a 1200 × 1200, sem ampliar: PNG se houver transparência ou JPEG se os pixels forem opacos. A falha de prévia não bloqueia processamento nem download.

Explicação técnica: O fallback usa o decoder de conversão e suas restrições; não suporta animações. O navegador pode mostrar nativamente uma variante que o fallback rejeita. Os bytes gerados são cacheados por identidade de Blob em WeakMap, compartilhados entre consumidores da sessão. Isso não é Redis, persistência nem histórico. Download, nome, tamanho e dimensões continuam descrevendo o arquivo real.

Aprofundamento: Gerar uma miniatura significa ter uma operação de thumbnails? Aqui ela serve à compatibilidade de exibição. Não há configuração independente de thumbnails, recorte ou composição oferecida ao usuário.

Referências: frontend/app/components/image-upload/browser-image-preview.tsx; preview-cache.ts; backend/internal/infrastructure/imaging/convert/preview.go.

**Aprofundamento:** Fallback vira download? Não; encoding/dimensões diferem. Blobs separados impedem compatibilidade visual de alterar resultado.

## 3 Bytes pixels e codecs

### 10 Qual a diferença entre extensão MIME e formato real

Resposta possível: Eu trato extensão como parte do nome e MIME do navegador como uma indicação. O backend decide pelos bytes, reconhecendo assinaturas e marcas de containers. Depois ainda precisa validar a variante e decodificar o conteúdo. Um arquivo chamado foto.png que contém JPEG segue o caminho JPEG; bytes inválidos não se tornam uma imagem por ter a extensão certa.

Explicação técnica: DetectFormat reconhece assinaturas JPEG/PNG/GIF/BMP/TIFF, estrutura RIFF/WEBP e marcas BMFF para AVIF/HEIF. Também rejeita assinaturas RAW como DNG e CR2 antes de tratá-las como TIFF. Assinatura válida não garante conteúdo íntegro, variante suportada ou codec disponível. O MIME da resposta vem da saída codificada, não do upload.

Aprofundamento: Por que isso importa para nomes? O helper de download remove diretórios, trata barras de Windows e escolhe extensão compatível com a família. A serialização Content-Disposition usa mime.FormatMediaType.

Referências: backend/internal/infrastructure/imaging/detection.go; backend/internal/infrastructure/http/handler/imagehttp/filename.go.

**Aprofundamento:** Assinatura prova validade? Não; escolhe parser, depois decode/variante/recursos validam. Sanitizar nome trata outra fronteira.

### 11 Como diferenciar decode transformação e encode

Resposta possível: Eu decodifico bytes em pixels, aplico a transformação necessária e codifico esses pixels em um arquivo de saída. Na compressão, a transformação pode incluir orientação; no Resize inclui escala; na conversão muda o encoder e pode compor transparência. Essa separação explica por que família, pixels e tamanho de arquivo são medidas diferentes.

Explicação técnica: image.Image descreve pixels e limites de coordenadas. image.RGBA é usado para a escala. bytes.Buffer acumula saída quando o codec permite. O helper HEIF precisa de arquivo temporário porque o binding usa WriteToFile. O resultado contém []byte, família, MIME, dimensões e propriedades de frames; não é um caminho persistente.

Aprofundamento: Por que um codec lossless não torna Resize lossless em relação ao original? Ele codifica sem perda os novos pixels; a interpolação já alterou o conteúdo. Preciso identificar a etapa à qual a garantia se aplica.

Referências: backend/internal/infrastructure/imaging/resize/decoder.go; convert/processor.go; imaging/heif.go.

**Aprofundamento:** Por que saída lossless não é resize lossless? Encoder conserva destino, mas interpolação já mudou origem. Bytes e pixels são equivalências distintas.

### 12 Por que diminuir pixels não garante diminuir bytes

Resposta possível: Eu separo resolução de tamanho codificado. Uma imagem 512 × 512 tem 262.144 pixels, mas seu arquivo depende de formato, qualidade, transparência, paleta e conteúdo. Reduzir largura e altura à metade reduz a área a um quarto; não fixa a proporção de bytes. Converter um JPEG para BMP pode aumentar muito o arquivo sem falhar.

Explicação técnica: O frontend calcula tamanho a partir de File.size e Blob.size e apresenta redução, aumento ou ausência de mudança. Content-Length reflete bytes realmente retornados. Os testes de conversão aceitam resultados maiores; um teste HTTP determinístico verifica um BMP maior e ainda baixável.

Aprofundamento: Se o objetivo fosse nunca aumentar bytes, o contrato seria outro. Seria necessário decidir se manteria o original, rejeitaria o resultado ou escolheria parâmetros/formatos. A conversão atual deve entregar a família solicitada.

Referências: frontend/app/components/image-convert/size-change.ts; frontend/tests/conversion-size.test.mjs; backend/internal/infrastructure/http/conversion_test.go.

**Aprofundamento:** Metade de dimensões reduz trabalho/bytes pela metade? Área cai cerca de quatro vezes; custos fixos/nativos/encoding/conteúdo variam. Geometria não mede vazão.

### 13 Quais padrões de qualidade e compressão são usados

Resposta possível: Eu uso JPEG e WebP com qualidade 82, AVIF e HEVC com qualidade 60. WebP estático usa método 4 e qualidade de alfa 100; AVIF usa alfa 100 e velocidade 6. PNG usa BestCompression e TIFF usa Deflate com predictor. GIF trabalha com paleta; BMP não oferece a mesma expectativa de redução de um encoder moderno.

Explicação técnica: As escalas de qualidade não são comparáveis entre codecs. JPEG, AVIF e HEVC têm perdas nesses padrões. PNG e TIFF codificam sem perda os pixels recebidos. Compression e Resize preservam o modo lossless de WebP estático quando detectado; conversão para WebP usa o padrão lossy. GIF de conversão/Resize quantiza cores com paleta WebSafe e dithering Floyd–Steinberg.

Aprofundamento: Por que esses números? São os padrões presentes no código, permitindo comportamento previsível. Não afirmo que vieram de um estudo perceptual ou benchmark histórico. Se precisasse justificá-los para outro requisito, compararia qualidade visual, bytes e custo de encoding em um conjunto representativo.

Referências: backend/internal/infrastructure/imaging/compress/compressor.go; resize/decoder.go; convert/processor.go.

**Aprofundamento:** Quality 60 compara codecs? Não como escore perceptual igual. Algoritmos/escalas exigem avaliação visual/custo; defaults são política, não benchmark.

### 14 Como funcionam proporção arredondamento e ampliação

Resposta possível: Eu calculo uma escala a partir da largura ou altura de referência quando a proporção está travada. Arredondo cada dimensão ao inteiro mais próximo, com mínimo de um pixel. Em porcentagem, reduzo cada dimensão em 25%, 50% ou 75%. Com proporção destravada, respeito largura e altura independentes; não recorto nem preencho a imagem.

Explicação técnica: Target usa math.Round e valida limites antes de converter valores de ponto flutuante em int. Um original 899 × 1599 reduzido em 50% vira 450 × 800. Arredondamento pode criar pequena diferença de proporção em dimensões ímpares. Pixels permite ampliar; o limite total é verificado pela divisão MaxPixels/height, evitando multiplicação inteira insegura.

Aprofundamento: Ampliar melhora detalhe? A interpolação estima valores intermediários, mas não recupera informação ausente. Os testes verificam dimensões maiores, não ganho de nitidez. Nos samples quadrados, as saídas 256 × 128 e 515 × 519 provam dimensões independentes.

Referências: backend/internal/application/imageresize/usecase.go; frontend/app/components/image-resize/resize-options.ts.

**Aprofundamento:** Por que validar antes de float→int? Fora de faixa causa overflow/trabalho excessivo. Arredondamento/mínimo um ainda muda proporção em dimensões ímpares.

### 15 Qual algoritmo de reamostragem é usado e qual seu custo

Resposta possível: Eu uso draw.CatmullRom.Scale de golang.org/x/image/draw, com destino RGBA pré-multiplicado e draw.Src. Catmull–Rom oferece interpolação suave e costuma preservar melhor transições do que vizinho mais próximo. Aceito maior processamento e possível ringing em bordas, sem prometer melhoria de detalhe ou qualidade universal.

Explicação técnica: Alfa pré-multiplicado representa componentes de cor associados à cobertura, reduzindo halos escuros em bordas transparentes durante a interpolação. O algoritmo é usado no Resize e no fallback de prévia. A chamada de escala não recebe context.Context; o código verifica cancelamento depois dela.

Alternativas: Vizinho mais próximo é simples e adequado a pixel art, mas pode ficar serrilhado em fotografias. Bilinear é mais simples, com tendência a suavizar. Uma escolha diferente exigiria avaliação visual e custo medido; não existe uma comparação experimental desses algoritmos no projeto.

Referências: backend/internal/infrastructure/imaging/resize/decoder.go, scaleImage; backend/internal/infrastructure/imaging/convert/preview.go.

**Aprofundamento:** Quando nearest-neighbor? Pixel art pode preferir amostras discretas. Catmull–Rom suaviza/pode gerar ringing; projeto não prova vencedor universal.

### 16 O que acontece com transparência

Resposta possível: Eu aplico políticas específicas. Na conversão, JPEG, BMP e HEIF recebem composição sobre branco. PNG, WebP, AVIF e TIFF preservam alfa pelos caminhos usados. GIF só representa transparência binária e usa limiar de 50%, então perde alfa parcial e pode alterar cores. A política evita fingir que todo formato representa a mesma informação.

Explicação técnica: O canvas branco recebe a origem com draw.Over. GIF combina quantização/dithering com uma correção de índices para que pixels transparentes continuem transparentes e pixels escuros opacos não usem a cor transparente por engano. Resize PNG/WebP tem testes de alfa parcial; BMP e HEIF de Resize seguem seus caminhos de encoder, sem a composição branca explícita da conversão.

Aprofundamento: A prévia PNG garante preservar o arquivo original? Ela preserva a transparência necessária para exibição de seus novos pixels. É outra imagem, potencialmente menor e sem todos os metadados. O original e o resultado real continuam separados.

Referências: backend/internal/infrastructure/imaging/convert/processor.go; resize/animation.go; resize/resize_test.go.

**Aprofundamento:** Por que toda família não conserva alpha parcial? JPEG/outros destinos não têm mesmo contrato. Composição/quantização explícita expõe perda em vez de prometer fidelidade ausente.

### 17 Como orientação metadados e perfis de cor são tratados

Resposta possível: Eu normalizo orientação quando o caminho oferece suporte: JPEG aplica EXIF aos pixels; AVIF usa autorrotação; HEIF usa transformações do codec. A conversão e a prévia também tentam aplicar EXIF reconhecido em outras famílias estáticas. Não prometo copiar universalmente EXIF, XMP ou ICC nem preservar toda fidelidade de cor.

Explicação técnica: Resize JPEG calcula alvos depois de orientar a imagem. Seus testes sintéticos usam orientação 6 e verificam dimensões e posição de regiões vermelha/azul, além de ausência de orientação obsoleta. Animated WebP de Resize copia ICC, mas não EXIF/XMP; a compressão WebP animada copia chunks suportados. Resize sem mudança devolve os bytes originais, comportamento distinto da recodificação.

Aprofundamento: Orientar é preservar metadados? É aplicar uma instrução aos pixels para que sejam exibidos na direção correta. Isso não equivale a reter o campo original ou todos os outros metadados. Prévia compatível e preservação documental são requisitos diferentes.

Referências: backend/internal/infrastructure/imaging/orientation.go; resize/decoder.go; convert/processor.go; compress/webp.go.

**Aprofundamento:** Por que EXIF antes de dimensões? Orientação troca largura/altura/pixels. Copiar metadados deixa geometria ambígua; transformar não conserva tudo.

### 18 Como animações e variantes são tratadas

Resposta possível: Eu separo família de formato de variante. Resize mantém animações GIF e WebP suportadas, com frames reconstruídos, tempos e loops. Rejeita AVIF animado/sequências porque o decoder não expõe loops de modo que permita preservar loops finitos. Conversão e fallback rejeitam animações em vez de devolver apenas um frame. APNG, TIFF multipágina e HEIF multi-imagem não suportado também são rejeitados nesses caminhos.

Explicação técnica: GIF pode ter frames parciais e disposal. Resize compõe o canvas, respeita o descarte da origem e reencoda frames completos, podendo mudar paleta e representação interna de disposal. WebP usa o decoder de animação e encoder com duração, loop e fundo. Compression GIF reencoda com gif.EncodeAll; Compression AVIF usa DecodeAll/EncodeAll, mas sua cobertura real é estática e não prova preservação universal de animações.

Aprofundamento: Por que rejeitar em vez de aproximar? Evita perda silenciosa de comportamento visual que o contrato não consegue garantir. Suporte a oito famílias não significa suporte a todas as versões e combinações possíveis.

Referências: backend/internal/infrastructure/imaging/resize/animation.go; variants.go; compress/avif.go; convert/processor.go.

**Aprofundamento:** Suportar GIF prova toda animação? Não. Reconstrução normaliza paleta/disposal. Testes precisam duração/loop/pixels, não só nome/família.

### 19 Quais bibliotecas fazem o trabalho real

Resposta possível: Eu uso image/jpeg, image/png e image/gif da biblioteca padrão; golang.org/x/image para BMP, TIFF e escala; deepteams/webp para WebP; gen2brain/avif para AVIF; e o binding Go de strukturag/libheif para HEIF. GoMetadata ajuda a ler orientação EXIF. Essas dependências têm responsabilidades reais, não são apenas nomes na lista de tecnologias.

Explicação técnica: go.mod declara Go 1.27 e as bibliotecas diretas. WebP e AVIF possuem suas próprias estratégias de execução; não descrevo tudo como codec escrito exclusivamente em Go. A dependência nativa que o Docker instala explicitamente é libheif com plugins HEVC. O funcionamento demonstrado é o do ambiente utilizado nos testes, não de toda plataforma possível.

Aprofundamento: Um formato detectado pode falhar por codec? Sim. A família pode ser conhecida e o conteúdo válido, mas o encoder/decoder necessário estar indisponível. ErrCodecUnavailable é distinto de ErrUnsupportedFormat e ErrInvalidImage.

Referências: backend/go.mod; backend/internal/infrastructure/imaging/heif.go; backend/internal/infrastructure/http/handler/imagehttp/errors.go.

**Aprofundamento:** Build aprovado pode falhar codec runtime? Sim; bibliotecas/plugins/plataforma importam. Nativas precisam combinar com artefatos, além dos módulos Go.

## 4 Contratos recursos e linguagem

### 20 Quais são os contratos HTTP principais

Resposta possível: Eu exponho POST /images/compress, /images/resize/info, /images/resize, /images/convert/info, /images/convert e /images/preview, além de GET /health. No navegador, os endpoints de imagem têm prefixo /api. Os uploads usam multipart com um arquivo image. Resize recebe opções específicas; conversão recebe um único targetFormat canônico.

Explicação técnica: Inspeção retorna width, height, format, contentType e frameCount em JSON. Sucesso de processamento retorna bytes, Content-Type, Content-Length e Content-Disposition com sufixo _compressed, _resized ou _converted. Resize fornece dimensões originais/finais; conversão também fornece X-Source-Format e X-Output-Format. Resize/conversão/prévia usam no-store; não atribuo indiscriminadamente todos os headers a todas as rotas.

Aprofundamento: Os validadores são idênticos? Não. Conversão rejeita campos extras e duplicados; seu info/preview aceita só image. Resize rejeita opções duplicadas e valida opções conhecidas, mas não implementa a mesma rejeição geral de campos desconhecidos. Contratos devem descrever o código real, não uniformidade presumida.

Referências: backend/internal/infrastructure/http/router.go; handler/resize_image/handler.go; handler/convert_image/handler.go.

**Aprofundamento:** Por que separar JSON/bytes? Proxy encaminha ambos; cliente usa Content-Type/rota. Presumir imagem em todo sucesso interpreta metadados errado.

### 21 Como erros e nomes de arquivos são tratados

Resposta possível: Eu retorno erros JSON com o campo error, usando 400 para entrada/opções inválidas, 413 para limites, 415 para família não suportada, 422 para variante rejeitada e 500 para falhas internas ou de codec. O proxy retorna 502 se não consegue acessar o backend. O nome de download é montado com base segura, sufixo da operação e extensão coerente com os bytes.

Explicação técnica: Erros sentinela e errors.Is permitem mapear categorias sem depender apenas de mensagens. fmt.Errorf com %w preserva a categoria ao adicionar contexto. Os handlers removem temporários multipart e têm recuperação de panic no processamento, registrando informações pelo slog. Recuperar panic não substitui validação nem resolve falha de memória/processo.

Aprofundamento: Sanitizar nome valida a imagem? Não. O helper elimina caminhos e serializa o header; a detecção e o decoder validam conteúdo em outra camada. Posso receber foto.jpg e responder foto_converted.png quando o destino é PNG.

Referências: backend/internal/infrastructure/http/handler/imagehttp/; handler/compress_image/filename.go.

**Aprofundamento:** Recover captura toda falha nativa? Não. OOM/processo/faults podem escapar. JSON não isola processo ou garante continuidade.

### 22 Quais limites existem e o que eles não garantem

Resposta possível: Eu limito o corpo HTTP a 50 MiB e o decode a 32 milhões de pixels. Animações têm orçamento de 64 milhões de pixels de canvas vezes frames. Resize também limita dimensões de saída e orçamento animado. Conversão limita saída codificada a 50 MiB depois do encode. Não digo que isso fixa toda a memória do processo.

Explicação técnica: ParseMultipartForm usa 8 MiB como limiar de memória antes de possíveis arquivos temporários, não como tamanho máximo do upload. Uma imagem RGBA de 32 milhões de pixels usa aproximadamente 128 milhões de bytes só para um buffer, antes de origem, destino, frames e encoder. Descritores GIF e informações de WebP são verificados antes da decodificação completa onde implementado. Algumas verificações, como AVIF multiframe em compressão, acontecem após decode.

Aprofundamento: E cem uploads simultâneos? Não há controle global de admissão nem benchmark. Os limites por requisição reduzem risco, mas concorrência pode multiplicar memória e CPU. Passar a suíte não demonstra capacidade de produção.

Referências: backend/internal/infrastructure/imaging/limits.go; backend/internal/application/imageresize/usecase.go; convert/processor.go.

**Aprofundamento:** Entrada válida cabe na memória concorrente? Não. Limites multiplicam e excluem buffers nativos/proxy. Admissão é hipotética.

### 23 Cancelamento e timeout interrompem imediatamente os codecs

Resposta possível: Eu uso cancelamento cooperativo. O frontend aborta requisições obsoletas e o proxy encaminha o signal. Go verifica ctx.Err em pontos da operação e entre frames em Resize. Entretanto, uma chamada nativa ou uma escala em andamento não é encerrada à força. A interface Compressor sequer recebe contexto; o caso de uso verifica antes/depois.

Explicação técnica: O servidor configura ReadHeaderTimeout de 5 segundos, ReadTimeout e WriteTimeout de 2 minutos e IdleTimeout de 60 segundos. São timeouts de conexão/leitura/escrita, não um orçamento rígido que mata o encoder. O processo trata sinais de encerramento e chama Shutdown com contexto de 10 segundos. Timeout de shutdown também não demonstra término instantâneo de trabalho nativo.

Aprofundamento: O que eu faria com um requisito rígido de isolamento? Primeiro definiria o orçamento e mediria o comportamento. Isolamento de processo e admissão poderiam ser alternativas, mas não são funcionalidades implementadas nem próximas etapas assumidas.

Referências: backend/internal/infrastructure/http/server.go; backend/cmd/api/main.go; application/imagecompression/usecase.go.

**Aprofundamento:** Timeout write de dois minutos mata encoder? Não; limita I/O. Código/nativo precisa de cancelamento/isolamento/medições separados.

### 24 Como acontece limpeza e gerenciamento de recursos

Resposta possível: Eu uso defer para fechar arquivos multipart e remover arquivos temporários criados durante parsing. HEIF cria um temporário do sistema, fecha o descritor, codifica, lê bytes e remove o arquivo ao sair, inclusive em caminhos de erro. No frontend, quem cria uma Object URL deve revogá-la quando deixa de usá-la.

Explicação técnica: MultipartForm.RemoveAll e os.Remove evitam transformar temporários em armazenamento durável. A saída dos testes reais fica em memória; não há arquivos gerados dentro das fixtures. Bibliotecas nativas têm ciclo de vida próprio; não afirmo que defer controla cada alocação feita pelo binding. A limpeza dos arquivos está explícita, mas não prova ausência universal de vazamento nativo.

Comparação útil: Em PHP/Laravel também preciso fechar recursos e decidir sobre temporários. Go torna comum declarar defer próximo da aquisição, mantendo o caminho de retorno legível; o coletor de lixo não remove automaticamente arquivos nem libera todos os recursos externos por uma regra universal.

Referências: backend/internal/infrastructure/imaging/heif.go; handler/convert_image/handler.go; handler/resize_image/handler.go.

**Aprofundamento:** Defer garante limpeza após morte abrupta? Não; retorno/erro difere de crash. Memória/arquivos nativos exigem modelo/teste próprio.

### 25 Qual a diferença entre File Blob e Object URL

Resposta possível: Eu trato File como um Blob com informações como nome e tipo. Blob guarda bytes do resultado ou da prévia. Object URL é uma referência temporária criada pelo navegador para exibir ou baixar esses bytes; não é um endereço público do servidor. Original, resultado e prévia têm identidades e responsabilidades diferentes.

Explicação técnica: ImageUploadForm mantém estado da seleção/resultado. BrowserImagePreview cria URLs de exibição e as revoga no cleanup. PreviewSession ignora respostas obsoletas. acquirePreview compartilha promessa por identidade do Blob, conta consumidores e aborta a geração quando o último sai antes de completar. O cache conserva bytes, não Object URLs duráveis. Reload limpa a sessão; não há localStorage nem IndexedDB.

Aprofundamento: Por que não reutilizar bytes de prévia no download? Podem ser JPEG/PNG menores, com outro formato e metadados. O resultado real precisa conservar seu contrato, MIME, nome, tamanho e dimensões independentemente da imagem exibida.

Referências: frontend/app/components/image-upload/preview-cache.ts; browser-image-preview.tsx; image-upload-form.tsx.

**Aprofundamento:** Por que identidade Blob importa? Bytes iguais em objetos diferentes são chaves distintas. Reuso é objeto de sessão, não deduplicação por conteúdo/histórico.

### 26 Como interfaces erros e construção de dependências aparecem em Go

Resposta possível: Eu defino interfaces pequenas a partir da responsabilidade que o caso de uso precisa. Compressor recebe bytes e retorna resultado; Decoder produz Source para inspecionar/redimensionar; Processor inspeciona e converte. NewRouter cria as implementações e injeta pelos construtores. Erros são valores retornados e classificados com errors.Is.

Explicação técnica: Implementação de interface em Go é implícita pela correspondência de métodos, sem implements. Os construtores NewUseCase recebem dependências explicitamente. O decoder retorna uma origem limitada à requisição, sem ID ou entidade persistida. O caminho de conversão também faz uma asserção para acessar Pixels do decoder concreto compartilhado; essa dependência deve ser reconhecida ao discutir desacoplamento.

Comparação útil: O conceito lembra serviços e contratos em Laravel, mas não depende do container do framework. Tipos comuns têm aliases no pacote de compressão para compatibilidade. A separação facilita testes com doubles onde necessário; não torna cada pacote totalmente independente de toda infraestrutura.

Referências: backend/internal/application/imageprocessing/image.go; imagecompression/usecase.go; imageresize/usecase.go; imageconversion/usecase.go; imaging/convert/processor.go.

**Aprofundamento:** Por que não ocultar tudo com ports? Só fronteira útil justifica. Conversão depende de acesso concreto a pixels, sem desacoplamento universal.

## 5 Docker testes e evidências

### 27 Por que CGO e quais dependências existem no Docker

Resposta possível: Eu preciso de CGO porque o binding HEIF chama libheif nativa. O build usa Go 1.27.1 em Alpine com build-base, pkgconf, libheif-dev e plugins libde265/x265. O runtime usa Alpine 3.24 com libheif e plugins, executando como usuário sem privilégios. A imagem final não precisa conter o compilador Go.

Explicação técnica: libheif-dev fornece headers; libde265 participa do decode HEVC e x265 do encode. Compilar com CGO_ENABLED=1 não significa produzir executável totalmente estático e independente dessas bibliotecas. O estágio de testes mantém toolchain e dependências de build. O ADR registra por que o runtime estático distroless anterior não atende a esse conjunto.

Aprofundamento: Separar containers reduz complexidade de produto? Ajuda a separar ambientes Node e Go/nativo, mas ainda exige configuração e builds. Não é prova de alta disponibilidade nem isolamento físico de falhas.

Referências: backend/Dockerfile; frontend/Dockerfile; docs/pt-BR/adr/001-native-image-codecs.md.

**Aprofundamento:** Por que CGO_ENABLED não basta? Binário precisa de libs/plugins compatíveis. Multi-stage mantém runtime sem compilador desnecessário.

### 28 Como reproduzir desenvolvimento e verificações

Resposta possível: Eu uso docker compose -f docker-compose.yml -f compose.development.yaml --profile dev up -d backend frontend-dev para desenvolvimento, com fontes e dependências montadas do host conforme docs/pt-BR/docker/development.md. Para backend, docker compose run --rm backend-test executa go test -v ./... no estágio de build, com as amostras montadas somente para leitura. O backend de runtime não contém o toolchain de testes.

Explicação técnica: Para frontend, executo node --test nos três arquivos de regressão, npx tsc --noEmit e npm run build com NODE_ENV=production no serviço frontend-dev. Quando dependências ou Dockerfiles mudam, reconstruo a imagem apropriada; npm ci usa o lockfile. Os binds do frontend guardam dependências/artefatos no host, não uploads ou histórico de processamento.

Aprofundamento: O que foi executado nesta conclusão? Houve suíte backend de base, testes ampliados dos codecs, suíte completa final, 12 testes frontend, TypeScript e build de produção. Não houve teste manual de navegador, carga ou nova execução com race detector.

Referências: docker-compose.yml; docs/pt-BR/testing/strategy.md; docs/pt-BR/docker/runtime.md.

**Aprofundamento:** Comandos provam execução hoje? Não; são reprodução. Histórico tem datas. Esta revisão só executou ferramentas documentais.

### 29 O que os novos testes de amostras reais verificam

Resposta possível: Eu preservei as nove amostras físicas e ampliei o teste existente de Resize para quatro transformações por arquivo. São 36 transformações mais os nove casos sem mudança que preservam bytes. Na conversão, testei nove origens contra oito destinos: 63 conversões válidas e nove rejeições esperadas de mesma família. Os testes decodificam a saída pelos codecs e não confiam apenas nas dimensões retornadas.

Explicação técnica: Todos os samples atuais são estáticos 512 × 512. Resize testa 256 × 256 proporcional, 516 × 516 proporcional, 256 × 128 independente e 515 × 519 independente. Assim, não aumenta dimensões excessivamente e usa fatores diferentes nos eixos destravados. Conversão compara família detectada, MIME, dimensões orientadas, frame único e bytes de origem intactos; verifica alfa/composição onde há pixels transparentes. A matriz exige política explícita quando o inventário mudar.

Aprofundamento: E variantes? Testes sintéticos separados verificam EXIF, alfa parcial, GIF disposal/tempos/loops, WebP animado, rejeição de AVIF animado/APNG/TIFF multipágina e limites. Pequenos testes HTTP de todos os destinos verificam nome/extensão, MIME, no-store, dimensões e tamanho real do corpo sem repetir a matriz cara.

Referências: backend/internal/infrastructure/imaging/resize/resize_test.go; convert/real_fixtures_test.go; backend/internal/infrastructure/http/conversion_test.go.

**Aprofundamento:** Por que decode independente? Cabeçalhos iguais podem esconder bytes ruins. Decode verifica família/dimensões; percepção/variantes são outras lacunas.

### 30 O que testes passando não provam

Resposta possível: Eu posso dizer que os comportamentos cobertos passaram no ambiente Docker usado. Não posso transformar isso em compatibilidade universal, qualidade visual perfeita, segurança concorrente comprovada ou capacidade de produção. Amostras estáticas quadradas são úteis, mas não representam toda imagem existente nem substituem os casos sintéticos de orientação e animação.

Explicação técnica: Testes frontend de funções e cache não verificam layout, foco, download real ou comportamento entre navegadores. Build/TypeScript verificam compilação e tipos. A documentação registra uma falha anterior de checkptr no binding libheif com race detector; essa execução não foi repetida nesta tarefa. Também não há benchmark de CPU, memória, latência ou vazão nem percentual de cobertura anunciado.

Aprofundamento: Como ampliar evidência sem inventar garantia? Eu escolheria um requisito concreto, casos representativos e métricas adequadas. Separaria regressão funcional, verificação visual, interação browser, concorrência e desempenho, relatando exatamente o que cada execução observou.

Referências: docs/pt-BR/testing/strategy.md; frontend/tests/; docs/pt-BR/docker/runtime.md.

**Aprofundamento:** O que apoia exposição pública? Inputs hostis/variantes, navegador, memória concorrente/falhas nativas e recuperação de deploy. Fixtures não implicam tudo.

## 6 Decisões e limites do produto

### 31 Por que não há histórico banco Redis fila ou worker

Resposta possível: Eu devolvo o resultado diretamente na resposta e mantenho a sessão temporariamente no navegador. Não preciso recuperar imagens por ID, consultar histórico ou executar jobs depois da resposta. Adicionar SQLite, outro banco, Redis, fila, worker ou object storage criaria persistência, retenção, retries e operação sem requisito atual. Essas funcionalidades estão fora do escopo deliberadamente.

Explicação técnica: Síncrono reduz componentes, aceitando que processamento ocupa a requisição e pode custar CPU/memória. Sem estado persistente simplifica ciclo de vida, aceitando perda no reload e reenvio do original. Não adiciono uma operação separada de thumbnails porque Resize cobre a necessidade básica de imagens menores. Editor tipo Paint e composição avançada seriam outro escopo.

Aprofundamento: Isso impede produção para sempre? Não é uma afirmação sobre todo futuro. Se surgisse requisito de jobs longos ou recuperação posterior, eu analisaria alternativas e custos. Hoje não há nova infraestrutura planejada e o projeto não declara prontidão para produção.

Referências: README.pt-BR.md; docs/pt-BR/architecture/overview.md, seção Trade-offs.

**Aprofundamento:** Quando persistir? Recuperação posterior/jobs/retomada exigiriam identidade, retenção, segurança storage e retries além do resultado direto.

### 32 Quais lições e limitações eu destacaria

Resposta possível: Eu destacaria que um problema pequeno de interface tem contratos técnicos relevantes: bytes diferem de nomes, pixels diferem de tamanho, alfa e animações dependem do destino, orientação não é preservação universal de metadados e cancelamento não mata automaticamente código nativo. Aprender Go aqui exige entender esses contratos e verificar a saída real, além de aprender sintaxe.

Explicação técnica: O escopo está concluído, com limites de compatibilidade de variantes, perfis de cor/metadados, recursos e cancelamento. Bibliotecas nativas fazem parte do custo operacional. A ausência de controle global de concorrência e de medição limita qualquer afirmação sobre escala. O guia não atribui a humanos ou IA etapas específicas do desenvolvimento que não foram documentadas.

Aprofundamento: Se perguntarem sobre IA, como responder? Eu explicaria com honestidade a assistência que efetivamente usei e que consigo confirmar, sem inventar um histórico. Consigo demonstrar compreensão percorrendo handler, regra de aplicação, codec e teste, incluindo pontos em que a abstração é limitada.

Referências: docs/pt-BR/architecture/overview.md; backend/internal/infrastructure/imaging/; docs/pt-BR/testing/strategy.md.

**Aprofundamento:** Como defender aprendizado sem inventar? Trace handler/caso/codec/teste e limites. Portfólio demonstra compreensão; produção profissional exige evidência própria.

## 7 Resumos para entrevista

### Explicação de aproximadamente 60 segundos

Eu tenho experiência principal em backend com PHP/Laravel e usei o Go Image Optimizer como aprendizado prático de Go. Ele permite comprimir, redimensionar e converter imagens numa interface Next.js, além de oferecer fallback de prévia quando o navegador não abre um formato suportado. O navegador envia multipart pelas rotas Next.js; o backend Go detecta a família pelos bytes, valida variantes e limites, decodifica, transforma e codifica a saída. O processamento é síncrono e sem persistência: o usuário recebe o resultado para download, com dimensões e tamanho reais, mesmo quando os bytes aumentam. HEIF usa CGO e libheif no Docker. Os testes cobrem nove arquivos reais, quatro transformações de Resize por arquivo e uma matriz com oito destinos, além de orientação, transparência, animações e contratos HTTP. O escopo está concluído, mas não alego escala medida, preservação universal de metadados ou prontidão para produção.

### Explicação de aproximadamente 30 segundos

Eu construí um portfólio de processamento de imagens em Go com interface Next.js para aprender Go a partir da minha experiência em PHP/Laravel. Ele comprime, redimensiona e converte imagens e tem fallback de prévia. Detecta formatos pelos bytes, aplica limites e retorna o arquivo diretamente, sem banco ou histórico. Os testes verificam amostras reais e propriedades como dimensões, orientação e transparência. O escopo está concluído, com limitações explícitas de variantes, metadados, recursos e cancelamento.

## 8 Quadro de decisões

| Decisão | Benefício | Custo aceito |
| --- | --- | --- |
| Processamento síncrono | Resultado na mesma resposta | Requisição ocupada durante trabalho pesado |
| Sem persistência nem histórico | Ciclo de vida simples | Reload perde a sessão; sem recuperação por ID |
| Inspeção separada | Configuração validada pelo backend | Novo upload/decode na execução |
| Decoder compartilhado | Política comum em Resize/conversão/prévia | Acoplamento e diferenças em relação à compressão |
| CGO e libheif | Decode/encode HEIF real | Dependências C e plugins em runtime |
| Prévia nativa com fallback | Exibição de famílias difíceis | Upload extra e rejeição de animações no fallback |
| Catmull–Rom | Interpolação suave | Custo maior e possível ringing |
| Padrões de qualidade | Comportamento previsível | Perdas e bytes não garantidos |
| Composição branca e GIF binário | Política explícita por destino | Perda de alfa e cores onde o formato limita |
| Rejeitar variantes | Evita achatamento silencioso | Compatibilidade limitada |
| Testar saída real | Verifica bytes e contratos | Não mede escala ou qualidade perceptual |
| Escopo encerrado | Projeto focado e explicável | Sem editor, thumbnails separados ou infraestrutura de jobs |

## 9 Afirmações a evitar

| Afirmação imprecisa | Alternativa tecnicamente defensável |
| --- | --- |
| Tenho experiência profissional em Go | Minha experiência principal é PHP/Laravel; Go é aprendizado prático neste portfólio |
| Toda compressão reduz tamanho | Meço bytes; arquivos já otimizados podem ficar iguais ou maiores |
| Conversão sempre melhora qualidade | Muda a representação; pode perder cores, alfa ou detalhes |
| Suporta qualquer imagem da família | Suporta famílias e variantes específicas; as demais são rejeitadas |
| Prévia compatível preserva metadados | Prévia serve à exibição; metadados não são preservados universalmente |
| Lossless significa Resize sem perda | O encoder pode ser lossless, mas a escala altera pixels |
| Cancelamento interrompe o codec | Verifico contexto cooperativamente; chamadas internas podem continuar |
| Dois containers são microsserviços | Separo runtime Node e Go/nativo em uma aplicação pequena |
| Testes passando provam escala | Demonstram os casos cobertos no ambiente de teste |
| Há suporte universal a animações | Resize GIF/WebP tem suporte específico; conversão/prévia rejeitam animações |
| Histórico e fila são próximos passos | Estão fora do escopo; não há novas funcionalidades planejadas |
| O projeto está pronto para produção | Está completo para o escopo atual, com limitações documentadas |

## 10 Estrutura final de raciocínio

Use este percurso para responder a perguntas novas, sem decorar frases: problema → requisito → alternativas → decisão → benefício → custo → falha → tratamento atual → limitação. Em cada etapa, diferencie fato implementado, consequência observável e hipótese futura. Se não houver medição, não substitua evidência por uma expectativa sobre tecnologia.

Exemplo aplicado à prévia: o problema é o navegador não abrir HEIC/TIFF. O requisito é mostrar a imagem sem trocar o arquivo baixado. As alternativas incluem exibir somente uma mensagem, instalar decoders no cliente ou gerar imagem no servidor. A decisão atual é tentar carregamento nativo e depois usar fallback JPEG/PNG. O benefício é compatibilidade de exibição de imagens estáticas suportadas; o custo é upload/decode adicional e gerenciamento de cache/URLs. A falha pode ser codec indisponível, variante rejeitada ou request obsoleto. O tratamento atual é erro local e retry, cancelamento por consumidores e descarte de respostas antigas. A limitação é não garantir prévia animada, metadados ou suporte universal de navegador.

Exercício aplicado a Resize: explique por que 50% menores reduz cada dimensão e não os bytes; depois mostre math.Round, o teto de pixels, Catmull–Rom, o encoder da família e a decodificação independente do teste. Se a saída ficar maior, a resposta continua válida e a interface informa o aumento. Identifique o ponto em que cancelamento é verificado e a etapa que não pode ser interrompida à força.

Referências para revisão: README.pt-BR.md apresenta escopo e fluxos; docs/pt-BR/architecture/overview.md detalha contratos e trade-offs; docs/pt-BR/docker/runtime.md descreve ambiente; docs/pt-BR/testing/strategy.md separa testes existentes de verificações executadas; docs/pt-BR/testing/strategy.md registra as amostras físicas. Ao estudar, percorra também as implementações e os testes citados, verificando o que realmente acontece antes de defender uma decisão.

## Aprofundamentos e estudo ordenado — 2026-10-09

O [contrato Resize](../../../../go-image-optimizer/docs/pt-BR/architecture/overview.md) diferencia padrões: `axis` omitido ou vazio usa `width`; `keepAspectRatio` explicitamente vazio é rejeitado. Números obrigatórios rejeitam vazio. Modal/helpers compartilhados não criam política universal de campo vazio.

**Pergunta: A checagem cliente de 50 MiB é igual ao limite do servidor?** Resposta modelo: “Proxy verifica image.size após parsing FormData; Go limita o corpo multipart inteiro. Overhead conta no backend, então arquivo próximo ao limite pode passar no cliente e falhar no servidor. Nenhuma checagem limita memória total do processo.”

**Aprofundamento:** Por que timeout de socket não interrompe codec? Como Resize sem mudança preserva metadados quando resize real não preserva tudo? Por que bytes iguais em dois Blobs criam entradas diferentes no cache? O que testes de cálculo/cache não provam sobre foco/download no navegador?

Ordem: bytes original/resultado/display e contratos HTTP → detecção/variantes → interfaces/erros → dimensões/orientação/alpha/animação → codecs/cancelamento/recursos → estado frontend/lifetimes → testes/evidência histórica → alternativas condicionais. Nenhuma feature extra é planejada e nenhum assunto é marcado concluído. Auditoria somente por leitura; testes/builds anteriores não foram repetidos.

## Aprofundamentos adicionais de entrevista fundamentados no código

Perguntas e respostas originais acima foram preservadas. IDs abaixo identificam a sequência adicional; não renumeram material retido. Níveis orientam estudo, não status implementado. Aprofundamentos incluem respostas para manter a sequência autossuficiente.

### Q001 — Introdutória: Por que compressão, resize, conversão e preview são operações separadas?

**Resposta:** Implementado: compressão recodifica na família detectada preservando dimensões orientadas; resize muda dimensões em famílias suportadas; conversão muda família; preview cria bytes exibíveis no navegador sem substituir download. Assim a UI explica a mudança e conserva o original para operações posteriores. Preview pode parecer semelhante, mas é artefato distinto com codificação/metadados diferentes. Teoria: representação, geometria e compatibilidade de exibição são preocupações separadas. Operação única reduziria requisições, mas precisaria de contrato combinado para orientação, alpha, animação, tamanho e formato; endpoints focados isolam políticas.

Aprofundamento: Compressão precisa reduzir bytes? Não. Entrada já eficiente, parâmetros de codec ou mudanças de metadados/representação podem aumentar saída. A UI informa bytes reais, não economia presumida. Aprofundamento: Mesmas dimensões implicam mesmos pixels ou fidelidade de cor? Não. Perda, quantização, perfis e política de frames podem alterar conteúdo. Matriz de variantes e fixtures são evidência limitada, não equivalência visual universal.

### Q002 — Intermediária: O que o proxy Next.js muda nas fronteiras de confiança e memória?

**Resposta:** Implementado: o navegador chama rotas `/api/images` da mesma origem. Next.js interpreta multipart em FormData e encaminha a URL do backend no servidor. Propaga status/corpo de erro e cabeçalhos selecionados, materializa bytes bem-sucedidos em ArrayBuffer e retorna no-store. Isso remove dependência do navegador do hostname backend, mas acrescenta processo com bytes não confiáveis e outra fronteira de buffering. O proxy não adiciona token ou autorização. A verificação de arquivo de 50 MiB ocorre após parsing; o limite Go inclui corpo e overhead. Assim arquivo próximo do limite pode passar no proxy e falhar no backend.

Aprofundamento: É streaming? Não ponta a ponta: parsing e ArrayBuffer materializam dados. Streaming reduziria cópias, mas exigiria cuidado com metadados, cancelamento e multipart. Aprofundamento: request.signal prova que CPU backend para? Não. Pode cancelar transporte; codec síncrono já pode estar executando e o caso de uso só verifica contexto antes/depois. Proxy é fronteira arquitetural, não sandbox nativa.

### Q003 — Desafiadora: Por que limites de pixels não garantem memória total segura?

**Resposta:** Implementado: trabalho estático tem limite de 32 milhões de pixels e animação de 64 milhões de pixels de canvas-frames. Verificações por divisão evitam overflow de multiplicação. Entretanto uma imagem RGBA no limite já ocupa aproximadamente 128 milhões de bytes, antes de origem/destino, frames, entrada/saída codificada, alocações nativas e cópias do proxy. Arquivo comprimido pequeno pode decodificar dimensões grandes; limite de bytes trata outro recurso. Verificações por variante não fornecem garantia global de pico de memória, e trabalho nativo pode preceder checks posteriores.

Aprofundamento: E dez uploads válidos concorrentes? Não há admissão global, então trabalho válido por requisição multiplica pressão de memória/CPU. Semáforo ponderado, fila ou worker isolado são hipotéticos; trocam latência, justiça, complexidade operacional e isolamento. Aprofundamento: Timeout libera memória nativa imediatamente? Não necessariamente. Timeouts HTTP limitam rede; chamadas nativas síncronas podem não observar contexto. Medição de formatos representativos e picos concorrentes é lacuna; limites numéricos são constantes, não capacidade medida.

### Q004 — Intermediária: O que interfaces Go e testes fake comprovam aqui?

**Resposta:** Implementado: o caso de uso de compressão depende da interface pequena Compressor; HTTP consome fronteira Execute. O router conecta implementação de imagens concreta sem container de framework. Isso separa multipart/status, validação/contexto e codec. Fake pode verificar rejeição de entrada vazia, propagação de contexto e mapeamento de respostas sem CGO. Não prova validade de saída nativa, preservação de alpha/orientação ou ABI. Testes de imagens reais e HTTP com casos de uso cobrem outras fronteiras.

Aprofundamento: Toda interface prova Clean Architecture? Não. Verifique direção das dependências e responsabilidades reais, não rótulos. Interface só de encaminhamento pode acrescentar custo sem isolar comportamento. Aprofundamento: Mais mocks provariam aplicação completa? Não. Composição, dependências nativas e ciclo de object URLs no navegador exigem evidências próprias. Testes/builds históricos continuam úteis, mas não foram repetidos. A limitação nativa de race/checkptr permanece; interface não elimina riscos de memória nativa. Dependência concreta única simplifica código, mas reduz substituição focada nos testes.

### Q005 — Desafiadora: Como raciocinar sobre atualização produtiva e requisições com falha?

**Resposta:** Implementado: resultados são por requisição, sem banco, job durável ou histórico servidor. Falha do proxy vira 502; falhas de processamento têm status explícitos; codec/inesperadas viram 500. Retry repete trabalho e pode aumentar carga mesmo com entrada igual. Não há garantia de entrega de download interrompido após processamento. Compose/Dockerfiles locais documentam dependências, não SLO medido ou pipeline de rollout. Atualizar backend exige bibliotecas nativas compatíveis; frontend precisa preservar expectativas de metadados/erros.

Aprofundamento: Rollback exigiria restauração de banco? Não há banco de uploads, mas seriam necessários artefatos antigos e contratos de proxy compatíveis. Não há ensaio de rollback evidenciado. Aprofundamento: O que coletar no diagnóstico? Status em cada salto, logs sanitizados, formato/variante detectado, dimensões e reproducer mínimo não sensível. Evite conteúdo de usuário nos logs. Worker separado mudaria persistência/retry dos resultados; proponha apenas para requisitos demonstrados. Não houve gráfico de desempenho, carga, navegador ou implantação runtime nesta revisão.

## Conciliação com o código — 2026-10-18

`2c9a27f40a2a2c8bef5f86f187256870c1960630`. Código, entradas API/CLI, limites de persistência/recursos e definições de testes foram revisados estaticamente. Explicações e respostas existentes continuam aplicáveis nos limites registrados. Não foram produzidos resultados de runtime. Consulte o [roteiro autossuficiente de implementação e entrevista](../../../../go-image-optimizer/docs/pt-BR/guides/implementation-study.md).
