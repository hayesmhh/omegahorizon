OMEGA HORIZON V8.9 - LATE-SNES AESTHETIC CONVERGENCE
=====================================================

V8.9 is a convergence pass aimed at the late-SNES target aesthetic: richer handcrafted sprite mass, more atmospheric backgrounds, denser bosses, and more shimmering shield presentation.

LATE-SNES CONVERGENCE
---------------
- Re-branches the build as V8.9 with a late-SNES convergence target.
- Reworks Pyroclast into a denser, more unified lava-beast silhouette.
- Rebalances hive-enemy readability away from amoeba halos and toward predatory toxic glints.
- Overhauls shield presentation into shimmering semi-transparent spherical fields with flicker and orbital motion.
- Adds an extra V8.9 convergence background pass for ice, hive, city, lava and omega themes.
- Preserves staged music, difficulty tiers, pickups and shield systems from prior builds.

TEMPORARY SHIELD PICKUPS
------------------------
AEGIS       Damage-absorption buffer.
REFLECTOR   Reflects a limited number of enemy projectiles.
PHASE       Short-duration damage negation / phase displacement.
INTERCEPTOR Neutralizes nearby enemy bullets with limited charges.

Only one shield is active at a time. Shield drops are controlled rather than pure RNG,
rarer than normal health but more common than extra-life rewards. Shield state is saved
with campaign checkpoints. TEST MODE includes a direct shield selector.

BUILD
-----
1. Replace all files in the existing GitHub repository with this package.
2. Commit to the default branch.
3. Actions -> Build Omega Horizon V8.9 for Windows -> Run workflow.
4. Wait for the source regression and packaged-EXE smoke test to turn green.
5. Download: OmegaHorizon-Windows-x64-V8.9-LATE-SNES-CONVERGENCE

The running window title contains V8.9-LATE-SNES-CONVERGENCE.

V8.9: synchronized source, workflow, source smoke-test, packaged smoke-test, artifact, and checksum release identities.
