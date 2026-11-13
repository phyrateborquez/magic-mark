"""Isolated installed-extension smoke test. Requires Playwright Python + Chromium."""
import json
import tempfile
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
class Fixture(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write((root / 'tests' / 'fixture.html').read_bytes())
    def log_message(self, *args):
        pass
server = HTTPServer(('127.0.0.1', 0), Fixture)
threading.Thread(target=server.serve_forever, daemon=True).start()
with tempfile.TemporaryDirectory(prefix='magic-mark-chromium-') as profile:
    with sync_playwright() as p:
        extension = str(root / 'dist' / 'chromium')
        context = p.chromium.launch_persistent_context(
            profile, channel="chromium", headless=True,
            args=[f'--disable-extensions-except={extension}', f'--load-extension={extension}'],
        )
        try:
            worker = context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
            page = context.pages[0]
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            # Headless shortcuts are not a reliable browser UI integration test.
            # Test the unmodified core in real DOM separately from worker loading.
            source = (root / 'extension' / 'background.js').read_text(encoding='utf-8')
            core = source[source.index('function markPage('):source.index('\nasync function run(')]
            page.evaluate('() => { globalThis.testMark = ' + core + '; }')
            page.evaluate("""() => { const r=document.createRange(); r.selectNodeContents(document.querySelector('#one')); getSelection().removeAllRanges(); getSelection().addRange(r); }""")
            assert page.evaluate("testMark('highlight')") == 'highlighted'
            assert page.evaluate("CSS.highlights.get('magic-mark-selection-v1').size") == 1
            page.screenshot(path=str(root / 'artifacts' / 'magic-mark-chromium-core.png'))
            page.evaluate("testMark('clear')")
            assert page.evaluate("!CSS.highlights.has('magic-mark-selection-v1') && !globalThis.__magicMark_v1")
            cdp = context.new_cdp_session(page)
            cdp.send('Performance.enable')
            measurements = []
            for number in (0, 1, 20, 100):
                timing = page.evaluate('''number => {
                    testMark('clear');
                    const start=performance.now();
                    for(let i=0;i<number;i++) {
                        const r=document.createRange();r.selectNodeContents(document.querySelector('#one'));
                        getSelection().removeAllRanges();getSelection().addRange(r);testMark('highlight');
                    }
                    return {totalMs:performance.now()-start, ranges:CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0};
                }''', number)
                assert timing['ranges'] == number
                cdp.send('HeapProfiler.collectGarbage')
                heap = cdp.send('Runtime.getHeapUsage')['usedSize']
                before = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
                started = time.perf_counter()
                time.sleep(1)
                after = {m['name']: m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
                measurements.append({'ranges': number, 'pageJSHeapBytes': heap,
                                     'batchMarkMs': timing['totalMs'],
                                     'idleRendererTaskMs': (after['TaskDuration']-before['TaskDuration'])*1000,
                                     'idleWallSeconds': time.perf_counter()-started})
            page.evaluate("testMark('clear')")
            cdp.send('HeapProfiler.collectGarbage')
            after_clear_heap = cdp.send('Runtime.getHeapUsage')['usedSize']
            (root / 'artifacts' / 'performance-core.json').write_text(json.dumps({
                'scope': 'Chromium page core only; not installed extension CPU/RSS',
                'browser': context.browser.version, 'measurements': measurements,
                'afterClearJSHeapBytes': after_clear_heap,
                'limitations': 'One local run, synthetic repeated selection, no process RAM or background worker measured; no general performance guarantee.'
            }, indent=2), encoding='utf-8')
            report = {'browser': context.browser.version, 'installedWorkerStarted': True,
                      'realDOMCorePassed': True, 'installedUserInteraction': 'pending',
                      'note': 'Core evaluated directly; no claim of activeTab/UI integration.'}
            (root / 'artifacts' / 'chromium-results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            print(json.dumps(report))
        finally:
            context.close()
            server.shutdown()
