"""Readable pre-build verification for Omega Horizon V9.6.8."""
from pathlib import Path
import omega_horizon_shmup as g
ROOT=Path(__file__).resolve().parent

def check(name,condition,detail=""):
    if not condition:
        raise AssertionError(f"[FAIL] {name}"+(f": {detail}" if detail else ""))
    print(f"[PASS] {name}")

check("build id",g.BUILD_ID=="V9.6.8-STAGE3-MAGMA-CATHEDRAL",g.BUILD_ID)
check("display version",g.DISPLAY_VERSION=="V9.6.8",g.DISPLAY_VERSION)
check("display subtitle",g.DISPLAY_SUBTITLE=="STAGE 3 MAGMA CATHEDRAL",g.DISPLAY_SUBTITLE)
check("Stage 1 refined ring asset",g.STAGE1_FLAGSHIP_ASSET=="assets/stage01_space_v9661.png",g.STAGE1_FLAGSHIP_ASSET)
check("Stage 1 ring center locked",g.STAGE1_RING_CENTERFIX and g.STAGE1_RING_CENTER==(227,54),str(g.STAGE1_RING_CENTER))
check("Stage 2 descent enabled",g.STAGE2_DESCENT_MODE is True)
check("fluid descent renderer enabled",g.STAGE2_CONTINUOUS_DESCENT is True)
check("single de-repeated descent source",g.STAGE2_DESCENT_ASSETS==(g.STAGE2_DESCENT_STRIP_ASSET,),str(g.STAGE2_DESCENT_ASSETS))
check("skyline de-repetition enabled",g.STAGE2_SKYLINE_DEREPETITION is True)
check("unique skyline clusters",g.STAGE2_SKYLINE_CLUSTER_COUNT>=6,str(g.STAGE2_SKYLINE_CLUSTER_COUNT))
check("single stabilized strip",g.STAGE2_DESCENT_STRIP_ASSET=="assets/stage02_descent_strip_v967.png",g.STAGE2_DESCENT_STRIP_ASSET)
check("Stage 3 Magma Cathedral enabled",g.STAGE3_MAGMA_CATHEDRAL_MODE is True)
check("Stage 3 authored panorama",g.STAGE3_MAGMA_STRIP_ASSET=="assets/stage03_magma_cathedral_v968.png",g.STAGE3_MAGMA_STRIP_ASSET)
check("Stage 3 section progression",g.STAGE3_MAGMA_SECTION_COUNT==8,str(g.STAGE3_MAGMA_SECTION_COUNT))
check("recovery baseline preserved",g.VISUAL_RECOVERY_BASELINE=="V9.4-BACKGROUNDS/V9.1-ENEMIES",g.VISUAL_RECOVERY_BASELINE)
check("authored enemies still disabled",g.AUTHORED_ENEMY_OVERRIDE is False)
for rel in (
    "assets/player_ship_v91.png","assets/pyroclast_v91.png","assets/title_screen_v96.png","assets/title_logo_v96.png",
    "assets/stage01_space_v9661.png","assets/stage05_station_v961.png","assets/stage08_ice_v961.png","assets/stage09_nebula_v961.png",
    g.STAGE2_DESCENT_STRIP_ASSET,g.STAGE3_MAGMA_STRIP_ASSET):
    check(f"required asset {rel}",(ROOT/rel).is_file())
src=(ROOT/"omega_horizon_shmup.py").read_text(encoding="utf-8")
check("old blob-haze renderer removed","pygame.draw.ellipse(haze" not in src)
check("old per-plate transform renderer removed","moving_plate(" not in src)
check("single-strip camera renderer",'ART_ASSETS.get("stage02_descent_strip")' in src)
offs=[g.stage2_camera_offset(i/100.0,663,203) for i in range(101)]
check("pixel-snapped monotonic camera",offs[0]==0 and offs[-1]==460 and offs==sorted(offs))
check("single strip loaded by runtime",'"stage02_descent_strip":(STAGE2_DESCENT_STRIP_ASSET,False)' in src)
check("Stage 3 panorama loaded by runtime",'"stage03_magma_strip":(STAGE3_MAGMA_STRIP_ASSET,False)' in src)
check("Stage 3 authored renderer",'ART_ASSETS.get("stage03_magma_strip")' in src)
check("PyInstaller bundles assets","('assets', 'assets')" in (ROOT/"OmegaHorizon.spec").read_text(encoding="utf-8"))
offs3=[g.stage3_camera_offset(i/100.0,2048,256) for i in range(101)]
check("Stage 3 pixel-snapped monotonic camera",offs3[0]==0 and offs3[-1]==1792 and offs3==sorted(offs3))
print("V9.6.8 RELEASE VERIFICATION OK")
