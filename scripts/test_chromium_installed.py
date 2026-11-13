"""Installed-extension action integration using the experimental CDP Extensions API."""
import json
import sys
import time
import tempfile
import shutil
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
class Fixture(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write((root/'tests'/'fixture.html').read_bytes())
    def log_message(self, *args): pass

server=HTTPServer(('127.0.0.1',0),Fixture)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
with tempfile.TemporaryDirectory(prefix='magic-mark-installed-') as profile, sync_playwright() as p:
    extension=str(root/'dist'/'chromium')
    minimum='--minimum' in sys.argv
    if '--native-minimum' in sys.argv:
        launch_options={'executable_path':json.loads((root/'artifacts/browsers/chrome-minimum.json').read_text())['executable']}
    elif minimum:
        copied=Path(profile)/'test-extension'
        shutil.copytree(extension,copied)
        manifest=json.loads((copied/'manifest.json').read_text())
        manifest['host_permissions']=['http://127.0.0.1/*']
        (copied/'manifest.json').write_text(json.dumps(manifest))
        extension=str(copied)
        launch_options={'executable_path':json.loads((root/'artifacts/browsers/chrome-minimum.json').read_text())['executable']}
    elif '--chrome' in sys.argv:
        launch_options={'executable_path':json.loads((root/'artifacts/browsers/chrome-stable.json').read_text())['executable']}
    else:
        launch_options = {'executable_path': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'} if '--edge' in sys.argv else {'channel':'chromium'}
    native_probe='--native-probe' in sys.argv
    context=p.chromium.launch_persistent_context(profile,headless=not minimum and not native_probe,**launch_options,
        args=[f'--disable-extensions-except={extension}',f'--load-extension={extension}',
              '--enable-unsafe-extension-debugging',*(['--headless=new'] if minimum else [])])
    try:
        worker=context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
        extension_id=worker.url.split('/')[2]
        browser_cdp=context.browser.new_browser_cdp_session()
        class FreshWorker:
            def __init__(self,url): self.url=url
            def evaluate(self,expression,arg=None):
                targets=browser_cdp.send('Target.getTargets')['targetInfos']
                target=next(t for t in targets if t['type']=='service_worker' and t['url']==self.url)
                sid=browser_cdp.send('Target.attachToTarget',{'targetId':target['targetId'],'flatten':False})['sessionId']
                answers=[]
                def received(event):
                    if event.get('sessionId')==sid:
                        message=json.loads(event['message'])
                        if message.get('id')==1:answers.append(message)
                browser_cdp.on('Target.receivedMessageFromTarget',received)
                try:
                    code=f'({expression})({json.dumps(arg)})' if '=>' in expression else expression
                    browser_cdp.send('Target.sendMessageToTarget',{'sessionId':sid,'message':json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':code,'awaitPromise':True,'returnByValue':True}})})
                    deadline=time.monotonic()+10
                    while not answers and time.monotonic()<deadline:context.pages[0].wait_for_timeout(20)
                    if not answers:raise TimeoutError('Fresh worker evaluation timed out')
                    answer=answers[0]
                    if 'error' in answer or 'exceptionDetails' in answer.get('result',{}):raise RuntimeError(str(answer))
                    return answer['result']['result'].get('value')
                finally:
                    browser_cdp.remove_listener('Target.receivedMessageFromTarget',received)
                    browser_cdp.send('Target.detachFromTarget',{'sessionId':sid})
        page=context.pages[0];page.goto(url)
        if native_probe:
            page.evaluate("url=>{const f=document.createElement('iframe');f.id='nativeframe';f.title='Marco de prueba Magic Mark';f.src=url+'frame';f.style='display:block;width:95%;height:300px';document.body.append(f);}",url)
            page.evaluate("document.body.tabIndex=-1;document.body.focus();const r=document.createRange();r.selectNodeContents(document.querySelector('#one'));getSelection().removeAllRanges();getSelection().addRange(r);")
            print('NATIVE_PROBE_READY: isolated unmodified package, automatic close in 300 seconds',flush=True)
            observations=[]
            for _ in range(100):
                page.wait_for_timeout(3000)
                frames=page.frames
                observations.append({'elapsedSeconds':(_+1)*3,'rootRanges':page.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0"),
                                     'frameRanges':[f.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0") for f in frames if f!=page.main_frame]})
                (root/'artifacts'/'native-observations.json').write_text(json.dumps({'browser':context.browser.version,'unmodifiedManifest':True,'observations':observations},indent=2),encoding='utf-8')
            page.screenshot(path=str(root/'artifacts'/'native-probe-final.png'))
            print('NATIVE_PROBE_FINAL_RANGES',page.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0"),flush=True)
            sys.exit(0)
        tab_targets={}
        def mark(page, selector):
            page.bring_to_front()
            page.eval_on_selector(selector,"node=>{const r=document.createRange();r.selectNodeContents(node);getSelection().removeAllRanges();getSelection().addRange(r);}")
            if minimum:
                worker.evaluate("""async()=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await run('highlight',tab);}""")
                return
            if page not in tab_targets:
                targets=browser_cdp.send('Target.getTargets',{'filter':[{'type':'tab','exclude':False},{'exclude':True}]})['targetInfos']
                candidates=[t for t in targets if t['targetId'] not in tab_targets.values() and t.get('url')==page.url]
                if len(candidates)!=1:
                    raise RuntimeError('Cannot uniquely identify tab target: '+json.dumps(targets))
                tab_targets[page]=candidates[0]['targetId']
            target=tab_targets[page]
            browser_cdp.send('Extensions.triggerAction',{'id':extension_id,'targetId':target})
        def count(page): return page.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0")
        mark(page,'#one');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===1")
        mark(page,'#two');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===2")
        zoom_result=None
        if '--zoom' in sys.argv:
            page.locator('#third a').focus()
            focused=page.evaluate("document.activeElement?.outerHTML")
            mark(page,'#third');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===3")
            assert page.evaluate("document.activeElement?.outerHTML")==focused
            stages=[]
            for zoom in (1,2):
                actual=worker.evaluate("""async zoom=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await chrome.tabs.setZoom(tab.id,zoom);return chrome.tabs.getZoom(tab.id);}""",zoom)
                page.wait_for_timeout(200)
                assert actual==zoom and count(page)==3
                bounds=page.evaluate("""()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,rects:[...CSS.highlights.get('magic-mark-selection-v1')].flatMap(r=>[...r.getClientRects()].map(x=>({left:x.left,right:x.right})))})""")
                assert not bounds['overflow']
                assert all(r['left']>=-1 and r['right']<=bounds['width']+1 for r in bounds['rects'])
                stages.append({'zoom':actual,'ranges':count(page),'horizontalOverflow':bounds['overflow']})
                # Viewport capture avoids full-page clip scaling with native tab zoom.
                page.screenshot(path=str(root/'artifacts'/f'magic-mark-zoom-{zoom*100}.png'),full_page=False)
            worker.evaluate("""async()=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await chrome.tabs.setZoom(tab.id,1);await run('undo',tab);}""")
            assert count(page)==2
            zoom_result={'stages':stages,'DOMFocusPreservedDuringInjectedAction':True,'limitation':'Does not validate focus movement through native toolbar/menu controls.'}
        lifecycle=None
        if '--lifecycle' in sys.argv:
            boot_nonce=worker.evaluate("globalThis.__magicMarkTestNonce=crypto.randomUUID()")
            closed=[]
            worker.on('close',lambda _:closed.append(True))
            targets=browser_cdp.send('Target.getTargets')['targetInfos']
            target=next(t for t in targets if t['type']=='service_worker' and t['url']==worker.url)
            browser_cdp.send('Target.closeTarget',{'targetId':target['targetId']})
            page.wait_for_timeout(500)
            remaining=browser_cdp.send('Target.getTargets')['targetInfos']
            print('WORKER_CLOSE_DIAGNOSTIC',json.dumps({'closeEvent':bool(closed),'oldTargetRemaining':any(t['targetId']==target['targetId'] for t in remaining)}),flush=True)
            assert not any(t['targetId']==target['targetId'] for t in remaining), 'Old worker target remains'
            assert count(page)==2
            print('WORKER_TERMINATED_MARKS_RETAINED',flush=True)
            mark(page,'#third');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===3")
            worker=FreshWorker(worker.url)
            worker.evaluate("""async()=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await run('undo',tab);}""")
            assert count(page)==2
            restarted=next(t for t in browser_cdp.send('Target.getTargets')['targetInfos'] if t['type']=='service_worker' and t['url']==worker.url)
            nonce_after=worker.evaluate("globalThis.__magicMarkTestNonce ?? null")
            assert nonce_after!=boot_nonce, 'Worker global state survived: restart not confirmed'
            lifecycle={'oldTarget':target['targetId'],'newTarget':restarted['targetId'],
                       'terminationConfirmedByTargetRemoval':True,'bootNonceCleared':True,'closeEventObserved':bool(closed),
                       'marksRetained':True,'newActionSucceeded':True}
        async_command="""async command=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await run(command,tab);} """
        worker.evaluate(async_command,'undo');assert count(page)==1
        worker.evaluate(async_command,'clear');assert count(page)==0
        mark(page,'#one');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===1")
        mark(page,'#two');page.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===2")
        page.evaluate("url=>{const f=document.createElement('iframe');f.id='testframe';f.src=url+'frame';document.body.append(f);}",url)
        child=page.frame_locator('#testframe')
        child.locator('#one').wait_for()
        child.locator('#one').evaluate("node=>{const r=document.createRange();r.selectNodeContents(node);getSelection().removeAllRanges();getSelection().addRange(r);}")
        frame_results=worker.evaluate("""async()=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});return chrome.scripting.executeScript({target:{tabId:tab.id,allFrames:true},func:()=>location.href});}""")
        frame_id=next(r['frameId'] for r in frame_results if r['result'].endswith('/frame'))
        worker.evaluate("""async frameId=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await run('highlight',tab,frameId);}""",frame_id)
        frame=page.locator('#testframe').element_handle().content_frame()
        assert frame.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size")==1
        assert count(page)==2
        foreign_origin_test=None
        if not minimum:
            page.evaluate("url=>{const f=document.createElement('iframe');f.id='foreignframe';f.src=url.replace('127.0.0.1','localhost')+'foreign';document.body.append(f);}",url)
            page.frame_locator('#foreignframe').locator('#one').wait_for()
            attempt=worker.evaluate("""async()=>{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});try{const r=await chrome.scripting.executeScript({target:{tabId:tab.id,allFrames:true},func:()=>location.hostname});return {origins:r.map(x=>x.result)};}catch{return {denied:true};}}""")
            assert 'localhost' not in attempt.get('origins',[])
            foreign=page.locator('#foreignframe').element_handle().content_frame()
            assert foreign.evaluate("CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0")==0
            foreign_origin_test={'unauthorizedFrameNotInjected':True,'probe':attempt}
        second=context.new_page();second.goto(url);assert count(second)==0
        mark(second,'#one');second.wait_for_function("CSS.highlights.get('magic-mark-selection-v1')?.size===1")
        assert count(page)==2
        page.screenshot(path=str(root/'artifacts'/'magic-mark-chromium-installed.png'))
        page.reload();assert count(page)==0
        second.close();fresh=context.new_page();fresh.goto(url);assert count(fresh)==0
        report={'product':'Edge' if '--edge' in sys.argv else ('Chrome for Testing' if '--chrome' in sys.argv or minimum else 'Chromium'),'browser':context.browser.version,'extensionVersion':json.loads((root/'package.json').read_text())['version'],
                'installedActionViaCDP':not minimum,'minimumRuntimeWithTestHostGrant':minimum,'multipleMarks':True,'undoClearViaInstalledBackground':True,
                'sameOriginFrameRouting':True,'tabIsolation':True,'reloadClears':True,
                'newTabClean':True,'workerLifecycle':lifecycle,'zoomAndFocus':zoom_result,'foreignOrigin':foreign_origin_test,'limitation':'CDP browser action, not physical toolbar click, context menu or OS keyboard.'}
        (root/'artifacts'/'chromium-installed-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        if '--edge' in sys.argv:
            (root/'artifacts'/'edge-installed-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        if '--chrome' in sys.argv:
            (root/'artifacts'/'chrome-installed-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        if minimum:
            report['limitation']='Exact production code with a LOCALHOST host grant in isolated test copy; does not verify activeTab/native UI on Chrome 123.'
            (root/'artifacts'/'chrome-minimum-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report),flush=True)
    finally:
        context.close();server.shutdown();server.server_close()
