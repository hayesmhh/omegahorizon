OMEGA HORIZON V9.6.5 - STAGE 2 FLUID DESCENT
================================================

V9.6.5 keeps the recovered visual/gameplay baseline and focuses only on the two approved polish targets: Stage 1's distant ringed planet and Stage 2's atmospheric descent continuity.

STAGE 1 RING POLISH
-------------------
- Rebuilds the upper-right planet ring on top of the successful ringless flagship plate.
- Centers the ring on the planet and uses a finer multi-band ellipse with front/back occlusion.
- Preserves the rest of Stage 1 unchanged.

STAGE 2 FLUID DESCENT
---------------------
- Uses five high-detail authored atmospheric plates with fully illustrated cloud structure.
- Removes the old translucent ellipse haze / white-blob cloud overlay entirely.
- Keeps plate camera transforms continuous when an incoming phase becomes the current phase, eliminating the V9.6.4 transform reset that caused visible jumpiness.
- Uses quintic easing for gentler phase handoffs.
- Retains restrained pixel velocity streaks and storm illumination as motion cues without covering the artwork.
- Progresses from orbital cloud tops through sunset storm layers to alien spires/civilization, setting up Stage 3.

BUILD
-----
Upload the package contents to the repository root, commit, then run:
Build Omega Horizon V9.6.5 for Windows

Artifact: OmegaHorizon-Windows-x64-V9.6.5-STAGE2-FLUID-DESCENT
