"""Installed-extension edge cases; no native mouse/keyboard automation."""
import base64
import json
import time
import sys


def run_extended(root, cmd, js, select, shortcut, count, port):
    results = []
    local = f'http://127.0.0.1:{port}'

    def record(name, details):
        results.append({'test': name, **details})
        (root / 'artifacts' / 'firefox-extended-results.json').write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
        print(name, json.dumps(details, ensure_ascii=False), flush=True)

    def navigate(path='/'):
        cmd('WebDriver:Navigate', {'url': local + path})

    navigate('/strict')
    select('one'); shortcut()
    accepted = js("return [...document.querySelectorAll('style')].filter(s=>s.textContent.includes('magic-mark-selection-v1')).some(s=>!!s.sheet);")
    record('strict_csp', {'ranges': count(), 'extensionStylesheetAccepted': accepted})
    screenshot = cmd('WebDriver:TakeScreenshot', {'id': None, 'full': False, 'scroll': False})['value']
    (root / 'artifacts' / 'magic-mark-strict-csp.png').write_bytes(base64.b64decode(screenshot))

    navigate()
    select('one'); shortcut(); assert count() == 1
    js("document.querySelector('#two').textContent += ' Actualización sin reemplazar el párrafo marcado.';")
    assert count() == 1
    original = js("return [...CSS.highlights.get('magic-mark-selection-v1')][0].toString();")
    js("document.querySelector('#one').replaceWith(Object.assign(document.createElement('p'),{id:'replacement',textContent:'Artículo reemplazado dinámicamente.'}));")
    remaining = js("return [...CSS.highlights.get('magic-mark-selection-v1')].map(r=>r.toString());")
    assert not any(remaining)
    select('replacement'); shortcut()
    record('dynamic_replacement', {'unrelatedUpdatePreservedMark': bool(original),
                                  'oldRangeBecameEmpty': not any(remaining), 'canMarkReplacement': count() == 1,
                                  'note': 'Empty old ranges are pruned on the next action; no automatic restoration.'})
    assert count() == 1
    assert js("return [...CSS.highlights.get('magic-mark-selection-v1')][0].toString().length > 0;")

    navigate()
    js("const r=document.createRange();r.setStart(document.querySelector('#one').firstChild,3);r.setEnd(document.querySelector('#two').firstChild,20);getSelection().removeAllRanges();getSelection().addRange(r);")
    shortcut(); assert count() == 1
    record('cross_paragraph_selection', {'passed': True})

    navigate()
    js("const r=document.createRange();r.setStartBefore(document.querySelector('#third'));r.setEndAfter(document.querySelector('#editor'));getSelection().removeAllRanges();getSelection().addRange(r);")
    shortcut(); assert count() == 0
    record('selection_crossing_editor', {'excluded': True})

    navigate()
    js("const frame=document.createElement('iframe');frame.id='sameframe';frame.src='/frame';document.body.prepend(frame);")
    for _ in range(30):
        if js("return !!document.querySelector('iframe').contentDocument?.querySelector('#one');"):
            break
        time.sleep(.1)
    js("const w=document.querySelector('iframe').contentWindow;const r=w.document.createRange();r.selectNodeContents(w.document.querySelector('#one'));w.getSelection().removeAllRanges();w.getSelection().addRange(r);getSelection().removeAllRanges();")
    shortcut()
    assert count() == 0
    record('frame_main_command_scope', {'parentNotIncorrectlyMarked': True,
                                       'contextMenuInFrame': 'not tested'})

    navigate()
    labels = js("return {links:[...document.querySelectorAll('a')].every(a=>a.textContent.trim()),editorLabel:document.querySelector('#editor').getAttribute('aria-label')};")
    before_markup = js('return document.body.innerHTML;')
    select('one'); shortcut()
    unchanged = before_markup == js('return document.body.innerHTML;')
    assert unchanged
    # WCAG relative luminance for the fixed highlight foreground/background.
    def luminance(rgb):
        values = [v / 255 for v in rgb]
        linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
        return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))
    ratio = (luminance((255,224,102))+.05)/(luminance((23,23,23))+.05)
    assert ratio >= 4.5
    record('basic_accessibility', {'highlightTextContrast': round(ratio, 2),
                                   'selectionMarkupUnchanged': unchanged,
                                   'fixtureLabels': labels, 'screenReaderAndNativeUI': 'not tested'})

    first = cmd('WebDriver:GetWindowHandle')['value']
    second = cmd('WebDriver:NewWindow', {'type': 'tab'})['handle']
    cmd('WebDriver:SwitchToWindow', {'handle': second})
    navigate(); select('one'); shortcut(); assert count() == 1
    cmd('WebDriver:CloseWindow')
    cmd('WebDriver:SwitchToWindow', {'handle': first})
    cmd('Marionette:SetContext', {'value': 'chrome'})
    try:
        restored = cmd('WebDriver:ExecuteScript', {'script': "let module;try{module=ChromeUtils.importESModule('moz-src:///browser/components/sessionstore/SessionStore.sys.mjs');}catch{module=ChromeUtils.importESModule('resource:///modules/sessionstore/SessionStore.sys.mjs');}const win=Services.wm.getMostRecentWindow('navigator:browser');module.SessionStore.undoCloseTab(win,0,win);return true;", 'args': []})['value']
    except Exception as error:
        restored = False
        record('undo_closed_tab_controller', {'status': 'unavailable', 'reason': str(error)[:200]})
    finally:
        cmd('Marionette:SetContext', {'value': 'content'})
    if restored:
        restored_handle = None
        for _ in range(40):
            handles = cmd('WebDriver:GetWindowHandles')
            if isinstance(handles, dict): handles = handles['value']
            restored_handle = next((h for h in handles if h != first), None)
            if restored_handle: break
            time.sleep(.1)
        if restored_handle:
            cmd('WebDriver:SwitchToWindow', {'handle': restored_handle})
            for _ in range(40):
                if js("return !!document.querySelector('#one');"): break
                time.sleep(.1)
            assert count() == 0
            record('undo_closed_tab', {'passed': True, 'rangesAfterRestore': count()})
        else:
            record('undo_closed_tab', {'status': 'unavailable in controller'})
    else:
        record('undo_closed_tab', {'status': 'unavailable in controller'})

    cmd('WebDriver:SetTimeouts', {'pageLoad': 12000, 'script': 15000})
    pages=() if '--local-only' in sys.argv else ('https://example.com/', 'https://developer.mozilla.org/en-US/docs/Web/API/Range',
                'https://en.wikipedia.org/wiki/Web_browser', 'https://docs.python.org/3/tutorial/',
                'https://www.w3.org/TR/css-highlight-api-1/')
    for url in pages:
        try:
            cmd('WebDriver:Navigate', {'url': url})
            text_length = js("const p=[...document.querySelectorAll('main p, article p, p')].find(p=>p.textContent.trim().length>50);if(!p)return 0;const r=document.createRange();r.selectNodeContents(p);getSelection().removeAllRanges();getSelection().addRange(r);return p.textContent.length;")
            if not text_length:
                record('public_page', {'url': url, 'status': 'unavailable/no suitable paragraph'})
                continue
            shortcut()
            record('public_page', {'url': url, 'status': 'passed' if count() else 'failed',
                                   'ranges': count(), 'selectedCharacterCount': text_length})
        except Exception as error:
            record('public_page', {'url': url, 'status': 'unavailable', 'reason': str(error)[:200]})
