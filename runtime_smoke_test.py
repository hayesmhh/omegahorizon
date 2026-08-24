"""GitHub Actions runtime smoke tests for Omega Horizon."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import omega_horizon_shmup as game

# Reproduce the Windows crash condition explicitly: stereo mixer.
pygame.mixer.quit()
pygame.mixer.init(frequency=game.AUDIO_RATE, size=-16, channels=2, buffer=512)
assert pygame.mixer.get_init()[2] == 2

audio = game.AudioSynth()
assert audio.enabled
assert audio.sfx.get("shot") is not None
assert audio.sfx.get("boom") is not None
assert audio.generate_stage_loop(0) is not None

# Exercise creation and one update/draw cycle using dummy SDL drivers.
g = game.Game()
g.reset_new_game()
g.begin_play()
g.update(1.0 / 60.0)
g.draw()
g.audio.stop_music()
pygame.quit()
print("OMEGA_RUNTIME_SMOKE_TEST_OK")
