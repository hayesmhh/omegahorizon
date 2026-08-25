OMEGA HORIZON V9.2 - AUTHORED WORLD EXPANSION
=============================================

V9.2 expands the asset-pipeline transition begun in V9.1. Major scene and enemy art
is progressively becoming shipped authored PNG artwork rather than runtime-built geometry.

V9.2 MAJOR CHANGES
------------------
- Adds a dedicated title/intro theme derived from the ending melody: mysterious and
  anticipatory at the title screen, then resolved heroically in the ending.
- Slows the post-OMEGA story scroll from 19 px/sec to 15 px/sec.
- Rebuilds ending composition so the hero ship stays behind the prose.
- Clips the story to a protected reading region, preventing overlap with the fixed header.
- Narrows ending copy to a 202-native-pixel maximum line width for more comfortable reading.
- Strengthens spherical shield depth with three rotating, depth-sorted great-circle bands,
  travelling shimmer segments, depth-scaled nodes and a moving specular crescent.

AUTHORED WORLD EXPANSION
------------------------
New shipped PNG assets in V9.2:
- assets/stage01_space_v92.png      Full Stage 1 space background plate.
- assets/stage05_station_v92.png    Stage 5 orbital-station upper background plate.
- assets/stage08_ice_v92.png        Stage 8 twin-moon ice-sky / mountain plate.
- assets/enemy_stage01_v92.png      Stage 1 four-archetype, two-frame enemy sheet.
- assets/enemy_stage09_v92.png      Stage 9 four-archetype, two-frame Veil enemy sheet.

V9.1 authored assets remain authoritative for:
- player ship (five frames)
- Pyroclast (four frames)
- Stage 9 panoramic nebula

Stage 1, 5, 8 and 9 now bypass older line-heavy beautification overlays so authored
composition remains visually authoritative instead of being covered by procedural clutter.

BUILD
-----
1. Replace all files in the existing GitHub repository with this package.
2. Keep the complete assets/ directory at repository root.
3. Commit to the default branch.
4. Actions -> Build Omega Horizon V9.2 for Windows -> Run workflow.
5. Wait for source regression and packaged-EXE smoke tests to pass.
6. Download artifact: OmegaHorizon-Windows-x64-V9.2-AUTHORED-WORLD-EXPANSION

The running window title contains V9.2-AUTHORED-WORLD-EXPANSION.
