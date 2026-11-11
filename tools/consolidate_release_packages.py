"""Preserve OpenMoHAA's winning bytes AND FS_ListFiles enumeration order.

FS_AddGameDirectory sorts archives ascending and prepends each search path.
FS_ListFilteredFiles then visits archives descending, in central-directory order.
Do not sort the merged members: shader enumeration order is significant.
"""
from pathlib import Path
import hashlib
import zipfile

PACKAGE_NAME = 'zz_AlliedCampaign.pk3'
GAMES = ('main', 'mainta', 'maintt')


def normalized(name):
    return name.replace('\\', '/').lower()


def effective_members(packages, hashes=False):
    members = {}
    for path in sorted(packages, key=lambda p: normalized(p.name), reverse=True):
        with zipfile.ZipFile(path) as archive:
            seen = set()
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                key = normalized(entry.filename)
                assert not key.startswith('/') and ':' not in key and '..' not in key.split('/'), key
                assert key not in seen, ('Ambiguous duplicate inside archive', path, key)
                seen.add(key)
                if key not in members:
                    data = archive.read(entry)
                    members[key] = (hashlib.sha256(data).digest() if hashes else data, path.name)
    return members


def consolidate(source, destination, owned_files):
    report = {}
    legacy = []
    for game in GAMES:
        rows = [r for r in owned_files if Path(r['path']).parent.as_posix() == game
                and r['path'].lower().endswith('.pk3')]
        assert rows and all('_AC_' in r['path'] for r in rows)
        packages = [source / row['path'] for row in rows]
        members = effective_members(packages)
        target = destination / game / PACKAGE_NAME
        target.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, (data, _) in members.items():
                entry = zipfile.ZipInfo(name, (2026, 11, 11, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data, compresslevel=9)
        merged = effective_members([target])
        assert list(merged) == list(members), 'Enumeration order changed'
        assert all(merged[k][0] == members[k][0] for k in members)
        # Check ordering against the installed WCR/base packages, too.
        base = [p for p in (source/game).glob('*.pk3') if p not in packages]
        before = effective_members(base + packages, hashes=True)
        after = effective_members(base + [target], hashes=True)
        assert list(before) == list(after), 'Base/AC enumeration changed'
        assert all(before[k][0] == after[k][0] for k in before), 'Base/AC resolution changed'
        report[game] = dict(old_packages=len(rows), new_package=target.name,
                            resolved_files=len(before), merged_files=len(members),
                            ordered_content_sha256=hashlib.sha256(b''.join(
                                k.encode()+b'\0'+v[0]
                                for k,v in before.items())).hexdigest())
        legacy.extend(dict(path=row['path'], sha256=row['sha256']) for row in rows)
    return report, legacy
