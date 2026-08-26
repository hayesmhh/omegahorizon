OMEGA HORIZON V9.6.4 - STAGE 2 CONTINUOUS DESCENT
==================================================

V9.6.4 builds on the recovered visual baseline and corrects the two issues identified in V9.6.3: the Stage 1 ring treatment and the slideshow-like Stage 2 transitions.

STAGE 1 POLISH
--------------
- Rebuilds the distant upper-right planet ring from the ringless flagship plate.
- Uses a thinner multi-band elliptical ring with front/back occlusion around the planet.
- Preserves the rest of the successful Stage 1 composition.

STAGE 2 CONTINUOUS DESCENT
--------------------------
- Keeps five authored atmospheric phases but removes static generated background ships from the plates.
- Applies a restrained sharpening pass so the scenery reads more crisply at the 256x224 native resolution.
- Replaces threshold-style scene changes with continuous moving-camera blends: each scene rises and subtly zooms while the next atmospheric layer moves into view.
- No fade-to-black transition is used.
- Adds fast parallax haze, sparse diagonal velocity streaks, and storm illumination that intensify as altitude falls.
- The final descent still transitions visually toward Stage 3's hostile volcanic world.

BUILD
-----
Upload the package contents to the repository root, commit, then run:
Build Omega Horizon V9.6.4 for Windows

Artifact: OmegaHorizon-Windows-x64-V9.6.4-STAGE2-CONTINUOUS-DESCENT
