"""Omega Horizon V8.1 source-level regression smoke test."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
import omega_horizon_shmup as game

assert game.BUILD_ID == "V8.1-ARTIST-PASS"
assert len(game.STAGES) == 10
assert len(game.WEAPON_NAMES) == 10
assert game.WEAPON_NAMES[4] == "HOMING ROCKET"
assert len({(s.theme, s.music_style, s.bpm, s.key) for s in game.STAGES}) == 10
assert len(game.PLAYER_PIXELS) >= 10
assert all(a in game.ENEMY_PIXEL_BANK for a in game.ARCHETYPES)
assert len(game.BASTION_HULL) >= 12

pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled, audio.last_error
assert len(audio.weapon_sfx) == 10
assert all(len(v) == 3 for v in audio.weapon_sfx)

# Verify actual left/right music data differs and the longer V8.1 arrangements
# render on several substantially different styles.
for stage_index in (0, 2, 3, 8, 9):
    snd = audio.generate_stage_mix(stage_index, boss=False)
    assert snd is not None
    arr = pygame.sndarray.array(snd)
    assert arr.ndim == 2 and arr.shape[1] == 2
    assert np.any(arr[:, 0] != arr[:, 1]), f"stage {stage_index+1} collapsed to dual mono"
    assert len(arr) > int(game.AUDIO_RATE * 10)

# Construct/draw all environments, enemy families, and bosses.
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

# Stage 3 readability regression: draw all four lava enemies over the actual
# cavern and verify each sprite region contains cool high-contrast pixels.
g.stage = 3
g.background.draw(g.canvas, 3)
for i, archetype in enumerate(game.ARCHETYPES):
    e = game.Enemy(90+i*35, 80+i*30, 3, 3000+i, i, archetype)
    e.draw(g.canvas)
    region = pygame.surfarray.array3d(g.canvas)[max(0,int(e.x)-12):min(256,int(e.x)+13), max(21,int(e.y)-12):min(224,int(e.y)+13)]
    # Cool rim palette has blue/green dominance unlike the lava background.
    assert np.any(region[:,:,2] > region[:,:,0]), f"lava {archetype} lacks cool contrast rim"

# Recovery cadence is configured on every stage and low-health gameplay can
# spawn a standard/major recovery item without requiring a flawless wave.
g.reset_new_game(); g.begin_play(); g.player.health=30; g.health_drop_timer=0
before=len(g.pickups); g.update_play(1/60)
assert len(g.pickups) > before
assert any(p.kind in ("health","major_health") for p in g.pickups)

# Campaign rewards still unlock all later weapons exactly once.
rewards = [p.reward_weapon for p in game.STAGES if p.reward_weapon is not None]
assert rewards == list(range(1, 10)), rewards

g.audio.stop_music()
pygame.quit()
print("OMEGA_V81_SOURCE_SMOKE_TEST_OK")
