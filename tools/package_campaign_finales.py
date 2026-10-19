"""Move AA/BT campaign completion before credits; retain WCR outros and SH finale.

Original scripts and resulting PK3s stay local and must not be committed.
"""
from pathlib import Path
import hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime-local/CP08-r1'
OUTPUT = ROOT / 'generated-local/campaign-finales'
PACKAGE = 'zzzzzzzzzzzzzz_AC_CampaignFinales.pk3'

def effective(folders, name):
    result = None
    for folder in folders:
        for path in sorted((RUNTIME / folder).glob('*.pk3'), key=lambda p: p.name.lower()):
            if path.name == PACKAGE:
                continue
            with zipfile.ZipFile(path) as archive:
                if name in archive.namelist():
                    result = (path, archive.read(name))
        loose = RUNTIME / folder / name
        if loose.exists():
            result = (loose, loose.read_bytes())
    assert result, name
    return result

def build():
    rows, audit = [], []
    for game, folder, script, anchor, operation, guard in [
        ('AA', 'main', 'maps/m6l3e.scr', '//*** show \'THE END\'', 13, 'level.end_level == 1'),
        ('BT', 'maintt', 'maps/e3l4/outro.scr', '\t//TKO Rules!', 11, 'level.escaped == 1'),
    ]:
        provider, original = effective(['main'] if folder == 'main' else ['main', folder], script)
        text = original.decode('latin1').replace('\r\n', '\n')
        assert text.count(anchor) == 1
        hook = f'''// Allied Campaign continues after this original campaign's outro.
if (int (getcvar ac_campaign_mode) == 1 && int (getcvar ac_operation) == {operation} && {guard})
{{
    println "AC_FINALE_CONTINUE {game}"
    missiontransition ac_campaign_end 1
    end
}}

'''
        patched = text.replace(anchor, hook + anchor)
        path = OUTPUT / 'packages' / folder / PACKAGE
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(script, patched.encode('latin1'))
        rows.append(dict(game=game, package=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        audit.append(dict(game=game, script=script, source=provider.relative_to(ROOT).as_posix(),
                          source_sha256=hashlib.sha256(original).hexdigest(), operation=operation, guard=guard))
    (OUTPUT / 'packages/package-report.json').write_text(json.dumps(rows, indent=2)+'\n')
    (OUTPUT / 'audit.json').write_text(json.dumps(audit, indent=2)+'\n')

if __name__ == '__main__':
    build()
