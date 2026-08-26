OMEGA HORIZON V9.6.2 - STAGE 1 FLAGSHIP SPACE OPENER
======================================================

V9.6.2 is an intentionally isolated visual-candidate build. It starts from the stable V9.6.1 Visual Regression Recovery baseline and changes only Stage 1's authored background plate.

STAGE 1 FLAGSHIP SPACE
----------------------
- Replaces the recovered Stage 1 plate with a substantially richer 256x203 authored cosmic panorama.
- Reference-guided composition: enormous blue/violet nebula, dense multi-depth starfield, textured planets and moons, a ringed distant planet, and a close foreground planetary arc.
- No ground plane is present; the lower-right planetary slice is a celestial foreground object rather than terrain.
- No player ship, enemies, HUD, projectiles or gameplay objects are baked into the background asset.
- Stage 1 keeps only the existing sparse animated star-glint finish over the authored plate.

CONTROLLED CANDIDATE RULE
-------------------------
Everything else remains on the V9.6.1 recovered baseline: Stages 2-10, all non-boss enemies, bosses, player ship, shields, death flow, title presentation, ending and gameplay systems. This makes Stage 1 easy to compare and reject without contaminating the stable baseline.

BUILD
-----
1. Replace the repository files with this package.
2. Replace the repository assets folder with the included assets folder to avoid stale-file checks.
3. Commit to the default branch.
4. Actions -> Build Omega Horizon V9.6.2 for Windows -> Run workflow.
5. Download artifact: OmegaHorizon-Windows-x64-V9.6.2-STAGE1-FLAGSHIP-SPACE

The Windows title bar contains V9.6.2-STAGE1-FLAGSHIP-SPACE for build verification; the public in-game title screen continues to omit internal release text.
