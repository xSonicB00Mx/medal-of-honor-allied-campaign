"""Fit static emplacement names into the existing extended ammo HUD canvas."""
import re


def expand_static_weapon_names(menu):
    def expand(match):
        block = match[0]
        # Emplacements often call their name "healthnumber" or just "name".
        # Exclude counters, separators and dynamic item labels.
        active = re.sub(r"//[^\n]*", "", block)
        if not re.search(r'(?mi)^\s*title\s+"[^"]*[A-Za-z][^"]*"', active):
            return block
        if not re.search(r"(?mi)^\s*textalign\s+right\s*$", active):
            return block
        if re.search(r"(?mi)^\s*(?:playerstat|itemstat|statbar)\s", active):
            return block
        rect = re.search(r"(?m)^rect\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", block)
        if not rect:
            return block
        x, y, width, height = map(float, rect.groups())
        # Preserve the right edge beside the meters. Use the empty area on
        # the left, without moving ammo, health, sprites or their bindings.
        return (block[:rect.start()] + f"rect 0 {y:g} {x+width:g} {max(height,22):g}"
                + block[rect.end():])
    return re.sub(r"(?ims)^resource\s+Label\s*\{[^{}]*\}", expand, menu)
