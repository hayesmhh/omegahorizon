OMEGA HORIZON - GITHUB WINDOWS BUILD V6
=======================================

V6 RUNTIME FIX
--------------
V6 fixes the Windows startup crash `Array must be 2-dimensional for stereo mixer`. The procedural synth now adapts generated NumPy sample arrays to the mixer channel count. The GitHub workflow also runs a forced-stereo audio/runtime smoke test before creating the EXE.


This package is designed to build OmegaHorizon.exe entirely on a free
GitHub-hosted Windows virtual machine. Your local Python installation,
PowerShell version, OneDrive path, and local virtual-environment behavior are
not used for the build.

WHAT THE CLOUD BUILD USES
-------------------------
- GitHub Actions Windows Server 2022 x64 runner
- CPython 3.13 x64
- pygame-ce 2.5.8
- NumPy 2.5.2
- PyInstaller 6.22.2
- One-file, windowed PyInstaller build
- Procedural game assets; no external runtime asset folder

WHAT IT PRODUCES
----------------
The workflow uploads an artifact named:

    OmegaHorizon-Windows-x64

Inside it are:

    OmegaHorizon.exe
    OmegaHorizon_SHA256.txt
    OmegaHorizon_Windows_x64.zip

The EXE is standalone. The Windows 11 PC that runs the game does not need
Python, pygame, NumPy, or PyInstaller installed.

FASTEST SETUP
-------------
1. Sign in to GitHub.
2. Create a new repository.
3. It can be PUBLIC for the simplest no-cost Actions usage.
4. Extract this V5 ZIP on your PC.
5. Upload ALL extracted files and folders to the repository, including:
       .github
       omega_horizon_shmup.py
       OmegaHorizon.spec
       omega_horizon.ico
       omega_horizon.png
       requirements-build.txt
       version_info.txt
6. Commit the files to the repository's main branch.
7. Open the repository's Actions tab.
8. Select:
       Build Omega Horizon for Windows
9. Click:
       Run workflow
10. Click the green:
       Run workflow
    button in the confirmation menu.
11. Wait for the workflow to finish with a green check mark.
12. Open the completed workflow run.
13. Scroll to the Artifacts section.
14. Download:
       OmegaHorizon-Windows-x64
15. Extract that artifact ZIP.
16. Run:
       OmegaHorizon.exe

IMPORTANT: SHOW HIDDEN .GITHUB FOLDER
-------------------------------------
The `.github` folder begins with a dot. Make sure it is uploaded. It contains:

    .github/workflows/build-windows-exe.yml

Without that file, GitHub has no workflow to run.

NO LOCAL BUILD IS REQUIRED
--------------------------
Do not run BUILD_WINDOWS_EXE.bat from older packages for this V5 method.
Everything is compiled in GitHub Actions.

SMARTSCREEN
-----------
The resulting program is a newly created unsigned executable. Windows Defender
SmartScreen may warn that the publisher is unknown. That does not mean the
build failed. Signing with an Authenticode certificate is a separate release
step if the game is eventually distributed publicly.

SOURCE OF TRUTH
---------------
The GitHub Actions workflow is:

    .github/workflows/build-windows-exe.yml

It is deliberately manual (`workflow_dispatch`) so uploading the repository
does not consume a build automatically. You decide when to press Run workflow.
