#!/usr/bin/env python3
"""
AXELAY-INSPIRED PSEUDO-3D SNES-STYLE SHMUP
==========================================
Single-file Pygame game with:
- 256x224 native canvas scaled with nearest-neighbor pixels.
- Software "Mode 7"-style floor casting / scanline perspective.
- Three-layer procedural parallax star/nebula sky.
- 10 stages with escalating enemy waves and bosses.
- 10 player weapons with distinct behavior.
- Procedural sprites only; no external art.
- Procedural synthwave soundtrack / SFX using NumPy + pygame.mixer.
- 5x7 bitmap HUD font.

Requires:
    pip install pygame numpy

Controls:
    Arrow keys / WASD : Move
    Space / Z          : Fire
    Q / E              : Previous / next weapon
    P                   : Pause
    Enter               : Start / restart / skip intro delay
    Esc                 : Quit
"""

import math
import random
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pygame

# ---------------------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------------------

NATIVE_W = 256
NATIVE_H = 224
SCALE = 4
WINDOW_W = NATIVE_W * SCALE
WINDOW_H = NATIVE_H * SCALE
FPS = 60
HORIZON_Y = 104
GROUND_H = NATIVE_H - HORIZON_Y
AUDIO_RATE = 44100

BLACK = (4, 5, 12)
WHITE = (236, 246, 255)
CYAN = (48, 224, 255)
TEAL = (0, 174, 199)
BLUE = (38, 92, 190)
NAVY = (10, 17, 50)
PURPLE = (145, 67, 214)
MAGENTA = (255, 66, 180)
RED = (255, 72, 72)
ORANGE = (255, 152, 58)
YELLOW = (255, 230, 88)
GREEN = (80, 240, 130)
DARK_GREEN = (20, 112, 74)
GRAY = (105, 119, 139)
DARK_GRAY = (48, 56, 76)

STAGE_TITLES = [
    "NEON HORIZON",
    "CHROME TEMPEST",
    "CRIMSON ORBIT",
    "PHANTOM CIRCUIT",
    "ION CITADEL",
    "VOID REACTOR",
    "STARFORGE GAUNTLET",
    "ECLIPSE ENGINE",
    "TERMINUS VEIL",
    "OMEGA TERMINUS",
]

# ---------------------------------------------------------------------------
# Tiny 5x7 bitmap font
# ---------------------------------------------------------------------------

