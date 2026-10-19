import { textAnchor, type TextAnchor } from './text-anchors';

const excluded = 'button,summary,input,select,textarea,[role="button"],pre,table,svg,img,figure,video,audio,canvas,[hidden],[aria-hidden="true"],[inert],[role="toolbar"],nav,.reader-diagram,.source-code,.reader-code,.source-reference,[data-highlight-unsupported]';

function eligible(node: Text, block: HTMLElement) {
  const parent = node.parentElement;
  if (!parent || parent.closest(excluded)) return false;
  // Collapsed disclosures keep their text in textContent; never paint or capture it.
  for (let element: Element | null = parent; element && block.contains(element); element = element.parentElement) {
    if (element instanceof HTMLDetailsElement && !element.open && !element.querySelector('summary')?.contains(node)) return false;
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
  }
  return true;
}

/** Keep legacy textContent offsets, splitting only the painted/captured DOM ranges. */
export function eligibleRanges(block: HTMLElement, start: number, end: number, selection?: Range): Range[] {
  const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
  const result: Range[] = [];
  let offset = 0;
  while (walker.nextNode()) {
    const node = walker.currentNode as Text;
    const from = Math.max(0, start - offset);
    const to = Math.min(node.length, end - offset);
    offset += node.length;
    if (from >= to || !eligible(node, block) || (selection && !selection.intersectsNode(node))) { continue; }
    const range = document.createRange();
    range.setStart(node, from); range.setEnd(node, to);
    if (selection) {
      if (range.compareBoundaryPoints(Range.START_TO_START, selection) < 0) range.setStart(selection.startContainer, selection.startOffset);
      if (range.compareBoundaryPoints(Range.END_TO_END, selection) > 0) range.setEnd(selection.endContainer, selection.endOffset);
    }
    if (range.collapsed) continue;
    // Separate nodes deliberately: a range spanning them could include an empty control.
    result.push(range);
  }
  return result;
}

export function selectedAnchors(block: HTMLElement, selection: Range): TextAnchor[] {
  const text = block.textContent ?? '';
  const result: TextAnchor[] = [];
  for (const range of eligibleRanges(block, 0, text.length, selection)) {
    const prefix = document.createRange(); prefix.selectNodeContents(block); prefix.setEnd(range.startContainer, range.startOffset);
    const start = prefix.toString().length;
    const end = start + range.toString().length;
    const previous = result.at(-1);
    if (previous && previous.end === start) result[result.length - 1] = textAnchor(block.dataset.highlightBlock!, text, previous.start, end);
    else result.push(textAnchor(block.dataset.highlightBlock!, text, start, end));
  }
  return result;
}
