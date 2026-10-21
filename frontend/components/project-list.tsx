/* eslint-disable @next/next/no-img-element */
'use client';
import Link from '@/components/navigation-link';
import type { Project } from '@/lib/catalog';
import { catalogHref, type Language } from '@/lib/i18n';
function ProjectIcon({ slug }: { slug: string }) {
  return <img className="ico" src={`/api/projects/${encodeURIComponent(slug)}/icon`} alt="" onError={event => { event.currentTarget.onerror = null; event.currentTarget.src = '/assets/project-fallback.svg'; }} />;
}
export function ProjectCard({ project, language, page }: { project: Project; language: Language; page: number }) {
  return <Link className="project" href={catalogHref(page, language, project.slug)}><ProjectIcon slug={project.slug}/><span><strong>{project.name}</strong><small>{project.description}</small></span><span className="chev" aria-hidden="true">›</span></Link>;
}
export function ProjectList({ projects, language, page }: { projects: Project[]; language: Language; page: number }) {
  return <div className="projects">{projects.map(project => <ProjectCard key={project.slug} project={project} language={language} page={page}/>)}</div>;
}
