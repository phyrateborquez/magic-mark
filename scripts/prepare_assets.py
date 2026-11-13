"""Deterministic asset export from the user's icon and real test screenshots.

Development only: python -m pip install Pillow==12.2.0
No drawing over screenshots, simulated highlights, or aspect-ratio distortion.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

root = Path(__file__).resolve().parent.parent
source = root / 'icono.png'
image = Image.open(source).convert('RGBA')
icons = root / 'extension/icons'
icons.mkdir(exist_ok=True)
# Preserve the supplied white background. Do not infer/remove background pixels.
for size in (48, 128):
    canvas = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    # 96px artwork inside 128px canvas follows the store's icon padding guidance.
    artwork = ImageOps.contain(image, (size * 3 // 4, size * 3 // 4), Image.Resampling.LANCZOS)
    canvas.alpha_composite(artwork, ((size-artwork.width)//2, (size-artwork.height)//2))
    canvas.save(icons/f'icon-{size}.png', optimize=True)

shots = root / 'store/screenshots'
def font(size, bold=False):
    candidates = [Path('C:/Windows/Fonts')/('segoeuib.ttf' if bold else 'segoeui.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError('Install Segoe UI or DejaVu Sans to export listing images')

records = []
for lang in ('es', 'en'):
    for stage, filename in [('highlight','01-firefox-highlights.png'), ('reload','02-firefox-reloaded.png')]:
        original = shots/filename
        shot = Image.open(original).convert('RGB')
        canvas = Image.new('RGB', (1280, 800), '#f6f7f9')
        draw = ImageDraw.Draw(canvas)
        draw.text((42,24), 'Magic Mark', font=font(28,True), fill='#17233b')
        draw.text((1110,30), 'MIT', font=font(22,True), fill='#17233b')
        titles = {'es':('Destaca lo importante.','Recarga. Empieza de nuevo.'),
                  'en':('Highlight what matters.','Reload. Start fresh.')}
        title = titles[lang][stage=='reload']
        draw.text((42,72), title, font=font(44,True), fill='#17233b')
        # Keep the entire original visible; unused space is a neutral frame.
        draw.rectangle((42,146,1237,726), fill='#19253b')
        reduced = ImageOps.contain(shot, (1196,580), Image.Resampling.LANCZOS)
        canvas.paste(reduced, (42+(1196-reduced.width)//2,146+(580-reduced.height)//2))
        caption = ('Captura real de Firefox · Página local de prueba · Interfaz en español' if lang=='es'
                   else 'Real Firefox screenshot · Local test page · Spanish interface')
        draw.text((42,752),caption,font=font(19),fill='#536274')
        output = shots/f'store-{lang}-{stage}-1280x800.png'
        canvas.save(output, optimize=True)
        with Image.open(output) as result:
            assert result.size == (1280,800) and result.mode == 'RGB'
        records.append({'file':output.name,'source':filename,'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
                        'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'size':[1280,800],
                        'processing':'contain entire original; add title and caption outside screenshot; no highlight edits'})
(shots/'exports.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(icons/'provenance.json').write_text(json.dumps({'source':'icono.png','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'source_size':list(image.size),'processing':'aspect-preserving resize, transparent outer padding, supplied background retained',
    'rights_status':'User states icon was composed from free anonymous SVG assets permitted for all uses; designated for this MIT project. Source URLs/license texts were not provided and were not independently verified.'},indent=2)+'\n',encoding='utf-8')
print('Exported 48/128px icons and four 1280x800 RGB listing images; originals preserved.')
