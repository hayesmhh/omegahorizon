"""Omega Horizon V9.6 flagship-art and recovery source regression smoke test."""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="omega_horizon_v96_")
os.environ["LOCALAPPDATA"] = _tmp
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
import omega_horizon_shmup as game

assert game.BUILD_ID == "V9.6-FLAGSHIP-ART-RECOVERY"
assert game.DISPLAY_VERSION == "V9.6"
assert game.DISPLAY_SUBTITLE == "FLAGSHIP ART & RECOVERY"
assert len(game.STAGES) == 10
assert len(game.WEAPON_NAMES) == 10
assert game.WEAPON_NAMES[4] == "HOMING ROCKET"
assert game.FIXED_DT == 1.0/game.FPS
assert game.DIFFICULTY_ORDER == ("EASY","HARDER","DIFFICULT","INSANE")
assert game.DIFFICULTY_PROFILES["INSANE"]["damage"] == 1.0
assert set(game.V96_SCENE_CHUNKS) == set(game.V95_SCENE_CHUNKS)
assert set(game.V96_SHIELD_PIXELS) == set(game.SHIELD_ORDER)
assert len({(s.theme, s.music_style, s.bpm, s.key) for s in game.STAGES}) == 10

# V9.4 preserves the authored world while removing the regressed unified boss sheet.
assert len(game.PLAYER_PIXELS) >= 15
assert max(map(len, game.PLAYER_PIXELS)) >= 35
assert all(a in game.ENEMY_PIXEL_BANK for a in game.ARCHETYPES)
assert all(len(game.ENEMY_PIXEL_BANK[a]) >= 11 for a in game.ARCHETYPES)
assert set(game.ENEMY_MATERIAL_PARTS) >= {"lava","water","station","hive","city","ice","veil","omega"}
assert callable(game.draw_material_readability)
assert callable(game.draw_enemy_material_parts)
assert set(game.V88_SCENE_CHUNKS) == {"space","atmosphere","lava","water","station","hive","city","ice","veil","omega"}
assert set(game.V88_SHIELD_PIXELS) == set(game.SHIELD_ORDER)
assert game.SHIELD_DATA["AEGIS"]["energy"] >= 60
assert game.SHIELD_DATA["REFLECTOR"]["charges"] >= 6
for art in (game.SPACE_WRECK_V86, game.ATMOS_RIDGE_V86, game.LAVA_COLUMN_V86,
            game.WATER_ARCH_V86, game.STATION_CONDUIT_V86, game.HIVE_RIB_V86,
            game.CITY_FACADE_V86, game.ICE_CLIFF_V86, game.VEIL_GATE_V86, game.OMEGA_RIB_V86):
    assert len(art) >= 7
for asset in (game.PYRO_PROFILE_HEAD, game.SENTINEL_CHASSIS, game.MOTHER_ABDOMEN,
              game.ARES_TORSO, game.WYRM_HEAD, game.SOVEREIGN_FACE, game.OMEGA_MASK):
    assert len(asset) >= 7

for rel in (
    "assets/player_ship_v91.png","assets/pyroclast_v91.png",
    "assets/title_screen_v96.png","assets/title_logo_v96.png",
    "assets/stage01_space_v95.png","assets/stage02_atmosphere_v95.png","assets/stage03_lava_v95.png",
    "assets/stage04_water_v95.png","assets/stage05_station_v95.png","assets/stage06_hive_v96.png",
    "assets/stage07_city_v96.png","assets/stage08_ice_v96.png","assets/stage09_nebula_v95.png","assets/stage10_omega_v95.png",
    *tuple(f"assets/enemy_stage{stage:02d}_v96.png" for stage in range(1,11))):
    assert os.path.exists(game.resource_path(rel)), rel
wrapped=game.build_ending_lines()
assert wrapped and max((game.text_width(line) for line in wrapped if line), default=0) <= game.ENDING_TEXT_WIDTH
assert game.ENDING_SCROLL_SPEED < 19
assert game.ENDING_STORY_TOP >= 44 and game.ENDING_STORY_BOTTOM <= 204
assert min(b-a for a,b in zip(game.TITLE_MENU_ROWS,game.TITLE_MENU_ROWS[1:])) >= 14
assert game.TITLE_LOGO_RECT[1]+game.TITLE_LOGO_RECT[3] < game.TITLE_MENU_ROWS[0]

pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled, audio.last_error
assert len(audio.weapon_sfx) == 10 and all(len(v) == 3 for v in audio.weapon_sfx)
for stage_index in (0, 2, 4, 7, 9):
    snd = audio.generate_stage_mix(stage_index, boss=False)
    arr = pygame.sndarray.array(snd)
    assert arr.ndim == 2 and arr.shape[1] == 2
    assert np.any(arr[:,0] != arr[:,1])
for stage_index in (2, 7, 9):
    snd = audio.generate_boss_stinger(stage_index)
    arr = pygame.sndarray.array(snd)
    assert np.any(arr[:,0] != arr[:,1])
intro = audio.generate_intro_theme()
arr = pygame.sndarray.array(intro)
assert arr.ndim == 2 and arr.shape[1] == 2 and np.any(arr[:,0] != arr[:,1])
ending = audio.generate_ending_theme()
arr = pygame.sndarray.array(ending)
assert arr.ndim == 2 and arr.shape[1] == 2

# Continuous fixed-step rendering and cached authored tile/surface allocations.
g = game.Game()
assert g.difficulty == "INSANE"
assert len(game.ART_ASSETS.get("player_ship_frames",[])) == 5
assert len(game.ART_ASSETS.get("pyroclast_frames",[])) == 4
assert game.ART_ASSETS["stage01_space"].get_size() == (256,203)
for key in ("stage02_atmosphere","stage03_lava","stage04_water","stage05_station","stage06_hive","stage07_city","stage08_ice","stage09_nebula","stage10_omega"):
    assert game.ART_ASSETS[key].get_size() == (256,91), key
assert game.ART_ASSETS["title_logo"].get_size() == (248,38)
for stage in range(1,11):
    frames=game.ART_ASSETS.get(f"enemy_stage{stage:02d}_frames",[])
    assert len(frames)==8
    assert frames[0].get_size()==(40,28)
assert game.ART_ASSETS["title_screen"].get_size() == (256,224)
assert "bosses_v93_sheet" not in game.ART_ASSETS
assert "boss_v93_frames" not in game.ART_ASSETS
assert g.audio.intro_sound is not None
bg = g.background
assert "ice" in bg.v86_tiles and "city" in bg.v86_tiles and "omega" in bg.v86_tiles
assert set(bg.v87_tiles) == {"space","atmosphere","lava","water","station","hive","city","ice","veil","omega"}
assert "lava_flip" in bg.v86_tiles
v86_ids={k:id(v) for k,v in bg.v86_tiles.items()}
bg.scroll = 255.9
bg.update(game.FIXED_DT, 3)
assert bg.scroll > 255.9
bg.draw(g.canvas,3)
ids_before = {k:id(v) for k,v in bg._floor_surfaces.items()}
bg.draw(g.canvas,3)
assert ids_before == {k:id(v) for k,v in bg._floor_surfaces.items()}
assert v86_ids == {k:id(v) for k,v in bg.v86_tiles.items()}

# Every environment, material-specific enemy and boss must render.
for stage in range(1, 11):
    g.stage = stage
    g.background.draw(g.canvas, stage)
    for i, archetype in enumerate(game.ARCHETYPES):
        e = game.Enemy(145+i*18, 58+i*31, stage, 1000+i, i, archetype)
        e.draw(g.canvas)
        assert e.damage_multiplier(0) > 0
    boss = game.Boss(stage)
    boss.intro = 0
    boss.draw(g.canvas)
    assert boss.damage_multiplier(0) > 0
    assert boss.rect().width >= 50

# Title-screen modal architecture suppresses the normal title/menu layer.
g.state="title"; g.draw_title(True,True); g.draw()
g.state="difficulty_select"; g.draw()
g.settings_return_state="title"; g.state="settings"; g.draw()
g.test_mode=True; g.test_return_state="title"; g.state="test_menu"; g.draw(); g.test_mode=False

