OMEGA HORIZON V9.6.1 - VISUAL REGRESSION RECOVERY
===================================================

V9.6.1 is a corrective release whose first rule is that newer art must not replace stronger art merely because it is authored. The recent V9.5/V9.6 full-stage plates and enemy-sheet branch is rolled back because playtest screenshots showed a clear loss of depth, texture, atmosphere and enemy detail.

VISUAL RECOVERY
---------------
- Restores the complete V9.4 layered background renderer as the authoritative visual baseline.
- Restores the stronger pre-regression authored plates for Stage 1, Stage 5, Stage 8 and the Stage 9 nebula.
- Stages 2, 3, 4, 6, 7 and 10 again use the richer layered procedural/metasprite scene composition instead of the simplified full-screen replacement plates.
- Restores the V9.1 detailed procedural/metasprite enemy renderer across all ten stages.
- Disables and removes every V9.6 authored enemy-family override from the release package.
- Preserves Stage 9's successful giant-nebula treatment.
- Preserves the V9.6 flagship title artwork/logo, V9.4 boss recovery, player ship, spherical shields, death sequence, ending sequence/music, menu-layer fixes and gameplay systems.

NON-NEGOTIABLE ART RULE
-----------------------
Future authored backgrounds, enemies, bosses and title assets must be dramatically richer than the recent simplified PNGs: illustrated late-SNES pixel art with dense hand-authored detail, material-specific shading, irregular silhouettes, lighting, texture, atmospheric depth and strong composition. The existing stronger asset remains authoritative until a replacement clearly wins a side-by-side quality review.

BUILD
-----
1. Replace the files in the existing GitHub repository with this package.
2. Keep the complete assets/ folder at repository root.
3. Commit to the default branch.
4. Actions -> Build Omega Horizon V9.6.1 for Windows -> Run workflow.
5. Download artifact: OmegaHorizon-Windows-x64-V9.6.1-VISUAL-REGRESSION-RECOVERY

The Windows title bar contains V9.6.1-VISUAL-REGRESSION-RECOVERY for build verification; the in-game public title screen continues to omit internal release text.
