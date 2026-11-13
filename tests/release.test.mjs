import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

// Exercise the build, checking distribution boundaries rather than implementation details.
const root = new URL('../', import.meta.url);
execFileSync(process.execPath, ['scripts/build.mjs'], { cwd: root });
const pkg = JSON.parse(readFileSync(new URL('package.json', root)));
for (const browser of ['firefox', 'chromium']) {
  test(`${browser} distribution has matching version, minimal permissions and valid assets`, () => {
    const manifest = JSON.parse(readFileSync(new URL(`dist/${browser}/manifest.json`, root)));
    assert.equal(manifest.version, pkg.version);
    assert.ok(manifest.description.length <= 132);
    assert.deepEqual(manifest.permissions, ['activeTab', 'scripting', 'contextMenus']);
    assert.equal(manifest.host_permissions, undefined);
    assert.equal(manifest.content_scripts, undefined);
    assert.ok(Object.values(manifest.commands).every(command => !command.suggested_key), 'Shortcuts must be assigned by the user to avoid browser/language conflicts');
    for (const icon of Object.values(manifest.icons)) {
      assert.equal(readFileSync(new URL(`dist/${browser}/${icon}`, root)).subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    }
    if (browser === 'firefox') {
      assert.ok(manifest.background.scripts);
      assert.deepEqual(manifest.browser_specific_settings.gecko.data_collection_permissions.required, ['none']);
    } else {
      assert.equal(manifest.background.service_worker, 'background.js');
      assert.equal(manifest.browser_specific_settings, undefined);
    }
  });
}
