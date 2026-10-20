# Shared visual assets / Recursos visuais compartilhados

Store reusable assets here, outside project chapters. Use lowercase kebab-case names and meaningful alt text. Do not duplicate the writer photograph or icons from frontend/public/assets. Asset files are never catalog chapters.

Guarde recursos reutilizáveis aqui, fora dos capítulos dos projetos. Use nomes em kebab-case e texto alternativo descritivo. Não duplique fotografias ou ícones existentes em frontend/public/assets. Recursos não são capítulos.

Markdown: `![Reader persistence](/img/diagrams/reader-storage.svg)`.

The reader maps /img/ to /api/shared-assets/, independently of project and language. Only image extensions are served, with realpath containment and a restrictive CSP. /assets/ references existing frontend public assets.

O leitor mapeia /img/ para /api/shared-assets/, independentemente do projeto e idioma. Apenas extensões de imagem são servidas, com contenção de realpath e CSP restritiva. /assets/ referencia recursos públicos existentes.
