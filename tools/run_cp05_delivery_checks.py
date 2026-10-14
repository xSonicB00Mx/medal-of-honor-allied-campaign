"""Final switches, migration, animation, UI and actual launcher checks, sequentially."""
import subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
cases=[
 ('options',['test_cp05_options.py']),
 ('compat-final',['test_cp05_compat.py','--run-id','compat-final']),
 ('live-AA',['test_body_wounds.py','AA','--checkpoint','CP05','--run-id','live-AA','--model','models/human/german_misc_worker.tik','--quick','--motion','--crouch','--death']),
 ('live-SH',['test_body_wounds.py','SH','--checkpoint','CP05','--run-id','live-SH','--model','models/human/german_winter_type2.tik','--quick','--motion','--crouch']),
 ('live-BT',['test_body_wounds.py','BT','--checkpoint','CP05','--run-id','live-BT','--model','models/human/Sc_AX_Ital_Inf.tik','--quick','--crouch']),
 ('ui-AA-4k',['test_cp01_ui.py','AA','--checkpoint','CP05','--run-id','ui-AA-4k','--width','3840','--height','2160']),
 ('ui-SH-fhd',['test_cp01_ui.py','SH','--checkpoint','CP05','--run-id','ui-SH-fhd','--width','1920','--height','1080']),
 ('ui-BT-wide',['test_cp01_ui.py','BT','--checkpoint','CP05','--run-id','ui-BT-wide','--width','3440','--height','1440']),
 ('launcher',['test_cp05_launcher.py'])]
for name,args in cases:
 with (r/'logs-local'/f'cp05-delivery-{name}.log').open('w') as log:
  completed=subprocess.run([sys.executable,str(r/'tools'/args[0]),*args[1:]],cwd=r,stdout=log,stderr=subprocess.STDOUT)
 assert completed.returncode==0,name
 print(name+': PASS',flush=True)
