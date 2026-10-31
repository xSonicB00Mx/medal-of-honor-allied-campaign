"""Lay out native captures without changing their color/exposure; include originals."""
import argparse,json,shutil,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False);full=a.out/'UHD';full.mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',32)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
subjects=[('church-side','Church exterior'),('church-interior','Church interior'),('farm-road','Village square'),('start-field','Covered trench')]
items=[]
for i,(name,title) in enumerate(subjects,1):
    canvas=Image.new('RGB',(2560,820),'#151a1e');d=ImageDraw.Draw(canvas)
    d.text((24,12),f'{i:02d}  {title}',font=font,fill='#e7dbc2')
    d.text((24,58),'BEFORE / Original lighting',font=small,fill='white')
    d.text((1304,58),'AFTER / Baked sky and diffuse bounce',font=small,fill='white')
    for j,(folder,label) in enumerate([(a.before,'Before'),(a.after,'After')]):
        source=folder/(name+'.png');im=Image.open(source);assert im.size==(3840,2160)
        shutil.copy2(source,full/f'{i:02d}-{name}-{label}.png')
        canvas.paste(im.resize((1280,720),Image.Resampling.LANCZOS),(j*1280,100))
    dst=a.out/f'{i:02d}-{name}-comparison.jpg';canvas.save(dst,quality=95,subsampling=0)
    items.append(dst.name)
(a.out/'Vergleich.txt').write_text('''Medal of Honor: Allied Campaign – Beleuchtungs-Pilot m3l3

Links: bisherige Beleuchtung. Rechts: neuer Offline-Bake.
Die UHD-Einzelbilder im Unterordner UHD sind unveränderte Engine-Screenshots.
Die Vergleichstafeln sind nur verkleinert und nebeneinander angeordnet.
Gleiche Kamera, Auflösung, Nebel, Gamma und Grafikoptionen. TAA, AO und
Modellschatten sind aktiv. Objektbewegungsunschärfe ist für beide Standbilder
ausgeschaltet. Kleine Unterschiede in bewegten Objekten/Blättern können durch
die getrennten Aufnahmen entstehen. Keine nachträgliche Farbkorrektur.

Der Pilot verändert nur die statische Beleuchtung dieses Levels und zugehörige
Modell-Lichtproben. Das trübe Wetter und der dichte Originalnebel bleiben.
Kein dynamisches GI und keine Änderung an Spielregeln oder Speicherformat.

Start-CP09-Relight-After.cmd startet die neue Beleuchtung in einer Profilkopie.
Start-CP09-Relight-Before.cmd startet die alte Beleuchtung in einer zweiten Kopie.
Für das reguläre Spiel einfach wieder den bisherigen Starter verwenden.
Dein persönlicher Spielstand und die normale Installation sind unverändert.
''',encoding='utf-8')
archive=a.out/'Allied-Campaign-Lighting-Before-After.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for f in list(a.out.glob('*.jpg'))+[a.out/'Vergleich.txt']+list(full.glob('*.png')):z.write(f,f.relative_to(a.out).as_posix())
(a.out/'captures.json').write_text(json.dumps(dict(before=json.loads((a.before/'result.json').read_text()),after=json.loads((a.after/'result.json').read_text()),comparisons=items,zip_bytes=archive.stat().st_size),indent=2))
print(str(archive));print(archive.stat().st_size)
