OMEGA HORIZON V8.2 - BOSS ARTIST PASS & SYSTEMS
================================================

V8.2 continues the V8.1 artist-direction work and adds the development/player
systems needed to test and play the expanding ten-stage campaign efficiently.

BOSS ARTIST PASS
----------------
- PYROCLAST is completely rebuilt as an authored metasprite lava creature:
  horned skull/head, eyes, jaw/teeth, broad torso, separate animated arms and
  claws, internal molten core/fissures, and a visually distinct obsidian-shell
  state. It should read as a magma monster before its details are examined.
- VALKYRIE CARRIER now uses an authored capital-ship body with command bridge,
  fighter bays, fins, identification lighting, and four engine nozzles.
- ABYSSAL LEVIATHAN now has an authored predatory head, jaw/teeth, eye/lure,
  fins, and repeated armored/bioluminescent body segments.
- TEMPEST BASTION retains the successful V8.1 airborne-fortress metasprite.
- Boss collision silhouettes were updated to better match the new large art.

AUDIO ESCALATION
----------------
- Stage arrangements grow from 12 to 16 bars.
- Stage-specific ambient sound beds are mixed into the actual stereo music.
- Boss arrangements add low ostinatos and stereo call/response phrases rather
  than merely increasing BPM.
- Existing unique stereo weapon sounds remain intact.
- Music and SFX volume are now independently adjustable in-game.

PAUSE / SETTINGS MENU
---------------------
Press P or Esc during gameplay.

Pause menu:
- Resume
- Save Game
- Load Game
- Settings
- Test Menu (only after TEST MODE activation)
- Quit to Title

Settings:
- Music volume 0-100
- SFX volume 0-100
- Fullscreen on/off
- Integer window scale 2x-5x
- Effects density Low/Medium/High

The game ALWAYS renders internally at 256x224. Window/fullscreen presentation
uses nearest-neighbor integer scaling and letterboxing where required.

SAVE / LOAD
-----------
F5 = quick save
F9 = quick load

The manual and quick save system uses reliable stage checkpoints rather than
trying to serialize every projectile and enemy on an arbitrary frame. It saves:
- current stage
- score
- lives
- health
- unlocked weapons
- active weapon

Loading resumes at the beginning of the saved stage with those campaign stats.
Save and settings files live in the Windows per-user LOCALAPPDATA\OmegaHorizon
folder. Missing/corrupt saves are handled without crashing.

DEVELOPER / CHEAT TEST MODE
---------------------------
At the TITLE SCREEN type:

    TERMINUS

A confirmation appears. Then press:

    F1

The TEST MODE menu can:
- select any Stage 01-10
- jump directly to that stage
- spawn that stage's boss immediately
- unlock all weapons
- refill health and raise lives to 9
- toggle God Mode

TEST MODE is deliberately excluded from normal campaign saving. If TEST MODE is
active, Save Game refuses to overwrite the normal campaign checkpoint.

BUILD
-----
Replace the files in the existing GitHub repository, commit, then run:

    Build Omega Horizon V8.2 for Windows

Wait for:

    Smoke-test the PACKAGED V8.2 EXE

to turn green.

Download ONLY:

    OmegaHorizon-Windows-x64-V8.2-BOSS-ART-SYSTEMS

The window title contains V8.2-BOSS-ART-SYSTEMS.
