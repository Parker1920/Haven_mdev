import sys, os
sys.path.insert(0, os.path.abspath('.'))
import re, json
from pathlib import Path

base = Path('.') / 'Haven-UI' / 'dist'
vm = base / 'VH-Map.html'
print('Parsing:', vm)

with open(vm, 'r', encoding='utf-8') as f:
    c = f.read()
md = re.search(r"window.DISCOVERIES_DATA\s*=\s*(\[.*?\]);", c, flags=re.S)
if md:
    ds = json.loads(md.group(1))
    print('VH map discoveries:', len(ds))
else:
    print('No discoveries array in VH-Map')

# per-system
for sysname in ['system_AURORA-7.html','system_NMS-OUTPOST-1.html','system_SERENITY-3.html']:
    sp = base / sysname
    print('\nParsing:', sp)
    if not sp.exists():
        print('Missing', sp)
        continue
    with open(sp, 'r', encoding='utf-8') as f:
        c2 = f.read()
    md2 = re.search(r"window.DISCOVERIES_DATA\s*=\s*(\[.*?\]);", c2, flags=re.S)
    if md2:
        ds2 = json.loads(md2.group(1))
        print(sysname, 'discoveries count', len(ds2))
        for d in ds2:
            print('  ', d['id'], d.get('discovery_type'), d.get('discovery_name'), 'sys=', d.get('system_id'), 'planet=', d.get('planet_id'), 'moon=', d.get('moon_id'))
    else:
        print('No discoveries array in', sysname)
