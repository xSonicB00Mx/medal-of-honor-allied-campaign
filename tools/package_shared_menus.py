"""Use the effective AA menu presentation in every campaign, with isolated artwork.

Medals, war records, saves, briefings and loading screens retain native definitions.
Only generated packages contain the local game assets.
"""
import hashlib
import json
import re
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
runtime = root / 'runtime-local/CP08-r1'
output = root / 'generated-local/shared-menus/packages'
entries = {}
for package in sorted((runtime / 'main').glob('*.pk3')):
    if package.name.endswith('_AC_SharedMenus.pk3'):
        continue
    with zipfile.ZipFile(package) as z:
        for name in z.namelist():
            entries[name.lower()] = (package, name)

def read(name):
    package, member = entries[name.lower()]
    with zipfile.ZipFile(package) as z:
        return z.read(member)

# Parse balanced shader bodies, ignoring comments before scanning braces.
shaders = {}
for name in sorted(entries):
    if not name.startswith('scripts/') or not name.endswith('.shader'):
        continue
    body = read(name).decode('latin1')
    body = re.sub(r'/\*.*?\*/|//[^\n]*', '', body, flags=re.S)
    pos = 0
    while match := re.search(r'([^\s{}]+)\s*\{', body[pos:]):
        start = pos + match.end() - 1
        depth, end = 1, start + 1
        while depth and end < len(body):
            depth += (body[end] == '{') - (body[end] == '}')
            end += 1
        assert depth == 0, name
        shaders[match[1].lower()] = body[start:end]
        pos = end

files, material = {}, {}
def texture(name):
    name = name.strip('"')
    if name.startswith('$'):
        return name
    candidates = [name] + [re.sub(r'\.(?:tga|jpg|png)$', '', name, flags=re.I) + ext
                           for ext in ['.tga', '.jpg', '.png']]
    source = next((n for n in candidates if n.lower() in entries), None)
    assert source, ('Missing AA texture', name)
    target = 'textures/ac/shared/' + source
    files[target] = read(source)
    return target

def shader(name):
    if name in material:
        return material[name][0]
    alias = 'ac_shared/' + name
    if name.lower() in shaders:
        body = shaders[name.lower()]
        def maps(m):
            tokens = m[2].split()
            offset = 1 if m[1].lower() == 'animmap' else 0
            tokens[offset:] = [texture(t) for t in tokens[offset:]]
            return m[1] + ' ' + ' '.join(tokens)
        body = re.sub(r'(?mi)^\s*(map|clampmap|animmap)\s+([^\n{}]+)', maps, body)
    else:
        body = '{\n nopicmip\n nomipmaps\n {\n clampmap '+texture(name)+'\n blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA\n rgbGen global\n alphaGen global\n }\n}'
    material[name] = alias, body
    return alias

menus = ['main', 'options_main', 'audio options', 'video options', 'advancedoptions',
         'controls', 'controls_reset', 'controls_recom']
for menu in menus:
    path = 'ui/' + menu + '.urc'
    text = read(path).decode('latin1')
    # All image-bearing UI directives and dynamic hover labels get private names.
    text = re.sub(r'(?mi)^(\s*(?:shader|hovershader|checked_shader|unchecked_shader|widescreenbackground)\s+)"([^"\n]+)"',
                  lambda m: m[1]+'"'+shader(m[2])+'"', text)
    signs = {'newgame_sign':'operations', 'options_sign':'options',
             'warrecords_sign':'war_records', 'briefingroom_sign':'briefing_room',
             'maplist_sign':'map_list', 'credits_sign':'credits'}
    def hover(m):
        name = m[2]
        if m[1] == 'set ui_signshader ' and name in signs:
            name = 'textures/ac/widescreen/'+signs[name]+'_sign'
        return m[1]+(shader(name) if name != '0' else '0')
    text = re.sub(r'(set ui_(?:signshader|optionshader) )([^";\s]+)', hover, text)
    files[path] = text.encode('latin1')

files['scripts/ac_shared_menus.shader'] = '\n'.join(alias+'\n'+body for alias, body in material.values()).encode('latin1')
reports = []
for game, folder in [('AA','main'), ('SH','mainta'), ('BT','maintt')]:
    path = output / folder / 'zzzzzzzzzzz_AC_SharedMenus.pk3'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(name, data)
    reports.append(dict(game=game, package=path.relative_to(root).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(output/'package-report.json').write_text(json.dumps(reports, indent=2)+'\n')
print(f'Packaged {len(menus)} AA menus, {len(material)} isolated materials for AA/SH/BT.')
