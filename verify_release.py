"""Readable pre-build verification for Omega Horizon V9.6.2."""
from pathlib import Path
import omega_horizon_shmup as g

ROOT = Path(__file__).resolve().parent


def check(name, condition, detail=""):
    if not condition:
        msg = f"[FAIL] {name}"
        if detail:
            msg += f": {detail}"
        raise AssertionError(msg)
    print(f"[PASS] {name}")


check("build id", g.BUILD_ID == "V9.6.2-STAGE1-FLAGSHIP-SPACE", g.BUILD_ID)
check("display version", g.DISPLAY_VERSION == "V9.6.2", g.DISPLAY_VERSION)
check("display subtitle", g.DISPLAY_SUBTITLE == "STAGE 1 FLAGSHIP SPACE", g.DISPLAY_SUBTITLE)
check("Stage 1 flagship mode", g.STAGE1_FLAGSHIP_MODE is True)
check("Stage 1 flagship asset path", g.STAGE1_FLAGSHIP_ASSET == "assets/stage01_space_v962.png", g.STAGE1_FLAGSHIP_ASSET)
check("recovery baseline preserved", g.VISUAL_RECOVERY_BASELINE == "V9.4-BACKGROUNDS/V9.1-ENEMIES", g.VISUAL_RECOVERY_BASELINE)
check("background recovery enabled", g.BACKGROUND_RECOVERY_MODE is True)
check("authored enemy overrides disabled", g.AUTHORED_ENEMY_OVERRIDE is False)
check("Homing Rocket identity", g.WEAPON_NAMES[4] == "HOMING ROCKET", g.WEAPON_NAMES[4])
check("difficulty ordering", g.DIFFICULTY_ORDER == ("EASY","HARDER","DIFFICULT","INSANE"), repr(g.DIFFICULTY_ORDER))
check("INSANE baseline damage", g.DIFFICULTY_PROFILES["INSANE"]["damage"] == 1.0)
check("V9.6.2 scene aliases", set(g.V962_SCENE_CHUNKS) == {"space","atmosphere","lava","water","station","hive","city","ice","veil","omega"})
check("V9.6.2 shield aliases", set(g.V962_SHIELD_PIXELS) == set(g.SHIELD_ORDER))
check("ending scroll remains slowed", g.ENDING_SCROLL_SPEED < 19, str(g.ENDING_SCROLL_SPEED))
check("ending text width", g.ENDING_TEXT_WIDTH <= 202, str(g.ENDING_TEXT_WIDTH))

for rel in (
    "assets/player_ship_v91.png",
    "assets/pyroclast_v91.png",
    "assets/title_screen_v96.png",
    "assets/title_logo_v96.png",
    "assets/stage01_space_v962.png",
    "assets/stage05_station_v961.png",
    "assets/stage08_ice_v961.png",
    "assets/stage09_nebula_v961.png",
):
    check(f"required asset {rel}", (ROOT / rel).is_file())

spec = (ROOT / "OmegaHorizon.spec").read_text(encoding="utf-8")
check("PyInstaller bundles assets directory", "('assets', 'assets')" in spec)
check("old unified boss sheet not configured", "bosses_v93_sheet" not in g.ART_ASSETS and "boss_v93_frames" not in g.ART_ASSETS)

print("V9.6.2 RELEASE VERIFICATION OK")
