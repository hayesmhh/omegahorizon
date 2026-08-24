"""Omega Horizon V8.2 source-level regression smoke test."""
import os
import tempfile

# Keep test saves/settings isolated from the runner profile.
_tmp = tempfile.mkdtemp(prefix="omega_horizon_v82_")
os.environ["LOCALAPPDATA"] = _tmp
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
import omega_horizon_shmup as game

assert game.BUILD_ID == "V8.2-BOSS-ART-SYSTEMS"
assert len(game.STAGES) == 10
assert len(game.WEAPON_NAMES) == 10
assert game.WEAPON_NAMES[4] == "HOMING ROCKET"
assert len({(s.theme, s.music_style, s.bpm, s.key) for s in game.STAGES}) == 10
assert len(game.PLAYER_PIXELS) >= 10
assert all(a in game.ENEMY_PIXEL_BANK for a in game.ARCHETYPES)
assert len(game.BASTION_HULL) >= 12
assert len(game.PYRO_HEAD) >= 15 and len(game.PYRO_TORSO) >= 18
assert len(game.CARRIER_BODY) >= 12 and len(game.LEVIATHAN_HEAD) >= 16

pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled, audio.last_error
assert len(audio.weapon_sfx) == 10
assert all(len(v) == 3 for v in audio.weapon_sfx)
audio.set_volumes(.47, .63)
assert abs(audio.music_volume-.47) < .01
assert abs(audio.sfx_volume-.63) < .01

# Verify true stereo and the richer 16-bar arrangement on representative styles.
for stage_index in (0, 1, 2, 3, 8, 9):
    snd = audio.generate_stage_mix(stage_index, boss=False)
    assert snd is not None
    arr = pygame.sndarray.array(snd)
    assert arr.ndim == 2 and arr.shape[1] == 2
    assert np.any(arr[:, 0] != arr[:, 1]), f"stage {stage_index+1} collapsed to dual mono"
    assert len(arr) > int(game.AUDIO_RATE * 14)

# Boss arrangements must also remain stereo and distinct.
boss_sound = audio.generate_stage_mix(2, boss=True)
barr = pygame.sndarray.array(boss_sound)
assert np.any(barr[:,0] != barr[:,1])

g = game.Game()
assert g.player.unlocked == [True] + [False] * 9

# Draw all environments, enemy families, and bosses.
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

# Pyroclast now has authored creature anatomy rather than its old polygon-only body.
pyro = game.Boss(3)
pyro.intro = 0
pyro.draw(g.canvas)
assert pyro.rect().width >= 70 and pyro.rect().height >= 65

# Recovery cadence remains dependable.
g.reset_new_game(); g.begin_play(); g.player.health=30; g.health_drop_timer=0
before=len(g.pickups); g.update_play(1/60)
assert len(g.pickups) > before
assert any(p.kind in ("health","major_health") for p in g.pickups)

# Save/load uses a clean checkpoint and preserves campaign data.
g.stage=4; g.score=23456; g.player.lives=5; g.player.health=57
g.player.unlocked[:5]=[True]*5; g.player.weapon=4
assert g.save_game()
g.score=1; g.player.health=3; g.player.weapon=0
assert g.load_game()
assert g.stage==4 and g.score==23456 and g.player.lives==5
assert int(g.player.health)==57 and g.player.unlocked[4] and g.player.weapon==4

# Settings can be changed and persisted without changing native render size.
g.settings["music_volume"]=.4; g.settings["sfx_volume"]=.5; g.settings["effects"]=0
g.apply_settings()
assert g.canvas.get_size()==(game.NATIVE_W,game.NATIVE_H)
assert g.background.fx_level==0

# Developer test mode can jump directly to all boss content and never save.
g.activate_test_mode(); assert g.test_mode
g.test_stage=3; g.test_spawn_boss(3)
assert g.boss is not None and g.boss.stage==3
g.unlock_all_test_weapons(); assert all(g.player.unlocked)
g.test_refill(); assert g.player.lives>=9 and g.player.health==g.player.max_health
g.god_mode=True; g.player.invuln=0; hp=g.player.health; g.player.hit(500,g); assert g.player.health==hp
assert not g.save_game(), "test mode must not overwrite campaign save"

# Render all player-facing menu paths.
g.state="pause"; g.draw()
g.open_settings("pause"); g.draw()
g.open_test_menu("settings"); g.draw()

g.audio.stop_music()
pygame.quit()
print("OMEGA_V82_SOURCE_SMOKE_TEST_OK")
