/** Run DOM-dependent Mermaid outside the application origin and event loop.
 * The frame is removed on cancellation/timeout; only an SVG string crosses back.
 */
export function renderIsolatedDiagram(source: string, signal: AbortSignal): Promise<string> {
  return new Promise((resolve, reject) => {
    const frame = document.createElement('iframe');
    const nonce = crypto.randomUUID();
    frame.sandbox.add('allow-scripts');
    frame.setAttribute('aria-hidden', 'true');
    frame.title = 'Isolated diagram renderer';
    frame.style.cssText = 'position:fixed;left:-10000px;top:0;width:1200px;height:900px;visibility:hidden;border:0';
    const script = new URL('/api/note-renderer/mermaid', location.origin).href;
    const cleanup = () => { clearTimeout(timer); window.removeEventListener('message', receive); signal.removeEventListener('abort', abort); frame.remove(); };
    const abort = () => { cleanup(); reject(new Error('Diagram rendering cancelled')); };
    const receive = (event: MessageEvent) => {
      if (event.source !== frame.contentWindow || event.data?.nonce !== nonce) return;
      if (event.data.ready) frame.contentWindow!.postMessage({ nonce, source }, '*');
      else { cleanup(); if (typeof event.data.svg === 'string') resolve(event.data.svg); else reject(new Error('Diagram rendering failed')); }
    };
    const timer = setTimeout(abort, 30000);
    window.addEventListener('message', receive);
    signal.addEventListener('abort', abort, { once: true });
    if (signal.aborted) { abort(); return; }
    // User content is transferred as data after load, never interpolated into HTML.
    frame.srcdoc = `<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}' ${script}; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'none'"><script src="${script}"></script><script nonce="${nonce}">
      mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',maxTextSize:5242880,maxEdges:Number.MAX_SAFE_INTEGER,secure:['secure','securityLevel','startOnLoad','maxTextSize','maxEdges','themeCSS'],suppressErrorRendering:true});
      addEventListener('message', async event => {
        if(event.source!==parent || event.data?.nonce!==${JSON.stringify(nonce)}) return;
        try { const result=await mermaid.render('isolated-diagram',event.data.source);parent.postMessage({nonce:${JSON.stringify(nonce)},svg:result.svg},'*'); }
        catch { parent.postMessage({nonce:${JSON.stringify(nonce)},failed:true},'*'); }
      });
      parent.postMessage({nonce:${JSON.stringify(nonce)},ready:true},'*');
    </script>`;
    document.body.append(frame);
  });
}
