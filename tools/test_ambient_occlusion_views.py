"""Additional native AO views: built architecture, viewmodel exclusion and resize.

The PNGs are evidence for visual review, not an automated visual-quality verdict.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from PIL import Image
import numpy as np

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('run')
a = ap.parse_args()
assert re.fullmatch('[a-zA-Z0-9-]+', a.run)
out = R/'generated-local/CP09'/a.run
out.mkdir(parents=True, exist_ok=False)
p = R/'profiles-local/CP09'/a.run
h = p/'main'
h.mkdir(parents=True, exist_ok=False)
rt = R/'runtime-local/CP09-r1'
build = R/'build-local/cp00-r3/RelWithDebInfo'
b = p/'bin'
b.mkdir()
personal = R/'profiles-local/CP08-r1/user'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():
    return {f.relative_to(personal).as_posix(): sha(f) for f in personal.rglob('*') if f.is_file()}
before = hashes()
for f in rt.glob('*.dll'):
    shutil.copy2(f, b/f.name)
shutil.copy2(build/'openmohaa.exe', b/'openmohaa.exe')
# AO must also work without any new model shadow pass. Diagnostic mode replaces
# opaque world colors while leaving the first-person weapon in its normal colors.
cmd = ['wait 800', 'map m3l2', 'wait 5000', 'finishloadingscreen', 'wait 1500',
       'set r_acAmbientOcclusion 0', 'wait 300', 'screenshot silent',
       'set r_acAmbientOcclusion 1', 'wait 300', 'screenshot silent',
       'set r_acAODebug 1', 'wait 300', 'screenshot silent', 'set r_acAODebug 2',
       'set r_customwidth 1280', 'set r_customheight 960', 'vid_restart',
       'wait 3500', 'finishloadingscreen', 'wait 400', 'screenshot silent',
       'map m6l3a', 'wait 5000', 'finishloadingscreen', 'wait 1200',
       'set r_acAmbientOcclusion 0', 'wait 300', 'screenshot silent',
       'set r_acAmbientOcclusion 1', 'wait 300', 'screenshot silent',
       'set r_acAODebug 1', 'wait 300', 'screenshot silent',
       'echo AC_AO_VIEWS_DONE', 'quit']
(h/'probe.cfg').write_text('\n'.join(cmd)+'\n')
args = [str(b/'openmohaa.exe')]
for k, v in dict(com_target_game=0, fs_basepath=rt, fs_homepath=p, fs_steampath=rt,
                 fs_gogpath=rt, fs_microsoftstorepath=rt, net_enabled=0, logfile=2,
                 developer=1, cheats=1, cl_playintro=0, r_fullscreen=0, r_mode=-1,
                 r_customwidth=1920, r_customheight=1080, r_fastsky=0,
                 r_acModelShadows=0, r_acShadowDebug=4, cg_shadows=0, r_acAODebug=2,
                 com_maxfps=60, com_maxfpsUnfocused=60).items():
    args += ['+set', k, str(v)]
proc = subprocess.run(args+['+exec', 'probe.cfg'], cwd=b, timeout=100)
log = (h/'qconsole.log').read_text(encoding='latin1')
assert proc.returncode == 0 and 'AC_AO_VIEWS_DONE' in log
assert 'AC AO shader:' not in log and 'AC AO framebuffer unsupported' not in log
costs = [(int(t), int(e), int(w), int(h)) for t, e, w, h in re.findall(
    r'AC_AO_COST ms=(\d+) gl_error=(\d+) size=(\d+)x(\d+)', log)]
assert costs and all(e == 0 for _, e, _, _ in costs), costs
assert {(w, h) for _, _, w, h in costs} == {(1920, 1080), (1280, 960)}
images = []
for i, f in enumerate(sorted((h/'screenshots').glob('*.tga'))):
    dst = out/f'view-{i}.png'
    Image.open(f).save(dst)
    images.append(dst.relative_to(R).as_posix())
assert len(images) == 7, images
# A formerly missing facade is a regression target: an opaque, flat wall must
# be present in the AO diagnostic, not retain its wood/plaster texture.
diagnostic = np.array(Image.open(R/images[2]).convert('RGB'))
assert np.median(diagnostic[270:400,1010:1200]) > 250, 'Facade missing from AO composite'
weapon = diagnostic[840:940,1040:1110].astype(float) # Wood/hand, not nearly neutral gunmetal.
assert weapon.mean() < 180 and (weapon.max(2)-weapon.min(2)).mean() > 8, 'Viewmodel was overwritten by AO'
assert hashes() == before
(out/'result.json').write_text(json.dumps(dict(engine_sha256=sha(build/'openmohaa.exe'),
    images=images, resolution_change=True, model_shadows_disabled=True,
    personal_files_unchanged=len(before), synchronized_ao_pass_ms=[t for t, _, _, _ in costs]), indent=2)+'\n')
print('PASS AO architecture, viewmodel and 16:9 -> 4:3 resize')
