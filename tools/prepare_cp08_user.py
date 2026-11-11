"""Copy existing preferences into the new campaign profile; preserve all old saves."""
import json,re,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];source=R/'profiles-local/CP05a-r3/user';dest=R/'profiles-local/CP08-r1/user';assert not dest.exists();dest.mkdir(parents=True);copied=[];configs=[]
for game,folder in [('AA','main'),('SH','mainta'),('BT','maintt')]:
 p=source/game/folder/'configs/omconfig.cfg';q=dest/folder/'configs/omconfig.cfg';q.parent.mkdir(parents=True)
 if p.exists():shutil.copy2(p,q);copied.append(dict(source=str(p.relative_to(R)),destination=str(q.relative_to(R)),sha256=hashlib.sha256(q.read_bytes()).hexdigest()));configs.append(p)
latest=max(configs,key=lambda p:p.stat().st_mtime)
names=set('ac_ui_auto ac_menu_scale ac_hud_scale ac_hud_safe ac_blood_mist ac_world_blood ac_body_wounds ac_corpse_effects cg_fov s_volume s_musicvolume sensitivity skill r_mode r_customwidth r_customheight r_fullscreen cl_playintro'.split())
lines=[]
for line in latest.read_text(encoding='latin1').splitlines():
 m=re.match(r'seta (\S+) "(.+)"',line)
 if line.startswith('bind ') or line=='unbindall' or (m and m[1] in names):lines.append(line)
for line in (source/'ac_ui_shared.cfg').read_text(encoding='latin1').splitlines():
 if re.match(r'seta ac_\w+ "[^"\n]+"$',line):lines.append(line)
(dest/'main/ac_shared.cfg').write_text('// Imported existing preferences; independent CP8 profile.\n'+'\n'.join(lines)+'\n',encoding='latin1')
(R/'checkpoints/CP08/user-preferences.json').write_text(json.dumps(dict(copied=copied,shared_from=str(latest.relative_to(R)),old_saves_unchanged=True,new_campaign_progress='fresh; no test unlocks copied'),indent=2)+'\n')
print('Three preference files and shared options copied; old saves stay in their existing profiles.')
