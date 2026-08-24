"""Omega Horizon V8 source-level regression smoke test."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
import omega_horizon_shmup as game

assert game.BUILD_ID == "V8-STAGE-IDENTITY"
assert len(game.STAGES) == 10
assert len(game.WEAPON_NAMES) == 10
assert game.WEAPON_NAMES[4] == "HOMING ROCKET"
assert len({(s.theme, s.music_style, s.bpm, s.key) for s in game.STAGES}) == 10

pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled, audio.last_error
assert len(audio.weapon_sfx) == 10
assert all(len(v) == 3 for v in audio.weapon_sfx)
assert all(v[0] is not None for v in audio.weapon_sfx)

# Verify actual left/right music data differs on multiple composition styles.
for stage_index in (0, 3, 9):
    snd = audio.generate_stage_mix(stage_index, boss=False)
    assert snd is not None
    arr = pygame.sndarray.array(snd)
    assert arr.ndim == 2 and arr.shape[1] == 2
    assert np.any(arr[:, 0] != arr[:, 1]), f"stage {stage_index+1} collapsed to dual mono"

# Construct and draw all ten environments, all four archetypes, and all bosses.
g = game.Game()
assert g.player.unlocked == [True] + [False] * 9
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

# Verify campaign reward map yields all nine later weapons exactly once.
rewards = [p.reward_weapon for p in game.STAGES if p.reward_weapon is not None]
assert rewards == list(range(1, 10)), rewards

# Exercise one actual gameplay frame.
g.stage = 1
g.reset_new_game()
g.begin_play()
g.update(1.0 / 60.0)
g.draw()
g.audio.stop_music()
pygame.quit()
print("OMEGA_V8_SOURCE_SMOKE_TEST_OK")
