"""Exclude multiplayer-only UI from Allied Campaign artwork preparation."""
from pathlib import PurePosixPath


def multiplayer_ui(name):
    stem = PurePosixPath(name.lower()).stem
    return stem.startswith(('multiplayer', 'dm_', 'join', 'mpoptions', 'mp_')) or stem in {
        'loadsave_mp', 'maprotationsetup', 'filtermenu', 'selectteam', 'objselectteam',
        'selectffamodel', 'selectweapon', 'selectaxisweapon', 'selectalliedweapon',
        'callvote', 'vote', 'badserveraddy', 'serverback', 'unterseite',
    }
