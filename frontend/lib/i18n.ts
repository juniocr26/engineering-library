export type Language = 'pt-BR' | 'en';
export const languageOf = (value?: string): Language => value === 'en' ? 'en' : 'pt-BR';
export const messages = {
  'pt-BR': { projects: 'Projetos', intro: 'Sua biblioteca pessoal de engenharia de software. Conhecimento, arquitetura e experiência reunidos em um só lugar.', language: 'Idioma', previous: 'Página anterior', next: 'Próxima página', page: 'Página', of: 'de', pagination: 'Páginas do catálogo', empty: 'Nenhum projeto disponível.', error: 'Não foi possível abrir o catálogo. Tente novamente em instantes.', retry: 'Tentar novamente', loading: 'Abrindo a biblioteca…', back: '← Voltar aos projetos', index: 'Índice de documentação', noDocs: 'Ainda não há categorias de documentação disponíveis.', alt: 'Escritor com pena em biblioteca clássica iluminada por velas', remote: 'Os índices abrem no repositório público.' },
  en: { projects: 'Projects', intro: 'Your personal software engineering library. Knowledge, architecture and experience in one place.', language: 'Language', previous: 'Previous page', next: 'Next page', page: 'Page', of: 'of', pagination: 'Catalog pages', empty: 'No projects available.', error: 'The catalog could not be opened. Please try again shortly.', retry: 'Try again', loading: 'Opening the library…', back: '← Back to projects', index: 'Documentation index', noDocs: 'No documentation categories are available yet.', alt: 'Writer with a quill in a candlelit classical library', remote: 'Indexes open in the public repository.' }
} as const;
export function catalogHref(page: number, language: Language, slug?: string) {
  return `${slug ? `/projects/${encodeURIComponent(slug)}` : '/'}?lang=${language}&page=${page}`;
}

export const categoryLabels: Record<Language, Record<string, string>> = {
  'pt-BR': { img: 'IMG', architecture: 'Arquitetura', adr: 'Decisões arquiteturais', guides: 'Guias', operations: 'Operações', faq: 'Perguntas e entrevistas técnicas', testing: 'Testes', env: 'Variáveis de ambiente', docker: 'Docker', api: 'API', security: 'Segurança', database: 'Banco de dados', integrations: 'Integrações' },
  en: { img: 'IMG', architecture: 'Architecture', adr: 'Architecture decisions', guides: 'Guides', operations: 'Operations', faq: 'Questions and technical interviews', testing: 'Testing', env: 'Environment variables', docker: 'Docker', api: 'API', security: 'Security', database: 'Database', integrations: 'Integrations' }
};
