/** Fixed compositions keep server rendering and hydration identical. CSS owns all assets. */
export function ManuscriptDecorations({ variant = 'catalog' }: { variant?: 'catalog' | 'reading' | 'illustration' }) {
  return <div className={`manuscript-decorations manuscript-decorations--${variant}`} aria-hidden="true">
    <span className="manuscript-burns" />
    <span className="manuscript-script manuscript-script--top" />
    <span className="manuscript-script manuscript-script--side" />
    <span className="manuscript-ink manuscript-ink--large" />
    <span className="manuscript-ink manuscript-ink--small" />
    <span className="manuscript-wax" />
  </div>;
}
