"""Readable pre-build verification for Omega Horizon V9.6.4."""
from pathlib import Path
import omega_horizon_shmup as g
ROOT=Path(__file__).resolve().parent

def check(name,condition,detail=""):
    if not condition:
        raise AssertionError(f"[FAIL] {name}"+(f": {detail}" if detail else ""))
    print(f"[PASS] {name}")

check("build id",g.BUILD_ID=="V9.6.4-STAGE2-CONTINUOUS-DESCENT",g.BUILD_ID)
check("display version",g.DISPLAY_VERSION=="V9.6.4",g.DISPLAY_VERSION)
check("display subtitle",g.DISPLAY_SUBTITLE=="STAGE 2 CONTINUOUS DESCENT",g.DISPLAY_SUBTITLE)
check("Stage 1 ringed asset retained",g.STAGE1_FLAGSHIP_ASSET=="assets/stage01_space_v964.png",g.STAGE1_FLAGSHIP_ASSET)
check("Stage 2 descent enabled",g.STAGE2_DESCENT_MODE is True)
check("continuous descent renderer enabled",g.STAGE2_CONTINUOUS_DESCENT is True)
check("five descent phases",len(g.STAGE2_DESCENT_ASSETS)==5,str(g.STAGE2_DESCENT_ASSETS))
check("descent thresholds",g.STAGE2_DESCENT_THRESHOLDS==(0.0,0.18,0.38,0.60,0.80),repr(g.STAGE2_DESCENT_THRESHOLDS))
check("recovery baseline preserved",g.VISUAL_RECOVERY_BASELINE=="V9.4-BACKGROUNDS/V9.1-ENEMIES",g.VISUAL_RECOVERY_BASELINE)
check("authored enemies still disabled",g.AUTHORED_ENEMY_OVERRIDE is False)
for rel in (
    "assets/player_ship_v91.png","assets/pyroclast_v91.png","assets/title_screen_v96.png","assets/title_logo_v96.png",
    "assets/stage01_space_v964.png","assets/stage05_station_v961.png","assets/stage08_ice_v961.png","assets/stage09_nebula_v961.png",
    *g.STAGE2_DESCENT_ASSETS):
    check(f"required asset {rel}",(ROOT/rel).is_file())
check("PyInstaller bundles assets","('assets', 'assets')" in (ROOT/"OmegaHorizon.spec").read_text(encoding="utf-8"))
print("V9.6.4 RELEASE VERIFICATION OK")
