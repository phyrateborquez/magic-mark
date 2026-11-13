"""Validate distribution boundaries and hashes without installing or publishing."""
import hashlib
import argparse
import json
from pathlib import Path
from zipfile import ZipFile

root = Path(__file__).resolve().parent.parent
version = json.loads((root / 'package.json').read_text())['version']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=root / 'artifacts')
output = parser.parse_args().output_dir.resolve()
expected_files = {'LICENSE', 'background.js', 'manifest.json', 'icons/icon-48.png', 'icons/icon-128.png'}
expected_permissions = ['activeTab', 'scripting', 'contextMenus']
hashes = dict(line.split('  ', 1)[::-1] for line in (output / 'SHA256SUMS.txt').read_text().splitlines())

for browser in ('firefox', 'chromium', 'source'):
    name = f'magic-mark-{version}-{browser}.zip'
    archive = output / name
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == hashes[name], f'Checksum mismatch: {name}'
    with ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names)), 'Duplicate archive path'
        assert zipped.testzip() is None, 'CRC failure'
        for entry in names:
            parts = entry.replace('\\', '/').split('/')
            assert not entry.startswith(('/', '\\')) and '..' not in parts, f'Unsafe path: {entry}'
            assert not set(parts) & {'.git', 'node_modules', 'artifacts', 'dist', '.npm-cache', '__pycache__'}, entry
            assert not any(p.startswith('.env') for p in parts), entry
        if browser != 'source':
            assert set(names) == expected_files, f'Unexpected extension files: {name}'
            assert archive.stat().st_size <= 32768, 'Initial installable ZIP size budget exceeded (32 KiB)'
            manifest = json.loads(zipped.read('manifest.json'))
            assert manifest['version'] == version
            assert manifest['permissions'] == expected_permissions
            assert not manifest.get('host_permissions') and not manifest.get('content_scripts')
            assert zipped.read('background.js') == (root / 'extension/background.js').read_bytes()
            assert zipped.read('LICENSE') == (root / 'LICENSE').read_bytes()
        else:
            assert not any(Path(n).suffix.lower() in {'.exe', '.dll', '.sqlite', '.log', '.pyc'} for n in names)
            for required in ('LICENSE', 'README.md', 'PRIVACY.md', 'package-lock.json',
                             '.github/workflows/ci.yml', 'scripts/build.mjs', 'extension/background.js',
                             'store/metadata.json', 'store/description.es.txt', 'store/description.en.txt', 'PUBLICAR.md', 'icono.png'):
                assert required in names, f'Missing source file: {required}'
            assert json.loads(zipped.read('package.json'))['version'] == version
            assert zipped.read('extension/background.js') == (root / 'extension/background.js').read_bytes()
    print(f'PASS {name}: hashes, CRC, paths and distribution boundaries')
