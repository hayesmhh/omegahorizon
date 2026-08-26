OMEGA HORIZON V9.4 - BOSS INTIMIDATION RECOVERY
================================================

V9.4 is a corrective boss-art release built from the V9.3 authored-world baseline.
The V9.3 standardized boss sprite sheet has been removed from the runtime because it
flattened detail, menace and material identity across the ten bosses.

BOSS INTIMIDATION RECOVERY
--------------------------
- Restores the stronger individual boss-specific rendering path used before V9.3.
- Completely disables/removes the V9.3 unified 96x72 boss-sheet runtime path.
- Adds a dedicated V9.4 intimidation/detail finish for every boss rather than applying
  one shared cartoon-like visual language.
- Mechanical bosses regain recessed armor, hardpoints, panel density, weapon detail,
  turbines, lenses, pistons and deeper shadow carving.
- Organic bosses gain darker facial structure, serrated jaws/teeth, chitin, gills,
  eye clusters, mandibles, bioluminescent organs and asymmetric anatomy.
- Parallax Sovereign regains a darker impossible-geometry focal mask instead of a
  simple symbolic face.
- OMEGA receives a final-boss-only terror layer: cathedral crown/horns, secondary
  eyes, layered mandible architecture, hostile living iris and expanded phase detail.
- Critical-health bosses now accumulate physical instability/scarring rather than
  merely flashing.

PRESERVED FROM V9.3
-------------------
- flagship authored title-screen illustration and cleaned title theme
- V9.2/V9.3 authored world backgrounds and higher-detail enemy families
- improved spherical rotating shields
- continuous post-OMEGA ending until player input
- slower, clipped and readable ending story scroll

REGRESSION GUARD
----------------
The source and GitHub smoke tests explicitly assert that boss_v93_frames and the
bosses_v93_sheet runtime asset are absent. This prevents the regressed standardized
boss path from silently returning in a future build.

BUILD
-----
1. Replace the repository contents with this package.
2. Commit to the default branch.
3. Actions -> Build Omega Horizon V9.4 for Windows -> Run workflow.
4. Wait for source regression and packaged-EXE smoke tests to pass.
5. Download: OmegaHorizon-Windows-x64-V9.4-BOSS-INTIMIDATION-RECOVERY

The running window title contains V9.4-BOSS-INTIMIDATION-RECOVERY.
