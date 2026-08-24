OMEGA HORIZON V8.1 - ARTIST PASS & PLAYABILITY POLISH
======================================================

PURPOSE
-------
V8.1 is the first dedicated craftsmanship pass after V8 established the ten
stage identities, weapon progression, enemy roles, unique bosses, and true
stereo soundtrack architecture.

THE BIG VISUAL CHANGE
---------------------
Finished combat sprites are moving away from runtime polygon silhouettes and
into authored indexed pixel matrices/metasprites stored directly in the Python
source. The game remains a single-file procedural/no-external-art project, but
its art is now constructed more like actual 16-bit sprite work.

V8.1 specifically includes:
- Rebuilt authored pixel-matrix player ship.
- Rebuilt authored enemy archetype sprites with stage-specific material ramps.
- Stage 3 Magma Caverns enemy readability correction using dark obsidian forms,
  cool rim lighting, brighter focal pixels, and a less noisy lava field.
- Completely rebuilt Stage 2 Tempest Bastion metasprite. It now has an obvious
  side-view airborne-fortress silhouette, main cannon, command tower, four
  animated lift turbines, engines, antennae, warning lights and damage effects.
- Additional hand-authored focal-detail tiles and lighting on the other bosses.
- Richer shaded pixel-cloud treatment in Stage 2.
- Cleaner, broader basalt/lava structures in Stage 3.
- Dependable periodic +30 HP recovery cadence/pity system, accelerated at low
  health, while preserving rare Major Health and Extra Life pickups.
- 12-bar stage arrangements with B-section counter-melodies, additional
  synthesized instrument colors, and section-end percussion fills.

BUILD
-----
Replace the files in your existing GitHub repository, including the workflow,
commit them, then run:

    Build Omega Horizon V8.1 for Windows

Wait for both regression testing and:

    Smoke-test the PACKAGED V8.1 EXE

to turn green.

Download ONLY the artifact:

    OmegaHorizon-Windows-x64-V8.1-ARTIST-PASS

The running window title contains V8.1-ARTIST-PASS so it is easy to distinguish
from older builds.
