import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../extension/background.js', import.meta.url), 'utf8');
test('a reported injection failure must not look like a successful mark', async () => {
  const titles = [];
  const event = { addListener() {} };
  const api = {
    scripting: { executeScript: async () => [{ error: { message: 'denied' } }] },
    action: { onClicked: event, setTitle: async args => titles.push(args.title) },
    runtime: { onInstalled: event }, contextMenus: { onClicked: event }, commands: { onCommand: event }
  };
  const context = vm.createContext({ browser: api });
  vm.runInContext(source, context);
  await context.run('highlight', { id: 42 });
  assert.equal(titles.length, 1);
  assert.match(titles[0], /no puede acceder/);
});
test('context-menu action targets the selected frame without granting other origins', async () => {
  const calls=[];let clicked;
  const event={addListener(){}};
  const context=vm.createContext({browser:{
    scripting:{executeScript:async args=>{calls.push(args);return [{result:'highlighted'}];}},
    action:{onClicked:event,setTitle:async()=>{}},runtime:{onInstalled:event},
    contextMenus:{onClicked:{addListener(fn){clicked=fn;}}},commands:{onCommand:event}
  }});
  vm.runInContext(source,context);
  clicked({menuItemId:'highlight',frameId:17},{id:42});
  assert.equal(calls.length,1);
  assert.equal(calls[0].target.tabId,42);
  assert.equal(calls[0].target.frameIds[0],17);
  assert.equal(calls[0].target.allFrames,undefined);
  clicked({menuItemId:'unrelated',frameId:0},{id:42});
  assert.equal(calls.length,1);
});
