OMEGA HORIZON V8 - STAGE IDENTITY & PROGRESSION OVERHAUL
========================================================

BUILD ID
--------
V8-STAGE-IDENTITY

This package replaces V7. Upload/replace the files in your existing GitHub
repository, commit them to the default branch, then run:

    Build Omega Horizon V8 for Windows

The successful artifact is deliberately named:

    OmegaHorizon-Windows-x64-V8-STAGE-IDENTITY

WHAT V8 CHANGES
---------------
- Ten visually distinct environments rather than one repeated background.
- Stage 1 deep space.
- Stage 2 atmospheric planetary descent.
- Stage 3 underground magma caverns.
- Stage 4 underwater/pelagic ruins.
- Stage 5 orbital space station.
- Stage 6 biomechanical alien hive.
- Stage 7 ruined future megacity.
- Stage 8 frozen moon/ice trenches.
- Stage 9 reality-warped alien ringworld.
- Stage 10 Omega's living machine core.

- Four tactical enemy archetypes: Interceptor, Heavy, Artillery, Ambusher.
- Stage-local names, colors/materials and behavior variants.
- Tactical weapon strengths without arbitrary hard immunity.
- Ten separate stage bosses with unique art, movement, attacks and weaknesses.
- Bosses visually reflect their stages, including Pyroclast in the magma
  caverns and Abyssal Leviathan on the water world.
- Visible boss damage effects.
- Player starts with Plasma Repeater only.
- One new weapon reward per boss through Stage 9.
- Weapon #05 is officially HOMING ROCKET.
- Standard green +30 health cross.
- Rare major +65 health core.
- Rare extra-life pickup.
- Skill-earned extra-life opportunities on selected no-death boss clears.
- Stage-specific environmental hazards.
- More detailed original procedural pixel-art player, enemies and bosses.
- Weapon-specific projectile art.

TRUE STEREO AUDIO OVERHAUL
--------------------------
V8 no longer generates one mono song and duplicates it to L/R.

The music engine now mixes independently panned voices into a stereo bus:
- bass
- percussion
- pads/chords
- lead
- arpeggiator/counterline
- stage-dependent instrumentation
- unequal left/right feedback delay

All ten stages use different BPM/key/style data AND different melodic/rhythmic
arrangements. Boss battles receive intensified stage-specific arrangements.

Every weapon now has its own layered procedural firing sound. There are three
micro-variants per weapon to reduce repetition, and weapon/explosion/pickup
sounds are stereo-positioned according to their screen X coordinate.

CLOUD TESTING
-------------
GitHub performs both:
1. Source-level regression tests across all ten stage renderers, enemy types,
   bosses, weapon progression and true stereo sample data.
2. A smoke test of the ACTUAL packaged OmegaHorizon.exe before upload.

BUILD
-----
1. Extract this ZIP.
2. Replace/upload ALL files into your existing repository.
3. Make sure .github/workflows/build-windows-exe.yml is replaced.
4. Commit to the default branch.
5. Open Actions.
6. Select "Build Omega Horizon V8 for Windows".
7. Run workflow.
8. Wait for every step to turn green, especially:
       Smoke-test the PACKAGED V8 EXE
9. Download ONLY:
       OmegaHorizon-Windows-x64-V8-STAGE-IDENTITY
10. Delete/rename older EXEs before extracting the V8 artifact.

SUCCESS OUTPUT
--------------
OmegaHorizon.exe
OmegaHorizon_V8_SHA256.txt
OmegaHorizon_V8_Windows_x64.zip

The finished EXE is standalone and does not require Python/Pygame/NumPy on
the computer that runs it.