FONT = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01111","10000","10000","10111","10001","10001","01110"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","10010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","11011","10001"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],
    ":": ["00000","00100","00100","00000","00100","00100","00000"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    "/": ["00001","00010","00100","01000","10000","00000","00000"],
    ".": ["00000","00000","00000","00000","00000","00100","00100"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    " ": ["00000"] * 7,
}

def draw_text(surface, text, x, y, color=WHITE, scale=1, shadow=False):
    """Draw a small fixed bitmap font. Unsupported glyphs become spaces."""
    text = str(text).upper()
    if shadow:
        draw_text(surface, text, x + scale, y + scale, (0, 0, 0), scale, False)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    pygame.draw.rect(
                        surface, color,
                        (cx + gx * scale, y + gy * scale, scale, scale)
                    )
        cx += 6 * scale

def text_width(text, scale=1):
    return max(0, len(str(text)) * 6 * scale - scale)

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def angle_to(dx, dy):
    return math.atan2(dy, dx)

# ---------------------------------------------------------------------------
# Procedural audio
# ---------------------------------------------------------------------------

class AudioSynth:
    """Lazy synthwave loop generator plus short arcade sound effects."""

    STAGE_MUSIC = [
        # bpm, root semitone, chord degrees, arp pattern
        (132, 0,  [0, 5, 3, 7], [0, 2, 1, 2, 0, 1, 2, 1]),
        (138, 2,  [0, 3, 5, 7], [0, 1, 2, 1, 0, 2, 1, 2]),
        (142, 5,  [0, 5, 7, 3], [0, 2, 0, 1, 2, 1, 0, 2]),
        (146, 7,  [0, 3, 8, 5], [0, 1, 2, 0, 2, 1, 2, 1]),
        (150, 9,  [0, 7, 5, 3], [0, 2, 1, 0, 1, 2, 0, 2]),
        (154, 1,  [0, 3, 6, 5], [0, 1, 0, 2, 1, 0, 2, 1]),
        (158, 4,  [0, 5, 3, 10],[0, 2, 1, 2, 1, 0, 2, 0]),
        (162, 6,  [0, 3, 5, 8], [0, 2, 1, 0, 2, 1, 2, 0]),
        (168, 8,  [0, 1, 6, 5], [0, 1, 2, 1, 2, 0, 1, 2]),
        (176, 0,  [0, 1, 6, 3], [0, 2, 1, 2, 0, 2, 1, 0]),
    ]

    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.music_cache = {}
        self.current = None
        self.sfx = {}
        if self.enabled:
            self._make_sfx()

    @staticmethod
    def midi_hz(note):
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    @staticmethod
    def osc(phase, kind):
        if kind == "square":
            return np.where(np.sin(phase) >= 0, 1.0, -1.0)
        if kind == "saw":
            return 2.0 * ((phase / (2 * np.pi)) % 1.0) - 1.0
        if kind == "tri":
            return 2.0 * np.abs(2.0 * ((phase / (2*np.pi)) % 1.0) - 1.0) - 1.0
        return np.sin(phase)

    def tone(self, freq, duration, kind="square", volume=0.35, attack=0.005, decay=0.08):
        n = max(1, int(AUDIO_RATE * duration))
        t = np.arange(n, dtype=np.float32) / AUDIO_RATE
        phase = 2 * np.pi * freq * t
        wave = self.osc(phase, kind)
        env = np.ones(n, dtype=np.float32)
        a = min(n, max(1, int(attack * AUDIO_RATE)))
        d = min(n, max(1, int(decay * AUDIO_RATE)))
        env[:a] *= np.linspace(0, 1, a, dtype=np.float32)
        env[-d:] *= np.linspace(1, 0, d, dtype=np.float32)
        return wave * env * volume

    def _sound_from_float(self, wave):
        if not self.enabled:
            return None

        # pygame.sndarray.make_sound() requires the NumPy array shape to
        # match the mixer channel count. Windows/SDL can initialize a stereo
        # mixer even when a mono preference was requested via pre_init().
        # Keep synthesis internally mono, then duplicate it into each actual
        # output channel at the final conversion step.
        wave = np.asarray(np.clip(wave, -1.0, 1.0), dtype=np.float32).reshape(-1)
        mono = np.ascontiguousarray((wave * 32767).astype(np.int16))

        mixer_info = pygame.mixer.get_init()
        channels = mixer_info[2] if mixer_info else 1
        if channels <= 1:
            arr = mono
        else:
            arr = np.ascontiguousarray(np.repeat(mono[:, None], channels, axis=1))

        return pygame.sndarray.make_sound(arr)

    def _make_sfx(self):
        # Player shot: quick falling square chirp
        dur = 0.07
        n = int(AUDIO_RATE * dur)
        t = np.arange(n) / AUDIO_RATE
        phase = 2*np.pi*(780*t - 260*t*t)
        self.sfx["shot"] = self._sound_from_float(
            0.22 * np.sign(np.sin(phase)) * np.linspace(1, 0, n)
        )
        # Explosion: filtered-ish noise envelope
        n = int(AUDIO_RATE * 0.22)
        noise = np.random.default_rng(4).uniform(-1, 1, n)
        env = np.linspace(1, 0, n) ** 2
        self.sfx["boom"] = self._sound_from_float(noise * env * 0.38)
        # Pickup
        parts = []
        for f in (660, 880, 1100):
            parts.append(self.tone(f, 0.055, "square", 0.18, decay=0.03))
        self.sfx["pickup"] = self._sound_from_float(np.concatenate(parts))
        # Player hit
        n = int(AUDIO_RATE * 0.16)
        t = np.arange(n) / AUDIO_RATE
        phase = 2*np.pi*(160*t + 110*t*t)
        self.sfx["hit"] = self._sound_from_float(
            np.sign(np.sin(phase)) * np.linspace(0.3, 0, n)
        )

    def play_sfx(self, key):
        if self.enabled and key in self.sfx:
            self.sfx[key].play()

    def generate_stage_loop(self, stage_index):
        """
        Generate an 8-bar mono synthwave loop.
        The composition changes BPM/root/chords/arp by stage.
        """
        if not self.enabled:
            return None
        if stage_index in self.music_cache:
            return self.music_cache[stage_index]

        bpm, root, degrees, arp = self.STAGE_MUSIC[stage_index]
        beats_per_bar = 4
        bars = 8
        beat = 60.0 / bpm
        total_duration = beat * beats_per_bar * bars
        total_n = int(total_duration * AUDIO_RATE)
        mix = np.zeros(total_n, dtype=np.float32)

        # Use A2-ish as roots, increasingly darker at high stages.
        base_midi = 45 + root
        minor_intervals = [0, 3, 7]
        rng = np.random.default_rng(100 + stage_index)

        def add(dst, start_s, signal):
            start = int(start_s * AUDIO_RATE)
            if start >= len(dst):
                return
            end = min(len(dst), start + len(signal))
            dst[start:end] += signal[:end-start]

        # Chord pads (triangle + quiet detuned saw).
        for bar in range(bars):
            deg = degrees[bar % len(degrees)]
            chord_root = base_midi + deg
            start = bar * beats_per_bar * beat
            duration = beats_per_bar * beat * 0.98
            for ci, interval in enumerate(minor_intervals):
                hz = self.midi_hz(chord_root + interval + 12)
                pad = self.tone(hz, duration, "tri", 0.065, attack=0.06, decay=0.18)
                add(mix, start, pad)
                if stage_index >= 5:
                    saw = self.tone(hz * 0.997, duration, "saw", 0.018, attack=0.05, decay=0.18)
                    add(mix, start, saw)

        # Bass eighth-notes.
        step = beat / 2
        for i in range(int(total_duration / step)):
            bar = int((i * step) / (beat * 4))
            deg = degrees[bar % len(degrees)]
            note = base_midi + deg + (12 if (i % 8 == 6 and stage_index < 5) else 0)
            hz = self.midi_hz(note)
            bass = self.tone(hz, step * 0.82, "square", 0.095, attack=0.003, decay=0.05)
            add(mix, i * step, bass)

        # Sixteenth arpeggiator.
        arp_step = beat / 4
        arp_intervals = [0, 3, 7]
        for i in range(int(total_duration / arp_step)):
            bar = int((i * arp_step) / (beat * 4))
            deg = degrees[bar % len(degrees)]
            sel = arp[i % len(arp)] % 3
            octave = 24 if (i + stage_index) % 8 < 4 else 12
            hz = self.midi_hz(base_midi + deg + arp_intervals[sel] + octave)
            sig = self.tone(hz, arp_step * 0.68, "square", 0.038 + stage_index*0.002,
                            attack=0.002, decay=0.025)
            add(mix, i * arp_step, sig)

        # Minimal synthesized drums: kick on 1/3, noise hat eighths, snare on 2/4.
        for beat_i in range(bars * 4):
            start = beat_i * beat
            # kick
            if beat_i % 2 == 0 or stage_index >= 7:
                n = int(AUDIO_RATE * 0.11)
                tt = np.arange(n) / AUDIO_RATE
                f0 = 95 + stage_index*3
                phase = 2*np.pi*(f0*tt - 210*tt*tt)
                kick = np.sin(phase) * np.linspace(0.18, 0, n)
                add(mix, start, kick)
            # snare
            if beat_i % 4 in (1, 3):
                n = int(AUDIO_RATE * 0.09)
                noise = rng.uniform(-1, 1, n) * np.linspace(0.10, 0, n)
                add(mix, start, noise)

        for i in range(bars * 8):
            start = i * beat / 2
            n = int(AUDIO_RATE * 0.035)
            hat = rng.uniform(-1, 1, n) * np.linspace(0.035, 0, n)
            add(mix, start, hat)

        # Soft saturation.
        mix = np.tanh(mix * 1.35) * 0.72
        sound = self._sound_from_float(mix)
        self.music_cache[stage_index] = sound
        return sound

    def play_stage(self, stage_index):
        if not self.enabled:
            return
        if self.current is not None:
            self.current.stop()
        self.current = self.generate_stage_loop(stage_index)
        if self.current:
            self.current.play(loops=-1)

    def stop_music(self):
        if self.current:
            self.current.stop()
        self.current = None

# ---------------------------------------------------------------------------
# Background / pseudo-Mode-7 renderer
# ---------------------------------------------------------------------------

class Background:
    """
    Procedural sky + software floor caster.

    For each screen scanline y below the horizon:
        depth = constant / (screen_y - horizon_y)
    Then x positions are projected into a looping mathematical texture.
    """

    def __init__(self):
        self.scroll = 0.0
        self.sky_scroll = 0.0
        self.texture = self._build_ground_texture(256)
        self.palette_surfaces = {}
        self.stars = []
        rng = random.Random(1337)
        # layer: (points, speed, brightness)
        for count, speed, brightness in [(42, .18, 90), (30, .42, 145), (20, .80, 220)]:
            pts = []
            for _ in range(count):
                pts.append((rng.randrange(NATIVE_W), rng.randrange(12, HORIZON_Y-3), rng.randrange(1, 3)))
            self.stars.append((pts, speed, brightness))
        self.nebula = []
        for i in range(14):
            y = 20 + i * 5 + rng.randrange(-2, 3)
            x = rng.randrange(0, NATIVE_W)
            ln = rng.randrange(14, 42)
            self.nebula.append((x, y, ln))

    @staticmethod
    def _build_ground_texture(size):
        yy, xx = np.indices((size, size))
        grid_major = ((xx % 32) < 2) | ((yy % 32) < 2)
        grid_minor = ((xx % 8) == 0) | ((yy % 8) == 0)
        checker = ((xx // 8 + yy // 8) & 1)
        noise = ((xx * 17 + yy * 31 + (xx ^ yy) * 7) & 15)
        tex = np.zeros((size, size, 3), dtype=np.uint8)
        tex[..., 0] = 10 + checker * 8 + noise // 5
        tex[..., 1] = 18 + checker * 12 + noise // 3
        tex[..., 2] = 35 + checker * 20 + noise
        tex[grid_minor] = (18, 62, 92)
        tex[grid_major] = (18, 128, 148)
        # Occasional magenta "energy lane" stripes.
        lanes = ((yy % 64) >= 29) & ((yy % 64) <= 31)
        tex[lanes] = (108, 34, 112)
        return tex

    def update(self, dt, stage):
        speed = 58.0 + stage * 5.5
        self.scroll = (self.scroll + speed * dt) % 256
        self.sky_scroll += dt * 22

    def draw_sky(self, surf, stage):
        # Dark gradient bands.
        for y in range(HORIZON_Y):
            t = y / max(1, HORIZON_Y-1)
            r = int(5 + 10*t + stage*0.35)
            g = int(7 + 8*t)
            b = int(20 + 30*t + (stage % 3)*4)
            pygame.draw.line(surf, (r, g, b), (0, y), (NATIVE_W, y))

        # Nebula streak layer.
        neb_speed = self.sky_scroll * 0.10
        for i, (x, y, ln) in enumerate(self.nebula):
            xx = int((x - neb_speed + i*7) % (NATIVE_W + 50)) - 25
            color = (32 + stage*2, 25, 64 + (i % 3)*12)
            pygame.draw.line(surf, color, (xx, y), (xx+ln, y), 1)
            if i % 3 == 0:
                pygame.draw.line(surf, (22, 20, 45), (xx+4, y+1), (xx+ln-4, y+1), 1)

        # Three star layers.
        for li, (pts, speed, brightness) in enumerate(self.stars):
            off = self.sky_scroll * speed
            for x, y, sz in pts:
                xx = int((x - off) % NATIVE_W)
                pulse = (brightness + int(20*math.sin((self.sky_scroll*0.8)+(x+y)*.04))) % 256
                col = (pulse//2, min(255,pulse), min(255, pulse+25))
                surf.set_at((xx, y), col)
                if li == 2 and sz > 1 and xx+1 < NATIVE_W:
                    surf.set_at((xx+1, y), col)

        # Horizon glow.
        pygame.draw.line(surf, (55, 56, 120), (0, HORIZON_Y-2), (NATIVE_W, HORIZON_Y-2))
        pygame.draw.line(surf, (80, 180, 200), (0, HORIZON_Y-1), (NATIVE_W, HORIZON_Y-1))

    def draw_ground(self, surf):
        # Render into NumPy (GROUND_H, W, 3), then blit.
        out = np.empty((GROUND_H, NATIVE_W, 3), dtype=np.uint8)
        xs = np.arange(NATIVE_W, dtype=np.float32) - NATIVE_W / 2
        texmask = self.texture.shape[0] - 1

        for row in range(GROUND_H):
            screen_y = HORIZON_Y + row
            dy = max(1.0, screen_y - HORIZON_Y)
            depth = 92.0 / dy  # requested inverse-depth relation
            distance = depth * 42.0
            # Camera moves in +texture-X, making ground appear to scroll left.
            world_x = self.scroll * 1.7 + distance + xs * depth * 0.72
            world_y = self.scroll * 0.23 + distance * 0.60 + xs * depth * 0.08
            tx = np.asarray(world_x, dtype=np.int32) & texmask
            ty = np.asarray(world_y, dtype=np.int32) & texmask
            line = self.texture[ty, tx].astype(np.float32)

            # Distance fog toward the horizon.
            near = row / max(1, GROUND_H-1)
            fog = 0.34 + 0.66 * (near ** 0.42)
            line *= fog
            out[row] = np.clip(line, 0, 255).astype(np.uint8)

        # pygame.surfarray array convention is (W,H,3).
        floor_surf = pygame.surfarray.make_surface(np.transpose(out, (1, 0, 2)))
        surf.blit(floor_surf, (0, HORIZON_Y))

    def draw(self, surf, stage):
        self.draw_sky(surf, stage)
        self.draw_ground(surf)

# ---------------------------------------------------------------------------
# Bullets and effects
# ---------------------------------------------------------------------------

@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    damage: float
    owner: str
    kind: str = "normal"
    radius: float = 2.0
    life: float = 3.0
    pierce: int = 0
    age: float = 0.0
    phase: float = 0.0
    split: bool = False
    splash: float = 0.0
    target: Optional[object] = None

    def update(self, dt, game):
        self.age += dt
        self.life -= dt

        if self.kind == "wave":
            self.x += self.vx * dt
            self.y += self.vy * dt + math.sin(self.age * 18 + self.phase) * 42 * dt
        elif self.kind == "homing":
            target = game.nearest_enemy(self.x, self.y)
            if target is not None:
                desired = angle_to(target.x - self.x, target.y - self.y)
                current = math.atan2(self.vy, self.vx)
                delta = (desired - current + math.pi) % (2*math.pi) - math.pi
                current += clamp(delta, -2.5*dt, 2.5*dt)
                speed = math.hypot(self.vx, self.vy)
                self.vx = math.cos(current) * speed
                self.vy = math.sin(current) * speed
            self.x += self.vx * dt
            self.y += self.vy * dt
        elif self.kind == "sonic":
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.radius = min(14, self.radius + 5.0 * dt)
        elif self.kind == "flak":
            self.x += self.vx * dt
            self.y += self.vy * dt
            if not self.split and self.age > 0.30:
                self.split = True
                self.life = 0
                for a in (-0.38, 0.0, 0.38):
                    speed = 125
                    game.player_bullets.append(Bullet(
                        self.x, self.y,
                        math.cos(a)*speed, math.sin(a)*speed,
                        self.damage*0.65, "player", "fragment", 1.5, 0.75
                    ))
        else:
            self.x += self.vx * dt
            self.y += self.vy * dt

    def alive(self):
        return (
            self.life > 0
            and -40 <= self.x <= NATIVE_W + 60
            and -40 <= self.y <= NATIVE_H + 40
        )

    def rect(self):
        if self.kind == "laser":
            return pygame.Rect(int(self.x), int(self.y-1), 34, 3)
        r = max(2, int(self.radius))
        return pygame.Rect(int(self.x-r), int(self.y-r), r*2, r*2)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if self.owner == "enemy":
            if self.kind == "tracking":
                pygame.draw.circle(surf, ORANGE, (x, y), int(self.radius)+1)
                pygame.draw.circle(surf, RED, (x, y), max(1,int(self.radius)-1))
            else:
                pygame.draw.circle(surf, RED, (x, y), int(self.radius)+1)
                pygame.draw.circle(surf, YELLOW, (x, y), max(1,int(self.radius)-1))
            return

        if self.kind == "laser":
            pygame.draw.rect(surf, (120, 255, 255), (x, y-1, 34, 3))
            pygame.draw.line(surf, WHITE, (x, y), (x+33, y))
        elif self.kind == "wave":
            pygame.draw.circle(surf, CYAN, (x, y), 4)
            pygame.draw.circle(surf, WHITE, (x+1, y), 2)
        elif self.kind == "grenade":
            pygame.draw.circle(surf, ORANGE, (x, y), 5)
            pygame.draw.circle(surf, YELLOW, (x-1, y-1), 3)
        elif self.kind == "flak":
            pygame.draw.rect(surf, (255, 210, 100), (x-3,y-2,6,4))
            pygame.draw.rect(surf, WHITE, (x-2,y-1,3,2))
        elif self.kind == "fragment":
            pygame.draw.circle(surf, YELLOW, (x, y), 1)
        elif self.kind == "homing":
            pygame.draw.polygon(surf, MAGENTA, [(x+5,y),(x-3,y-3),(x-2,y),(x-3,y+3)])
            pygame.draw.line(surf, YELLOW, (x-4,y), (x-7,y))
        elif self.kind == "sonic":
            pygame.draw.circle(surf, (150, 238, 255), (x, y), int(self.radius), 1)
            if self.radius > 7:
                pygame.draw.circle(surf, (80, 140, 255), (x, y), int(self.radius)-3, 1)
        elif self.kind == "micro":
            pygame.draw.line(surf, GREEN, (x-2,y), (x+3,y))
        else:
            pygame.draw.rect(surf, CYAN, (x-3,y-2,7,4))
            pygame.draw.rect(surf, WHITE, (x+1,y-1,3,2))

@dataclass
class Explosion:
    x: float
    y: float
    life: float = 0.35
    max_life: float = 0.35
    size: float = 12.0
    green: bool = False

    def update(self, dt):
        self.life -= dt

    def draw(self, surf):
        t = 1.0 - max(0, self.life) / self.max_life
        r = max(1, int(self.size * t))
        color = GREEN if self.green else (YELLOW if t < .45 else ORANGE)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), r, 1)
        if r > 3:
            pygame.draw.circle(surf, WHITE if not self.green else (180,255,200),
                               (int(self.x), int(self.y)), max(1,r//2), 1)

@dataclass
class HealthPickup:
    x: float
    y: float
    vx: float = -36
    phase: float = 0.0
    life: float = 8.0

    def update(self, dt):
        self.x += self.vx * dt
        self.phase += dt
        self.life -= dt

    def rect(self):
        return pygame.Rect(int(self.x-5), int(self.y-5), 10, 10)

    def draw(self, surf):
        flash = int(self.phase * 10) % 2 == 0
        col = (115,255,145) if flash else (20,180,90)
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surf, (8,42,24), (x-6,y-6,12,12))
        pygame.draw.rect(surf, col, (x-2,y-5,4,10))
        pygame.draw.rect(surf, col, (x-5,y-2,10,4))
        pygame.draw.rect(surf, WHITE if flash else GREEN, (x-1,y-4,2,8))

# ---------------------------------------------------------------------------
# Weapon system
# ---------------------------------------------------------------------------

class Weapon:
    NAMES = [
        "PLASMA REPEATER",
        "SPREAD VULCAN",
        "WAVE BEAM",
        "LASER LANCE",
        "PHOTON GRENADE",
        "REAR GUARD",
        "ORBITAL ORBITERS",
        "FLAK CANNON",
        "HOMOR ROCKET",
        "SONIC RING",
    ]
    COOLDOWNS = [0.095, 0.17, 0.15, 0.22, 0.38, 0.16, 0.18, 0.26, 0.42, 0.34]

    @classmethod
    def fire(cls, index, player, game):
        x = player.x + 9
        y = player.y
        bullets = game.player_bullets

        if index == 0:  # Plasma Repeater
            bullets.append(Bullet(x, y, 175, 0, 7, "player", "normal", 3, 1.8))

        elif index == 1:  # Spread Vulcan
            for vy in (-52, 0, 52):
                bullets.append(Bullet(x, y, 150, vy, 5, "player", "normal", 2, 1.5))

        elif index == 2:  # Wave Beam
            bullets.append(Bullet(x, y, 135, 0, 9, "player", "wave", 4, 2.0,
                                  phase=player.weapon_phase))
            player.weapon_phase += 1.3

        elif index == 3:  # Laser Lance
            bullets.append(Bullet(x, y, 170, 0, 16, "player", "laser", 2, 0.58, pierce=4))

        elif index == 4:  # Photon Grenade
            bullets.append(Bullet(x, y, 82, 0, 28, "player", "grenade", 5, 2.6, splash=24))

        elif index == 5:  # Rear Guard
            bullets.append(Bullet(x, y, 150, 0, 7, "player", "normal", 2, 1.7))
            bullets.append(Bullet(player.x-8, y, -140, 0, 7, "player", "normal", 2, 1.0))

        elif index == 6:  # Orbital Orbiters
            # Main ship fires lightly; orbiters add micro-lasers separately.
            bullets.append(Bullet(x, y, 140, 0, 5, "player", "normal", 2, 1.5))
            for ox, oy in player.orbiter_positions():
                bullets.append(Bullet(ox+3, oy, 165, 0, 3.5, "player", "micro", 1.5, 1.3))

        elif index == 7:  # Flak Cannon
            bullets.append(Bullet(x, y, 118, 0, 9, "player", "flak", 3, 1.4))

        elif index == 8:  # Homor Rocket (name preserved from specification)
            bullets.append(Bullet(x, y, 104, 0, 22, "player", "homing", 3, 3.1))

        elif index == 9:  # Sonic Ring
            bullets.append(Bullet(x, y, 72, 0, 14, "player", "sonic", 6, 3.0, pierce=2))

        game.audio.play_sfx("shot")

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.x = 42.0
        self.y = 136.0
        self.speed = 104.0
        self.max_health = 100
        self.health = 100
        self.lives = 3
        self.weapon = 0
        self.fire_timer = 0.0
        self.invuln = 1.2
        self.weapon_phase = 0.0
        self.orbit_phase = 0.0

    def reset_position(self):
        self.x, self.y = 42.0, 136.0
        self.invuln = 1.6

    def rect(self):
        return pygame.Rect(int(self.x-5), int(self.y-4), 11, 9)

    def orbiter_positions(self):
        pts = []
        for a in (self.orbit_phase, self.orbit_phase + math.pi):
            pts.append((self.x + math.cos(a)*12, self.y + math.sin(a)*9))
        return pts

    def update(self, dt, keys, game):
        dx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - \
             (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        dy = (1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0) - \
             (1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        if dx or dy:
            mag = math.hypot(dx, dy)
            dx, dy = dx/mag, dy/mag
        self.x = clamp(self.x + dx*self.speed*dt, 9, NATIVE_W-15)
        self.y = clamp(self.y + dy*self.speed*dt, 24, NATIVE_H-10)

        self.fire_timer -= dt
        self.invuln = max(0, self.invuln-dt)
        self.orbit_phase = (self.orbit_phase + dt*4.2) % (math.pi*2)

        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.fire_timer <= 0:
            Weapon.fire(self.weapon, self, game)
            self.fire_timer = Weapon.COOLDOWNS[self.weapon]

    def hit(self, damage, game):
        if self.invuln > 0:
            return
        self.health -= damage
        self.invuln = 0.85
        game.audio.play_sfx("hit")
        game.explosions.append(Explosion(self.x, self.y, .24, .24, 9))
        if self.health <= 0:
            self.lives -= 1
            if self.lives <= 0:
                game.game_over()
            else:
                self.health = self.max_health
                self.reset_position()
                game.enemy_bullets.clear()

    def draw(self, surf):
        # Blink while invulnerable.
        if self.invuln > 0 and int(self.invuln * 12) % 2 == 0:
            return
        x, y = int(self.x), int(self.y)

        # Exhaust flame.
        flame = 5 + (pygame.time.get_ticks() // 60) % 3
        pygame.draw.polygon(surf, ORANGE, [(x-7,y-2),(x-7-flame,y),(x-7,y+2)])
        pygame.draw.line(surf, YELLOW, (x-7,y), (x-11,y))

        # Main ship: faceted 16-bit silhouette.
        pygame.draw.polygon(surf, (36,74,124),
                            [(x-7,y-4),(x+2,y-5),(x+9,y),(x+2,y+5),(x-7,y+4)])
        pygame.draw.polygon(surf, (78,190,218),
                            [(x-3,y-3),(x+4,y-2),(x+8,y),(x+3,y+1),(x-3,y+1)])
        pygame.draw.polygon(surf, (30,48,92),
                            [(x-4,y+1),(x+2,y+5),(x-6,y+6),(x-9,y+2)])
        pygame.draw.rect(surf, WHITE, (x+2,y-2,3,2))
        pygame.draw.rect(surf, (130,235,255), (x-1,y-3,3,2))

        # Dithered armor pixels.
        for px, py in [(-5,-2),(-3,2),(0,3),(1,-4)]:
            surf.set_at((x+px,y+py), (130,150,180))

        if self.weapon == 6:
            for ox, oy in self.orbiter_positions():
                ox, oy = int(ox), int(oy)
                pygame.draw.circle(surf, (70,230,210), (ox,oy), 3)
                pygame.draw.circle(surf, WHITE, (ox,oy), 1)

# ---------------------------------------------------------------------------
# Enemies and waves
# ---------------------------------------------------------------------------

class Enemy:
    def __init__(self, x, y, stage, wave_id, slot, formation="sine"):
        self.x = float(x)
        self.base_y = float(y)
        self.y = float(y)
        self.stage = stage
        self.wave_id = wave_id
        self.slot = slot
        self.formation = formation
        self.age = slot * 0.16
        self.speed = 46 + stage*3.3 + (slot%3)*2
        self.health = 14 + stage*4.5
        self.max_health = self.health
        self.phase = slot * 0.78
        self.fire_timer = 0.6 + (slot % 4)*0.28 + random.random()*0.8
        self.dead = False
        self.escaped = False

    def rect(self):
        return pygame.Rect(int(self.x-6), int(self.y-5), 12, 10)

    def update(self, dt, game):
        self.age += dt
        self.x -= self.speed * dt

        amp = 10 + min(7, self.stage)
        if self.formation == "tight":
            amp *= 0.55
            self.y = self.base_y + math.sin(self.age*3.2 + self.phase)*amp
        elif self.formation == "chevron":
            self.y = self.base_y + math.sin(self.age*2.1 + self.phase)*amp*0.75
        elif self.formation == "column":
            self.y = self.base_y + math.sin(self.age*3.6 + self.phase)*5
        else:
            self.y = self.base_y + math.sin(self.age*2.5 + self.phase)*amp

        self.fire_timer -= dt
        if self.x < NATIVE_W-20 and self.fire_timer <= 0 and game.state == "play":
            self.fire_timer = max(0.55, 1.9 - self.stage*0.09) + random.random()*0.55
            # Increasing chance of aimed fire.
            if random.random() < 0.28 + self.stage*0.045:
                ang = angle_to(game.player.x-self.x, game.player.y-self.y)
                spd = 58 + self.stage*5
                game.enemy_bullets.append(Bullet(
                    self.x-4, self.y, math.cos(ang)*spd, math.sin(ang)*spd,
                    9, "enemy", "normal", 2.2, 5
                ))

        if self.x < -14:
            self.dead = True
            self.escaped = True
            game.wave_enemy_escaped(self.wave_id)

    def hit(self, damage, game, hit_x=None, hit_y=None):
        if self.dead:
            return False
        self.health -= damage
        if self.health <= 0:
            self.dead = True
            game.score += 90 + self.stage*25
            game.audio.play_sfx("boom")
            game.explosions.append(Explosion(self.x, self.y, .32, .32, 12))
            game.wave_enemy_destroyed(self.wave_id, self.x, self.y)
            return True
        return False

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        # Procedural "bat fighter".
        main = (180, 45 + self.stage*8 % 160, 100 + self.stage*9 % 140)
        pygame.draw.polygon(surf, (45,34,72),
                            [(x-6,y),(x-1,y-5),(x+6,y-3),(x+7,y+3),(x-1,y+5)])
        pygame.draw.polygon(surf, main,
                            [(x-5,y),(x+2,y-3),(x+6,y),(x+2,y+3)])
        pygame.draw.rect(surf, (250,160,90), (x-4,y-1,3,2))
        # Wing pixel dither.
        surf.set_at((x,y-4), (220,180,220))
        surf.set_at((x+2,y+4), (110,90,140))

# ---------------------------------------------------------------------------
# Bosses
# ---------------------------------------------------------------------------

class Boss:
    def __init__(self, stage):
        self.stage = stage
        self.x = 215.0
        self.y = 118.0
        self.age = 0.0
        self.intro = 1.8
        self.radius = 25 if stage < 10 else 34
        self.max_health = 420 + stage*155 if stage < 10 else 2400
        self.health = float(self.max_health)
        self.burst_timer = 1.0
        self.ring_timer = 2.5
        self.track_timer = 1.6
        self.phase = 1
        self.dead = False

    def rect(self):
        r = self.radius
        return pygame.Rect(int(self.x-r), int(self.y-r), r*2, r*2)

    def hit(self, damage, game):
        if self.intro > 0 or self.dead:
            return False
        self.health -= damage
        if self.health <= 0:
            self.dead = True
            game.score += 5000 + self.stage*1500
            game.audio.play_sfx("boom")
            for i in range(18 if self.stage < 10 else 36):
                a = i * (math.tau/(18 if self.stage<10 else 36))
                rr = random.uniform(2, self.radius)
                game.explosions.append(Explosion(
                    self.x+math.cos(a)*rr,
                    self.y+math.sin(a)*rr,
                    .3+random.random()*.5, .8, 8+random.random()*14
                ))
            return True
        return False

    def fire_aimed(self, game, count=3, spread=0.16, speed=None):
        speed = speed or (76 + self.stage*5)
        base = angle_to(game.player.x-self.x, game.player.y-self.y)
        mid = (count-1)/2
        for i in range(count):
            a = base + (i-mid)*spread
            game.enemy_bullets.append(Bullet(
                self.x-self.radius*.55, self.y,
                math.cos(a)*speed, math.sin(a)*speed,
                11, "enemy", "normal", 2.5, 6
            ))

    def fire_ring(self, game, count=12, speed=None, offset=0.0):
        speed = speed or (55 + self.stage*4)
        for i in range(count):
            a = offset + i*(math.tau/count)
            game.enemy_bullets.append(Bullet(
                self.x, self.y,
                math.cos(a)*speed, math.sin(a)*speed,
                9, "enemy", "normal", 2.2, 6
            ))

    def fire_tracking(self, game, count=2):
        for i in range(count):
            a = angle_to(game.player.x-self.x, game.player.y-self.y) + (i-(count-1)/2)*0.22
            spd = 55 + self.stage*3
            game.enemy_bullets.append(Bullet(
                self.x-8, self.y, math.cos(a)*spd, math.sin(a)*spd,
                12, "enemy", "tracking", 3, 8
            ))

    def update(self, dt, game):
        self.age += dt
        if self.intro > 0:
            self.intro -= dt
            self.x += (191 - self.x) * min(1, dt*2.4)
            return

        if self.stage == 10:
            hp_ratio = self.health / self.max_health
            self.phase = 1 if hp_ratio > .66 else 2 if hp_ratio > .33 else 3
            if self.phase == 1:
                self.y = 112 + math.sin(self.age*1.45)*52
                target_x = 194
            elif self.phase == 2:
                self.y = 112 + math.sin(self.age*2.1)*62
                target_x = 185 + math.sin(self.age*.7)*12
            else:
                self.y = 112 + math.sin(self.age*3.0)*72
                target_x = 177 + math.sin(self.age*1.4)*16
            self.x += (target_x-self.x)*dt*1.7
        else:
            self.y = 116 + math.sin(self.age*(1.15+self.stage*.055))*45
            self.x += (192-self.x)*dt*1.8

        self.burst_timer -= dt
        self.ring_timer -= dt
        self.track_timer -= dt

        if self.stage < 10:
            if self.burst_timer <= 0:
                self.burst_timer = max(.42, 1.18-self.stage*.055)
                self.fire_aimed(game, 3 + (1 if self.stage >= 6 else 0), .13)
            if self.ring_timer <= 0:
                self.ring_timer = max(1.15, 2.8-self.stage*.12)
                self.fire_ring(game, 10 + self.stage, offset=self.age*.35)
            if self.stage >= 5 and self.track_timer <= 0:
                self.track_timer = 2.5 - self.stage*.08
                self.fire_tracking(game, 1)
        else:
            if self.phase == 1:
                if self.burst_timer <= 0:
                    self.burst_timer = .52
                    self.fire_aimed(game, 5, .11, 112)
                if self.ring_timer <= 0:
                    self.ring_timer = 1.65
                    self.fire_ring(game, 18, 78, self.age*.55)
            elif self.phase == 2:
                if self.burst_timer <= 0:
                    self.burst_timer = .36
                    self.fire_aimed(game, 7, .095, 128)
                if self.ring_timer <= 0:
                    self.ring_timer = 1.05
                    self.fire_ring(game, 24, 86, self.age*.9)
                if self.track_timer <= 0:
                    self.track_timer = 1.45
                    self.fire_tracking(game, 3)
            else:
                if self.burst_timer <= 0:
                    self.burst_timer = .24
                    self.fire_aimed(game, 9, .08, 145)
                if self.ring_timer <= 0:
                    self.ring_timer = .72
                    self.fire_ring(game, 30, 96, self.age*1.2)
                    # Counter-rotating second ring.
                    self.fire_ring(game, 15, 72, -self.age*.8)
                if self.track_timer <= 0:
                    self.track_timer = .88
                    self.fire_tracking(game, 4)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        r = self.radius

        # Multi-tile procedural boss: stacked rectangles/polygons emulate
        # sprite tiles and dithered 16-bit shading.
        pygame.draw.rect(surf, (28,24,54), (x-r, y-r+5, r*2, r*2-10))
        pygame.draw.rect(surf, (70,45,104), (x-r+4, y-r+1, r*2-8, r*2-2))
        pygame.draw.polygon(surf, (120,50,120),
                            [(x-r,y-10),(x-r-9,y),(x-r,y+10),(x-r+8,y)])
        pygame.draw.polygon(surf, (120,50,120),
                            [(x+r,y-10),(x+r+9,y),(x+r,y+10),(x+r-8,y)])
        pygame.draw.rect(surf, (35,75,120), (x-r+6,y-r+4, r*2-12, 7))
        pygame.draw.rect(surf, (35,75,120), (x-r+6,y+r-11, r*2-12, 7))

        # Central reactor.
        core_r = 8 if self.stage < 10 else 12
        core_col = RED if self.stage == 10 and self.phase == 3 else MAGENTA
        pygame.draw.circle(surf, (32,16,48), (x-7,y), core_r+4)
        pygame.draw.circle(surf, core_col, (x-7,y), core_r)
        pygame.draw.circle(surf, WHITE, (x-9,y-2), max(2,core_r//3))

        # "Turret" tiles.
        for oy in (-r+9, r-9):
            pygame.draw.rect(surf, DARK_GRAY, (x-r-4,y+oy-3,11,6))
            pygame.draw.rect(surf, ORANGE, (x-r-6,y+oy-1,4,2))
        for oy in (-12, 12):
            pygame.draw.rect(surf, (90,100,145), (x+r-8,y+oy-4,9,8))
            pygame.draw.rect(surf, CYAN, (x+r-5,y+oy-1,3,2))

        # Dithered highlights.
        for yy in range(y-r+5, y+r-5, 5):
            for xx in range(x-r+6, x+r-6, 6):
                if ((xx+yy)//2) % 2 == 0:
                    if 0 <= xx < NATIVE_W and 0 <= yy < NATIVE_H:
                        surf.set_at((xx,yy), (108,82,138))

        if self.stage == 10:
            # Tower extensions.
            pygame.draw.rect(surf, (50,44,88), (x+8,y-r-16,10,18))
            pygame.draw.rect(surf, (50,44,88), (x+8,y+r-2,10,18))
            pygame.draw.rect(surf, RED, (x+11,y-r-13,4,6))
            pygame.draw.rect(surf, RED, (x+11,y+r+7,4,6))

# ---------------------------------------------------------------------------
# Main game state machine
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        pygame.mixer.pre_init(AUDIO_RATE, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("OMEGA HORIZON - 16 BIT PSEUDO 3D SHMUP")
        self.window = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.canvas = pygame.Surface((NATIVE_W, NATIVE_H)).convert()
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = Background()
        self.audio = AudioSynth()
        self.player = Player()

        self.stage = 1
        self.state = "title"
        self.state_timer = 0.0
        self.stage_distance = 0.0
        self.stage_goal = self.stage_distance_goal()

        self.score = 0
        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.pickups = []
        self.explosions = []
        self.boss = None

        self.wave_serial = 0
        self.waves = {}
        self.spawn_timer = 1.0
        self.boss_warning = 0.0
        self.shake = 0.0

    def stage_distance_goal(self):
        return 2600 + (self.stage-1)*260

    def reset_new_game(self):
        self.player = Player()
        self.score = 0
        self.stage = 1
        self.start_stage(1)

    def start_stage(self, stage):
        self.stage = stage
        self.stage_distance = 0.0
        self.stage_goal = self.stage_distance_goal()
        self.enemies.clear()
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.pickups.clear()
        self.explosions.clear()
        self.boss = None
        self.waves.clear()
        self.spawn_timer = 1.1
        self.state = "stage_intro"
        self.state_timer = 2.4
        self.boss_warning = 0
        self.audio.play_stage(stage-1)

    def begin_play(self):
        self.state = "play"
        self.state_timer = 0

    def game_over(self):
        self.state = "game_over"
        self.state_timer = 0
        self.audio.stop_music()

    def win_game(self):
        self.state = "victory"
        self.state_timer = 0
        self.audio.stop_music()

    def boss_defeated(self):
        self.enemy_bullets.clear()
        self.state = "stage_clear"
        self.state_timer = 2.6

    def nearest_enemy(self, x, y):
        candidates = [e for e in self.enemies if not e.dead]
        if self.boss and not self.boss.dead and self.boss.intro <= 0:
            candidates.append(self.boss)
        if not candidates:
            return None
        return min(candidates, key=lambda e: (e.x-x)**2 + (e.y-y)**2)

    # ------------------------- wave bookkeeping -------------------------

    def spawn_wave(self):
        if self.boss is not None:
            return

        self.wave_serial += 1
        wid = self.wave_serial

        # Linear stage scaling plus increasingly tight formations.
        count = min(9, 4 + self.stage//2 + random.randint(0,2))
        variants = ["sine"]
        if self.stage >= 3:
            variants.append("chevron")
        if self.stage >= 5:
            variants.append("tight")
        if self.stage >= 7:
            variants.append("column")
        formation = random.choice(variants)

        self.waves[wid] = {
            "total": count, "kills": 0, "failed": False, "last": (NATIVE_W-20,112)
        }

        center = random.randint(55, 172)
        spacing = max(11, 20 - self.stage)
        for i in range(count):
            if formation == "chevron":
                yy = center + (abs(i-(count-1)/2))*spacing*0.65 * (-1 if i%2 else 1)
            elif formation == "column":
                yy = center + (i-(count-1)/2)*max(8,spacing*.7)
            elif formation == "tight":
                yy = center + (i-(count-1)/2)*max(6,spacing*.58)
            else:
                yy = center + math.sin(i*1.3)*spacing
            yy = clamp(yy, 35, NATIVE_H-22)
            xx = NATIVE_W + 12 + i*11
            self.enemies.append(Enemy(xx, yy, self.stage, wid, i, formation))

    def wave_enemy_destroyed(self, wid, x, y):
        data = self.waves.get(wid)
        if not data:
            return
        data["kills"] += 1
        data["last"] = (x,y)
        if data["kills"] >= data["total"] and not data["failed"]:
            self.pickups.append(HealthPickup(x, y))
            del self.waves[wid]

    def wave_enemy_escaped(self, wid):
        data = self.waves.get(wid)
        if data:
            data["failed"] = True

    # ------------------------- collisions ------------------------------

    @staticmethod
    def circle_rect_collision(b, rect):
        cx = clamp(b.x, rect.left, rect.right)
        cy = clamp(b.y, rect.top, rect.bottom)
        return (b.x-cx)**2 + (b.y-cy)**2 <= b.radius**2

    def splash_damage(self, x, y, radius, damage):
        for e in self.enemies:
            if not e.dead and (e.x-x)**2 + (e.y-y)**2 <= radius**2:
                e.hit(damage, self)
        if self.boss and not self.boss.dead:
            if (self.boss.x-x)**2 + (self.boss.y-y)**2 <= (radius+self.boss.radius)**2:
                self.boss.hit(damage*.55, self)
        self.explosions.append(Explosion(x,y,.28,.28,radius*.75))

    def handle_collisions(self):
        # Player bullets vs enemies and boss.
        for b in list(self.player_bullets):
            if b.life <= 0:
                continue
            hit_something = False

            for e in self.enemies:
                if e.dead:
                    continue
                if b.rect().colliderect(e.rect()):
                    e.hit(b.damage, self, b.x, b.y)
                    hit_something = True
                    if b.kind == "grenade":
                        self.splash_damage(b.x,b.y,b.splash,b.damage*.55)
                    if b.pierce > 0:
                        b.pierce -= 1
                    else:
                        b.life = 0
                    break

            if b.life > 0 and self.boss and not self.boss.dead and self.boss.intro <= 0:
                if b.rect().colliderect(self.boss.rect()):
                    self.boss.hit(b.damage, self)
                    hit_something = True
                    if b.kind == "grenade":
                        self.splash_damage(b.x,b.y,b.splash,b.damage*.45)
                    if b.pierce > 0:
                        b.pierce -= 1
                    else:
                        b.life = 0

        # Enemy bullets vs player.
        pr = self.player.rect()
        for b in self.enemy_bullets:
            if b.life > 0 and self.circle_rect_collision(b, pr):
                b.life = 0
                self.player.hit(b.damage, self)

        # Enemy bodies vs player.
        for e in self.enemies:
            if not e.dead and e.rect().colliderect(pr):
                e.dead = True
                self.wave_enemy_escaped(e.wave_id)
                self.player.hit(18, self)

        # Boss body vs player.
        if self.boss and not self.boss.dead and self.boss.intro <= 0:
            if self.boss.rect().colliderect(pr):
                self.player.hit(25, self)

        # Health pickups.
        for p in list(self.pickups):
            if p.rect().colliderect(pr):
                self.player.health = min(self.player.max_health, self.player.health + 30)
                p.life = 0
                self.audio.play_sfx("pickup")
                self.explosions.append(Explosion(p.x,p.y,.30,.30,12,True))

    # ------------------------- update ----------------------------------

    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self)
        self.background.update(dt, self.stage)

        if self.boss is None:
            # Distance progression and linearly increasing spawn pressure.
            self.stage_distance += dt * (78 + self.stage*4)
            self.spawn_timer -= dt
            spawn_interval = max(0.62, 2.25 - (self.stage-1)*0.13)
            if self.spawn_timer <= 0 and self.stage_distance < self.stage_goal:
                self.spawn_wave()
                self.spawn_timer = spawn_interval

            if self.stage_distance >= self.stage_goal:
                self.boss_warning += dt
                if self.boss_warning > 1.35:
                    self.enemies.clear()
                    self.waves.clear()
                    self.boss = Boss(self.stage)
                    self.enemy_bullets.clear()
        else:
            self.boss.update(dt, self)
            if self.boss.dead:
                self.boss_defeated()

        for e in self.enemies:
            if not e.dead:
                e.update(dt, self)

        for b in self.player_bullets:
            b.update(dt, self)
        for b in self.enemy_bullets:
            # Tracking enemy shots get light homing behavior.
            if b.kind == "tracking":
                desired = angle_to(self.player.x-b.x, self.player.y-b.y)
                cur = math.atan2(b.vy,b.vx)
                delta = (desired-cur+math.pi)%(2*math.pi)-math.pi
                cur += clamp(delta, -1.1*dt, 1.1*dt)
                sp = math.hypot(b.vx,b.vy)
                b.vx,b.vy = math.cos(cur)*sp, math.sin(cur)*sp
            b.update(dt, self)

        for p in self.pickups:
            p.update(dt)
        for ex in self.explosions:
            ex.update(dt)

        self.handle_collisions()

        self.enemies = [e for e in self.enemies if not e.dead]
        self.player_bullets = [b for b in self.player_bullets if b.alive()]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive()]
        self.pickups = [p for p in self.pickups if p.life > 0 and p.x > -10]
        self.explosions = [e for e in self.explosions if e.life > 0]

    def update(self, dt):
        if self.state == "play":
            self.update_play(dt)
        else:
            self.background.update(dt*0.45, self.stage)
            for ex in self.explosions:
                ex.update(dt)
            self.explosions = [e for e in self.explosions if e.life > 0]

            if self.state == "stage_intro":
                self.state_timer -= dt
                if self.state_timer <= 0:
                    self.begin_play()
            elif self.state == "stage_clear":
                self.state_timer -= dt
                if self.state_timer <= 0:
                    if self.stage >= 10:
                        self.win_game()
                    else:
                        self.start_stage(self.stage+1)

    # ------------------------- input -----------------------------------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

            elif self.state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_new_game()

            elif self.state in ("game_over","victory") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_new_game()

            elif self.state == "stage_intro" and event.key == pygame.K_RETURN:
                self.begin_play()

            elif self.state == "play":
                if event.key == pygame.K_q:
                    self.player.weapon = (self.player.weapon-1) % 10
                elif event.key == pygame.K_e:
                    self.player.weapon = (self.player.weapon+1) % 10
                elif event.key == pygame.K_p:
                    self.state = "pause"

            elif self.state == "pause" and event.key == pygame.K_p:
                self.state = "play"

    # ------------------------- rendering -------------------------------

    def draw_hud(self):
        s = self.canvas

        # Two-row 16-bit top HUD plate. Everything requested lives here:
        # STAGE, SCORE, WEAPON, LIVES, and the graphical health bar.
        pygame.draw.rect(s, (5,9,22), (0,0,NATIVE_W,21))
        pygame.draw.line(s, (14,40,66), (0,19), (NATIVE_W,19))
        pygame.draw.line(s, (52,130,170), (0,20), (NATIVE_W,20))

        draw_text(s, f"STAGE {self.stage:02d}", 3, 2, CYAN)
        draw_text(s, f"SCORE {self.score:07d}", 65, 2, WHITE)
        draw_text(s, f"LIVES {max(0,self.player.lives)}", 183, 2, YELLOW)

        wname = Weapon.NAMES[self.player.weapon]
        draw_text(s, f"WEAPON: {wname}", 3, 11, (180,240,255))

        bx, by, bw, bh = 176, 11, 75, 7
        draw_text(s, "HP", 160, 11, WHITE)
        pygame.draw.rect(s, (20,24,35), (bx,by,bw,bh))
        pygame.draw.rect(s, GRAY, (bx,by,bw,bh), 1)
        fill = int((bw-2) * max(0,self.player.health)/self.player.max_health)
        hpcol = GREEN if self.player.health > 50 else YELLOW if self.player.health > 25 else RED
        if fill > 0:
            pygame.draw.rect(s, hpcol, (bx+1,by+1,fill,bh-2))

        if self.boss and not self.boss.dead:
            # Boss health immediately below the player HUD.
            bw2 = 108
            bx2 = NATIVE_W//2-bw2//2
            pygame.draw.rect(s,(10,9,20),(bx2,23,bw2,6))
            ratio = max(0,self.boss.health/self.boss.max_health)
            pygame.draw.rect(s,RED,(bx2+1,24,int((bw2-2)*ratio),4))
            draw_text(s,"BOSS",bx2-29,23,MAGENTA)

    def draw_gameplay(self):
        self.background.draw(self.canvas, self.stage)

        for p in self.pickups:
            p.draw(self.canvas)
        for e in self.enemies:
            e.draw(self.canvas)
        if self.boss and not self.boss.dead:
            self.boss.draw(self.canvas)
        for b in self.player_bullets:
            b.draw(self.canvas)
        for b in self.enemy_bullets:
            b.draw(self.canvas)
        for ex in self.explosions:
            ex.draw(self.canvas)

        self.player.draw(self.canvas)

        # Boss warning scanline.
        if self.boss is None and self.stage_distance >= self.stage_goal:
            if int(self.boss_warning*8)%2 == 0:
                pygame.draw.rect(self.canvas,(35,0,20),(58,96,140,18))
                pygame.draw.rect(self.canvas,RED,(58,96,140,18),1)
                draw_text(self.canvas,"WARNING BOSS SIGNAL",67,102,YELLOW)

        self.draw_hud()

    def draw_overlay_center(self, title, subtitle=None, col=WHITE):
        # Semi-opaque style achieved with dithered dark plate.
        w = max(150, text_width(title)+18)
        x = (NATIVE_W-w)//2
        y = 79
        pygame.draw.rect(self.canvas, (6,7,18), (x,y,w,48))
        pygame.draw.rect(self.canvas, (48,90,128), (x,y,w,48),1)
        # Dithered border.
        for xx in range(x+2,x+w-2,4):
            self.canvas.set_at((xx,y+2),(75,130,160))
            self.canvas.set_at((xx,y+45),(45,80,110))
        draw_text(self.canvas,title,(NATIVE_W-text_width(title))//2,y+10,col,shadow=True)
        if subtitle:
            draw_text(self.canvas,subtitle,(NATIVE_W-text_width(subtitle))//2,y+28,(175,210,235))

    def draw(self):
        if self.state == "title":
            self.background.draw(self.canvas, 1)
            # title ship silhouette
            pygame.draw.polygon(self.canvas,(38,90,150),[(38,119),(70,105),(104,112),(120,119),(104,126),(70,133)])
            pygame.draw.polygon(self.canvas,CYAN,[(58,118),(91,112),(111,119),(90,122)])
            draw_text(self.canvas,"OMEGA HORIZON",38,55,CYAN,2,True)
            draw_text(self.canvas,"PSEUDO 3D 16 BIT SHMUP",57,82,WHITE)
            draw_text(self.canvas,"ENTER TO START",83,155,YELLOW)
            draw_text(self.canvas,"MOVE WASD  FIRE Z",74,176,(170,210,230))
            draw_text(self.canvas,"WEAPON Q E  PAUSE P",67,187,(170,210,230))
        else:
            self.draw_gameplay()

            if self.state == "stage_intro":
                title = f"STAGE {self.stage:02d}"
                self.draw_overlay_center(title, STAGE_TITLES[self.stage-1], CYAN)

            elif self.state == "stage_clear":
                self.draw_overlay_center("STAGE CLEAR", f"SCORE {self.score:07d}", GREEN)

            elif self.state == "pause":
                self.draw_overlay_center("PAUSED", "PRESS P TO RETURN", YELLOW)

            elif self.state == "game_over":
                self.draw_overlay_center("GAME OVER", "ENTER TO RESTART", RED)

            elif self.state == "victory":
                self.draw_overlay_center("OMEGA DESTROYED", "ENTER TO RESTART", GREEN)
                draw_text(self.canvas, f"FINAL SCORE {self.score:07d}",
                          (NATIVE_W-text_width(f"FINAL SCORE {self.score:07d}"))//2, 139, WHITE)

        # Nearest-neighbor integer scaling only.
        scaled = pygame.transform.scale(self.canvas, (WINDOW_W, WINDOW_H))
        self.window.blit(scaled, (0,0))
        pygame.display.flip()

    # ------------------------- main loop -------------------------------

    def run(self):
        while self.running:
            dt = min(1/20, self.clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()

        self.audio.stop_music()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
