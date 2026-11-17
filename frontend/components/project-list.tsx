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
export function ProjectCard({ project, language, page }: { project: Project; language: Language; page: number }) {
  return <Link className="project" href={catalogHref(page, language, project.slug)}><ProjectIcon slug={project.slug}/><span><strong>{project.name}</strong><small>{project.description}</small></span><span className="chev" aria-hidden="true">›</span></Link>;
}
export function ProjectList({ projects, language, page }: { projects: Project[]; language: Language; page: number }) {
  return <div className="projects">{projects.map(project => <ProjectCard key={project.slug} project={project} language={language} page={page}/>)}</div>;
}
