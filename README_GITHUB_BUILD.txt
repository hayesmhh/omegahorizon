OMEGA HORIZON V9.5 - WORLD BEAUTY & PRESENTATION PASS
=====================================================

V9.5 is a focused visual/presentation release built from V9.4. Its primary goal is to
bring every stage environment closer to the authored beauty and atmosphere of Stage 9,
while fixing the title-screen UI architecture and adding a proper player death sequence.

WORLD BEAUTY PASS
-----------------
- All ten stages now use shipped authored background plates as their primary scenic art.
- Stage 9's well-received nebula plate is deliberately preserved as the benchmark.
- New/rebuilt authored plates cover atmospheric descent, magma caverns, underwater ruins,
  Ion Citadel, biomechanical hive, ruined megacity, frozen moon and OMEGA's final core.
- Older line-heavy procedural background stacks are bypassed on all stages. Runtime drawing
  is now restricted mainly to perspective floor motion, particles, weather and restrained FX.
- Ion Citadel receives denser reactor architecture, machinery banks, warning lights and depth.
- Underwater, hive, city and OMEGA plates receive extra texture/detail passes.

TITLE PRESENTATION
------------------
- Removes the boxed OMEGA HORIZON title treatment.
- Removes visible build/version text from the public title screen.
- Adds a custom authored transparent OMEGA HORIZON pixel-logo asset.
- Separates title artwork, logo, normal menu and modal-menu layers.
- Opening Difficulty, Settings or Test Mode suppresses the normal title/menu text underneath,
  preventing the text-on-text collisions seen in earlier builds.
- The normal title footer uses fixed vertical lanes and status messages replace the footer
  instead of drawing over it.

PLAYER DEATH SEQUENCE
---------------------
- Lethal damage no longer instantly teleports/resets the player.
- The player enters a 1.55-second destruction state with a core blast, secondary detonations,
  sparks and multiple spinning ship-debris fragments.
- Normal player control/collision is suspended during the death sequence.
- If a life remains, the ship respawns at full HP with a longer invulnerability window and
  cleared nearby enemy fire/hazards.
- If no lives remain, GAME OVER appears only after the destruction sequence completes.

BOSS CONTINUITY
---------------
- V9.4's recovery of individualized boss renderers remains intact.
- Stage 9 Parallax Sovereign and Stage 10 OMEGA specifically bypass the V9.4 intimidation
  overlay so they preserve the stronger pre-V9.4 presentation the user identified.
- The regressed V9.3 standardized boss-sheet path remains absent and guarded by smoke tests.

BUILD
-----
1. Replace the repository contents with this package.
2. Commit to the default branch.
3. Actions -> Build Omega Horizon V9.5 for Windows -> Run workflow.
4. Wait for source regression and packaged-EXE smoke tests to pass.
5. Download: OmegaHorizon-Windows-x64-V9.5-WORLD-BEAUTY-PRESENTATION

The Windows title bar contains V9.5-WORLD-BEAUTY-PRESENTATION for build verification;
the in-game title screen intentionally does not display internal version/build text.
