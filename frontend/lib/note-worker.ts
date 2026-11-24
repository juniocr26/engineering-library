import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import { isolateNoteHtml } from './note-html';

self.onmessage = async (event: MessageEvent<string>) => {
  try {
    const processor = unified().use(remarkParse).use(remarkGfm).use(remarkRehype, { allowDangerousHtml: true }).use(rehypeRaw).use(isolateNoteHtml);
    self.postMessage({ tree: await processor.run(processor.parse(event.data)) });
  } catch { self.postMessage({ error: 'Could not render this note. The original source is preserved.' }); }
};
