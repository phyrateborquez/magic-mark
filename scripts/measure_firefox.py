"""Process-level measurements for the isolated Firefox test, not extension-only RAM."""
import json
import statistics
import sys
import time


def measure(root, cmd, js, select, shortcut, count, configured_package=None):
    sys.path.insert(0, str(root / 'artifacts' / 'test-tools'))
    import psutil

    def chrome(script):
        cmd('Marionette:SetContext', {'value': 'chrome'})
        try:
            return cmd('WebDriver:ExecuteScript', {'script': script, 'args': []})['value']
        finally:
            cmd('Marionette:SetContext', {'value': 'content'})

    pid = chrome('return Services.appinfo.processID;')
    browser = psutil.Process(pid)
    samples = []
    version = json.loads((root / 'package.json').read_text())['version']
    install_package = configured_package or root / 'artifacts' / f'magic-mark-{version}-firefox.zip'
    browser_version = chrome('return Services.appinfo.version;')

    def snapshot():
        entries = {}
        for process in [browser, *browser.children(recursive=True)]:
            try:
                with process.oneshot():
                    if process.name().lower() != 'firefox.exe':
                        continue
                    times = process.cpu_times()
                    memory = process.memory_info()
                    entries[(process.pid, process.create_time())] = {
                        'cpu': times.user + times.system, 'rss': memory.rss,
                        'private': getattr(memory, 'private', None),
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return time.perf_counter(), entries

    def observe(label, seconds):
        print(f'MEASURE {label}: {seconds}s', flush=True)
        start, initial = snapshot()
        previous_time, previous = start, initial
        intervals = []
        while time.perf_counter() - start < seconds:
            time.sleep(min(5, max(0, seconds - (time.perf_counter() - start))))
            now, current = snapshot()
            elapsed = now - previous_time
            cpu = sum(max(0, value['cpu'] - previous[key]['cpu'])
                      for key, value in current.items() if key in previous)
            intervals.append({'elapsedSeconds': elapsed,
                              'cpuPercentOneCore': cpu / elapsed * 100,
                              'rssBytes': sum(v['rss'] for v in current.values()),
                              'privateBytes': sum(v['private'] or 0 for v in current.values()),
                              'processCount': len(current)})
            previous_time, previous = now, current
        result = {'scenario': label, 'seconds': previous_time - start,
                  'meanCPUPercentOneCore': sum(x['cpuPercentOneCore'] * x['elapsedSeconds'] for x in intervals) / (previous_time-start),
                  'medianRSSMiB': statistics.median(x['rssBytes'] for x in intervals) / 1048576,
                  'medianPrivateMiB': statistics.median(x['privateBytes'] for x in intervals) / 1048576,
                  'intervals': intervals}
        samples.append(result)
        checkpoint='firefox-ab-checkpoint.json' if '--ab' in sys.argv else 'firefox-process-performance-checkpoint.json'
        (root / 'artifacts' / checkpoint).write_text(json.dumps({
            'extensionVersion': version, 'browserVersion': browser_version,
            'complete': False, 'samples': samples,
        }, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in result.items() if k != 'intervals'}), flush=True)

    if '--ab' in sys.argv:
        addon='magic-mark@magic-mark.local'
        installed=True
        cmd('WebDriver:SetTimeouts',{'pageLoad':20000,'script':15000})
        pages=['https://example.com/','https://en.wikipedia.org/wiki/Web_browser','https://developer.mozilla.org/en-US/docs/Web/API/Range']
        runs=[]
        for pair,url in enumerate(pages):
            for mode in (['A','B'] if pair%2==0 else ['B','A']):
                if installed:
                    cmd('Addon:Uninstall',{'id':addon});installed=False
                if mode=='B':
                    cmd('Addon:Install',{'path':str(install_package),'temporary':True});installed=True
                loaded=True
                try:cmd('WebDriver:Navigate',{'url':url})
                except Exception:loaded=False
                if not loaded:
                    runs.append({'pair':pair,'mode':mode,'url':url,'status':'navigation unavailable'})
                    print('AB_NAVIGATION_UNAVAILABLE',url,mode,flush=True)
                    continue
                if mode=='B':
                    for _ in range(20):
                        ready=js("const p=[...document.querySelectorAll('main p,article p,p')].find(p=>p.textContent.trim().length>50);if(!p)return false;const r=document.createRange();r.selectNodeContents(p);getSelection().removeAllRanges();getSelection().addRange(r);return true;")
                        if not ready:break
                        shortcut()
                    if not ready or count()!=20:
                        raise AssertionError('A/B marked phase did not create 20 ranges')
                time.sleep(5)
                observe(f'Pair {pair+1} {mode}: {url}',60)
                runs.append({'pair':pair,'mode':mode,'url':url,'status':'measured','measurement':samples[-1]})
                (root/'artifacts'/'firefox-ab-results.json').write_text(json.dumps({'complete':False,'runs':runs},indent=2),encoding='utf-8')
        (root/'artifacts'/'firefox-ab-results.json').write_text(json.dumps({
            'complete':True,'extensionVersion':version,'browserVersion':browser_version,'runs':runs,
            'design':'Three paired public pages; order AB, BA, AB; A uninstalled, B installed with 20 ranges; 60s observation + 5s settling per phase.',
            'limitations':'One browser session with caching/startup/network noise; missing phases excluded, three pairs are not a causal estimate or leak proof. CPU and memory cover the entire isolated Firefox tree.'
        },indent=2),encoding='utf-8')
        print('AB_COMPLETE',flush=True)
        return

    # Warm the local document and let installation/startup finish before the baseline.
    time.sleep(5)
    addon_id = 'magic-mark@magic-mark.local'
    cmd('Addon:Uninstall', {'id': addon_id})
    observe('Firefox without Magic Mark, one local tab', 15)
    cmd('Addon:Install', {'path': str(install_package), 'temporary': True})
    observe('Magic Mark installed, zero marks', 15)
    for target in (1, 20, 100):
        while count() < target:
            expected = count() + 1
            select('one')
            shortcut()
            assert count() == expected
        observe(f'One tab, {target} ranges', 15 if target != 100 else 60)
    first = cmd('WebDriver:GetWindowHandle')['value']
    url = js('return location.href;')
    for _ in range(2):
        handle = cmd('WebDriver:NewWindow', {'type': 'tab'})['handle']
        cmd('WebDriver:SwitchToWindow', {'handle': handle})
        cmd('WebDriver:Navigate', {'url': url})
        for i in range(20):
            select('two')
            shortcut()
            assert count() == i + 1
    observe('Three tabs, 140 total ranges', 20)
    cmd('WebDriver:SwitchToWindow', {'handle': first})
    cmd('WebDriver:Refresh')
    assert count() == 0
    observe('First tab reloaded, other tabs still marked', 15)
    handles = cmd('WebDriver:GetWindowHandles')
    if isinstance(handles, dict):
        handles = handles['value']
    for handle in handles:
        if handle != first:
            cmd('WebDriver:SwitchToWindow', {'handle': handle})
            cmd('WebDriver:CloseWindow')
    cmd('WebDriver:SwitchToWindow', {'handle': first})
    assert count() == 0
    observe('One clean tab after closing marked tabs', 15)
    report = {'extensionVersion': version, 'browserVersion': browser_version, 'complete': True,
              'platform': sys.platform, 'psutilVersion': psutil.__version__, 'samples': samples,
              'scope': 'Sum of isolated Firefox root and descendant firefox.exe processes; headless, local synthetic page.',
              'limitations': ['CPU is percent of one logical core, not machine-normalized.',
                             'RSS sums can double-count shared pages; private bytes are committed private memory, not resident-only RAM.',
                             'Counters from processes that exit between samples may be missed.',
                             'Sequential single run with warm-up/cache/GC noise; baseline differences do not isolate extension cost.',
                             'Repeated ranges on the same paragraphs; not a real news browsing session or leak proof.']}
    (root / 'artifacts' / 'firefox-process-performance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('RESOURCE_REPORT_SAVED', flush=True)
