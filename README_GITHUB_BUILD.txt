OMEGA HORIZON V9.1 - AUTHORED ART FOUNDATION
=============================================

V9.1 begins the new visual-production pipeline requested after the V9.0 playtest.
Major visual elements now start moving out of runtime-drawn geometry and into shipped,
original PNG sprite sheets and background plates.

FIRST TRUE AUTHORED-ASSET WAVE
------------------------------
- Adds assets/player_ship_v91.png: a 5-frame player-ship sprite sheet with neutral,
  bank-up, bank-down, firing and damage artwork.
- Adds assets/pyroclast_v91.png: a 4-frame cohesive Pyroclast boss sheet covering
  molten/cooled shell and jaw states.
- Adds assets/stage09_nebula_v91.png: a full 256-pixel-wide far-background plate.
  The nebula is now a huge horizon-spanning cosmic structure rather than small
  midground nebula blobs.
- PyInstaller now bundles the assets directory into the standalone EXE.

VISUAL CORRECTIONS
------------------
- Terminus Veil bypasses the older procedural line/arc overlay stack when rendering
  the new authored background plate.
- Veil floor texture replaces its old straight grid with a mottled cosmic surface.
- Eclipse Engine removes the unexplained full-width aurora lines and reduces the
  ruler-straight ice-floor ray pattern into recognizable branching cracks.
- The player ship runtime now displays the authored frames directly.
- Pyroclast runtime now displays the authored cohesive boss frames directly.

SPHERICAL SHIELD V3
-------------------
The shield renderer now uses projected 3D great-circle mathematics rather than a
flat oval. Back-hemisphere rings/nodes render before the ship and front-hemisphere
rings/nodes render afterward, so energy visibly rotates behind and in front of the
craft. The outer silhouette is circular, translucent, flickering, and hit-reactive.

ENDING FIX
----------
- Ending narration is dynamically wrapped against a strict 218-pixel text width.
- The ending is now a standalone presentation state and no longer draws the gameplay
  HUD underneath the scrolling story.
- Story lines remain centered and inside the 256x224 native canvas.
- The original V9.0 heroic ending theme is retained.

BUILD
-----
1. Replace the repository contents with this package, including the assets folder.
2. Commit to the default branch.
3. Actions -> Build Omega Horizon V9.1 for Windows -> Run workflow.
4. Wait for source regression, syntax, packaged-EXE smoke test and packaging to pass.
5. Download artifact: OmegaHorizon-Windows-x64-V9.1-AUTHORED-ART-FOUNDATION

The running window title contains V9.1-AUTHORED-ART-FOUNDATION.
