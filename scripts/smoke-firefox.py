import socket,json,time,subprocess,threading,base64,os,sys
from http.server import HTTPServer, BaseHTTPRequestHandler
class Fixture(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
  if self.path.startswith('/strict'):self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'none'; script-src 'none'")
  self.end_headers();self.wfile.write((root/'tests'/'fixture.html').read_bytes())
 def log_message(self,*args):pass
server=HTTPServer(("127.0.0.1",0),Fixture)
threading.Thread(target=server.serve_forever,daemon=True).start()
from pathlib import Path
root=Path(__file__).resolve().parent.parent; profile=root/'artifacts'/('firefox-test-'+str(int(time.time()))); profile.mkdir(exist_ok=True)
probe=socket.socket();probe.bind(('127.0.0.1',0));port=probe.getsockname()[1];probe.close()
(profile/'user.js').write_text(f'user_pref("marionette.port", {port});\nuser_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.startup.homepage_override.mstone", "ignore");\n')
log=open(root/'artifacts'/'firefox-test.log','w')
interactive = '--interactive' in sys.argv
firefox_executable = os.environ.get('MAGIC_MARK_FIREFOX', r'C:\Program Files\Mozilla Firefox\firefox.exe')
p=subprocess.Popen([firefox_executable,* ([] if interactive else ['--headless']),'--no-remote','--profile',str(profile),'--marionette','--remote-allow-system-access','about:blank'],stdout=log,stderr=log,env={**os.environ,"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS":"1"})
s=None
try:
 for i in range(60):
  try: s=socket.create_connection(('127.0.0.1',port),timeout=1);break
  except OSError: time.sleep(.25)
 if s is None: raise RuntimeError('Marionette did not start')
 s.settimeout(15)
 def recv():
  n=b''
  while True:
   c=s.recv(1)
   if c==b':':break
   if not c:raise RuntimeError('Connection closed')
   n+=c
  data=b''
  while len(data)<int(n):data+=s.recv(int(n)-len(data))
  return json.loads(data)
 recv(); counter=0
 def cmd(name,args={}):
  global counter
  counter+=1;data=json.dumps([0,counter,name,args]).encode();s.sendall(str(len(data)).encode()+b':'+data)
  res=recv()
  if res[2]:raise RuntimeError(str(res[2]))
  return res[3]
 session_browser_version=cmd('WebDriver:NewSession',{'capabilities':{'alwaysMatch':{'acceptInsecureCerts':True}}})['capabilities']['browserVersion']
 print('SESSION',session_browser_version,flush=True)
 package = root/'artifacts'/('magic-mark-'+json.loads((root/'package.json').read_text())['version']+'-firefox.zip')
 if '--test-shortcuts' in sys.argv:
  # Bind optional commands in an isolated test copy; shipped defaults stay intact.
  from zipfile import ZipFile, ZIP_DEFLATED
  test_package = profile/'test-shortcuts.zip'
  with ZipFile(package) as source, ZipFile(test_package,'w',ZIP_DEFLATED) as target:
   for entry in source.namelist():
    data=source.read(entry)
    if entry=='manifest.json':
     manifest=json.loads(data)
     for name,key in [('highlight','M'),('undo','U'),('clear','L')]:manifest['commands'][name]['suggested_key']={'default':'Alt+Shift+'+key}
     data=json.dumps(manifest).encode()
    target.writestr(entry,data)
  package=test_package
 print('INSTALL',cmd('Addon:Install',{'path':str(package),'temporary':True}))
 cmd('Marionette:SetContext', {'value':'content'})
 cmd('WebDriver:Navigate',{'url':f'http://127.0.0.1:{server.server_port}/'})
 def js(script):return cmd('WebDriver:ExecuteScript',{'script':script,'args':[]})['value']
 def select(id):js("const r=document.createRange();r.selectNodeContents(document.getElementById('"+id+"'));getSelection().removeAllRanges();getSelection().addRange(r);")
 def shortcut(command='highlight'):
  cmd('Marionette:SetContext',{'value':'chrome'})
  key={'highlight':'M','undo':'U','clear':'L'}[command]
  cmd('WebDriver:ExecuteScript',{'script':"const key=[...document.querySelectorAll('#ext-keyset-id-magic-mark_magic-mark_local key')].find(k=>k.getAttribute('key').toUpperCase()===arguments[0]);if(!key)throw Error('Missing configured command');key.dispatchEvent(new Event('command'));",'args':[key]})
  cmd('Marionette:SetContext',{'value':'content'})
  time.sleep(.04 if '--performance' in sys.argv else .4)
 def count():return js("return CSS.highlights.get('magic-mark-selection-v1')?.size ?? 0;")
 if '--extended' in sys.argv:
  from test_firefox_extended import run_extended
  run_extended(root, cmd, js, select, shortcut, count, server.server_port)
  sys.exit(0)
 if '--performance' in sys.argv or '--ab' in sys.argv:
  from measure_firefox import measure
  measure(root, cmd, js, select, shortcut, count, configured_package=package)
  sys.exit(0)
 if interactive:
  print('READY: isolated Firefox; JSON lines: eval, select, raw, count, quit',flush=True)
  for line in sys.stdin:
   try:
    request=json.loads(line)
    if request['op']=='quit':break
    elif request['op']=='eval':result=js(request['script'])
    elif request['op']=='select':select(request['id']);result=count()
    elif request['op']=='raw':result=cmd(request['name'],request.get('args',{}))
    elif request['op']=='count':result=count()
    else:raise ValueError('Unknown test operation')
    print(json.dumps({'result':result}),flush=True)
   except Exception as error:print(json.dumps({'error':str(error)}),flush=True)
  sys.exit(0)
 select('one');shortcut(); print('SHORTCUT_COUNT',count());assert count()==1
 select('two');shortcut()
 assert count()==2
 if '--test-shortcuts' in sys.argv:
  shortcut('undo');assert count()==1
  shortcut('clear');assert count()==0
  select('one');shortcut();select('two');shortcut();assert count()==2
  print('CONFIGURED_UNDO_CLEAR_COMMANDS',True,flush=True)
 capture=cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'scroll':False})['value']
 (root/'artifacts'/'magic-mark-firefox-highlighted.png').write_bytes(base64.b64decode(capture))
 print('SCREENSHOT_SAVED')
 first=cmd('WebDriver:GetWindowHandle')['value']
 second=cmd('WebDriver:NewWindow',{'type':'tab'})['handle']
 cmd('WebDriver:SwitchToWindow',{'handle':second})
 cmd('WebDriver:Navigate',{'url':f'http://127.0.0.1:{server.server_port}/'})
 assert count()==0
 select('one');shortcut();assert count()==1
 cmd('WebDriver:SwitchToWindow',{'handle':first});assert count()==2
 print('TAB_ISOLATION',True)
 cmd('WebDriver:SwitchToWindow',{'handle':second});cmd('WebDriver:CloseWindow')
 cmd('WebDriver:SwitchToWindow',{'handle':first});assert count()==2
 reopened=cmd('WebDriver:NewWindow',{'type':'tab'})['handle']
 cmd('WebDriver:SwitchToWindow',{'handle':reopened})
 cmd('WebDriver:Navigate',{'url':f'http://127.0.0.1:{server.server_port}/'});assert count()==0
 print('CLOSE_AND_NEW_TAB_CLEAN',True)
 cmd('WebDriver:SwitchToWindow',{'handle':first})
 cmd('WebDriver:Navigate',{'url':f'http://127.0.0.1:{server.server_port}/other'})
 cmd('WebDriver:Back');assert count()==0
 print('BACK_CLEARS',True)
 select('one');shortcut();assert count()==1
 cmd('WebDriver:Refresh');assert count()==0
 print('RELOAD_CLEARS',True)
 select('editor');shortcut();assert count()==0
 print('EDITOR_EXCLUDED',True)
 js("document.body.style.background='#17233b';document.body.style.color='white';")
 select('third');shortcut();assert count()==1
 print('MIXED_INLINE_TEXT',True)
 cmd('WebDriver:Refresh');assert count()==0
 result={'browser':session_browser_version,'extensionVersion':json.loads((root/'package.json').read_text())['version'],'installedCommandIntegration':True,'independentTabs':True,'reloadClears':True,'backClears':True,'closedTabNewDocumentClean':True,'editorExcluded':True,'mixedInlineText':True,'configuredUndoClearCommandsTested':'--test-shortcuts' in sys.argv,'physicalKeyboardAndMouse':'pending'}
 for report_name in ['firefox-results.json',f'firefox-{session_browser_version}-results.json']:
  (root/'artifacts'/report_name).write_text(json.dumps(result,indent=2))
 capture=cmd('WebDriver:TakeScreenshot',{'id':None,'full':False,'scroll':False})['value']
 (root/'artifacts'/'magic-mark-firefox-reloaded.png').write_bytes(base64.b64decode(capture))
 cmd('Marionette:Quit',{'flags':['eForceQuit']})
finally:
 if s:
  try:cmd('Marionette:Quit',{'flags':['eForceQuit']})
  except Exception:pass
  s.close()
 if p.poll() is None:p.terminate()
 server.shutdown();server.server_close();log.close()
