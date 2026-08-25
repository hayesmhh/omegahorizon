OMEGA HORIZON V8.6 - FULL SPRITE ART & MATERIAL READABILITY
===========================================================

V8.6 continues the late-SNES visual-fidelity program across the entire game.
It is not a boss-only or readability-only patch.

PRIMARY CHANGES
---------------
- Replaces the universal bright enemy halo with material-specific edge lighting.
  Hive enemies retain a broken bioluminescent membrane contour; mechanical,
  ice, lava, aquatic, dimensional and Omega enemies use different hard-pixel
  highlight/shadow treatments appropriate to their material.
- Larger authored player-ship sprite plus banking-light animation states.
- Larger, more distinctive core enemy silhouettes for interceptor, heavy,
  artillery and ambusher roles.
- Stage-material metasprite components modify those enemy silhouettes with
  fins, armor pods, spikes, tendrils, crystals and dimensional structures.
- Adds another authored scenery layer to all ten stages: space wreckage,
  atmospheric ridges, cavern columns, submerged arches, station conduits,
  hive ribs, grounded city facades, irregular ice cliffs, Veil gates and
  Omega living-machine ribs.
- Health, major-health, life and weapon pickups receive authored indexed art.
- Bosses receive another material/anatomy finishing pass, including a more
  threatening OMEGA face, brow, fangs and iris activity.
- V8.5's EASY / HARDER / DIFFICULT / INSANE balance remains unchanged;
  INSANE is still the original pre-difficulty balance.
- Test mode, saves, settings, true stereo audio, fixed-step rendering and
  continuous perspective scrolling remain intact.

BUILD
-----
Replace the files in your existing GitHub repository, commit, then run:

    Actions -> Build Omega Horizon V8.6 for Windows -> Run workflow

The cloud workflow source-tests the artist assets and then launches the actual
packaged EXE in smoke-test mode before uploading it.

DOWNLOAD ARTIFACT
-----------------
    OmegaHorizon-Windows-x64-V8.6-SPRITE-ART

The running window title contains V8.6-SPRITE-ART.
