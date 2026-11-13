import { mkdir, readFile, writeFile, copyFile, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const { version } = JSON.parse(await readFile(path.join(root, 'package.json'), 'utf8'));
const base = {
  manifest_version: 3,
  name: 'Magic Mark',
  version,
  description: 'Destaca texto temporalmente. Al recargar o salir de la página, las marcas desaparecen. Sin cuentas ni almacenamiento.',
  permissions: ['activeTab', 'scripting', 'contextMenus'],
  icons: { 48: 'icons/icon-48.png', 128: 'icons/icon-128.png' },
  action: { default_title: 'Magic Mark — destacar selección', default_icon: { 48: 'icons/icon-48.png' } },
  commands: {
    highlight: { description: 'Destacar selección' },
    undo: { description: 'Deshacer último destacado' },
    clear: { description: 'Borrar destacados de la página' }
  }
};
for (const browser of ['firefox', 'chromium']) {
  const out = path.join(root, 'dist', browser);
  await rm(out, { recursive: true, force: true });
  await mkdir(path.join(out, 'icons'), { recursive: true });
  const manifest = structuredClone(base);
  manifest.background = browser === 'firefox' ? { scripts: ['background.js'] } : { service_worker: 'background.js' };
  if (browser === 'firefox') manifest.browser_specific_settings = {
    gecko: { id: 'magic-mark@magic-mark.local', strict_min_version: '140.0', data_collection_permissions: { required: ['none'] } },
    gecko_android: { strict_min_version: '142.0' }
  };
  else manifest.minimum_chrome_version = '123';
  await writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  await copyFile(path.join(root, 'extension', 'background.js'), path.join(out, 'background.js'));
  for (const size of [48, 128]) await copyFile(path.join(root, 'extension', 'icons', `icon-${size}.png`), path.join(out, 'icons', `icon-${size}.png`));
  await copyFile(path.join(root, 'LICENSE'), path.join(out, 'LICENSE'));
  console.log(`Built dist/${browser}`);
}
