OMEGA HORIZON - GITHUB WINDOWS BUILD V8.4.1
========================================

V8.4.1 is the Pixel Art Production Overhaul. It preserves the V8.3 fixed-step /
continuous-scroll stability work and moves stage scenery further away from
primitive runtime geometry toward reusable authored pixel-art chunks.

VISUAL BENCHMARK
----------------
Stage 8 is the lead benchmark for this release. The old triangle-like ice
mountains are replaced by four multi-shade authored ridge families with snow
shelves, faceted light/shadow planes, fracture veins, atmospheric mist, a
separate 2x midground ridge layer, and cropped foreground glacier masses.

Other stages gain authored reusable environmental chunks as well: volcanic
arches, underwater ruin towers, station machinery, hive arches, damaged city
towers, dimensional monoliths and Omega bio-machine columns.

Bosses receive a second material/articulation finish pass with persistent
damage scars, stronger silhouettes, more lighting cues and stage-specific
animated details.

TESTING
-------
Type TERMINUS on the title screen, then press F1 to use Test Mode.

BUILD
-----
Upload/replace all files in the existing GitHub repository, then run:

    Build Omega Horizon V8.4.1 for Windows

Download only:

    OmegaHorizon-Windows-x64-V8.4.1-PIXEL-ART-OVERHAUL

The packaged EXE is smoke-tested on the Windows runner before upload.


VISIBLE VERSION HOTFIX
----------------------
V8.4.1 fixes two stale title-screen strings that still displayed V8.3 even
though the executable itself was V8.4. Visible version text is now derived
from centralized DISPLAY_VERSION / DISPLAY_SUBTITLE constants, and the cloud
workflow asserts those values before packaging.


V8.5 adds EASY / HARDER / DIFFICULT / INSANE; INSANE preserves V8.4 balance.
It also grounds city scenery, applies stage-specific color-math/readability separation, adds silhouette rims to enemies, and substantially enlarges/reworks OMEGA.
