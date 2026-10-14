# Map provenance

Spherical Mercator, north up, with uniform scale per view and WGS84 coordinates. The generator expands geographic bounds to the 560 x 330 logical map rectangle with padding. Raster and native markers use the same transformation. Two views (North Africa & Italy, Europe) cover all fifteen operations. Only unlocked operations appear. Nearby visible anchors form a selectable group; the side list preserves individual access. No political borders, front lines or implied route of a single soldier are drawn.

Coastlines are a cropped, rounded transformation of [Natural Earth 1:50m land](https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-land/), acquired from the maintainer's [repository](https://github.com/nvkelso/natural-earth-vector). Natural Earth data are [public domain](https://www.naturalearthdata.com/about/terms-of-use/). The unmodified download stays local; `coastlines.json` contains derived geometry. The crop exceeds every projected viewport.

Place anchors come from [GeoNames](https://www.geonames.org/export/) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Specific IDs, names, coordinates and links appear with each operation in `missions.json`. Downloads and SHA-256 hashes are recorded in `geography-sources.json`. Credit: GeoNames, used with attribution; the regional anchor selection and projection are adaptations.

All markers describe approximate mission areas. Normandy uses Caen as a regional anchor shared by three operations; it does not place Omaha Beach at Caen. Brittany uses Brest. The fictional Schmerzen fort is shown as a broad Siegfried Line region near Trier, not a known fort location. Monte Cassino uses Cassino town, Kasserine its town/region, and Sicily the island's region anchor. Labels and markers are independent native UI controls, never baked into the raster.

Installed game texts provide dates. Inconsistencies and missing dates remain explicit in the manifest and CP7 report. Historical context for Berlin agrees with the [National Army Museum's April 1945 account](https://www.nam.ac.uk/explore/april-1945), which does not establish an exact date for the fictional mission.

`tools/prepare_campaign_geography.py` extracts selected records and clips land from locally retained downloads. `tools/generate_campaign_map.py` creates two 2240 x 1320 textures, shaders and the native marker table. Decorative grain is seeded and does not alter coordinates. No original game assets are included here or uploaded.
