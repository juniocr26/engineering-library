'use client';
import { Fragment, memo, useEffect, useId, useState, type ReactNode } from 'react';
import Link from 'next/link';
import { SourceCode } from './source-code';
import { ReaderTable, useTableScroll } from './reader-table';
import { ExpandableMedia } from './expandable-media';
import Markdown, { defaultUrlTransform } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { resolveDocumentLink } from '../lib/document-links';
import type { MarkdownUnit as Unit } from '../lib/markdown';
import type { Root, Element, RootContent } from 'hast';
import type { SourceReference } from '../lib/source-links';
import type { Language } from '../lib/i18n';

let mermaidModule: Promise<typeof import('mermaid')> | undefined;
const diagramCache = new Map<string, Promise<string>>();
let diagramSerial = 0;
function Diagram({ source, language, query }: { source: string; language: Language; query: string }) {
  const id = `diagram-${useId().replace(/[^a-zA-Z0-9]/g, '')}`;
  const [result, setResult] = useState<{ svg?: string; failed?: boolean } | null>(null);
  useEffect(() => {
    let live = true;
    if (!diagramCache.has(source)) diagramCache.set(source, (async () => {
      mermaidModule ??= import('mermaid').then(module => { module.default.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'neutral', flowchart: { htmlLabels: false }, suppressErrorRendering: true }); return module; });
      const { default: mermaid } = await mermaidModule;
      const key = `mermaid-${++diagramSerial}`;
      const { svg } = await mermaid.render(key, source);
      return svg.replaceAll(key, '__DIAGRAM_ID__');
    })());
    void diagramCache.get(source)!.then(svg => { if (live) setResult({ svg: svg.replaceAll('__DIAGRAM_ID__', id) }); }, () => { if (live) setResult({ failed: true }); });
    return () => { live = false; };
  }, [source, id]);
  return <div className="reader-diagram" data-measure-pending={!result ? 'true' : 'false'}>
    {result?.svg ? <ExpandableMedia svg={result.svg} language={language} alt={language === 'en' ? 'Documentation diagram' : 'Diagrama da documentação'}><div role="img" aria-label={language === 'en' ? 'Documentation diagram' : 'Diagrama da documentação'} dangerouslySetInnerHTML={{ __html: result.svg }}/></ExpandableMedia> : !result ? <p>{language === 'en' ? 'Rendering diagram…' : 'Renderizando diagrama…'}</p> : null}
    <details open={result?.failed || !!query}><summary>{language === 'en' ? 'Diagram source' : 'Código do diagrama'}</summary><pre><code>{highlighted(source, query)}</code></pre></details>
  </div>;
}

function highlighted(children: ReactNode, query: string): ReactNode {
  if (typeof children === 'string' && query) {
    const index = children.toLowerCase().indexOf(query.toLowerCase());
    if (index >= 0) return <>{children.slice(0, index)}<mark>{children.slice(index, index + query.length)}</mark>{children.slice(index + query.length)}</>;
  }
  if (Array.isArray(children)) return children.map((child, index) => <Fragment key={index}>{highlighted(child, query)}</Fragment>);
  return children;
}

function disclosurePlugin(references: SourceReference[]) {
  return () => (tree: Root) => {
    const counts = new Map<string, number>();
    const visit = (node: Root | RootContent) => {
      if (node.type === 'element' && node.tagName === 'a') {
        const href = String(node.properties.href ?? '');
        const ordinal = counts.get(href) ?? 0; counts.set(href, ordinal + 1);
        const reference = references.filter(ref => ref.href === href)[ordinal];
        if (reference) node.properties['data-source-id'] = reference.id;
      }
      if ('children' in node) node.children.forEach(child => visit(child as Element));
    };
    visit(tree);
  };
}

export const MarkdownUnit = memo(function MarkdownUnit({ unit, project, document, language, query, plainTable = false, expanded, toggleSource, location }: { location?: string; expanded?: ReadonlySet<string>; toggleSource?: (id: string) => void; plainTable?: boolean; unit: Unit; project: string; document: string; language: Language; query: string }) {
  const scroll = useTableScroll(`${project}/${document}/${language}/${unit.tableOrigin ?? unit.id}`);
  if (unit.code) return <SourceCode collapse={toggleSource ? () => toggleSource(unit.code!.id) : undefined} unit={unit} language={language} query={query} location={location}/>;
  const source = unit.table && unit.tablePart ? `${unit.table.header}${unit.table.rows.slice(unit.tablePart.start, unit.tablePart.end).join('\n')}\n\n${unit.table.definitions}` : unit.source;
  return <div className="reader-markdown"><Markdown skipHtml remarkPlugins={[remarkGfm]} rehypePlugins={[disclosurePlugin(unit.references ?? [])]} urlTransform={(url, key) => defaultUrlTransform(key === 'href' && unit.references?.some(ref => ref.href === url) ? url : resolveDocumentLink(project, document, language, url, key === 'src') ?? '')} components={{
    a: ({ href, children, node }) => { const ref = unit.references?.find(ref => ref.id === node?.properties['data-source-id']); if (ref) return <button type="button" className="source-reference" aria-expanded={expanded?.has(ref.id) ?? false} onClick={() => toggleSource?.(ref.id)}><span aria-hidden="true">{expanded?.has(ref.id) ? '▾ ' : '▸ '}</span>{children}</button>; return href?.startsWith('/projects/') ? <Link href={href}>{highlighted(children, query)}</Link> : <a href={href} rel={href?.startsWith('http') ? 'noreferrer' : undefined}>{highlighted(children, query)}</a>; },
    img: ({ src, alt }) => <ExpandableMedia src={typeof src === 'string' ? src : undefined} alt={alt ?? ''} language={language}/>,
    pre: ({ children }) => <div className="reader-code">{children}</div>,
    code: ({ className, children }) => className === 'language-mermaid' ? <Diagram source={String(children).trim()} language={language} query={query}/> : <code className={className}>{highlighted(children, query)}</code>,
    table: ({ children }) => plainTable ? <table>{children}</table> : <ReaderTable canSplit={!!unit.table} part={unit.tablePart} language={language} scroll={scroll} fullTable={() => <MarkdownUnit unit={{ ...unit, tablePart: undefined }} project={project} document={document} language={language} query={query} plainTable/>}>{children}</ReaderTable>,
    p: ({ children }) => <p>{highlighted(children, query)}</p>,
    li: ({ children }) => <li>{highlighted(children, query)}</li>,
    h1: ({ children }) => <h1>{highlighted(children, query)}</h1>,
    h2: ({ children }) => <h2>{highlighted(children, query)}</h2>,
    h3: ({ children }) => <h3>{highlighted(children, query)}</h3>,
    h4: ({ children }) => <h4>{highlighted(children, query)}</h4>,
    h5: ({ children }) => <h5>{highlighted(children, query)}</h5>,
    h6: ({ children }) => <h6>{highlighted(children, query)}</h6>,
    td: ({ children, style }) => <td style={style}>{highlighted(children, query)}</td>,
    th: ({ children, style }) => <th scope="col" style={style}>{highlighted(children, query)}</th>,
    strong: ({ children }) => <strong>{highlighted(children, query)}</strong>,
    em: ({ children }) => <em>{highlighted(children, query)}</em>,
  }}>{source}</Markdown></div>;
});
