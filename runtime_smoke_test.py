"""Omega Horizon V8.5 source-level regression smoke test."""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="omega_horizon_v85_")
os.environ["LOCALAPPDATA"] = _tmp
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
import omega_horizon_shmup as game

assert game.BUILD_ID == "V8.5-SCENE-READABILITY"
assert len(game.STAGES) == 10
assert len(game.WEAPON_NAMES) == 10
assert game.WEAPON_NAMES[4] == "HOMING ROCKET"
assert game.FIXED_DT == 1.0/game.FPS
assert len({(s.theme, s.music_style, s.bpm, s.key) for s in game.STAGES}) == 10
assert len(game.PLAYER_PIXELS) >= 10
assert all(a in game.ENEMY_PIXEL_BANK for a in game.ARCHETYPES)
for asset in (game.PYRO_PROFILE_HEAD, game.SENTINEL_CHASSIS, game.MOTHER_ABDOMEN,
              game.ARES_TORSO, game.WYRM_HEAD, game.SOVEREIGN_FACE, game.OMEGA_MASK):
    assert len(asset) >= 7
for art in (game.ICE_RIDGE_V84_A, game.ICE_RIDGE_V84_B, game.ICE_RIDGE_V84_C, game.ICE_RIDGE_V84_D,
            game.LAVA_ARCH_V84, game.WATER_RUIN_V84, game.STATION_MACHINE_V84,
            game.HIVE_ARCH_V84, game.CITY_TOWER_V84_A, game.VEIL_MONOLITH_V84, game.OMEGA_COLUMN_V84):
    assert len(art) >= 20

pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled, audio.last_error
assert len(audio.weapon_sfx) == 10 and all(len(v) == 3 for v in audio.weapon_sfx)

# Representative music, boss arrangement and boss stinger must all be true stereo.
for stage_index in (0, 2, 4, 7, 9):
    snd = audio.generate_stage_mix(stage_index, boss=False)
    arr = pygame.sndarray.array(snd)
    assert arr.ndim == 2 and arr.shape[1] == 2
    assert np.any(arr[:,0] != arr[:,1])
for stage_index in (2, 7, 9):
    snd = audio.generate_boss_stinger(stage_index)
    arr = pygame.sndarray.array(snd)
    assert np.any(arr[:,0] != arr[:,1])

# Render-stability regression: old camera wrap at 256 must never return.
g = game.Game()
assert g.difficulty == "INSANE"
assert game.DIFFICULTY_PROFILES["INSANE"]["boss_hp"] == 1.0
assert game.DIFFICULTY_PROFILES["INSANE"]["bullet_speed"] == 1.0
bg = g.background
assert len(bg.v84_tiles['ice_far']) == 4 and len(bg.v84_tiles['ice_near']) == 3
tile_ids = [id(x) for x in bg.v84_tiles['ice_far']]
bg.scroll = 255.9
bg.update(game.FIXED_DT, 3)
assert bg.scroll > 255.9
bg.draw(g.canvas,3)
ids_before = {k:id(v) for k,v in bg._floor_surfaces.items()}
bg.draw(g.canvas,3)
assert ids_before == {k:id(v) for k,v in bg._floor_surfaces.items()}
bg.draw(g.canvas,8)
assert tile_ids == [id(x) for x in bg.v84_tiles['ice_far']]

# Every environment, archetype and artist-pass boss must render.
for stage in range(1, 11):
    g.stage = stage
    g.background.draw(g.canvas, stage)
    for i, archetype in enumerate(game.ARCHETYPES):
        e = game.Enemy(145+i*20, 58+i*31, stage, 1000+i, i, archetype)
        e.draw(g.canvas)
        assert e.damage_multiplier(0) > 0
    boss = game.Boss(stage)
    boss.intro = 0
    boss.draw(g.canvas)
    assert boss.damage_multiplier(0) > 0
    assert boss.rect().width >= 50

# Recovery cadence.
g.reset_new_game(); g.begin_play(); g.player.health=30; g.health_drop_timer=0
before=len(g.pickups); g.update_play(game.FIXED_DT)
assert len(g.pickups) > before
assert any(p.kind in ("health","major_health") for p in g.pickups)

# Save/load + settings + developer test workflow.
g.difficulty="HARDER"; g.difficulty_index=game.DIFFICULTY_ORDER.index("HARDER")
g.stage=4; g.score=23456; g.player.lives=5; g.player.health=57
g.player.unlocked[:5]=[True]*5; g.player.weapon=4
assert g.save_game(); g.score=1; g.player.health=3; g.player.weapon=0
assert g.load_game(); assert g.stage==4 and g.score==23456 and int(g.player.health)==57 and g.difficulty=="HARDER"
g.settings["music_volume"]=.4; g.settings["sfx_volume"]=.5; g.settings["effects"]=0
g.apply_settings(); assert g.canvas.get_size()==(game.NATIVE_W,game.NATIVE_H)
g.activate_test_mode(); g.test_stage=10; g.test_spawn_boss(10)
assert g.boss is not None and g.boss.stage==10
g.unlock_all_test_weapons(); assert all(g.player.unlocked)
g.test_refill(); assert g.player.lives>=9 and g.player.health==g.player.max_health
g.god_mode=True; g.player.invuln=0; hp=g.player.health; g.player.hit(500,g); assert g.player.health==hp
assert not g.save_game()

# Several fixed update frames and all menu draw paths.
g.state="pause"; g.draw(); g.open_settings("pause"); g.draw(); g.open_test_menu("settings"); g.draw()
g.state="play"
for _ in range(8): g.update(game.FIXED_DT)
g.draw()

g.audio.stop_music(); pygame.quit()
print("OMEGA_V85_SOURCE_SMOKE_TEST_OK")

assert game.DIFFICULTY_ORDER == ("EASY","HARDER","DIFFICULT","INSANE")
assert game.DIFFICULTY_PROFILES["INSANE"]["enemy_hp"] == 1.0
