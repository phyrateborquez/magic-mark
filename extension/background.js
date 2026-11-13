/* Magic Mark — MIT. No storage, network, timers or resident content listeners. */
const api = globalThis.browser ?? globalThis.chrome;

// Serialized by scripting.executeScript: keep this function self-contained.
function markPage(command) {
  const key = '__magicMark_v1';
  const name = 'magic-mark-selection-v1';
  let state = globalThis[key];
  function release() {
    if (!state) return;
    CSS.highlights.delete(name);
    state.highlight.clear();
    state.ranges.length = 0;
    state.style.remove();
    window.removeEventListener('pagehide', state.release);
    delete globalThis[key];
    state = undefined;
  }
  // Live ranges can collapse when a dynamic page replaces its text. Prune only
  // on explicit actions so invisible marks don't consume the range cap forever.
  if (state && command !== 'clear') {
    state.ranges = state.ranges.filter(range => {
      if (range.collapsed || range.startContainer?.isConnected === false || range.endContainer?.isConnected === false) {
        state.highlight.delete(range);
        return false;
      }
      return true;
    });
    if (!state.highlight.size) {
      state.release();
      state = undefined;
    }
  }
  if (command === 'clear') {
    state?.release();
    return 'cleared';
  }
  if (command === 'undo') {
    if (!state) return 'empty';
    const last = state.ranges.pop();
    state.highlight.delete(last);
    if (!state.highlight.size) state.release();
    return 'undone';
  }
  if (command !== 'highlight') return 'invalid';
  if (!globalThis.CSS?.highlights || typeof Highlight === 'undefined') return 'unsupported';
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed || !selection.rangeCount) return 'no-selection';
  const ranges = [];
  for (let i = 0; i < selection.rangeCount; i++) {
    const range = selection.getRangeAt(i);
    if (range.collapsed || !range.toString().trim()) continue;
    // Reject selections touching editors, including an editor between endpoints.
    const root = range.commonAncestorContainer;
    const element = root.nodeType === Node.ELEMENT_NODE ? root : root.parentElement;
    const editor = 'input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="textbox"]';
    if (element?.closest(editor)) return 'editor';
    if (element) {
      for (const candidate of element.querySelectorAll(editor)) {
        if (range.intersectsNode(candidate)) return 'editor';
      }
    }
    ranges.push(range.cloneRange());
  }
  if (!ranges.length) return 'no-selection';
  // Bound retained ranges without copying selected text into extension storage.
  if ((state?.highlight.size ?? 0) + ranges.length > 500) return 'limit';
  if (!state) {
    const style = document.createElement('style');
    style.textContent = `::highlight(${name}) { background-color: #ffe066; color: #171717; }`;
    (document.head ?? document.documentElement).append(style);
    state = { highlight: new Highlight(), ranges: [], style, release };
    globalThis[key] = state;
    // Also clear when leaving a document kept in the back/forward cache.
    window.addEventListener('pagehide', release);
  }
  for (const range of ranges) {
    state.highlight.add(range);
    state.ranges.push(range);
  }
  CSS.highlights.set(name, state.highlight);
  selection.removeAllRanges();
  return 'highlighted';
}

async function run(command, tab, frameId = 0) {
  if (!Number.isInteger(tab?.id)) return;
  try {
    const results = await api.scripting.executeScript({
      target: { tabId: tab.id, frameIds: [frameId] },
      func: markPage,
      args: [command]
    });
    if (!results.length || results[0].error) throw new Error('Injection failed');
    const result = results[0]?.result;
    const messages = {
      'no-selection': 'Selecciona texto y pulsa Magic Mark.',
      unsupported: 'Esta versión del navegador no admite destacados nativos.',
      editor: 'Selecciona texto fuera de formularios y editores.',
      limit: 'Límite de 500 fragmentos por página. Borra algunos para continuar.'
    };
    await api.action.setTitle({ tabId: tab.id, title: messages[result] ?? 'Magic Mark — destacar selección' });
  } catch {
    // Browser-internal pages, restricted sites and inaccessible frames.
    await api.action.setTitle({ tabId: tab.id, title: 'Magic Mark no puede acceder a esta página o marco.' }).catch(() => {});
  }
}

api.runtime.onInstalled.addListener(() => {
  api.contextMenus.removeAll().then(() => {
    api.contextMenus.create({ id: 'highlight', title: 'Magic Mark: destacar selección', contexts: ['selection'] });
    api.contextMenus.create({ id: 'undo', title: 'Magic Mark: deshacer último destacado', contexts: ['page', 'selection'] });
    api.contextMenus.create({ id: 'clear', title: 'Magic Mark: borrar destacados', contexts: ['page', 'selection'] });
  });
});
api.action.onClicked.addListener(tab => run('highlight', tab));
api.contextMenus.onClicked.addListener((info, tab) => {
  if (['highlight', 'undo', 'clear'].includes(info.menuItemId)) run(info.menuItemId, tab, info.frameId ?? 0);
});
api.commands.onCommand.addListener(async command => {
  if (!['highlight', 'undo', 'clear'].includes(command)) return;
  try {
    const [tab] = await api.tabs.query({ active: true, currentWindow: true });
    await run(command, tab);
  } catch {
    // The active window can close between a command and its tab lookup.
  }
});
