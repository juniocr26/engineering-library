import { manuscriptMarks } from '../lib/manuscript';
export function ManuscriptDecorations({ variant = 'catalog', project = 'library', identity = variant }: { variant?: 'catalog' | 'reading' | 'illustration'; project?: string; identity?: string }) {
  const marks = manuscriptMarks(project, identity, variant);
  return <div className={`manuscript-decorations manuscript-decorations--${variant}`} aria-hidden="true" data-decoration-id={`${project}:${identity}`}>
    <span className="manuscript-burns" />
    {marks.map((mark, index) => <span key={index} className={`seeded-mark seeded-mark--${mark.kind}`} style={{ [mark.edge]: -mark.size * .32, top: `${mark.top}%`, width: mark.size, height: mark.size, transform: `rotate(${mark.rotation}deg)`, opacity: mark.kind === 'abrasion' ? .22 : mark.kind === 'ink' ? mark.opacity + .25 : mark.opacity + .15 }}/>) }
  </div>;
}