# Lethal damage must play the death sequence and then respawn if a life remains.
g.state="play"; g.player.lives=2; g.player.health=1; g.player.invuln=0; g.god_mode=False
g.player.hit(999,g)
assert g.player_dead and g.player.health==0 and g.player.lives==1
assert len(g.player_debris)>=10 and len(g.explosions)>=1
for _ in range(int(1.7/game.FIXED_DT)): g.update(game.FIXED_DT)
assert not g.player_dead and g.state=="play" and g.player.lives==1 and g.player.health==g.player.max_health
g.player.health=1; g.player.lives=1; g.player.invuln=0; g.player.hit(999,g)
assert g.player_dead and g.player.lives==0 and g.state=="play"
for _ in range(int(1.7/game.FIXED_DT)): g.update(game.FIXED_DT)
assert g.state=="game_over" and not g.player_dead

# Recovery cadence and authored pickup drawing.
g.reset_new_game(); g.begin_play(); g.player.health=30; g.health_drop_timer=0
before=len(g.pickups); g.update_play(game.FIXED_DT)
assert len(g.pickups) > before
for p in g.pickups:p.draw(g.canvas)

# Temporary shield mechanics and visual pickup paths.
g.player.activate_shield("AEGIS",g); g.player.invuln=0; hp=g.player.health; energy=g.player.shield_energy
g.player.hit(12,g); assert g.player.health==hp and g.player.shield_energy<energy
g.player.activate_shield("PHASE",g); g.player.invuln=0; hp=g.player.health; g.player.hit(80,g); assert g.player.health==hp
g.player.activate_shield("REFLECTOR",g); b=game.Bullet(g.player.x,g.player.y,-100,0,10,"enemy","normal",2,2); before=len(g.player_bullets); assert g.player.shield_projectile(b,g); assert len(g.player_bullets)==before+1
g.player.activate_shield("INTERCEPTOR",g); assert g.player.shield_charges>0
for sk in game.SHIELD_ORDER:
    p=game.Pickup(100,100,"shield_"+sk.lower()); p.draw(g.canvas)

# Save/load + settings + developer test workflow remain intact.
g.difficulty="HARDER"; g.difficulty_index=game.DIFFICULTY_ORDER.index("HARDER")
g.stage=4; g.score=23456; g.player.lives=5; g.player.health=57
g.player.unlocked[:5]=[True]*5; g.player.weapon=4; g.player.activate_shield("AEGIS",g); saved_shield=g.player.shield_energy
assert g.save_game(); g.score=1; g.player.health=3; g.player.weapon=0; g.player.clear_shield()
assert g.load_game(); assert g.stage==4 and g.score==23456 and int(g.player.health)==57 and g.difficulty=="HARDER"
assert g.player.shield_kind=="AEGIS" and g.player.shield_energy==saved_shield
g.activate_test_mode(); g.test_stage=10; g.test_spawn_boss(10)
assert g.boss is not None and g.boss.stage==10
g.unlock_all_test_weapons(); assert all(g.player.unlocked)
g.test_refill(); assert g.player.lives>=9 and g.player.health==g.player.max_health
g.god_mode=True; g.player.invuln=0; hp=g.player.health; g.player.hit(500,g); assert g.player.health==hp
assert not g.save_game()

g.win_game(); assert g.state=="ending" and not g.ending_complete
start_scroll=g.ending_scroll
g.update(game.FIXED_DT); assert g.ending_scroll < start_scroll and (start_scroll-g.ending_scroll) < (19*game.FIXED_DT)
g.draw()
g.ending_complete=True; held=g.ending_scroll; g.update(game.FIXED_DT*10)
assert g.state=="ending" and g.ending_scroll==held
g.state="victory"; g.draw()
g.state="pause"; g.draw(); g.open_settings("pause"); g.draw(); g.open_test_menu("settings"); g.draw()
g.state="play"
for _ in range(8): g.update(game.FIXED_DT)
g.draw()

g.audio.stop_music(); pygame.quit()
print("OMEGA_V960_SOURCE_SMOKE_TEST_OK")
