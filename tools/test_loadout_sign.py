"""Check the shared door/sign and its actual LOADOUT action in isolated homes."""
from pathlib import Path
import argparse, json, re, shutil, subprocess, zipfile
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("run")
args = ap.parse_args()
r = Path(__file__).resolve().parents[1]
rt = r / "runtime-local/CP08-r1"
root = r / "profiles-local/loadout" / args.run
root.mkdir(parents=True, exist_ok=False)
results = []
for game, folder in enumerate(["main", "mainta", "maintt"]):
    p = root / folder
    b = p / "bin"
    b.mkdir(parents=True)
    for f in rt.glob("*.dll"):
        shutil.copy2(f, b / f.name)
    for n in ["openmohaa.exe", "cgame.dll"]:
        shutil.copy2(r / "build-local/cp00-r3/RelWithDebInfo" / n, b / n)
    for base in ["main", "mainta", "maintt"]:
        (p / base).mkdir()
        for f in (r / "generated-local/loadout/packages" / base).glob("*.pk3"):
            shutil.copy2(f, p / base / f.name)
    h = p / folder
    with zipfile.ZipFile(next(h.glob("*_AC_Loadout.pk3"))) as z:
        menu = z.read("ui/main.urc").decode("latin1")
        assert "ac_loadout_hover" not in menu
        assert "textures/ac/widescreen/loadout_sign" in menu
    # Actions enqueue at the end of the buffer. Test continuations run only
    # after the original hover and click commands have executed.
    menu = menu.replace('stuffcommand "ac_loadout"', 'stuffcommand "ac_loadout; exec opened.cfg"')
    menu, count = re.subn(
        r'(hovercommand "[^"]*textures/ac/widescreen/loadout_sign[^"]*)"',
        r'\1; exec hovered.cfg"', menu)
    assert count == 1
    with zipfile.ZipFile(h / "zzzzzzzzzzzzzzzzz_AC_SignProbe.pk3", "w") as z:
        z.writestr("ui/main.urc", menu)
    (h / "start.cfg").write_text("wait 800\nac_main_menu\nwait 300\nscreenshot silent\nwidgetcommand loadout mouse_entered 690 230 0\n")
    (h / "hovered.cfg").write_text("wait 300\nscreenshot silent\nwidgetcommand loadout left_mouse_down 690 230 1\nwidgetcommand loadout left_mouse_up 690 230 0\n")
    (h / "opened.cfg").write_text("wait 300\nac_ui_report ac_loadout\nscreenshot silent\necho SIGN_DONE\nquit\n")
    settings = dict(com_target_game=game, fs_basepath=rt, fs_homepath=p,
                    fs_steampath=rt, fs_gogpath=rt, fs_microsoftstorepath=rt,
                    net_enabled=0, logfile=2, cl_playintro=0, ui_console=0,
                    r_fullscreen=0, r_mode=-1, r_customwidth=960,
                    r_customheight=540, com_maxfps=60)
    command = [str(b / "openmohaa.exe")]
    for k, v in settings.items():
        command += ["+set", k, str(v)]
    proc = subprocess.run(command + ["+exec", "start.cfg"], cwd=rt, timeout=35,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = (h / "qconsole.log").read_text(encoding="latin1")
    assert proc.returncode == 0 and "SIGN_DONE" in log
    assert "AC_UI_CURRENT ac_loadout" in log
    assert not re.search(r"Unknown command|Invalid event|Script Error", log)
    for f in (h / "screenshots").glob("*.tga"):
        Image.open(f).save(f.with_suffix(".png"))
    results.append(dict(game=folder, door_opens_loadout=True))
    print(folder, "sign/door passed", flush=True)
(root / "result.json").write_text(json.dumps(results, indent=2) + "\n")
