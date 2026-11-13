import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../extension/background.js', import.meta.url), 'utf8');
const core = source.slice(source.indexOf('function markPage('), source.indexOf('\nasync function run('));
function page(HighlightCtor = Set) {
  const listeners = new Map();
  const element = { closest: () => null, querySelectorAll: () => [] };
  const range = { collapsed: false, toString: () => 'article', commonAncestorContainer: { nodeType: 3, parentElement: element }, cloneRange() { return { ...this }; } };
  const selection = { isCollapsed: false, rangeCount: 1, getRangeAt: () => range, removeAllRanges() { this.isCollapsed = true; } };
  const context = vm.createContext({
    CSS: { highlights: new Map() }, Highlight: HighlightCtor, Node: { ELEMENT_NODE: 1 },
    document: { head: { append() {} }, createElement: () => ({ remove() {} }) },
    window: { getSelection: () => selection, addEventListener: (name, fn) => listeners.set(name, fn), removeEventListener: (name, fn) => { if (listeners.get(name) === fn) listeners.delete(name); } }
  });
  vm.runInContext(core, context);
  return { context, selection, element, listeners, run: cmd => context.markPage(cmd) };
}
test('independent documents, undo and full release', () => {
  const a = page(), b = page();
  assert.equal(a.run('highlight'), 'highlighted');
  a.selection.isCollapsed = false;
  assert.equal(a.run('highlight'), 'highlighted');
  assert.equal(a.context.__magicMark_v1.highlight.size, 2);
  assert.equal(b.context.CSS.highlights.size, 0);
  a.run('undo');
  assert.equal(a.context.__magicMark_v1.highlight.size, 1);
  a.run('undo');
  assert.equal(a.context.__magicMark_v1, undefined);
  assert.equal(a.context.CSS.highlights.size, 0);
  assert.equal(a.listeners.size, 0);
});
test('pagehide clears state before a cached document can return', () => {
  const p = page(); p.run('highlight'); p.listeners.get('pagehide')();
  assert.equal(p.context.__magicMark_v1, undefined);
  assert.equal(p.context.CSS.highlights.size, 0);
  assert.equal(p.listeners.size, 0);
});
test('clear removes the original listener and a new mark has a fresh lifecycle', () => {
  const p = page(); p.run('highlight'); p.run('clear');
  assert.equal(p.listeners.size, 0);
  p.selection.isCollapsed = false; p.run('highlight');
  assert.equal(p.listeners.size, 1);
  p.listeners.get('pagehide')();
  assert.equal(p.context.__magicMark_v1, undefined);
});
test('empty selection and editors retain no state', () => {
  const p = page(); p.selection.isCollapsed = true;
  assert.equal(p.run('highlight'), 'no-selection');
  p.selection.isCollapsed = false; p.element.closest = () => ({});
  assert.equal(p.run('highlight'), 'editor');
  assert.equal(p.context.__magicMark_v1, undefined);
});
test('range cap prevents unbounded retention', () => {
  const p = page();
  for (let i = 0; i < 500; i++) { p.selection.isCollapsed = false; p.run('highlight'); }
  p.selection.isCollapsed = false;
  assert.equal(p.run('highlight'), 'limit');
  assert.equal(p.context.__magicMark_v1.highlight.size, 500);
  p.run('clear'); assert.equal(p.context.__magicMark_v1, undefined);
});
test('dynamic replacement cannot exhaust the cap with invisible ranges', () => {
  const p = page();
  for (let i = 0; i < 510; i++) {
    if (p.context.__magicMark_v1) {
      for (const range of p.context.__magicMark_v1.highlight) range.collapsed = true;
    }
    p.selection.isCollapsed = false;
    assert.equal(p.run('highlight'), 'highlighted');
    assert.equal(p.context.__magicMark_v1.highlight.size, 1);
  }
  p.run('clear');
  assert.equal(p.listeners.size, 0);
});
test('mark and undo do not enumerate native Highlight across Firefox compartments', () => {
  class RestrictedHighlight extends Set {
    [Symbol.iterator]() { throw Error('Xray wrapping of iterators not supported'); }
    forEach() { throw Error('Permission denied to access object'); }
  }
  const p = page(RestrictedHighlight);
  p.run('highlight'); p.selection.isCollapsed = false; p.run('highlight');
  assert.equal(p.context.__magicMark_v1.highlight.size, 2);
  p.run('undo');
  assert.equal(p.context.__magicMark_v1.highlight.size, 1);
  p.run('undo');
  assert.equal(p.context.__magicMark_v1, undefined);
});
