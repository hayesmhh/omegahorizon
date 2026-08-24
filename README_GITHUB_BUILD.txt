OMEGA HORIZON - GITHUB WINDOWS BUILD V7
=======================================

V7 is deliberately impossible to confuse with the earlier broken EXE.

VISIBLE IDENTITY
----------------
The running game window title contains:

    OMEGA HORIZON V7-STEREO-AUDIOFIX

The title screen also contains:

    BUILD V7 AUDIOFIX

The GitHub artifact is named:

    OmegaHorizon-Windows-x64-V7-AUDIOFIX

A build that does not show those identifiers is NOT V7.

AUDIO FIX
---------
V7 adapts generated mono synth data to the ACTUAL pygame mixer channel count.
With a stereo mixer it creates a contiguous (samples, 2) int16 array before
calling pygame.sndarray.make_sound().

V7 also fails soft: an unexpected audio-device problem disables audio instead
of crashing the entire game at startup.

TWO LEVELS OF CLOUD TESTING
---------------------------
Before GitHub uploads the EXE, it now runs:

1. Source-level stereo audio/render smoke test.
2. The actual packaged dist\OmegaHorizon.exe with --smoke-test.

The artifact is uploaded only if BOTH tests exit successfully.

HOW TO UPDATE YOUR EXISTING REPOSITORY
--------------------------------------
1. Extract this V7 ZIP.
2. Upload/replace ALL files in your existing GitHub repository.
3. Pay particular attention to:
       omega_horizon_shmup.py
       runtime_smoke_test.py
       .github/workflows/build-windows-exe.yml
       version_info.txt
4. Commit the replacements to the default branch.
5. Go to Actions.
6. Run:
       Build Omega Horizon V7 for Windows
7. Wait for every step to turn green, including:
       Smoke-test the PACKAGED EXE itself
8. Download ONLY the artifact named:
       OmegaHorizon-Windows-x64-V7-AUDIOFIX
9. Delete/rename older OmegaHorizon.exe copies before extracting V7.
10. Run the new OmegaHorizon.exe.
11. Confirm the window title contains V7-STEREO-AUDIOFIX.

If the title does not contain V7-STEREO-AUDIOFIX, Windows is running an older
copy of the executable.
