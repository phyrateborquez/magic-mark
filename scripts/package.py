"""Create repeatable unsigned release archives; Python standard library only."""
import hashlib
import argparse
import json
import os
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(__file__).resolve().parent.parent
version = json.loads((root / 'package.json').read_text(encoding='utf-8'))['version']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=root / 'artifacts')
output = parser.parse_args().output_dir.resolve()
output.mkdir(parents=True, exist_ok=True)
checksums = []
for browser in ('firefox', 'chromium', 'source'):
    source = root if browser == 'source' else root / 'dist' / browser
    target = output / f'magic-mark-{version}-{browser}.zip'
    if browser == 'source':
        files = [p for p in root.iterdir() if p.is_file() and (p.suffix == '.md' or p.name in
                 ('LICENSE', 'package.json', 'package-lock.json', '.gitignore', 'icono.png'))]
        for directory in ('.github', 'extension', 'scripts', 'tests', 'store'):
            files.extend(p for p in (root / directory).rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
    else:
        files = [p for p in source.rglob('*') if p.name != 'provenance.json']
    # Finish the archive before replacing a previous release file.
    descriptor, temporary_name = tempfile.mkstemp(prefix='package-', suffix='.zip', dir=output)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with ZipFile(temporary, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
            for file in sorted(files):
                if file.is_file():
                    info = ZipInfo(file.relative_to(source).as_posix(), (2026, 1, 1, 0, 0, 0))
                    info.compress_type = ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, file.read_bytes())
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    checksums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}')
    print(f'{target.name}: {target.stat().st_size} bytes')
(output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
