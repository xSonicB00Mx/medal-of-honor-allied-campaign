#pragma once

// Allied Campaign deliberately exposes no multiplayer entry points.
static inline bool ACIsMultiplayerMenu(const char *name)
{
    if (!name) return false;
    const char *prefixes[] = {"multiplayer", "join", "dm_", "mpoptions", "mpoptions_"};
    for (const char *prefix : prefixes)
        if (!Q_stricmpn(name, prefix, (int)strlen(prefix))) return true;
    const char *menus[] = {"loadsave_mp", "maprotationsetup", "FilterMenu",
        "SelectTeam", "ObjSelectTeam", "SelectFFAModel", "SelectWeapon",
        "SelectAxisWeapon", "SelectAlliedWeapon", "callvote", "vote"};
    for (const char *menu : menus)
        if (!Q_stricmp(name, menu)) return true;
    return false;
}
