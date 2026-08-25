OMEGA HORIZON V9.3 - CINEMATIC ART ESCALATION
==============================================

V9.3 consolidates the authored-art transition into a more cinematic release. It focuses
on the places V9.2 still looked or sounded weaker: title presentation, boss intimidation,
Citadel scenery, authored enemy detail, and the final ending-state behavior.

V9.3 MAJOR CHANGES
------------------
- Adds a flagship 256x224 authored title-screen illustration featuring the hero ship,
  a large nebula, planets, hostile craft, and a subtle OMEGA presence.
- Cleans the title composition so the illustration owns most of the screen and utility
  text is confined to a restrained lower panel.
- Removes the independent FM/arpeggio phrase from the title theme that could fight the
  primary beat; the main intro/ending motif remains intact.
- Replaces the base art for ALL TEN BOSSES with a shipped two-frame authored boss sheet.
  Runtime effects now add damage scars, focal lighting and phase spectacle on top of the
  authored silhouettes instead of reconstructing the bosses from primitive geometry.
- Redraws the authored Stage 1 and Stage 9 enemy sheets with more shading, hardpoints,
  sharper silhouettes and post-sprite engine/specular detail.
- Rebuilds the Stage 5 Ion Citadel upper environment with a larger reactor vault, layered
  machinery bays, conduits, gantries, lighting and architectural hierarchy.
- Repaints Stage 1 and Stage 8 authored plates with richer celestial/environmental depth.
- Keeps the ending sequence in the ENDING state indefinitely after the story settles;
  it only advances when the player explicitly presses Enter/Space (Esc returns to title).
- Preserves the slower 15 px/sec ending scroll and the V9.2 spherical shield improvements.

AUTHORED V9.3 ASSETS
--------------------
- assets/title_screen_v93.png
- assets/bosses_v93.png
- assets/stage01_space_v93.png
- assets/stage05_station_v93.png
- assets/stage08_ice_v93.png
- assets/enemy_stage01_v93.png
- assets/enemy_stage09_v93.png

V9.1/V9.2 authored assets remain bundled where they are still authoritative, including
player_ship_v91.png and stage09_nebula_v91.png.

BUILD
-----
1. Replace the repository files with this package.
2. Keep the complete assets/ directory at repository root.
3. Commit to the default branch.
4. Actions -> Build Omega Horizon V9.3 for Windows -> Run workflow.
5. Wait for source regression and packaged-EXE smoke tests to pass.
6. Download artifact: OmegaHorizon-Windows-x64-V9.3-CINEMATIC-ART-ESCALATION

The running window title contains V9.3-CINEMATIC-ART-ESCALATION.
