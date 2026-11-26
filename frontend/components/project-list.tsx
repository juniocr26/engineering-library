/* eslint-disable @next/next/no-img-element */
'use client';
import Link from '@/components/navigation-link';
import type { Project } from '@/lib/catalog';
import { catalogHref, type Language } from '@/lib/i18n';
function recoverIcon(image: HTMLImageElement) {
  if (image.getAttribute('src') !== '/assets/project-fallback.webp') image.src = '/assets/project-fallback.webp';
}
function ProjectIcon({ slug }: { slug: string }) {
  return <img className="ico" width={32} height={32} src={`/api/projects/${encodeURIComponent(slug)}/icon`} alt="" ref={image => { if (image?.complete && !image.naturalWidth) recoverIcon(image); }} onError={event => recoverIcon(event.currentTarget)} />;
}
type Action = (action: 'update' | 'remove', project: Project) => void;
type OperationStatus = { projectId?: string; slug?: string; deleting: boolean; message: string; paused?: boolean };
export function OperationIndicator({ deleting, message, paused }: Pick<OperationStatus, 'deleting' | 'message' | 'paused'>) {
  return <span className={`catalog-operation${deleting ? ' catalog-operation--deleting' : ''}${paused ? ' catalog-operation--paused' : ''}`} role="status" aria-live="polite" aria-atomic="true">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d={deleting ? 'M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 10v7m4-7v7' : 'M20 7v5h-5M4 17v-5h5M19 12a7 7 0 0 0-12-5L4 10m16 4-3 3a7 7 0 0 1-12-5'}/></svg>
    <span>{message}</span>
  </span>;
}
export function ProjectCard({ project, language, page, onAction, operation, actionsDisabled }: { project: Project; language: Language; page: number; onAction?: Action; operation?: OperationStatus; actionsDisabled?: boolean }) {
  const status = operation && ((operation.projectId && operation.projectId === project.id) || operation.slug === project.slug) ? operation : undefined;
  const link = <Link className="project" href={catalogHref(page, language, project.slug)}><ProjectIcon slug={project.slug}/><span><strong>{project.name}</strong><small>{project.description}</small>{status && <OperationIndicator {...status}/>}</span><span className="chev" aria-hidden="true">›</span></Link>;
  if (!onAction || !project.id) return link;
  return <div className="catalog-entry">{link}<div className="catalog-actions"><button type="button" className="catalog-icon" disabled={actionsDisabled} aria-label={`${language === 'en' ? 'Update documentation' : 'Atualizar documentação'}: ${project.name}`} onClick={() => onAction('update', project)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 7v5h-5M4 17v-5h5M19 12a7 7 0 0 0-12-5L4 10m16 4-3 3a7 7 0 0 1-12-5"/></svg></button><button type="button" className="catalog-icon" disabled={actionsDisabled} aria-label={`${language === 'en' ? 'Remove project' : 'Remover projeto'}: ${project.name}`} onClick={() => onAction('remove', project)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 10v7m4-7v7"/></svg></button></div></div>;
}
export function ProjectList({ projects, language, page, onAction, operation, actionsDisabled }: { projects: Project[]; language: Language; page: number; onAction?: Action; operation?: OperationStatus; actionsDisabled?: boolean }) {
  return <div className="projects">{projects.map(project => <ProjectCard key={project.slug} project={project} language={language} page={page} onAction={onAction} operation={operation} actionsDisabled={actionsDisabled}/>)}</div>;
}
