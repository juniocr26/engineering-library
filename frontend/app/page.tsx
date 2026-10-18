import { BackendStatus } from '@/components/backend-status';
export const dynamic = 'force-dynamic';
export default function Home() {
  return <main id="main"><header><span className="monogram" aria-hidden="true">EL</span><span>Engineering Library</span><span className="edition">FOUNDATION · 01</span></header>
    <article><p className="eyebrow">A FIELD GUIDE TO SOFTWARE ENGINEERING</p><h1>Good engineering.<br /><em>Worth keeping.</em></h1>
      <p className="intro">A quiet home for technical documentation, architectural decisions, and the lessons behind the code.</p>
      <hr /><section aria-labelledby="chapter"><p className="eyebrow">THE OPENING CHAPTER</p><h2 id="chapter">Building the foundation</h2>
      <p>The documentation platform is under development. Our existing English and Brazilian Portuguese engineering guides remain available in the repository.</p>
      <a href="https://github.com/juniocr26/engineering-library/tree/main/docs">Browse the documentation <span aria-hidden="true">↗</span></a></section>
      <footer><BackendStatus /><span>ENGLISH & PORTUGUÊS BRASILEIRO</span></footer></article></main>;
}
