OMEGA HORIZON V8.3 - FULL VISUAL FIDELITY PASS
===============================================

V8.3 continues the broad late-16-bit visual overhaul rather than limiting the
artist pass to one or two bosses.

PRIMARY V8.3 CHANGES
--------------------
- Full artist/metasprite redraws for the previously abstract boss designs:
  Pyroclast, Citadel Sentinel, Mother Null, Ares-IX, Cryon Wyrm,
  Parallax Sovereign and OMEGA.
- Pyroclast is now a side-profile horned lava beast with head/jaw, torso,
  forelimb/claw, legs, tail and magma channels rather than a circular golem.
- Ares-IX now reads as an articulated siege mech with legs, head/visor,
  torso, primary cannon, secondary arm, shoulder weapons and reactor spine.
- Cryon Wyrm now has a jawed head and a long chain of authored serpent armor
  segments and ice fins.
- Broad environment art pass: more detailed city buildings, station
  bulkheads, hive pods/ribs, glacier ridges, reality monoliths and Omega
  machinery/depth structures.
- Normal enemy archetypes receive animated hardpoints, propulsion cues and
  stronger stage-material detailing.
- Player-ship lighting/engine effects and invulnerability presentation are
  upgraded.
- Explosions are layered flash/fire/smoke/debris-style effects rather than
  primarily expanding outline circles.
- HUD receives a smaller beveled stage-accented presentation.

SCREEN JUMP / REPEAT FIX
------------------------
V8.2 periodically wrapped Background.scroll at exactly 256 even though the
software perspective sampler multiplied that camera value by 1.8 and 0.23.
255.9 -> 0 therefore did NOT represent an equivalent texture position and
could cause the whole floor/background to visibly snap or appear to repeat.

V8.3 keeps camera scroll continuous and performs wrapping only when texture
indices are sampled.

V8.3 also:
- uses one exact 1/60 simulation step per presented frame;
- deliberately avoids multi-step catch-up after a stall, preventing catch-up jumps;
- uses tick_busy_loop for steadier desktop pacing;
- reuses NumPy floor buffers and SDL floor surfaces rather than allocating new
  floor surfaces every frame.

AUDIO V8.3
----------
- Existing distinct 16-bar stage compositions remain.
- Additional FM-like, pulse-lead and harp timbres are used by selected stages.
- Final-section melodic hook reprises strengthen loop identity.
- Every stage has its own synthesized stereo boss-entry stinger.
- True stereo music, positional SFX and all unique weapon sounds remain.

TEST MODE / SAVE / SETTINGS
---------------------------
All V8.2 systems remain:
- Type TERMINUS on the title screen, then F1, for the developer test menu.
- Jump directly to any stage or spawn any stage boss.
- Unlock all weapons, refill health/lives, toggle God Mode.
- F5 quick-save / F9 quick-load.
- Pause menu and settings for music, SFX, fullscreen, scale and effects.

GITHUB BUILD
------------
1. Replace the files in your existing GitHub repository with this package.
2. Commit to the default branch.
3. Open Actions.
4. Run: Build Omega Horizon V8.3 for Windows
5. Wait for every check to turn green, especially:
       Smoke-test the PACKAGED V8.3 EXE
6. Download only:
       OmegaHorizon-Windows-x64-V8.3-VISUAL-FIDELITY
7. Run the new OmegaHorizon.exe.

The window title must contain:
    V8.3-VISUAL-FIDELITY

The finished EXE is standalone and does not require Python/Pygame/NumPy on
machines that only run the game.
