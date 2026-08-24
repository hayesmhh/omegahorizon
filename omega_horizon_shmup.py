#!/usr/bin/env python3
"""
OMEGA HORIZON V8.2 - BOSS ARTIST PASS & SYSTEMS
=========================================================
Single-file procedural Pygame shooter designed around a 256x224 SNES-like
canvas, software perspective rendering, original artist-directed pixel art,
true stereo procedural audio, ten distinct stages, enemy archetypes, unique
boss behavior, weapon progression, tactical weapon matchups, and rare pickups.

Requires for source execution:
    pip install pygame-ce numpy

Controls:
    Arrow keys / WASD : Move
    Space / Z          : Fire
    Q / E              : Previous / next UNLOCKED weapon
    P / Esc             : Pause menu
    Enter               : Start / confirm / skip stage card
    F5                  : Quick save campaign checkpoint
    F9                  : Quick load campaign checkpoint
    F1                  : Test menu after hidden TEST MODE activation

Developer code:
    Type TERMINUS on the title screen to enable TEST MODE.

Build identity: V8.2-BOSS-ART-SYSTEMS
"""

import json
import math
import os
import random
import sys
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
HUD_H = 21
HORIZON_Y = 104
AUDIO_RATE = 44100
BUILD_ID = "V8.2-BOSS-ART-SYSTEMS"

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
ICE = (164, 232, 255)
LAVA = (255, 88, 26)

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
    "+": ["00000","00100","00100","11111","00100","00100","00000"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    " ": ["00000"] * 7,
}


def draw_text(surface, text, x, y, color=WHITE, scale=1, shadow=False):
    text = str(text).upper()
    if shadow:
        draw_text(surface, text, x + scale, y + scale, (0, 0, 0), scale, False)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    pygame.draw.rect(surface, color,
                                     (cx + gx * scale, y + gy * scale, scale, scale))
        cx += 6 * scale


def text_width(text, scale=1):
    return max(0, len(str(text)) * 6 * scale - scale)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def angle_to(dx, dy):
    return math.atan2(dy, dx)


def color_lerp(a, b, t):
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))


def safe_set(surface, x, y, color):
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


# ---------------------------------------------------------------------------
# Authored indexed pixel-art / metasprite helpers
# ---------------------------------------------------------------------------

def draw_indexed_sprite(surface, rows, x, y, palette, flip_x=False, scale=1):
    """Draw an authored palette-indexed sprite matrix.

    `.` is transparent. Other characters are palette keys.  Finished combat
    sprites use these matrices so their identity comes from intentional pixel
    clusters rather than runtime polygons.
    """
    for gy,row in enumerate(rows):
        iterable = row[::-1] if flip_x else row
        for gx,key in enumerate(iterable):
            if key == '.':
                continue
            col=palette.get(key)
            if col is None:
                continue
            if scale==1:
                safe_set(surface,x+gx,y+gy,col)
            else:
                pygame.draw.rect(surface,col,(x+gx*scale,y+gy*scale,scale,scale))


def draw_pixel_cloud(surface, x, y, scale=1, light=(194,211,218), mid=(142,169,181), shadow=(88,121,137)):
    """Chunky three-value cloud cluster designed to read like painted tiles."""
    rows=[
        "........22222........",
        ".....22223333222......",
        "...222333333333222....",
        ".2223333333333333322..",
        "222333333333333333322.",
        "111222333333333322211.",
        ".1111222222222222111..",
        "...11111111111111.....",
    ]
    draw_indexed_sprite(surface,rows,x,y,{'1':shadow,'2':mid,'3':light},scale=scale)


PLAYER_PIXELS=[
    ".............11...............",
    ".........11112211.............",
    "......1112223344211...........",
    "..1111222333444554211.........",
    "..112222333444556643211.......",
    "771222333444455566554332111...",
    "777122333444455555544443321188",
    "771222333444455566554332111...",
    "..112222333444556643211.......",
    "..1111222333444554211.........",
    "......1112223344211...........",
    ".........11112211.............",
    ".............11...............",
]

ENEMY_PIXEL_BANK={
    'interceptor':[
        ".......11.......",
        "....111221.......",
        "..1122334411.....",
        "112234455443311..",
        "81123445555544331",
        "112234455443311..",
        "..1122334411.....",
        "....111221.......",
        ".......11.......",
    ],
    'heavy':[
        "...111111111.....",
        ".1122222222211....",
        "112233333332211...",
        "1223344444332211..",
        "812345555554332211",
        "1223344444332211..",
        "112233333332211...",
        ".1122222222211....",
        "...111111111.....",
    ],
    'artillery':[
        "......1111.......",
        "...111222211......",
        ".1122333332211.....",
        "112334444433211....",
        "88812345554332211..",
        "112334444433211....",
        ".1122333332211.....",
        "...111222211......",
        "......1111.......",
    ],
    'ambusher':[
        "....11......11....",
        "...1221....1221...",
        "..1233211123321...",
        ".12334444443321....",
        "8123445555443321..",
        ".12334444443321....",
        "..1233211123321...",
        "...1221....1221...",
        "....11......11....",
    ],
}

# Tempest Bastion is intentionally constructed as a hand-authored metasprite.
# It reads as a side-view airborne fortress: cannon on the left, command deck
# above the hull, four lift turbines, and engine exhaust on the right.
BASTION_HULL=[
    "......................111111.....................",
    ".................111112222221111................",
    "............111112222233333322221111............",
    ".......11111222233333444444333322221111.........",
    "...111122223333444445555554444433332222111......",
    "111122223333444455555666555544443333222211111...",
    "777712223333444455566666655544443333222211111188",
    "777712223333444455566666655544443333222211111188",
    "111122223333444455555666555544443333222211111...",
    "...111122223333444445555554444433332222111......",
    ".......11111222233333444444333322221111.........",
    "............111112222233333322221111............",
    ".................111112222221111................",
    "......................111111.....................",
]

BASTION_TOWER=[
    "......11......",
    "....112211....",
    "...12233221...",
    "..1223443221..",
    ".122344443221.",
    "11223444432211",
    "11111111111111",
]

BASTION_TURBINE_A=[
    "....11111....",
    "..112222211..",
    ".12223332221.",
    "1223311333221",
    "1233115113321",
    "1233155513321",
    "1233115113321",
    "1223311333221",
    ".12223332221.",
    "..112222211..",
    "....11111....",
]
BASTION_TURBINE_B=[
    "....11111....",
    "..112222211..",
    ".12223132221.",
    "1223331333221",
    "1233155513321",
    "1233115113321",
    "1233155513321",
    "1223331333221",
    ".12223132221.",
    "..112222211..",
    "....11111....",
]


# ---------------------------------------------------------------------------
# V8.2 authored boss metasprites
# ---------------------------------------------------------------------------

# Pyroclast is a horned magma golem rather than an abstract molten polygon.
# The separate head/torso/limbs give it readable anatomy and animation.
PYRO_HEAD=[
    "1.................1",
    "11.......1.......11",
    ".11.....121.....11.",
    "..111..12221..111..",
    "...1222233322221...",
    "..122334444332221..",
    ".12234588854332221.",
    ".12345566554333221.",
    "1234566666544333221",
    "1234556665544333221",
    ".12344455444333221.",
    ".12233344333322221.",
    "..122223322222221..",
    "...1112333211111...",
    ".....1233321.......",
    ".....122221........",
    "......111..........",
]
PYRO_TORSO=[
    "..........111111111..........",
    "......11112222222221111......",
    "...11122223333333332222111...",
    "..1222233334444444333322221..",
    ".122233344455555554443332221.",
    "12233444555666666655544332221",
    "12334455666667776666655443321",
    "12344566677777777776665544321",
    "12345667777777777777766544321",
    "12345667777666667777766544321",
    "12345667776655566777766544321",
    "12345667776655566777766544321",
    "12345667777666667777766544321",
    "12344566677777777776665544321",
    "12334455666777777666555443321",
    "12233445556666666655544332221",
    ".122333445555555554443332221.",
    "..1222233444444444333322221..",
    "...11122233333333332222111...",
    "......1112222222221111.......",
    "..........11111111...........",
]
PYRO_ARM_L=[
    ".........111..",
    "......1112221.",
    "....1122333321",
    "...12234443321",
    "..123455443321",
    ".12345655443321",
    "123456655443321",
    "123456655443321",
    ".12345554433221",
    "..123444433221.",
    "...1223332221..",
    "....11222211...",
    "...11221.......",
    "..1221.........",
    ".1221..........",
    "1221...........",
    "121............",
    "11.............",
]
PYRO_ARM_R=[
    "..111.........",
    ".1222111......",
    "123332211....",
    "12334443221...",
    "123344554321..",
    "1234455654321.",
    "12344556654321",
    "12344556654321",
    "1223345554321.",
    ".122334444321..",
    "..1222333221...",
    "...11222211....",
    ".......12211...",
    ".........1221..",
    "..........1221.",
    "...........1221",
    "............121",
    ".............11",
]
PYRO_CLAW=[
    "..1...1..",
    ".121.121.",
    "123212321",
    ".1234321.",
    "..12321..",
]

# Stage 1 carrier becomes a long, readable capital ship with flight deck,
# command bridge, hangar bays and engine block.
CARRIER_BODY=[
    "....................111111111111111....................",
    "...............111112222222222222211111...............",
    "..........111112222233333333333333222221111..........",
    "......1111222233334444444444444444333322221111.......",
    "..11112222333344445555555555555554444333322221111....",
    "111222233344445555666666666666665555444433322221111..",
    "77772222334444555566666666666666555544443332222111188",
    "77772222334444555566666666666666555544443332222111188",
    "111222233344445555666666666666665555444433322221111..",
    "..11112222333344445555555555555554444333322221111....",
    "......1111222233334444444444444444333322221111.......",
    "..........111112222233333333333333222221111..........",
    "...............111112222222222222211111...............",
    "....................111111111111111....................",
]
CARRIER_BRIDGE=[
    "......11111......",
    "...11122222111...",
    "..1222333333221..",
    ".122344555443221.",
    "12234456665443321",
    "11111111111111111",
]
CARRIER_HANGAR=[
    "111111111111111",
    "122222222222221",
    "129999999999921",
    "122222222222221",
    "111111111111111",
]

# Leviathan has an authored predatory head plus repeated armored body segments.
LEVIATHAN_HEAD=[
    "...........111111..........",
    ".......1111222222111.......",
    "....111222233333322211.....",
    "..1122233334444443332211...",
    ".122334444555555544433221..",
    "12234455566666666555433221.",
    "123455666677777766655443321",
    "123455666777777776655443321",
    "123456667777777776665443321",
    "123456667788887776665443321",
    "123455666777777776655443321",
    "123455666677777766655443321",
    "12234455566666666555433221.",
    ".122334444555555544433221..",
    "..1122233334444443332211...",
    "....111222233333322211.....",
    ".......1111222222111.......",
    "...........111111..........",
]
LEVIATHAN_SEGMENT=[
    "...1111111...",
    ".11222222211.",
    "1223333333221",
    "1233445443321",
    "1234566543321",
    "1233445443321",
    "1223333333221",
    ".11222222211.",
    "...1111111...",
]

BOSS_DETAIL_TILES={
    'carrier': [".111.","12221","12321","12221",".111."],
    'pyroclast':[".111.","12321","13431","12321",".111."],
    'leviathan':["..11.",".1221","12331",".1221","..11."],
    'sentinel':["11111","12221","12321","12221","11111"],
    'mother':[".111.","12321","13431","12321",".111."],
    'ares':["11111","12321","13331","12221",".111."],
    'wyrm':["..1..",".121.","12321",".121.","..1.."],
    'sovereign':["..1..",".121.","12321",".121.","..1.."],
    'omega':[".111.","12321","13431","12321",".111."],
}


# ---------------------------------------------------------------------------
# Stage identity data
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StageProfile:
    title: str
    subtitle: str
    theme: str
    boss_name: str
    boss_kind: str
    palette: tuple
    enemy_names: tuple
    reward_weapon: Optional[int]
    music_style: str
    bpm: int
    key: int


STAGES = [
    StageProfile("NEON HORIZON", "DEEP SPACE", "space", "VALKYRIE CARRIER", "carrier",
                 ((6,8,26),(32,53,105),(68,206,255),(240,83,190)),
                 ("NEEDLE", "GUNSHIP", "ARC TURRET", "DART"), 1, "heroic", 132, 0),
    StageProfile("CHROME TEMPEST", "ATMOSPHERIC DESCENT", "atmosphere", "TEMPEST BASTION", "bastion",
                 ((16,25,45),(62,87,112),(132,180,206),(235,225,148)),
                 ("STORMWING", "GLIDE TANK", "LIGHTNING POD", "SKY RAZOR"), 2, "storm", 146, 2),
    StageProfile("CRIMSON ORBIT", "MAGMA CAVERNS", "lava", "PYROCLAST", "pyroclast",
                 ((20,5,5),(83,20,12),(255,72,15),(255,211,74)),
                 ("MAGMA BAT", "CRUST RAM", "MOLTEN SPITTER", "EMBER CLAW"), 3, "industrial", 138, 5),
    StageProfile("PHANTOM CIRCUIT", "PELAGIC RUINS", "water", "ABYSSAL LEVIATHAN", "leviathan",
                 ((2,23,48),(5,72,100),(32,170,177),(125,242,216)),
                 ("RAZORFIN", "NAUTILUS", "JELLY MINE", "TORPEDO EEL"), 4, "aquatic", 116, 7),
    StageProfile("ION CITADEL", "ORBITAL FORTRESS", "station", "CITADEL SENTINEL", "sentinel",
                 ((8,12,20),(54,67,83),(80,189,203),(255,180,64)),
                 ("SEC DRONE", "WARDEN", "RAIL NODE", "CUTTER"), 5, "mechanical", 152, 9),
    StageProfile("VOID REACTOR", "BIOMECH HIVE", "hive", "MOTHER NULL", "mother",
                 ((15,5,20),(63,24,59),(152,48,103),(119,245,151)),
                 ("BONEWING", "CHITIN BULK", "PLASMA NODE", "PARASITE"), 6, "organic", 124, 1),
    StageProfile("STARFORGE GAUNTLET", "RUINED MEGACITY", "city", "ARES-IX", "ares",
                 ((10,13,24),(45,52,68),(188,76,54),(255,198,79)),
                 ("WARHAWK", "SIEGE POD", "ROOFTOP GUN", "HUNTER"), 7, "war", 164, 4),
    StageProfile("ECLIPSE ENGINE", "FROZEN MOON", "ice", "CRYON WYRM", "wyrm",
                 ((4,14,31),(37,74,109),(125,198,229),(225,249,255)),
                 ("SHARDWING", "CRYO BULK", "ICE CANNON", "BURROWER"), 8, "crystal", 128, 6),
    StageProfile("TERMINUS VEIL", "PARALLAX RINGWORLD", "veil", "PARALLAX SOVEREIGN", "sovereign",
                 ((10,4,25),(58,23,106),(206,58,209),(94,255,224)),
                 ("MIRROR", "PRISM", "PHASE NODE", "FOLDING ONE"), 9, "unreal", 157, 8),
    StageProfile("OMEGA TERMINUS", "THE FINAL CORE", "omega", "OMEGA", "omega",
                 ((3,3,8),(40,18,44),(171,25,82),(255,233,172)),
                 ("OMEGA NEEDLE", "OMEGA BULK", "OMEGA EYE", "OMEGA HUNTER"), None, "omega", 176, 0),
]

# Weapon order intentionally follows campaign unlock order.
WEAPON_NAMES = [
    "PLASMA REPEATER",
    "SPREAD VULCAN",
    "WAVE BEAM",
    "LASER LANCE",
    "HOMING ROCKET",
    "PHOTON GRENADE",
    "REAR GUARD",
    "ORBITAL ORBITERS",
    "FLAK CANNON",
    "SONIC RING",
]

# Tactical damage. These are modest multipliers layered on top of mechanical
# advantages, not hard gates.
WEAPON_VS_ARCHETYPE = {
    "interceptor": [1.0,1.35,1.25,.85,1.35,.80,.95,1.10,.95,1.10],
    "heavy":       [.80,.70,.85,1.45,1.00,1.45,.85,1.00,1.25,1.05],
    "artillery":   [1.0,.90,1.00,1.30,1.30,1.15,.90,1.25,1.00,1.00],
    "ambusher":    [1.0,1.10,1.15,.90,1.15,.90,1.45,1.00,1.40,1.35],
}

# ---------------------------------------------------------------------------
# True stereo procedural audio engine
# ---------------------------------------------------------------------------

class AudioSynth:
    """Original SNES-inspired stereo music/SFX synthesizer.

    The engine composes each stage from independent voices with real pan,
    different instrument palettes, distinct chord/rhythm structures, stereo
    delay, and a dedicated boss arrangement. Weapon SFX are separate layered
    designs rather than one generic shot sample.
    """

    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.current = None
        self.music_sound = None
        self.boss_sound = None
        self.weapon_sfx = [[] for _ in range(10)]
        self.sfx = {}
        self.last_error = None
        self.music_volume = .80
        self.sfx_volume = .90
        self.rng = np.random.default_rng(8080)
        if self.enabled:
            try:
                self._make_sfx()
            except Exception as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
                self.enabled = False

    def set_volumes(self, music=None, sfx=None):
        if music is not None:
            self.music_volume=clamp(float(music),0.0,1.0)
        if sfx is not None:
            self.sfx_volume=clamp(float(sfx),0.0,1.0)
        try:
            if self.current:
                self.current.set_volume(self.music_volume)
        except Exception:
            pass

    @staticmethod
    def midi_hz(note):
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    @staticmethod
    def _osc(phase, kind):
        if kind == "square":
            return np.where(np.sin(phase) >= 0, 1.0, -1.0)
        if kind == "saw":
            return 2.0 * ((phase / (2*np.pi)) % 1.0) - 1.0
        if kind == "tri":
            return 2.0 * np.abs(2.0 * ((phase/(2*np.pi)) % 1.0) - 1.0) - 1.0
        if kind == "pulse25":
            return np.where(((phase/(2*np.pi)) % 1.0) < .25, 1.0, -1.0)
        return np.sin(phase)

    def voice(self, freq, duration, kind="square", volume=.25,
              attack=.004, decay=.08, vibrato=0.0, vibrato_rate=5.5):
        n = max(1, int(AUDIO_RATE * duration))
        t = np.arange(n, dtype=np.float32) / AUDIO_RATE
        inst_freq = freq * (1.0 + vibrato * np.sin(2*np.pi*vibrato_rate*t))
        phase = 2*np.pi*np.cumsum(inst_freq) / AUDIO_RATE
        wave = self._osc(phase, kind).astype(np.float32)
        env = np.ones(n, dtype=np.float32)
        a = min(n, max(1, int(attack*AUDIO_RATE)))
        d = min(n, max(1, int(decay*AUDIO_RATE)))
        env[:a] *= np.linspace(0,1,a,dtype=np.float32)
        env[-d:] *= np.linspace(1,0,d,dtype=np.float32)
        return wave * env * volume

    @staticmethod
    def pan_mono(mono, pan=0.0):
        pan = clamp(pan, -1.0, 1.0)
        # Equal-power pan.
        angle = (pan + 1.0) * math.pi / 4.0
        left = math.cos(angle)
        right = math.sin(angle)
        return np.column_stack((mono*left, mono*right)).astype(np.float32)

    @staticmethod
    def add_stereo(dst, start_s, sig):
        start = int(start_s * AUDIO_RATE)
        if start >= len(dst):
            return
        end = min(len(dst), start + len(sig))
        dst[start:end] += sig[:end-start]

    def stereo_delay(self, mix, delay_l=.145, delay_r=.205, feedback=.20):
        out = mix.copy()
        for channel, delay in ((0,delay_l),(1,delay_r)):
            n = int(delay*AUDIO_RATE)
            if n < len(out):
                out[n:, channel] += mix[:-n, channel] * feedback
                if n*2 < len(out):
                    out[n*2:, channel] += mix[:-n*2, channel] * (feedback*.42)
        return out

    def _sound_from_stereo(self, wave):
        if not self.enabled:
            return None
        arr = np.asarray(wave, dtype=np.float32)
        if arr.ndim == 1:
            arr = self.pan_mono(arr, 0)
        arr = np.clip(arr, -1.0, 1.0)
        mixer_info = pygame.mixer.get_init()
        channels = mixer_info[2] if mixer_info else 2
        if channels <= 1:
            pcm = np.ascontiguousarray((arr.mean(axis=1)*32767).astype(np.int16))
        elif channels == 2:
            pcm = np.ascontiguousarray((arr[:,:2]*32767).astype(np.int16))
        else:
            mono = arr.mean(axis=1)
            pcm = np.ascontiguousarray(np.repeat((mono*32767).astype(np.int16)[:,None], channels, axis=1))
        return pygame.sndarray.make_sound(pcm)

    def _noise(self, duration, volume=.2, seed=1):
        n = int(duration*AUDIO_RATE)
        rng = np.random.default_rng(seed)
        return rng.uniform(-1,1,n).astype(np.float32) * np.linspace(1,0,n,dtype=np.float32) * volume

    def _weapon_variant(self, idx, variant):
        detune = [0.985, 1.0, 1.018][variant]
        rng = np.random.default_rng(9000 + idx*31 + variant)

        if idx == 0:  # Plasma: electrical crack + compressed body
            d=.085; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            body=np.sin(2*np.pi*(520*detune*t + 520*t*t))*np.exp(-t*26)
            crack=rng.uniform(-1,1,n)*np.exp(-t*65)
            mono=.28*body+.12*crack
        elif idx == 1:  # Vulcan: mechanical ballistic-energy chatter
            d=.055; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.22*np.sign(np.sin(2*np.pi*175*detune*t))*np.exp(-t*48)
            mono += .16*rng.uniform(-1,1,n)*np.exp(-t*85)
            mono += .08*np.sin(2*np.pi*720*t)*np.exp(-t*70)
        elif idx == 2:  # Wave: resonant sweeping harmonic
            d=.16; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            phase=2*np.pi*(270*detune*t + 420*t*t)
            mono=.18*np.sin(phase)+.10*np.sin(phase*2.01)
            mono*=np.sin(np.pi*np.clip(t/d,0,1))
        elif idx == 3:  # Laser: snap + sustained coherent beam
            d=.14; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            snap=rng.uniform(-1,1,n)*np.exp(-t*110)
            mono=.24*np.sin(2*np.pi*1180*detune*t)*np.exp(-t*9)+.10*snap
        elif idx == 4:  # Homing Rocket: launcher thunk + ignition roar
            d=.23; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            thunk=np.sin(2*np.pi*(105*detune*t-45*t*t))*np.exp(-t*28)
            roar=rng.uniform(-1,1,n)*(1-np.exp(-t*45))*np.exp(-t*8)
            mono=.28*thunk+.10*roar
        elif idx == 5:  # Photon grenade: deep capacitive launcher
            d=.20; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.32*np.sin(2*np.pi*(88*detune*t+45*t*t))*np.exp(-t*13)
            mono += .11*np.sin(2*np.pi*390*t)*np.exp(-t*27)
        elif idx == 6:  # Rear Guard: paired electromagnetic snaps
            d=.09; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.20*np.sign(np.sin(2*np.pi*420*detune*t))*np.exp(-t*34)
            mono += .09*np.sin(2*np.pi*760*t)*np.exp(-t*50)
        elif idx == 7:  # Orbiters: precise micro emitters
            d=.07; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.13*np.sin(2*np.pi*1320*detune*t)*np.exp(-t*43)
            mono += .05*np.sin(2*np.pi*1960*t)*np.exp(-t*60)
        elif idx == 8:  # Flak: heavy cannon + metallic action
            d=.15; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.27*np.sin(2*np.pi*130*detune*t)*np.exp(-t*25)
            mono += .14*rng.uniform(-1,1,n)*np.exp(-t*50)
            mono += .07*np.sin(2*np.pi*620*t)*np.exp(-t*70)
        else:  # Sonic ring: pressure wave + resonant tail
            d=.30; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
            mono=.25*np.sin(2*np.pi*78*detune*t)*np.exp(-t*8)
            mono += .14*np.sin(2*np.pi*(240*detune*t-55*t*t))*np.exp(-t*6)
        return mono.astype(np.float32)

    def _make_sfx(self):
        # Three micro-variants of every weapon to avoid robotic repetition.
        for idx in range(10):
            for variant in range(3):
                mono = self._weapon_variant(idx, variant)
                self.weapon_sfx[idx].append(self._sound_from_stereo(self.pan_mono(mono,0)))

        # Layered explosion.
        d=.30; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
        rng=np.random.default_rng(404)
        boom=.38*np.sin(2*np.pi*(72*t-35*t*t))*np.exp(-t*9)
        boom+=.24*rng.uniform(-1,1,n)*np.exp(-t*12)
        self.sfx["boom"] = self._sound_from_stereo(self.pan_mono(boom,0))

        # Large explosion.
        d=.55; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
        rng=np.random.default_rng(405)
        big=.44*np.sin(2*np.pi*(54*t-18*t*t))*np.exp(-t*5)
        big+=.26*rng.uniform(-1,1,n)*np.exp(-t*7)
        self.sfx["big_boom"] = self._sound_from_stereo(self.pan_mono(big,0))

        # Pickup tiers and life.
        for key, notes in {
            "health": (72,76,79), "major_health": (67,72,79,84),
            "life": (72,79,84,91,96), "weapon": (60,67,72,79,84)
        }.items():
            chunks=[]
            for note in notes:
                chunks.append(self.voice(self.midi_hz(note), .055, "square", .12, decay=.025))
            self.sfx[key]=self._sound_from_stereo(self.pan_mono(np.concatenate(chunks),0))

        d=.14; n=int(d*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
        hit=.22*np.sign(np.sin(2*np.pi*(165*t+90*t*t)))*np.exp(-t*19)
        self.sfx["hit"]=self._sound_from_stereo(self.pan_mono(hit,0))
        frag=self._noise(.10,.16,812)+self.voice(360,.10,"square",.08,decay=.08)
        self.sfx["flak_split"]=self._sound_from_stereo(self.pan_mono(frag,0))

    def _play_positioned(self, sound, x=NATIVE_W/2, volume=1.0):
        if not self.enabled or sound is None:
            return
        try:
            ch=sound.play()
            if ch:
                p=clamp(x/(NATIVE_W-1),0,1)
                volume*=self.sfx_volume
                left=math.cos(p*math.pi/2)*volume
                right=math.sin(p*math.pi/2)*volume
                ch.set_volume(left,right)
        except Exception as exc:
            self.last_error=f"{type(exc).__name__}: {exc}"

    def play_weapon(self, idx, x, volume=.88):
        if self.enabled and self.weapon_sfx[idx]:
            self._play_positioned(random.choice(self.weapon_sfx[idx]), x, volume)

    def play_sfx(self, key, x=NATIVE_W/2, volume=1.0):
        self._play_positioned(self.sfx.get(key), x, volume)

    # -------------------- music instruments ---------------------------

    def instrument(self, kind, note, duration, volume=.12):
        hz=self.midi_hz(note)
        if kind == "bass":
            a=self.voice(hz,duration,"square",volume,attack=.002,decay=.08)
            b=self.voice(hz/2,duration,"sine",volume*.35,attack=.002,decay=.10)
            return a+b
        if kind == "bell":
            a=self.voice(hz,duration,"sine",volume,attack=.002,decay=duration*.65)
            b=self.voice(hz*2.01,duration,"sine",volume*.43,attack=.002,decay=duration*.5)
            c=self.voice(hz*3.98,duration,"sine",volume*.18,attack=.002,decay=duration*.35)
            return a+b+c
        if kind == "brass":
            a=self.voice(hz,duration,"saw",volume*.64,attack=.035,decay=.12,vibrato=.003)
            b=self.voice(hz*.997,duration,"square",volume*.26,attack=.035,decay=.12)
            return a+b
        if kind == "glass":
            return self.voice(hz,duration,"tri",volume,attack=.02,decay=.16,vibrato=.008,vibrato_rate=4)
        if kind == "guitar":
            a=self.voice(hz,duration,"saw",volume*.62,attack=.003,decay=.10)
            b=np.tanh(a*3.0)*.34
            return a+b
        if kind == "choir":
            return (self.voice(hz,duration,"tri",volume*.55,attack=.12,decay=.25,vibrato=.007) +
                    self.voice(hz*1.005,duration,"sine",volume*.45,attack=.15,decay=.28,vibrato=.005))
        if kind == "pluck":
            return self.voice(hz,duration,"pulse25",volume,attack=.001,decay=max(.03,duration*.75))
        if kind == "strings":
            return (self.voice(hz,duration,"saw",volume*.34,attack=.08,decay=.22,vibrato=.004) +
                    self.voice(hz*1.006,duration,"tri",volume*.48,attack=.10,decay=.25,vibrato=.006))
        if kind == "organ":
            return (self.voice(hz,duration,"square",volume*.46,attack=.012,decay=.10) +
                    self.voice(hz*2,duration,"sine",volume*.25,attack=.012,decay=.11) +
                    self.voice(hz*3,duration,"sine",volume*.10,attack=.012,decay=.08))
        if kind == "mallet":
            return (self.voice(hz,duration,"sine",volume,attack=.001,decay=max(.04,duration*.72)) +
                    self.voice(hz*2.99,duration,"sine",volume*.20,attack=.001,decay=max(.03,duration*.42)))
        return self.voice(hz,duration,"square",volume,attack=.004,decay=.08)

    def _kick(self, duration=.13, strength=.18):
        n=int(duration*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
        phase=2*np.pi*(92*t-210*t*t)
        return np.sin(phase).astype(np.float32)*np.exp(-t*28)*strength

    def _snare(self, seed, duration=.11, strength=.11):
        n=int(duration*AUDIO_RATE); t=np.arange(n)/AUDIO_RATE
        rng=np.random.default_rng(seed)
        return (rng.uniform(-1,1,n)*np.exp(-t*23)*strength +
                np.sin(2*np.pi*185*t)*np.exp(-t*31)*strength*.34).astype(np.float32)

    def generate_stage_mix(self, stage_index, boss=False):
        """Build a genuinely different stereo composition for one stage."""
        p=STAGES[stage_index]
        bpm = p.bpm + (14 if boss else 0)
        beat=60.0/bpm
        bars=16
        total=bars*4*beat
        mix=np.zeros((int(total*AUDIO_RATE),2),dtype=np.float32)

        # Each style defines its own harmonic/rhythmic/instrument identity.
        styles={
            "heroic":     dict(deg=[0,5,3,7], mode=[0,4,7], lead="brass", pad="glass", basspat=[0,0,7,0,5,0,7,10], drum="drive"),
            "storm":      dict(deg=[0,7,5,3], mode=[0,3,7], lead="guitar", pad="brass", basspat=[0,7,0,10,0,5,7,3], drum="sync"),
            "industrial": dict(deg=[0,1,6,0], mode=[0,3,6], lead="guitar", pad="brass", basspat=[0,0,1,0,6,0,1,3], drum="stomp"),
            "aquatic":    dict(deg=[0,5,8,3], mode=[0,3,7], lead="bell", pad="choir", basspat=[0,7,5,7,3,7,8,7], drum="half"),
            "mechanical": dict(deg=[0,3,7,6], mode=[0,3,7], lead="pluck", pad="brass", basspat=[0,0,3,0,7,6,7,3], drum="machine"),
            "organic":    dict(deg=[0,6,1,5], mode=[0,3,7], lead="glass", pad="choir", basspat=[0,6,0,1,0,5,6,1], drum="pulse"),
            "war":        dict(deg=[0,5,7,3], mode=[0,3,7], lead="guitar", pad="brass", basspat=[0,0,5,7,0,3,7,5], drum="double"),
            "crystal":    dict(deg=[0,8,5,10], mode=[0,3,7], lead="bell", pad="glass", basspat=[0,7,8,7,5,7,10,7], drum="sparse"),
            "unreal":     dict(deg=[0,1,8,6], mode=[0,3,6], lead="glass", pad="choir", basspat=[0,6,1,8,0,1,6,11], drum="odd"),
            "omega":      dict(deg=[0,1,6,3], mode=[0,3,6], lead="guitar", pad="choir", basspat=[0,0,1,6,0,3,1,6], drum="final"),
        }
        cfg=styles[p.music_style]
        base=45+p.key

        # Pads: long stereo voices with alternating wide pan.
        for bar in range(bars):
            degree=cfg["deg"][bar%len(cfg["deg"])]
            chord_root=base+degree+12
            for j,interval in enumerate(cfg["mode"]):
                sig=self.instrument(cfg["pad"], chord_root+interval, beat*3.85, .045 if not boss else .052)
                pan=(-.64 + j*.64) * (-1 if bar%2 else 1)
                self.add_stereo(mix,bar*4*beat,self.pan_mono(sig,pan))

        # Bass patterns differ in subdivision across style.
        bass_sub = 2 if p.music_style in ("aquatic","crystal") else 4
        step=beat*4/bass_sub
        for bar in range(bars):
            degree=cfg["deg"][bar%len(cfg["deg"])]
            for i in range(bass_sub):
                pat=cfg["basspat"][(bar*bass_sub+i)%len(cfg["basspat"])]
                note=base+degree+(pat%12)
                sig=self.instrument("bass",note,step*.78,.075 if not boss else .09)
                self.add_stereo(mix,(bar*4*beat+i*step),self.pan_mono(sig,0))

        # Stage-specific lead melodies, deliberately different contour/rhythm.
        melodies={
            "heroic": [12,16,19,21,19,16,14,12, 7,12,14,16,19,21,23,19],
            "storm": [12,15,19,18,15,12,10,7, 12,19,17,15,12,10,7,6],
            "industrial": [12,13,18,12,13,15,18,13, 12,18,13,12,10,13,6,7],
            "aquatic": [12,19,17,15,14,10,12,7, 15,17,19,22,19,17,15,10],
            "mechanical": [12,15,19,15,18,15,22,19, 12,15,18,21,18,15,13,10],
            "organic": [12,18,13,17,12,10,13,6, 12,13,18,19,13,12,10,6],
            "war": [12,12,19,17,15,12,19,22, 24,22,19,17,15,19,17,12],
            "crystal": [24,22,19,17,15,17,19,22, 24,27,24,22,19,17,15,10],
            "unreal": [12,13,20,18,11,17,6,13, 24,18,25,13,19,8,14,1],
            "omega": [12,13,18,15,12,10,6,1, 12,18,19,15,13,12,6,0],
        }
        melody=melodies[p.music_style]
        lead_step=beat/2 if p.music_style not in ("aquatic","crystal") else beat
        start_bar=1 if not boss else 0
        for i,noteoff in enumerate(melody*(2 if lead_step==beat/2 else 1)):
            start=(start_bar*4*beat)+i*lead_step
            if start>=total: break
            dur=lead_step*(.68 if p.music_style in ("mechanical","industrial") else .86)
            sig=self.instrument(cfg["lead"],base+noteoff,dur,.055 if not boss else .075)
            # Genuine stereo motion varies by musical identity.
            if p.music_style in ("unreal","omega"):
                pan=math.sin(i*1.7)*.78
            elif p.music_style in ("aquatic","crystal"):
                pan=math.sin(i*.52)*.55
            else:
                pan=(-.38 if i%4<2 else .38)
            self.add_stereo(mix,start,self.pan_mono(sig,pan))

        # B-section counter-melody gives the loop an actual arrangement arc.
        counter_instruments={
            "heroic":"strings","storm":"organ","industrial":"mallet","aquatic":"glass","mechanical":"mallet",
            "organic":"choir","war":"strings","crystal":"glass","unreal":"organ","omega":"strings"}
        counter_motifs={
            "heroic":[7,9,12,11,9,7,4,5], "storm":[3,7,10,8,7,3,2,0],
            "industrial":[0,6,1,7,0,3,1,6], "aquatic":[7,10,12,14,12,10,7,5],
            "mechanical":[0,3,7,10,7,3,6,3], "organic":[0,6,5,1,3,6,8,5],
            "war":[7,12,10,7,5,7,3,5], "crystal":[12,10,7,5,3,5,7,10],
            "unreal":[0,8,1,6,11,3,9,1], "omega":[0,1,6,3,8,6,1,0]}
        cinst=counter_instruments[p.music_style]; motif=counter_motifs[p.music_style]
        for section_bar in (4,8,12):
            for i,noff in enumerate(motif):
                st=(section_bar*4*beat)+i*(beat/2)
                if st>=total:break
                sig=self.instrument(cinst,base+12+noff,beat*.42,.028 if not boss else .040)
                pan=.48 if i%2 else -.48
                self.add_stereo(mix,st,self.pan_mono(sig,pan))

        # Arpeggiator/counterline, absent or sparse on slower aquatic stage.
        arp_intervals=cfg["mode"]+[cfg["mode"][1]+12]
        arp_step=beat/4 if p.music_style not in ("aquatic","crystal") else beat/2
        for i in range(int(total/arp_step)):
            if p.music_style=="aquatic" and i%4==3: continue
            bar=int((i*arp_step)/(beat*4))
            deg=cfg["deg"][bar%len(cfg["deg"])]
            interval=arp_intervals[(i*(2 if p.music_style=="unreal" else 1))%len(arp_intervals)]
            sig=self.instrument("pluck",base+deg+interval+24,arp_step*.54,.025 if not boss else .032)
            pan=(-.72 if i%2==0 else .72)
            self.add_stereo(mix,i*arp_step,self.pan_mono(sig,pan))

        # Percussion styles.
        for bi in range(bars*4):
            st=bi*beat
            kick=False; snare=False
            kind=cfg["drum"]
            if kind=="half":
                kick=bi%4==0; snare=bi%4==2
            elif kind=="sparse":
                kick=bi%4 in (0,3); snare=bi%4==2
            elif kind=="odd":
                kick=bi%5 in (0,3); snare=bi%4 in (1,3)
            elif kind=="double":
                kick=True if bi%2==0 else (boss and bi%4==3); snare=bi%4 in (1,3)
            elif kind=="stomp":
                kick=bi%2==0; snare=bi%4==2
            else:
                kick=bi%4 in (0,2); snare=bi%4 in (1,3)
            if kick:
                self.add_stereo(mix,st,self.pan_mono(self._kick(.13,.15 if not boss else .19),0))
            if snare:
                self.add_stereo(mix,st,self.pan_mono(self._snare(2000+stage_index*100+bi,strength=.09 if not boss else .12),.08))

        # Section-end fills at bars 4/8/12 keep the loop from sounding like a
        # continuously repeated procedural groove.
        for bar_end in (4,8,12,16):
            start=(bar_end*4*beat)-beat
            for j in range(4):
                sig=self._snare(7000+stage_index*50+bar_end*4+j,duration=.075,strength=.045+.012*j)
                self.add_stereo(mix,start+j*(beat/4),self.pan_mono(sig,-.35+j*.23))

        # Hi-hats/percussion have style-dependent density and stereo separation.
        hat_step=beat/2 if p.music_style in ("aquatic","crystal") else beat/4
        for i in range(int(total/hat_step)):
            if p.music_style=="industrial" and i%4==1: continue
            n=int(.035*AUDIO_RATE)
            rng=np.random.default_rng(3000+stage_index*200+i)
            hat=rng.uniform(-1,1,n).astype(np.float32)*np.linspace(.032,0,n,dtype=np.float32)
            pan=.58 if i%2 else -.58
            self.add_stereo(mix,i*hat_step,self.pan_mono(hat,pan))

        # Stage-signature ambience: subtle enough to remain musical, but it
        # gives each world an immediately different "air" behind the notes.
        ambient_seed=5100+stage_index*97+(1 if boss else 0)
        arng=np.random.default_rng(ambient_seed)
        n=len(mix); tt=np.arange(n,dtype=np.float32)/AUDIO_RATE
        if p.music_style=="heroic":
            amb=.008*np.sin(2*np.pi*54*tt)+.004*np.sin(2*np.pi*81*tt)
        elif p.music_style=="storm":
            amb=arng.uniform(-1,1,n).astype(np.float32)*.006
            amb*=.55+.45*np.sin(2*np.pi*.37*tt)**2
        elif p.music_style=="industrial":
            amb=.010*np.sign(np.sin(2*np.pi*27*tt))*np.sin(2*np.pi*.5*tt)**2
        elif p.music_style=="aquatic":
            amb=.010*np.sin(2*np.pi*(43+2*np.sin(2*np.pi*.11*tt))*tt)
        elif p.music_style=="mechanical":
            amb=.006*np.sign(np.sin(2*np.pi*96*tt))*(.5+.5*np.sin(2*np.pi*2*tt))
        elif p.music_style=="organic":
            amb=.009*np.sin(2*np.pi*(39+3*np.sin(2*np.pi*.19*tt))*tt)
        elif p.music_style=="war":
            amb=arng.uniform(-1,1,n).astype(np.float32)*.004 + .006*np.sin(2*np.pi*48*tt)
        elif p.music_style=="crystal":
            amb=.007*np.sin(2*np.pi*132*tt)+.004*np.sin(2*np.pi*198.7*tt)
        elif p.music_style=="unreal":
            amb=.008*np.sin(2*np.pi*(57+9*np.sin(2*np.pi*.07*tt))*tt)
        else:
            amb=.010*np.sin(2*np.pi*41*tt)+arng.uniform(-1,1,n).astype(np.float32)*.003
        # Slow opposing pan modulation keeps ambience stereo rather than centered.
        panwave=np.sin(2*np.pi*.035*tt+stage_index*.4)
        mix[:,0]+=amb*(.65-.22*panwave)
        mix[:,1]+=amb*(.65+.22*panwave)

        # Boss versions gain a stage-specific low ostinato and a second lead
        # response, making them arrangements rather than simply faster loops.
        if boss:
            boss_pattern={
                "heroic":[0,7,12,7],"storm":[0,3,10,7],"industrial":[0,1,6,1],
                "aquatic":[0,5,3,7],"mechanical":[0,3,6,7],"organic":[0,6,1,3],
                "war":[0,5,7,10],"crystal":[0,8,5,10],"unreal":[0,1,8,6],"omega":[0,1,6,3]
            }[p.music_style]
            ost_step=beat/2
            for i in range(int(total/ost_step)):
                note=base-12+boss_pattern[i%len(boss_pattern)]
                sig=self.instrument("bass",note,ost_step*.48,.045)
                self.add_stereo(mix,i*ost_step,self.pan_mono(sig,-.10 if i%2 else .10))
            response=[7,10,12,15,12,10,7,5]
            for section_bar in (3,7,11,15):
                for i,noff in enumerate(response):
                    st=section_bar*4*beat+i*(beat/2)
                    if st>=total: break
                    sig=self.instrument("brass" if p.music_style not in ("aquatic","crystal") else "bell",
                                        base+12+noff,beat*.34,.035)
                    self.add_stereo(mix,st,self.pan_mono(sig,.58 if i%2 else -.58))

        mix=self.stereo_delay(mix,
                              .22 if p.music_style in ("aquatic","crystal") else .135,
                              .29 if p.music_style in ("aquatic","crystal") else .185,
                              .24 if not boss else .18)
        mix=np.tanh(mix*1.4)*.72
        return self._sound_from_stereo(mix)

    def play_stage(self, stage_index):
        if not self.enabled: return
        try:
            if self.current: self.current.stop()
            self.music_sound=self.generate_stage_mix(stage_index,False)
            self.current=self.music_sound
            if self.current:
                self.current.set_volume(self.music_volume)
                self.current.play(loops=-1)
        except Exception as exc:
            self.last_error=f"{type(exc).__name__}: {exc}"; self.enabled=False

    def play_boss(self, stage_index):
        if not self.enabled: return
        try:
            if self.current: self.current.stop()
            self.boss_sound=self.generate_stage_mix(stage_index,True)
            self.current=self.boss_sound
            if self.current:
                self.current.set_volume(self.music_volume)
                self.current.play(loops=-1)
        except Exception as exc:
            self.last_error=f"{type(exc).__name__}: {exc}"; self.enabled=False

    def stop_music(self):
        try:
            if self.current: self.current.stop()
        except Exception:
            pass
        self.current=None

# ---------------------------------------------------------------------------
# Stage-specific software background renderer
# ---------------------------------------------------------------------------

class Background:
    def __init__(self):
        self.scroll=0.0
        self.time=0.0
        self.rng=random.Random(1337)
        self.fx_level=2
        self.stars=[]
        for count,speed,bright in [(46,.16,90),(34,.40,150),(24,.82,230)]:
            pts=[(self.rng.randrange(NATIVE_W),self.rng.randrange(HUD_H+2,NATIVE_H-8),self.rng.randrange(1,3)) for _ in range(count)]
            self.stars.append((pts,speed,bright))
        self.textures={theme:self._build_texture(theme,256) for theme in
                       ("atmosphere","lava","water","station","hive","city","ice","veil","omega")}

    def _build_texture(self, theme, size):
        yy,xx=np.indices((size,size))
        tex=np.zeros((size,size,3),dtype=np.uint8)
        if theme=="atmosphere":
            stripes=((yy//12)%2)
            tex[...,0]=24+stripes*9; tex[...,1]=54+stripes*14; tex[...,2]=74+stripes*16
            ridges=((xx*3+yy*2)%53)<3; tex[ridges]=(78,105,97)
        elif theme=="lava":
            # Large cooled basalt plates separated by readable molten channels.
            # V8's fine-grain noise competed with enemy silhouettes.
            plate=((xx//18 + yy//15)&1)
            broad=((xx*3+yy*2+(xx^yy))&15)
            tex[...,0]=18+plate*8+broad//5; tex[...,1]=5+plate*3; tex[...,2]=5+plate*2
            cracks=(((xx*3+yy*2)%67)<2)|(((xx-yy*2)%83)<2)
            tex[cracks]=(205,47,11)
            hot=(((xx+yy*2)%109)<2)&cracks; tex[hot]=(255,199,49)
        elif theme=="water":
            wave=((np.sin(xx*.11)+np.sin(yy*.17))*12).astype(np.int16)
            tex[...,0]=np.clip(4+wave,0,255); tex[...,1]=np.clip(58+wave,0,255); tex[...,2]=np.clip(91+wave*2,0,255)
            ruins=((xx%48)<3)|((yy%40)<2); tex[ruins]=(21,92,96)
        elif theme=="station":
            tex[:]=(18,24,31)
            panels=((xx%32)<2)|((yy%24)<2); tex[panels]=(58,72,82)
            rails=((yy%64)>=29)&((yy%64)<=32); tex[rails]=(22,151,171)
            hazard=((xx//8+yy//8)%7==0); tex[hazard]=(130,82,25)
        elif theme=="hive":
            pulse=((np.sin(xx*.09)+np.cos(yy*.12))*10).astype(np.int16)
            tex[...,0]=np.clip(45+pulse,0,255); tex[...,1]=np.clip(13+pulse//4,0,255); tex[...,2]=np.clip(42+pulse,0,255)
            veins=(((xx*2+yy*3)%57)<3); tex[veins]=(123,31,84)
            nodes=((xx%73<3)&(yy%61<3)); tex[nodes]=(75,219,128)
        elif theme=="city":
            tex[:]=(19,23,31)
            roads=((yy%48)<16); tex[roads]=(30,34,42)
            lanes=((yy%48)==7); tex[lanes]=(214,164,58)
            seams=((xx%32)<2); tex[seams]=(60,61,68)
        elif theme=="ice":
            tex[:]=(75,125,157)
            bands=((xx+yy*2)%31)<2; tex[bands]=(178,231,248)
            cracks=((xx*7-yy*5)%89)<2; tex[cracks]=(24,73,109)
        elif theme=="veil":
            tex[...,0]=35+(((xx^yy)&31)*2)
            tex[...,1]=12+(((xx*3+yy)&15)*2)
            tex[...,2]=65+(((xx+yy*5)&31)*3)
            grid=((xx%29)<2)|((yy%37)<2); tex[grid]=(190,49,210)
        elif theme=="omega":
            tex[:]=(15,9,17)
            ribs=((xx%24)<3)|((yy%32)<3); tex[ribs]=(78,24,56)
            conduits=((yy%64)>=29)&((yy%64)<=32); tex[conduits]=(235,53,105)
            sparks=((xx*7+yy*11)%127)<2; tex[sparks]=(255,220,142)
        return tex

    def update(self,dt,stage):
        self.time+=dt
        self.scroll=(self.scroll+(52+stage*4)*dt)%256

    def _gradient(self,surf,top,bottom,y0=HUD_H,y1=NATIVE_H):
        for y in range(y0,y1):
            t=(y-y0)/max(1,y1-y0-1)
            pygame.draw.line(surf,color_lerp(top,bottom,t),(0,y),(NATIVE_W,y))

    def _stars(self,surf,ymin=HUD_H,ymax=NATIVE_H,speedmul=1.0,tint=(1.0,1.0,1.0)):
        for li,(pts,speed,bright) in enumerate(self.stars):
            off=self.time*28*speed*speedmul
            for pi,(x,y,sz) in enumerate(pts):
                if self.fx_level==0 and pi%3: continue
                if self.fx_level==1 and pi%2: continue
                if not ymin<=y<ymax: continue
                xx=int((x-off)%NATIVE_W)
                pulse=clamp(bright+int(18*math.sin(self.time*2+(x+y)*.04)),40,255)
                col=(int(pulse*tint[0]),int(pulse*tint[1]),int(min(255,pulse*tint[2])))
                safe_set(surf,xx,y,col)
                if li==2 and sz>1: safe_set(surf,xx+1,y,col)

    def _floor_cast(self,surf,theme,horizon=104,warp=0.0,fog=(0,0,0)):
        h=NATIVE_H-horizon
        out=np.empty((h,NATIVE_W,3),dtype=np.uint8)
        xs=np.arange(NATIVE_W,dtype=np.float32)-NATIVE_W/2
        tex=self.textures[theme]
        mask=255
        for row in range(h):
            y=horizon+row
            dy=max(1.0,y-horizon)
            depth=92.0/dy
            distance=depth*42.0
            wobble=math.sin(self.time*1.7+row*.09)*warp
            wx=self.scroll*1.8+distance+xs*depth*.72+wobble
            wy=self.scroll*.23+distance*.60+xs*depth*.08
            tx=np.asarray(wx,dtype=np.int32)&mask
            ty=np.asarray(wy,dtype=np.int32)&mask
            line=tex[ty,tx].astype(np.float32)
            near=row/max(1,h-1)
            factor=.30+.70*(near**.42)
            line=line*factor+np.asarray(fog,dtype=np.float32)*(1-factor)*.28
            out[row]=np.clip(line,0,255).astype(np.uint8)
        fs=pygame.surfarray.make_surface(np.transpose(out,(1,0,2)))
        surf.blit(fs,(0,horizon))

    def draw(self,surf,stage):
        theme=STAGES[stage-1].theme
        fn=getattr(self,f"draw_{theme}")
        fn(surf,stage)

    def draw_space(self,surf,stage):
        self._gradient(surf,(3,4,18),(11,5,32))
        self._stars(surf,HUD_H,NATIVE_H,1.0,(.7,.9,1.0))
        # Large distant violet nebula bands.
        for i in range(8):
            y=40+i*11+int(math.sin(self.time*.18+i)*4)
            x=int((i*47-self.time*(3+i*.2))%(NATIVE_W+80))-40
            pygame.draw.line(surf,(22+i*2,15,48+i*3),(x,y),(x+72,y),2)
        # Planet/moon parallax.
        px=int(214-self.time*1.3)%340-40
        pygame.draw.circle(surf,(24,31,65),(px,67),22)
        pygame.draw.circle(surf,(50,66,111),(px-5,62),16)
        pygame.draw.arc(surf,(98,153,184),(px-23,44,46,46),2.4,5.0,1)
        # Debris perspective stream.
        for i in range(12 if self.fx_level==2 else 7 if self.fx_level==1 else 4):
            t=(self.time*.16+i/12)%1
            x=int(280-t*310); y=int(108+(i%5-2)*8+t*92); r=max(1,int(t*4))
            pygame.draw.rect(surf,(75,85,108),(x,y,r+1,r))

    def draw_atmosphere(self,surf,stage):
        self._gradient(surf,(8,16,40),(94,129,148),HUD_H,105)
        self._stars(surf,HUD_H,68,.55,(.6,.75,1.0))
        # Planet curvature / atmosphere glow.
        pygame.draw.ellipse(surf,(36,86,112),(-72,67,400,155))
        pygame.draw.arc(surf,(128,211,229),(-72,60,400,160),3.2,6.1,2)
        # Painterly pixel-cloud parallax. Three-value clusters give the clouds
        # actual volume instead of reading as flat geometric ellipses.
        cloud_sets=[
            (7,73,1,(203,219,224),(149,176,187),(92,124,140)),
            (14,91,1,(173,196,205),(118,151,165),(69,105,122)),
            (25,108,1,(139,171,183),(89,129,145),(48,85,104)),
        ]
        for layer,(spd,ybase,sc,light,mid,shadow) in enumerate(cloud_sets):
            for i in range(6):
                x=int((i*58-self.time*spd)%(NATIVE_W+90))-45
                y=ybase+int(math.sin(i*1.9+self.time*.3)*5)
                draw_pixel_cloud(surf,x,y,sc,light,mid,shadow)
        self._floor_cast(surf,"atmosphere",112,0,(47,75,84))
        # Lightning.
        if int(self.time*2.1)%11==0:
            x=170+int(math.sin(self.time*9)*26)
            pts=[(x,48),(x-5,62),(x+3,70),(x-4,83),(x+2,94)]
            pygame.draw.lines(surf,(225,245,255),False,pts,1)

    def draw_lava(self,surf,stage):
        self._gradient(surf,(16,4,5),(50,9,7),HUD_H,99)
        # Layered cavern walls and stalactites.
        for i in range(18):
            x=int((i*23-self.scroll*.28)%300)-22
            h=18+(i*17)%38
            col=(37+(i%3)*8,10,9)
            pygame.draw.polygon(surf,col,[(x,HUD_H),(x+18,HUD_H),(x+12,HUD_H+h),(x+8,HUD_H+h+10)])
        # molten waterfall in distance
        wx=int((194-self.scroll*.12)%330)-20
        pygame.draw.rect(surf,(115,25,8),(wx,47,12,64))
        pygame.draw.rect(surf,(245,69,13),(wx+3,48,6,65))
        pygame.draw.line(surf,(255,211,71),(wx+5,48),(wx+5,110),1)
        # A darker midground shelf separates combat sprites from the hottest
        # floor texture while retaining the oppressive cavern atmosphere.
        pygame.draw.polygon(surf,(20,7,10),[(0,91),(42,86),(81,92),(126,84),(171,91),(215,85),(256,91),(256,105),(0,105)])
        pygame.draw.line(surf,(91,31,24),(0,103),(256,103),1)
        self._floor_cast(surf,"lava",105,1.0,(48,6,5))
        # Foreground basalt silhouettes.
        for i in range(7):
            x=int((i*47-self.scroll*.62)%330)-30
            base=213; top=170-(i%3)*13
            pygame.draw.polygon(surf,(27,8,7),[(x-10,base),(x,top),(x+8,top-10),(x+18,base)])
        # Embers.
        for i in range(22 if self.fx_level==2 else 12 if self.fx_level==1 else 6):
            x=int((i*37+self.time*(7+i%4))%NATIVE_W)
            y=198-int((self.time*(18+i%5)+i*19)%105)
            safe_set(surf,x,y,YELLOW if i%4==0 else ORANGE)

    def draw_water(self,surf,stage):
        self._gradient(surf,(2,34,68),(3,78,92))
        # Surface shimmer at top.
        for i in range(12):
            x=int((i*31-self.time*8)%300)-20
            pygame.draw.line(surf,(62,147,177),(x,29+i%3*5),(x+22,29+i%3*5),1)
        # Distant ruins.
        for i in range(7):
            x=int((i*53-self.scroll*.14)%340)-45
            h=25+(i*9)%45
            pygame.draw.rect(surf,(8,55,69),(x,92-h,13,h))
            pygame.draw.rect(surf,(10,82,88),(x+4,92-h+6,3,max(3,h-10)))
        self._floor_cast(surf,"water",101,2.6,(1,31,47))
        # Caustic lines.
        for y in range(112,NATIVE_H,16):
            off=int(math.sin(self.time*2+y*.11)*7)
            for x in range(-20,NATIVE_W+20,33):
                pygame.draw.line(surf,(39,135,145),(x+off,y),(x+off+15,y+2),1)
        # Bubbles.
        for i in range(20 if self.fx_level==2 else 11 if self.fx_level==1 else 5):
            x=(i*43+17)%NATIVE_W
            y=NATIVE_H-int((self.time*(9+i%5)+i*31)%(NATIVE_H-HUD_H))
            pygame.draw.circle(surf,(99,190,198),(x,y),1,1)

    def draw_station(self,surf,stage):
        self._gradient(surf,(7,11,18),(14,21,27),HUD_H,105)
        # Repeating corridor ribs.
        for i in range(9):
            x=int((i*46-self.scroll*.5)%360)-52
            pygame.draw.rect(surf,(42,51,60),(x,33,8,77))
            pygame.draw.rect(surf,(81,93,101),(x+2,37,2,69))
            pygame.draw.line(surf,(26,116,135),(x+7,52),(x+7,96),1)
        # Window strip reveals space.
        pygame.draw.rect(surf,(4,8,21),(0,63,NATIVE_W,19))
        for i in range(14):
            x=int((i*31-self.time*12)%NATIVE_W); safe_set(surf,x,70,(120,190,230))
        self._floor_cast(surf,"station",105,0,(9,15,20))
        # Moving mechanical arms foreground.
        for i in range(3):
            x=int((70+i*96-self.scroll*.8)%360)-50
            pygame.draw.rect(surf,(52,57,64),(x,126,6,70))
            pygame.draw.line(surf,(96,105,112),(x+3,127),(x+19,143),3)
            pygame.draw.circle(surf,(235,157,51),(x+20,144),3)

    def draw_hive(self,surf,stage):
        self._gradient(surf,(18,5,20),(48,10,39))
        # Pulsing organic wall lobes.
        for i in range(9):
            x=int((i*39-self.scroll*.18)%330)-30
            r=17+int(math.sin(self.time*2+i)*3)
            pygame.draw.ellipse(surf,(67,18,57),(x,39+(i%3)*15,r*2,r+14))
            pygame.draw.ellipse(surf,(104,29,77),(x+5,44+(i%3)*15,r,r+4),1)
        # Hanging membranes.
        for i in range(10):
            x=int((i*29-self.scroll*.25)%290)-15
            length=16+(i*11)%34
            pygame.draw.line(surf,(91,28,73),(x,HUD_H),(x+int(math.sin(self.time+i)*4),HUD_H+length),3)
        self._floor_cast(surf,"hive",103,1.7,(38,8,30))
        # Bioluminescent nodes.
        for i in range(12):
            x=int((i*53-self.scroll*.45)%330)-30; y=127+(i*17)%79
            pulse=2+(int(self.time*5+i)%2)
            pygame.draw.circle(surf,(52,194,120),(x,y),pulse)
            safe_set(surf,x-1,y-1,(169,255,194))

    def draw_city(self,surf,stage):
        self._gradient(surf,(12,10,25),(70,42,40),HUD_H,105)
        # Multiple skyline layers.
        for layer,(spd,col,base) in enumerate([(7,(25,27,42),99),(15,(39,40,51),108),(27,(51,48,53),117)]):
            for i in range(9):
                x=int((i*43-self.time*spd)%340)-35
                h=22+((i*17+layer*11)%52)
                pygame.draw.rect(surf,col,(x,base-h,25,h))
                if layer>0:
                    for wy in range(base-h+5,base-3,8):
                        safe_set(surf,x+5,wy,(174,93,50)); safe_set(surf,x+15,wy,(39,104,127))
        self._floor_cast(surf,"city",109,0,(23,22,27))
        # Smoke/fire columns.
        for i in range(5):
            x=int((38+i*61-self.scroll*.20)%320)-25
            y=91-(i%2)*14
            pygame.draw.circle(surf,(86,62,61),(x,y),5)
            pygame.draw.circle(surf,(52,47,54),(x+3,y-6),7)
            if i%2==0: pygame.draw.line(surf,ORANGE,(x,y+8),(x+2,y+13),2)

    def draw_ice(self,surf,stage):
        self._gradient(surf,(5,15,36),(40,81,118),HUD_H,103)
        # Giant planet in sky.
        pygame.draw.circle(surf,(45,78,121),(200,56),31)
        pygame.draw.circle(surf,(87,122,157),(191,48),21)
        pygame.draw.arc(surf,(165,211,232),(166,22,69,69),.5,2.6,2)
        # Distant glacier silhouettes.
        for i in range(10):
            x=int((i*36-self.scroll*.13)%320)-30
            h=17+(i*13)%38
            pygame.draw.polygon(surf,(58,101,132),[(x,104),(x+10,104-h),(x+19,90),(x+29,104)])
            pygame.draw.line(surf,(142,206,228),(x+10,104-h),(x+19,90),1)
        self._floor_cast(surf,"ice",103,.5,(21,55,83))
        # Blowing snow.
        for i in range(34 if self.fx_level==2 else 18 if self.fx_level==1 else 8):
            x=int((i*23-self.time*(22+i%6))%NATIVE_W)
            y=HUD_H+(i*37)%198
            safe_set(surf,x,y,(190,229,244))

    def draw_veil(self,surf,stage):
        self._gradient(surf,(8,3,22),(30,7,54))
        # Ringworld arcs.
        pygame.draw.arc(surf,(76,33,121),(-70,18,390,176),3.25,6.15,7)
        pygame.draw.arc(surf,(192,57,206),(-72,21,394,178),3.35,6.05,1)
        self._stars(surf,HUD_H,105,-.7,(1.0,.5,1.0))
        self._floor_cast(surf,"veil",101,8.0,(26,3,39))
        # Reality tears.
        for i in range(5):
            x=int((i*63+self.time*(7 if i%2 else -5))%300)-20
            y=50+(i*33)%130
            h=18+(i*9)%30
            pygame.draw.line(surf,(73,255,220),(x,y),(x+int(math.sin(self.time*3+i)*8),y+h),1)
            pygame.draw.line(surf,(227,60,232),(x+3,y),(x+4,y+h),1)

    def draw_omega(self,surf,stage):
        self._gradient(surf,(3,3,8),(31,5,22))
        # Enormous living-machine core in depth.
        pulse=4+int((math.sin(self.time*3)+1)*2)
        pygame.draw.circle(surf,(60,12,42),(198,69),37+pulse)
        pygame.draw.circle(surf,(116,19,64),(198,69),26+pulse,3)
        pygame.draw.circle(surf,(255,73,117),(198,69),10+pulse)
        pygame.draw.circle(surf,(255,225,169),(194,65),3)
        # Conduit ribs.
        for i in range(11):
            x=int((i*31-self.scroll*.35)%300)-20
            pygame.draw.line(surf,(65,21,54),(x,HUD_H),(x+18,105),4)
            pygame.draw.line(surf,(151,31,78),(x+2,HUD_H),(x+20,105),1)
        self._floor_cast(surf,"omega",101,4.0,(25,3,12))
        # Energy filaments foreground.
        for i in range(8 if self.fx_level==2 else 5 if self.fx_level==1 else 3):
            x=int((i*49+self.time*11)%300)-20
            pygame.draw.line(surf,(226,47,104),(x,128),(x+int(math.sin(self.time*4+i)*16),216),1)
            if i%3==0: safe_set(surf,x,145+(i*9)%60,(255,230,173))

# ---------------------------------------------------------------------------
# Bullets, explosions, pickups, hazards
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
    weapon_index: int = 0

    def update(self,dt,game):
        self.age+=dt; self.life-=dt
        if self.kind=="wave":
            self.x+=self.vx*dt
            self.y+=self.vy*dt+math.sin(self.age*18+self.phase)*42*dt
        elif self.kind=="homing":
            target=game.nearest_enemy(self.x,self.y)
            if target is not None:
                desired=angle_to(target.x-self.x,target.y-self.y)
                cur=math.atan2(self.vy,self.vx)
                delta=(desired-cur+math.pi)%(2*math.pi)-math.pi
                cur+=clamp(delta,-2.9*dt,2.9*dt)
                sp=math.hypot(self.vx,self.vy)
                self.vx,self.vy=math.cos(cur)*sp,math.sin(cur)*sp
            self.x+=self.vx*dt; self.y+=self.vy*dt
        elif self.kind=="sonic":
            self.x+=self.vx*dt; self.y+=self.vy*dt
            self.radius=min(15,self.radius+7*dt)
        elif self.kind=="flak":
            self.x+=self.vx*dt; self.y+=self.vy*dt
            if not self.split and self.age>.30:
                self.split=True; self.life=0
                game.audio.play_sfx("flak_split",self.x,.7)
                for a in (-.42,0,.42):
                    sp=138
                    game.player_bullets.append(Bullet(
                        self.x,self.y,math.cos(a)*sp,math.sin(a)*sp,
                        self.damage*.70,"player","fragment",1.5,.82,
                        weapon_index=self.weapon_index))
        else:
            self.x+=self.vx*dt; self.y+=self.vy*dt

    def alive(self):
        return self.life>0 and -48<=self.x<=NATIVE_W+70 and -48<=self.y<=NATIVE_H+48

    def rect(self):
        if self.kind=="laser": return pygame.Rect(int(self.x),int(self.y-1),38,3)
        r=max(2,int(self.radius)); return pygame.Rect(int(self.x-r),int(self.y-r),r*2,r*2)

    def draw(self,surf):
        x,y=int(self.x),int(self.y)
        if self.owner=="enemy":
            if self.kind=="mine":
                pygame.draw.circle(surf,(90,22,40),(x,y),5)
                pygame.draw.circle(surf,RED,(x,y),3)
                for a in range(0,360,90):
                    aa=math.radians(a); pygame.draw.line(surf,ORANGE,(x,y),(x+int(math.cos(aa)*7),y+int(math.sin(aa)*7)),1)
            elif self.kind=="tracking":
                pygame.draw.circle(surf,ORANGE,(x,y),int(self.radius)+1)
                pygame.draw.circle(surf,RED,(x,y),max(1,int(self.radius)-1))
                pygame.draw.line(surf,YELLOW,(x+3,y),(x+6,y),1)
            elif self.kind=="ice":
                pygame.draw.polygon(surf,ICE,[(x+4,y),(x,y-3),(x-4,y),(x,y+3)])
            elif self.kind=="lava":
                pygame.draw.circle(surf,LAVA,(x,y),int(self.radius)+1)
                safe_set(surf,x-1,y-1,YELLOW)
            else:
                pygame.draw.circle(surf,RED,(x,y),int(self.radius)+1)
                pygame.draw.circle(surf,YELLOW,(x,y),max(1,int(self.radius)-1))
            return

        # Player projectiles each have distinct visual language.
        if self.kind=="laser":
            pygame.draw.rect(surf,(49,183,234),(x,y-2,39,5))
            pygame.draw.rect(surf,(150,250,255),(x,y-1,39,3))
            pygame.draw.line(surf,WHITE,(x,y),(x+38,y))
        elif self.kind=="wave":
            pygame.draw.circle(surf,(67,82,227),(x,y),5)
            pygame.draw.circle(surf,CYAN,(x,y),4,1)
            pygame.draw.circle(surf,WHITE,(x+1,y),2)
        elif self.kind=="grenade":
            pygame.draw.circle(surf,(89,32,109),(x,y),6)
            pygame.draw.circle(surf,MAGENTA,(x,y),5,1)
            pygame.draw.circle(surf,YELLOW,(x-1,y-1),2)
            for a in (0,math.pi/2,math.pi,math.pi*1.5):
                safe_set(surf,x+int(math.cos(a+self.age*7)*7),y+int(math.sin(a+self.age*7)*7),CYAN)
        elif self.kind=="flak":
            pygame.draw.rect(surf,(83,62,36),(x-4,y-3,8,6))
            pygame.draw.rect(surf,(255,196,70),(x-3,y-2,5,4))
            pygame.draw.rect(surf,WHITE,(x+1,y-1,3,2))
        elif self.kind=="fragment":
            pygame.draw.line(surf,YELLOW,(x-2,y),(x+2,y),1)
        elif self.kind=="homing":
            pygame.draw.polygon(surf,(205,205,216),[(x+6,y),(x-3,y-3),(x-1,y),(x-3,y+3)])
            pygame.draw.rect(surf,MAGENTA,(x-1,y-1,3,2))
            flame=ORANGE if int(self.age*20)%2 else YELLOW
            pygame.draw.line(surf,flame,(x-4,y),(x-8,y),2)
        elif self.kind=="sonic":
            pygame.draw.circle(surf,(153,245,255),(x,y),int(self.radius),1)
            pygame.draw.circle(surf,(75,130,245),(x,y),max(1,int(self.radius)-3),1)
            for a in range(0,360,90):
                aa=math.radians(a+self.age*4)
                safe_set(surf,x+int(math.cos(aa)*self.radius),y+int(math.sin(aa)*self.radius),WHITE)
        elif self.kind=="micro":
            pygame.draw.line(surf,(100,255,171),(x-2,y),(x+5,y))
            safe_set(surf,x+3,y,WHITE)
        elif self.kind=="vulcan":
            pygame.draw.line(surf,(255,184,64),(x-3,y),(x+4,y),2)
            safe_set(surf,x+4,y,WHITE)
        elif self.kind=="rear":
            pygame.draw.rect(surf,(109,222,255),(x-3,y-2,7,4))
            safe_set(surf,x+2,y-1,WHITE)
        else:
            pygame.draw.rect(surf,(25,132,192),(x-4,y-3,8,6))
            pygame.draw.rect(surf,CYAN,(x-3,y-2,6,4))
            pygame.draw.rect(surf,WHITE,(x+1,y-1,3,2))


@dataclass
class Explosion:
    x: float
    y: float
    life: float=.42
    max_life: float=.42
    size: float=12.0
    color_mode: str="fire"

    def update(self,dt): self.life-=dt

    def draw(self,surf):
        t=1-max(0,self.life)/self.max_life
        x,y=int(self.x),int(self.y)
        r=max(1,int(self.size*(.25+t*.85)))
        if self.color_mode=="green": cols=[WHITE,(145,255,187),GREEN,DARK_GREEN]
        elif self.color_mode=="ice": cols=[WHITE,ICE,(75,142,205),(26,68,112)]
        elif self.color_mode=="void": cols=[WHITE,MAGENTA,PURPLE,(44,12,67)]
        else: cols=[WHITE,YELLOW,ORANGE,(128,35,27)]
        idx=min(3,int(t*4))
        pygame.draw.circle(surf,cols[idx],(x,y),r,1)
        if r>3: pygame.draw.circle(surf,cols[max(0,idx-1)],(x,y),max(1,r//2),1)
        # sparks/debris
        for i in range(4):
            a=i*math.pi/2+.7
            rr=int(r*(1.25+i*.12))
            safe_set(surf,x+int(math.cos(a)*rr),y+int(math.sin(a)*rr),cols[min(idx,2)])


@dataclass
class Pickup:
    x: float
    y: float
    kind: str="health"
    vx: float=-34
    phase: float=0.0
    life: float=9.0
    weapon_index: Optional[int]=None

    def update(self,dt,game):
        self.phase+=dt; self.life-=dt
        # Weapon rewards gently home to the player so progression cannot be missed.
        if self.kind=="weapon":
            self.x+=self.vx*dt
            self.y+=(game.player.y-self.y)*min(1,dt*1.2)
        else:
            self.x+=self.vx*dt
            self.y+=math.sin(self.phase*3)*5*dt

    def rect(self): return pygame.Rect(int(self.x-7),int(self.y-7),14,14)

    def draw(self,surf):
        x,y=int(self.x),int(self.y); flash=int(self.phase*10)%2==0
        if self.kind=="health":
            pygame.draw.rect(surf,(7,38,24),(x-6,y-6,12,12))
            col=(117,255,151) if flash else GREEN
            pygame.draw.rect(surf,col,(x-2,y-5,4,10)); pygame.draw.rect(surf,col,(x-5,y-2,10,4))
            safe_set(surf,x-1,y-4,WHITE)
        elif self.kind=="major_health":
            pygame.draw.rect(surf,(12,52,38),(x-7,y-7,14,14))
            pygame.draw.rect(surf,(68,218,130),(x-6,y-6,12,12),1)
            col=WHITE if flash else (137,255,188)
            pygame.draw.rect(surf,col,(x-2,y-6,4,12)); pygame.draw.rect(surf,col,(x-6,y-2,12,4))
            pygame.draw.circle(surf,(35,143,88),(x,y),7,1)
        elif self.kind=="life":
            # Miniature glowing player-ship core.
            pygame.draw.circle(surf,(45,65,100),(x,y),7)
            pygame.draw.circle(surf,YELLOW,(x,y),7,1)
            pygame.draw.polygon(surf,CYAN,[(x-5,y),(x+1,y-4),(x+6,y),(x+1,y+4)])
            pygame.draw.rect(surf,WHITE,(x+1,y-1,3,2))
            if flash: pygame.draw.circle(surf,(255,245,160),(x,y),9,1)
        elif self.kind=="weapon":
            idx=self.weapon_index or 0
            hue=[CYAN,ORANGE,(118,100,255),WHITE,MAGENTA,PURPLE,(88,230,255),GREEN,YELLOW,(137,211,255)][idx]
            pygame.draw.rect(surf,(18,24,42),(x-7,y-7,14,14))
            pygame.draw.rect(surf,hue,(x-6,y-6,12,12),1)
            pygame.draw.circle(surf,hue,(x,y),4,1)
            pygame.draw.line(surf,WHITE,(x-3,y),(x+3,y),1)
            if flash: safe_set(surf,x,y,WHITE)


class Hazard:
    """Stage-specific environmental hazard with telegraph and active phase."""
    def __init__(self,stage):
        self.stage=stage; self.age=0.0; self.life=2.0
        self.x=random.randint(70,235); self.y=random.randint(45,195)
        self.active=False
        self.kind={2:"lightning",3:"geyser",4:"current",5:"laser_gate",6:"spore",
                   7:"debris",8:"icefall",9:"rift",10:"surge"}.get(stage,"none")

    def update(self,dt,game):
        self.age+=dt; self.life-=dt
        self.active=self.age>.72
        if self.kind=="current" and self.active:
            game.player.y=clamp(game.player.y+math.sin(self.age*3)*14*dt,HUD_H+8,NATIVE_H-10)
        if self.kind in ("debris","icefall") and self.active:
            self.y+=65*dt
        if self.kind=="rift" and self.active:
            self.y+=math.sin(self.age*9)*20*dt

    def collides(self,rect):
        if not self.active: return False
        if self.kind=="lightning": return rect.colliderect(pygame.Rect(self.x-3,HUD_H,7,NATIVE_H-HUD_H))
        if self.kind=="geyser": return rect.colliderect(pygame.Rect(self.x-7,135,14,89))
        if self.kind=="laser_gate": return rect.colliderect(pygame.Rect(self.x-2,45,5,160))
        if self.kind in ("spore","debris","icefall","rift","surge"):
            return rect.colliderect(pygame.Rect(int(self.x-7),int(self.y-7),14,14))
        return False

    def draw(self,surf):
        x,y=int(self.x),int(self.y)
        tele=self.age<=.72
        if self.kind=="lightning":
            if tele: pygame.draw.line(surf,(118,106,75),(x,HUD_H),(x,NATIVE_H),1)
            else:
                pts=[(x,HUD_H),(x-5,59),(x+4,86),(x-4,120),(x+3,157),(x,211)]
                pygame.draw.lines(surf,WHITE,False,pts,2); pygame.draw.lines(surf,(98,194,255),False,pts,1)
        elif self.kind=="geyser":
            col=(104,38,14) if tele else LAVA
            pygame.draw.polygon(surf,col,[(x-7,220),(x-3,153),(x,135),(x+4,157),(x+7,220)])
            if not tele: pygame.draw.line(surf,YELLOW,(x,145),(x,214),2)
        elif self.kind=="laser_gate":
            col=(108,30,22) if tele else RED
            pygame.draw.line(surf,col,(x,45),(x,205),1 if tele else 3)
            pygame.draw.rect(surf,(68,72,78),(x-5,42,10,7)); pygame.draw.rect(surf,(68,72,78),(x-5,202,10,7))
        elif self.kind=="spore":
            pygame.draw.circle(surf,(118,44,103),(x,y),6)
            pygame.draw.circle(surf,GREEN,(x,y),2)
        elif self.kind=="debris":
            pygame.draw.polygon(surf,(94,70,61),[(x-6,y+5),(x-2,y-7),(x+7,y-2),(x+4,y+7)])
            pygame.draw.line(surf,ORANGE,(x-2,y-7),(x+2,y-10),1)
        elif self.kind=="icefall":
            pygame.draw.polygon(surf,ICE,[(x,y+8),(x-5,y-5),(x,y-8),(x+5,y-5)])
        elif self.kind=="rift":
            pygame.draw.line(surf,MAGENTA,(x-5,y-10),(x+4,y+11),2)
            pygame.draw.line(surf,(87,255,225),(x+3,y-9),(x-3,y+10),1)
        elif self.kind=="surge":
            pygame.draw.circle(surf,(156,33,88),(x,y),7,1); pygame.draw.circle(surf,YELLOW,(x,y),3)

# ---------------------------------------------------------------------------
# Weapon system / progression
# ---------------------------------------------------------------------------

class Weapon:
    NAMES=WEAPON_NAMES
    COOLDOWNS=[.095,.17,.15,.22,.39,.38,.16,.18,.26,.34]

    @classmethod
    def fire(cls,index,player,game):
        x=player.x+11; y=player.y; b=game.player_bullets
        if index==0:
            b.append(Bullet(x,y,184,0,7,"player","normal",3,1.7,weapon_index=index))
        elif index==1:
            for vy in (-58,0,58): b.append(Bullet(x,y,156,vy,5,"player","vulcan",2,1.45,weapon_index=index))
        elif index==2:
            b.append(Bullet(x,y,142,0,9,"player","wave",4,2.0,phase=player.weapon_phase,weapon_index=index)); player.weapon_phase+=1.37
        elif index==3:
            b.append(Bullet(x,y,178,0,17,"player","laser",2,.62,pierce=5,weapon_index=index))
        elif index==4:
            b.append(Bullet(x,y,108,0,20,"player","homing",3,3.1,weapon_index=index))
        elif index==5:
            b.append(Bullet(x,y,84,0,29,"player","grenade",5,2.6,splash=26,weapon_index=index))
        elif index==6:
            b.append(Bullet(x,y,154,0,7,"player","rear",2,1.7,weapon_index=index))
            b.append(Bullet(player.x-10,y,-148,0,8,"player","rear",2,1.1,weapon_index=index))
        elif index==7:
            b.append(Bullet(x,y,145,0,5,"player","normal",2,1.5,weapon_index=index))
            for ox,oy in player.orbiter_positions(): b.append(Bullet(ox+3,oy,172,0,3.8,"player","micro",1.5,1.25,weapon_index=index))
        elif index==8:
            b.append(Bullet(x,y,122,0,10,"player","flak",3,1.4,weapon_index=index))
        else:
            b.append(Bullet(x,y,75,0,15,"player","sonic",6,3.0,pierce=3,weapon_index=index))

        # Spatial emitter identity for multi-emitter weapons.
        if index==6:
            game.audio.play_weapon(index,clamp(player.x+24,0,NATIVE_W),.58)
            game.audio.play_weapon(index,clamp(player.x-24,0,NATIVE_W),.58)
        elif index==7:
            game.audio.play_weapon(index,player.x,.40)
            for ox,_ in player.orbiter_positions(): game.audio.play_weapon(index,ox,.42)
        else:
            game.audio.play_weapon(index,player.x)

# ---------------------------------------------------------------------------
# Player ship - richer original pixel-art construction
# ---------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.x=43.0; self.y=136.0; self.speed=106.0
        self.max_health=100; self.health=100; self.lives=3
        self.weapon=0; self.unlocked=[True]+[False]*9
        self.fire_timer=0.0; self.invuln=1.3; self.weapon_phase=0.0; self.orbit_phase=0.0
        self.bank=0.0

    def reset_position(self): self.x,self.y=43.0,136.0; self.invuln=1.7
    def rect(self): return pygame.Rect(int(self.x-7),int(self.y-5),14,10)

    def orbiter_positions(self):
        return [(self.x+math.cos(a)*13,self.y+math.sin(a)*10) for a in (self.orbit_phase,self.orbit_phase+math.pi)]

    def cycle_weapon(self,direction):
        idx=self.weapon
        for _ in range(10):
            idx=(idx+direction)%10
            if self.unlocked[idx]: self.weapon=idx; return

    def unlock(self,index):
        if index is None: return False
        fresh=not self.unlocked[index]; self.unlocked[index]=True
        if fresh: self.weapon=index
        return fresh

    def update(self,dt,keys,game):
        dx=(1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0)-(1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        dy=(1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0)-(1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        if dx or dy:
            m=math.hypot(dx,dy); dx/=m; dy/=m
        self.bank=lerp(self.bank,dy,min(1,dt*8))
        self.x=clamp(self.x+dx*self.speed*dt,11,NATIVE_W-16)
        self.y=clamp(self.y+dy*self.speed*dt,HUD_H+9,NATIVE_H-11)
        self.fire_timer-=dt; self.invuln=max(0,self.invuln-dt); self.orbit_phase=(self.orbit_phase+dt*4.4)%(math.tau)
        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.fire_timer<=0:
            Weapon.fire(self.weapon,self,game); self.fire_timer=Weapon.COOLDOWNS[self.weapon]

    def hit(self,damage,game):
        if getattr(game,"god_mode",False):
            self.invuln=max(self.invuln,.12)
            return
        if self.invuln>0:return
        self.health-=damage; self.invuln=.88
        game.audio.play_sfx("hit",self.x,.8)
        game.explosions.append(Explosion(self.x,self.y,.25,.25,10))
        if self.health<=0:
            self.lives-=1
            game.stage_deaths += 1
            if game.boss is not None:
                game.boss.no_death_bonus = False
            if self.lives<=0: game.game_over()
            else:
                self.health=self.max_health; self.reset_position(); game.enemy_bullets.clear()

    def draw(self,surf):
        if self.invuln>0 and int(self.invuln*14)%2==0:return
        x,y=int(self.x),int(self.y)
        # Palette-indexed authored ship sprite. Banking shifts the sprite by one
        # pixel instead of deforming its silhouette with arbitrary polygons.
        bank=int(round(self.bank))
        pal={
            '1':(10,27,57), '2':(25,61,104), '3':(43,107,151),
            '4':(72,170,199), '5':(132,223,235), '6':WHITE,
            '7':ORANGE, '8':(119,236,255),
        }
        draw_indexed_sprite(surf,PLAYER_PIXELS,x-15,y-6+bank,pal)
        # Animated exhaust is a separate metasprite/effect layer.
        flame=4+(pygame.time.get_ticks()//55)%4
        for fx in range(flame):
            col=YELLOW if fx<2 else ORANGE if fx<4 else (149,45,50)
            safe_set(surf,x-14-fx,y,col)
            if fx<3:safe_set(surf,x-13-fx,y+1,col)
        # Canopy gleam and weapon hardpoint flash add sub-frame life.
        safe_set(surf,x+2,y-3+bank,WHITE)
        if self.fire_timer>0 and self.fire_timer<.045:
            safe_set(surf,x+13,y,WHITE); safe_set(surf,x+14,y,CYAN)
        if self.weapon==7:
            for ox,oy in self.orbiter_positions():
                ox,oy=int(ox),int(oy)
                orb=["..1..",".232.","12321",".242.","..1.."]
                draw_indexed_sprite(surf,orb,ox-2,oy-2,{'1':(11,45,61),'2':(43,142,150),'3':WHITE,'4':GREEN})

# ---------------------------------------------------------------------------
# Enemy archetypes and stage-local visual families
# ---------------------------------------------------------------------------

ARCHETYPES=("interceptor","heavy","artillery","ambusher")

class Enemy:
    def __init__(self,x,y,stage,wave_id,slot,archetype="interceptor",formation="sine",from_rear=False):
        self.x=float(x); self.base_y=float(y); self.y=float(y)
        self.stage=stage; self.wave_id=wave_id; self.slot=slot; self.archetype=archetype; self.formation=formation
        self.age=slot*.13; self.phase=slot*.82; self.from_rear=from_rear
        mult={"interceptor":.76,"heavy":1.55,"artillery":1.12,"ambusher":.88}[archetype]
        self.max_health=(13+stage*4.1)*mult; self.health=self.max_health
        self.speed=(54+stage*3.2)*({"interceptor":1.25,"heavy":.62,"artillery":.72,"ambusher":1.35}[archetype])
        if from_rear:self.speed*=-1
        self.fire_timer=.5+random.random()*1.0; self.dead=False; self.escaped=False
        self.stop_x=random.randint(165,218); self.charge_done=False
        self.radius={"interceptor":6,"heavy":9,"artillery":8,"ambusher":7}[archetype]

    @property
    def name(self): return STAGES[self.stage-1].enemy_names[ARCHETYPES.index(self.archetype)]

    def rect(self):
        r=self.radius; return pygame.Rect(int(self.x-r),int(self.y-r*.7),r*2,int(r*1.4))

    def damage_multiplier(self,weapon_index):
        return WEAPON_VS_ARCHETYPE[self.archetype][weapon_index]

    def update(self,dt,game):
        self.age+=dt
        if self.archetype=="interceptor":
            direction=1 if self.from_rear else -1
            self.x+=direction*abs(self.speed)*dt
            self.y=self.base_y+math.sin(self.age*3.3+self.phase)*(9+self.stage*.45)
        elif self.archetype=="heavy":
            self.x-=abs(self.speed)*dt
            self.y=self.base_y+math.sin(self.age*1.4+self.phase)*5
        elif self.archetype=="artillery":
            if self.x>self.stop_x:self.x-=abs(self.speed)*dt
            else:self.x+=math.sin(self.age*.8+self.phase)*5*dt
            self.y=self.base_y+math.sin(self.age*1.7+self.phase)*7
        else: # ambusher
            if not self.charge_done:
                direction=1 if self.from_rear else -1
                self.x+=direction*abs(self.speed)*dt
                self.y+=math.sin(self.age*5+self.phase)*24*dt
                if (not self.from_rear and self.x<145) or (self.from_rear and self.x>100): self.charge_done=True
            else:
                # curve sharply across the player's vertical plane
                self.x-=abs(self.speed)*.65*dt
                self.y+=(game.player.y-self.y)*dt*1.15

        self.fire_timer-=dt
        if self.fire_timer<=0 and 4<self.x<NATIVE_W-8 and game.state=="play":
            self.fire_timer={"interceptor":1.5,"heavy":1.15,"artillery":.82,"ambusher":1.35}[self.archetype]-min(.35,self.stage*.025)+random.random()*.35
            self.fire(game)

        if self.x<-22 or self.x>NATIVE_W+28 or self.y<-24 or self.y>NATIVE_H+24:
            self.dead=True; self.escaped=True; game.wave_enemy_escaped(self.wave_id)

    def fire(self,game):
        sp=60+self.stage*4.5
        if self.archetype=="interceptor":
            a=angle_to(game.player.x-self.x,game.player.y-self.y)
            game.enemy_bullets.append(Bullet(self.x,self.y,math.cos(a)*sp,math.sin(a)*sp,8,"enemy","normal",2,5))
        elif self.archetype=="heavy":
            base=angle_to(game.player.x-self.x,game.player.y-self.y)
            for d in (-.16,0,.16):
                a=base+d; game.enemy_bullets.append(Bullet(self.x,self.y,math.cos(a)*sp*.82,math.sin(a)*sp*.82,10,"enemy","normal",2.5,5))
        elif self.archetype=="artillery":
            # Stage-specific artillery: water/station use mines, later stages track.
            if self.stage in (4,5,6):
                game.enemy_bullets.append(Bullet(self.x-5,self.y,-34,math.sin(self.age)*8,12,"enemy","mine",4,5))
            else:
                a=angle_to(game.player.x-self.x,game.player.y-self.y)
                kind="tracking" if self.stage>=7 else "normal"
                game.enemy_bullets.append(Bullet(self.x,self.y,math.cos(a)*sp*.9,math.sin(a)*sp*.9,11,"enemy",kind,3,6))
        else:
            # Assault/ambusher fires backward or forward depending entry vector.
            direction=-1 if self.x>game.player.x else 1
            game.enemy_bullets.append(Bullet(self.x,self.y,direction*sp,0,10,"enemy","normal",2.5,4))

    def hit(self,damage,game,weapon_index=0):
        if self.dead:return False
        self.health-=damage*self.damage_multiplier(weapon_index)
        if self.health<=0:
            self.dead=True
            game.score+=int((90+self.stage*24)*({"interceptor":1,"heavy":2,"artillery":1.6,"ambusher":1.4}[self.archetype]))
            game.audio.play_sfx("boom",self.x,.65)
            mode="ice" if self.stage==8 else "void" if self.stage in (6,9,10) else "fire"
            game.explosions.append(Explosion(self.x,self.y,.36,.36,self.radius*1.8,mode))
            game.wave_enemy_destroyed(self.wave_id,self.x,self.y,self.archetype)
            return True
        return False

    def draw(self,surf):
        x,y=int(self.x),int(self.y); theme=STAGES[self.stage-1].theme
        p=STAGES[self.stage-1].palette
        # Material-aware indexed palette. Stage 3 deliberately uses cool rim
        # lighting and an almost-black obsidian outline so enemies never merge
        # into the orange/red cavern texture.
        if theme=='lava':
            pal={'1':(3,5,14),'2':(30,24,36),'3':(61,43,52),'4':(101,166,190),'5':(184,231,235),'8':(255,119,34)}
        elif theme=='water':
            pal={'1':(1,21,35),'2':(6,58,76),'3':(13,104,117),'4':(43,178,181),'5':(150,255,235),'8':(82,224,255)}
        elif theme=='ice':
            pal={'1':(7,25,48),'2':(37,80,117),'3':(76,139,172),'4':(139,210,233),'5':WHITE,'8':(91,183,255)}
        elif theme=='hive':
            pal={'1':(28,7,30),'2':(73,18,64),'3':(123,34,91),'4':(177,58,118),'5':(142,255,177),'8':(72,231,137)}
        elif theme=='veil':
            pal={'1':(12,5,28),'2':(58,24,104),'3':(108,39,155),'4':(207,63,216),'5':(104,255,228),'8':WHITE}
        elif theme=='omega':
            pal={'1':(14,5,16),'2':(63,15,46),'3':(118,24,67),'4':(207,43,98),'5':(255,220,157),'8':RED}
        else:
            pal={'1':(8,17,35),'2':p[0],'3':p[1],'4':p[2],'5':p[3],'8':ORANGE}
        rows=ENEMY_PIXEL_BANK[self.archetype]
        draw_indexed_sprite(surf,rows,x-len(rows[0])//2,y-len(rows)//2,pal,flip_x=self.from_rear)
        # Stage-specific authored accents, kept sparse so silhouettes remain clean.
        if theme=='atmosphere':
            safe_set(surf,x-3,y-5,pal['5']); safe_set(surf,x+3,y+5,pal['4'])
        elif theme=='lava':
            safe_set(surf,x-5,y-4,pal['5']); safe_set(surf,x-4,y-3,pal['4'])
            safe_set(surf,x,y,pal['8'])
        elif theme=='station':
            safe_set(surf,x-5,y+4,(255,177,67)); safe_set(surf,x+4,y-3,(128,231,243))
        elif theme=='city':
            safe_set(surf,x-4,y-4,(233,184,75)); safe_set(surf,x+2,y+3,(195,77,50))
        elif theme=='veil':
            safe_set(surf,x-8,y-6,pal['5']); safe_set(surf,x+8,y+6,pal['4'])

# ---------------------------------------------------------------------------
# Ten stage-specific bosses
# ---------------------------------------------------------------------------

class Boss:
    def __init__(self,stage):
        self.stage=stage
        self.profile=STAGES[stage-1]
        self.x=218.0; self.y=116.0; self.age=0.0; self.intro=1.8; self.dead=False
        self.phase=1; self.timer_a=.8; self.timer_b=1.8; self.timer_c=2.8
        self.flash=0.0; self.shell=False; self.teleport_flash=0.0
        self.radius=[28,30,31,31,29,31,34,33,30,38][stage-1]
        self.max_health=[520,660,760,820,900,1020,1160,1280,1450,2500][stage-1]
        self.health=float(self.max_health)
        self.no_death_bonus=True
        self.component_state=0

    def rect(self):
        r=self.radius
        # Collision silhouettes track the larger authored metasprites.
        if self.stage==1:return pygame.Rect(int(self.x-40),int(self.y-24),82,48)
        if self.stage==2:return pygame.Rect(int(self.x-45),int(self.y-33),92,65)
        if self.stage==3:return pygame.Rect(int(self.x-38),int(self.y-39),77,70)
        if self.stage==4:return pygame.Rect(int(self.x-24),int(self.y-25),86,50)
        if self.stage==8:return pygame.Rect(int(self.x-r-16),int(self.y-r),int(r*2+28),int(r*2))
        return pygame.Rect(int(self.x-r),int(self.y-r),int(r*2),int(r*2))

    def damage_multiplier(self,weapon_index):
        # Stage-specific preferences. Modest, readable through mechanics.
        weak={1:{1:1.25},2:{2:1.25},3:{3:1.45,5:1.2},4:{4:1.45,2:1.15},5:{3:1.3,5:1.3},
              6:{5:1.25,6:1.3},7:{3:1.25,8:1.25},8:{5:1.2,8:1.4},9:{9:1.4,4:1.2},10:{0:1.0,1:1.0,2:1.0,3:1.1,4:1.1,5:1.1,6:1.1,7:1.1,8:1.1,9:1.2}}
        mult=weak.get(self.stage,{}).get(weapon_index,1.0)
        # Pyroclast's obsidian shell strongly favors penetrating laser/grenade.
        if self.stage==3 and self.shell:
            mult*=1.0 if weapon_index in (3,5) else .58
        # Citadel shield cycle favors explosive/laser weapons.
        if self.stage==5 and self.phase==1 and weapon_index not in (3,5): mult*=.72
        return mult

    def hit(self,damage,game,weapon_index=0):
        if self.intro>0 or self.dead:return False
        self.health-=damage*self.damage_multiplier(weapon_index); self.flash=.08
        if self.health<=0:
            self.dead=True; game.score+=6000+self.stage*1700
            game.audio.play_sfx("big_boom",self.x,1.0)
            count=20 if self.stage<10 else 42
            mode="ice" if self.stage==8 else "void" if self.stage in (6,9,10) else "fire"
            for i in range(count):
                a=i*math.tau/count; rr=random.uniform(3,self.radius*1.2)
                game.explosions.append(Explosion(self.x+math.cos(a)*rr,self.y+math.sin(a)*rr,
                                                 .35+random.random()*.7,1.0,8+random.random()*14,mode))
            return True
        return False

    def _bullet(self,game,a,speed=80,damage=10,kind="normal",radius=2.5,origin=None):
        ox,oy=origin if origin else (self.x-self.radius*.45,self.y)
        game.enemy_bullets.append(Bullet(ox,oy,math.cos(a)*speed,math.sin(a)*speed,damage,"enemy",kind,radius,7))

    def aimed(self,game,count=3,spread=.15,speed=85,kind="normal",origin=None):
        base=angle_to(game.player.x-self.x,game.player.y-self.y); mid=(count-1)/2
        for i in range(count):self._bullet(game,base+(i-mid)*spread,speed,10,kind,2.5,origin)

    def ring(self,game,count=12,speed=65,offset=0,kind="normal"):
        for i in range(count):self._bullet(game,offset+i*math.tau/count,speed,9,kind,2.3,(self.x,self.y))

    def fan(self,game,angles,speed=75,kind="normal"):
        for a in angles:self._bullet(game,a,speed,10,kind)

    def update(self,dt,game):
        self.age+=dt; self.flash=max(0,self.flash-dt); self.teleport_flash=max(0,self.teleport_flash-dt)
        if self.intro>0:
            self.intro-=dt; self.x+=(190-self.x)*min(1,dt*2.2); return
        ratio=self.health/self.max_health
        self.phase=1 if ratio>.66 else 2 if ratio>.33 else 3
        self.timer_a-=dt; self.timer_b-=dt; self.timer_c-=dt
        getattr(self,f"update_{self.profile.boss_kind}")(dt,game)

    # 1: carrier - horizontal/vertical maneuver + fighter launches + missile fans.
    def update_carrier(self,dt,game):
        self.x+=(190+math.sin(self.age*.7)*7-self.x)*dt*1.8
        self.y=112+math.sin(self.age*(1.4+self.phase*.18))*49
        if self.timer_a<=0:
            self.timer_a=max(.36,.78-self.phase*.11); self.aimed(game,2+self.phase,.12,82+self.phase*8)
        if self.timer_b<=0:
            self.timer_b=2.3-self.phase*.25
            game.spawn_boss_add("interceptor",self.x-18,self.y-14); game.spawn_boss_add("interceptor",self.x-18,self.y+14)

    # 2: bastion - hovers, lightning columns, rotating fan.
    def update_bastion(self,dt,game):
        self.x+=(193+math.sin(self.age*.45)*5-self.x)*dt*1.5; self.y=105+math.sin(self.age*.9)*33
        if self.timer_a<=0:
            self.timer_a=.72-self.phase*.08
            self.fan(game,[math.pi+d for d in (-.48,-.24,0,.24,.48)],88+self.phase*7)
        if self.timer_b<=0:
            self.timer_b=2.0-self.phase*.2
            # Lightning-style vertical projectiles aimed at player's x path.
            for yy in (50,92,134,176):
                a=angle_to(game.player.x-self.x,yy-self.y); self._bullet(game,a,95,11,"tracking",2.5)

    # 3: Pyroclast - lava monster toggles hardened shell and erupts.
    def update_pyroclast(self,dt,game):
        self.shell=(int(self.age/3.0)%2)==1
        self.x+=(188+math.sin(self.age*.55)*8-self.x)*dt*1.7
        self.y=143+math.sin(self.age*1.2)*37
        if self.timer_a<=0:
            self.timer_a=.62 if not self.shell else .92
            base=math.pi
            for d in (-.55,-.28,0,.28,.55):self._bullet(game,base+d,72+self.phase*7,11,"lava",3)
        if self.timer_b<=0:
            self.timer_b=2.25
            game.hazards.append(Hazard(3))
        if self.timer_c<=0:
            self.timer_c=3.1
            self.ring(game,10+self.phase*2,60,self.age*.2,"lava")

    # 4: Leviathan - diving serpentine passes and torpedo tracking attacks.
    def update_leviathan(self,dt,game):
        dive=math.sin(self.age*.72)
        self.x=187+math.sin(self.age*.62)*22
        self.y=112+dive*72
        if self.timer_a<=0:
            self.timer_a=.78-self.phase*.09; self.aimed(game,2+self.phase,.18,75+self.phase*8,"tracking")
        if self.timer_b<=0:
            self.timer_b=2.4-self.phase*.25
            game.spawn_boss_add("ambusher",self.x-12,self.y)
        if self.timer_c<=0:
            self.timer_c=2.8; game.hazards.append(Hazard(4))

    # 5: Sentinel - mostly stationary modular fortress, shield then component loss.
    def update_sentinel(self,dt,game):
        self.x+=(194-self.x)*dt*2; self.y=112+math.sin(self.age*.65)*12
        self.component_state=0 if self.phase==1 else 1 if self.phase==2 else 2
        if self.timer_a<=0:
            self.timer_a=.55-self.phase*.07
            origins=[(self.x-18,self.y-16),(self.x-18,self.y+16)]
            for o in origins:self.aimed(game,2,.11,96+self.phase*6,"normal",o)
        if self.timer_b<=0:
            self.timer_b=1.75
            self.ring(game,12+self.phase*3,67,self.age*.42)
        if self.timer_c<=0:
            self.timer_c=2.7; game.hazards.append(Hazard(5))

    # 6: Mother Null - organic pulsing, spawn swarm, mines/spores.
    def update_mother(self,dt,game):
        self.x=194+math.sin(self.age*.5)*10; self.y=112+math.sin(self.age*1.1)*45
        if self.timer_a<=0:
            self.timer_a=.65-self.phase*.08; self.aimed(game,3+self.phase,.15,74+self.phase*8,"tracking")
        if self.timer_b<=0:
            self.timer_b=1.7
            for yy in (-18,0,18):game.spawn_boss_add("ambusher",self.x-10,self.y+yy)
        if self.timer_c<=0:
            self.timer_c=1.9; game.hazards.append(Hazard(6))

    # 7: Ares-IX - cyborg siege mech, dashes and weapon-arm barrages.
    def update_ares(self,dt,game):
        target_x=174 if self.phase>=2 else 191
        self.x+=(target_x+math.sin(self.age*.7)*8-self.x)*dt*2
        self.y=112+math.sin(self.age*(1.25+self.phase*.2))*54
        if self.timer_a<=0:
            self.timer_a=.43-self.phase*.05
            self.aimed(game,4+self.phase,.10,112+self.phase*7,"normal",(self.x-24,self.y-13))
        if self.timer_b<=0:
            self.timer_b=1.45
            self.fan(game,[math.pi+d for d in (-.8,-.4,0,.4,.8)],98,"normal")
        if self.timer_c<=0:
            self.timer_c=2.4; game.hazards.append(Hazard(7))

    # 8: Cryon Wyrm - segmented serpent traverses the vertical axis and ice volleys.
    def update_wyrm(self,dt,game):
        self.x=185+math.sin(self.age*.8)*24; self.y=112+math.sin(self.age*1.55)*70
        if self.timer_a<=0:
            self.timer_a=.58-self.phase*.06
            base=angle_to(game.player.x-self.x,game.player.y-self.y)
            for d in (-.35,-.17,0,.17,.35):self._bullet(game,base+d,92+self.phase*6,10,"ice",3)
        if self.timer_b<=0:
            self.timer_b=2.0; game.hazards.append(Hazard(8))
        if self.timer_c<=0:
            self.timer_c=2.8; self.ring(game,14+self.phase*2,72,self.age*.5,"ice")

    # 9: Sovereign - teleportation, counter-rotating geometry, dimensional rifts.
    def update_sovereign(self,dt,game):
        if self.timer_c<=0:
            self.timer_c=max(1.1,2.35-self.phase*.35); self.teleport_flash=.18
            self.x=random.randint(155,216); self.y=random.randint(48,180)
        else:
            self.x+=math.sin(self.age*1.7)*10*dt; self.y+=math.cos(self.age*1.3)*13*dt
        if self.timer_a<=0:
            self.timer_a=.48-self.phase*.055
            self.ring(game,10+self.phase*4,82,self.age*1.1)
            if self.phase>=2:self.ring(game,7+self.phase*2,63,-self.age*.8)
        if self.timer_b<=0:
            self.timer_b=1.6; self.aimed(game,3+self.phase,.21,112,"tracking")
            game.hazards.append(Hazard(9))

    # 10: OMEGA - mastery boss with radically changing phases and prior motifs.
    def update_omega(self,dt,game):
        if self.phase==1:
            self.x+=(194-self.x)*dt*1.8; self.y=112+math.sin(self.age*1.1)*43
        elif self.phase==2:
            self.x+=(180+math.sin(self.age*.9)*14-self.x)*dt*2; self.y=112+math.sin(self.age*2.0)*65
        else:
            self.x=174+math.sin(self.age*1.6)*20; self.y=112+math.sin(self.age*2.8)*76
        if self.timer_a<=0:
            self.timer_a=[.48,.32,.22][self.phase-1]
            self.aimed(game,4+self.phase*2,.09,120+self.phase*10,"normal")
        if self.timer_b<=0:
            self.timer_b=[1.45,.90,.62][self.phase-1]
            self.ring(game,16+self.phase*6,78+self.phase*8,self.age*(.6+self.phase*.25))
            if self.phase>=2:self.ring(game,10+self.phase*3,62,-self.age*.9,"tracking" if self.phase==3 else "normal")
        if self.timer_c<=0:
            self.timer_c=[2.5,1.6,.95][self.phase-1]
            game.hazards.append(Hazard(10))
            if self.phase>=2:game.spawn_boss_add(random.choice(ARCHETYPES),self.x-25,self.y+random.randint(-25,25))

    # -------------------------- boss art ------------------------------

    def draw(self,surf):
        getattr(self,f"draw_{self.profile.boss_kind}")(surf)
        self._artist_detail_overlay(surf)
        if self.flash>0:
            # sparse white hit highlights without blanking the art
            x,y=int(self.x),int(self.y)
            pygame.draw.circle(surf,WHITE,(x-5,y-3),3,1)
        if self.teleport_flash>0:
            pygame.draw.circle(surf,(165,255,239),(int(self.x),int(self.y)),self.radius+6,1)

    def _artist_detail_overlay(self,surf):
        """Small authored material tiles and rim-light clusters shared by boss art.

        Stage 2 is fully rebuilt as a metasprite; the other nine retain their
        successful unique silhouettes but receive denser pixel-authored facial,
        mechanical, or organic focal detail in this pass.
        """
        if self.profile.boss_kind in ('bastion','carrier','pyroclast','leviathan'): return
        tile=BOSS_DETAIL_TILES.get(self.profile.boss_kind)
        if not tile:return
        x,y=int(self.x),int(self.y)
        theme=self.profile.theme
        if theme=='lava': pal={'1':(12,5,6),'2':(86,23,14),'3':LAVA,'4':YELLOW}
        elif theme=='water': pal={'1':(2,28,39),'2':(10,91,103),'3':(59,205,198),'4':WHITE}
        elif theme=='ice': pal={'1':(10,31,55),'2':(55,114,151),'3':ICE,'4':WHITE}
        elif theme in ('hive','omega'): pal={'1':(27,7,25),'2':(102,25,73),'3':(223,59,119),'4':(179,255,191)}
        elif theme=='veil': pal={'1':(17,7,37),'2':(86,29,132),'3':MAGENTA,'4':(103,255,225)}
        else: pal={'1':(12,21,34),'2':(54,82,101),'3':self.profile.palette[2],'4':WHITE}
        draw_indexed_sprite(surf,tile,x-2,y-2,pal)
        # Directional rim highlight changes with stage lighting.
        rim=pal['4'] if self.stage in (3,4,8,9) else self.profile.palette[2]
        for ox,oy in [(-self.radius+3,-7),(-self.radius+4,-6),(-self.radius+5,10)]:
            safe_set(surf,x+ox,y+oy,rim)

    def _damage_fx(self,surf,points):
        ratio=self.health/self.max_health
        x,y=int(self.x),int(self.y)
        count=0 if ratio>.75 else 1 if ratio>.5 else 2 if ratio>.25 else 4
        for px,py in points[:count]:
            pygame.draw.line(surf,ORANGE,(x+px,y+py),(x+px+3,y+py-4),1)
            safe_set(surf,x+px+1,y+py-2,YELLOW)

    def draw_carrier(self,surf):
        x,y=int(self.x),int(self.y)
        pal={'1':(6,15,34),'2':(17,37,70),'3':(35,67,108),'4':(61,108,151),
             '5':(91,170,193),'6':(157,224,232),'7':(255,141,54),'8':CYAN,'9':MAGENTA}
        # Main flight-deck body.
        draw_indexed_sprite(surf,CARRIER_BODY,x-38,y-7,pal)
        draw_indexed_sprite(surf,CARRIER_BRIDGE,x-4,y-19,pal)
        # Two clearly recessed fighter bays.
        draw_indexed_sprite(surf,CARRIER_HANGAR,x-28,y-14,pal)
        draw_indexed_sprite(surf,CARRIER_HANGAR,x-28,y+9,pal)
        # Long dorsal and ventral fins emphasize a capital-ship silhouette.
        pygame.draw.line(surf,pal['4'],(x-7,y-16),(x+15,y-27),3)
        pygame.draw.line(surf,pal['2'],(x-8,y+15),(x+14,y+26),3)
        # Four hot engine nozzles.
        for ey in (-8,-3,4,9):
            pygame.draw.rect(surf,pal['2'],(x+31,y+ey-1,8,3))
            pygame.draw.line(surf,pal['8'],(x+38,y+ey),(x+45,y+ey),2)
            safe_set(surf,x+46,y+ey,WHITE)
        # Bridge lamps / identification strip.
        for wx in (-1,4,9): safe_set(surf,x+wx,y-16,pal['6'])
        pygame.draw.line(surf,pal['9'],(x-25,y),(x-12,y),1)
        self._damage_fx(surf,[(-24,-10),(12,12),(-5,-20),(24,-5)])

    def draw_bastion(self,surf):
        x,y=int(self.x),int(self.y)
        # Hand-authored metasprite fortress. It faces left: cannon/nose at left,
        # command tower above, lift turbines around the hull, engines at right.
        pal={'1':(10,18,29),'2':(27,45,61),'3':(54,78,94),'4':(91,125,139),
             '5':(149,189,200),'6':(218,235,235),'7':(225,159,55),'8':(71,205,238)}
        hx=x-33; hy=y-7
        # Structural trusses visibly connect the lift pods to the armored hull.
        for ax,ay,bx,by in ((x-8,y-6,x-8,y-17),(x+13,y-5,x+14,y-13),(x-8,y+7,x-8,y+16),(x+13,y+6,x+14,y+13)):
            pygame.draw.line(surf,pal['1'],(ax,ay),(bx,by),5)
            pygame.draw.line(surf,pal['4'],(ax,ay),(bx,by),2)
        draw_indexed_sprite(surf,BASTION_HULL,hx,hy,pal)
        draw_indexed_sprite(surf,BASTION_TOWER,x-4,y-22,pal)
        turbine=BASTION_TURBINE_A if int(self.age*8)%2==0 else BASTION_TURBINE_B
        for ox,oy in ((-8,-22),(14,-18),(-8,13),(14,9)):
            draw_indexed_sprite(surf,turbine,x+ox-6,y+oy-5,pal)
        # Main rail cannon with visible barrel and muzzle capacitor.
        cannon=["11111111111111","12222223333447","11111111111111"]
        draw_indexed_sprite(surf,cannon,x-44,y-1,pal)
        safe_set(surf,x-45,y,WHITE if int(self.age*5)%2 else pal['7'])
        # Rear engines and downward lift exhaust.
        for ey in (-4,3):
            pygame.draw.line(surf,pal['8'],(x+23,y+ey),(x+30,y+ey),2)
            safe_set(surf,x+31,y+ey,WHITE)
        for ox in (-8,14):
            safe_set(surf,x+ox,y+20,pal['8']); safe_set(surf,x+ox,y+21,(54,113,154))
        # Lightning rods / antenna mast make the military-platform silhouette obvious.
        pygame.draw.line(surf,pal['5'],(x+2,y-22),(x+2,y-31),1)
        pygame.draw.line(surf,pal['5'],(x+9,y-20),(x+12,y-27),1)
        safe_set(surf,x+2,y-32,WHITE if int(self.age*6)%3==0 else pal['8'])
        # Warning lamps/windows.
        for wx in (-12,-5,2,9): safe_set(surf,x+wx,y-3,pal['7'])
        self._damage_fx(surf,[(-22,-5),(11,9),(2,-20),(-7,14)])

    def draw_pyroclast(self,surf):
        x,y=int(self.x),int(self.y)
        # Strong readable material ramp: almost-black silhouette, cool obsidian
        # edge, then volcanic rock and extremely bright internal magma.
        if self.shell:
            pal={'1':(8,6,7),'2':(28,27,28),'3':(56,51,49),'4':(92,78,68),
                 '5':(131,104,82),'6':(190,82,38),'7':(255,91,20),'8':(181,225,239)}
        else:
            pal={'1':(15,5,5),'2':(48,12,8),'3':(88,22,11),'4':(139,35,12),
                 '5':(204,56,13),'6':(255,100,18),'7':(255,209,58),'8':WHITE}
        # Torso first, with a slight breathing/heat heave.
        heave=int(math.sin(self.age*2.1)*1.5)
        draw_indexed_sprite(surf,PYRO_TORSO,x-15,y-6+heave,pal)
        # Horned skull sits above the body and moves independently.
        head_y=y-25+int(math.sin(self.age*2.7)*2)
        draw_indexed_sprite(surf,PYRO_HEAD,x-9,head_y,pal)
        # Massive forelimbs swing instead of staying as rigid triangles.
        arm_swing=int(math.sin(self.age*2.0)*3)
        draw_indexed_sprite(surf,PYRO_ARM_L,x-32,y-3+arm_swing,pal)
        draw_indexed_sprite(surf,PYRO_ARM_R,x+17,y-3-arm_swing,pal)
        draw_indexed_sprite(surf,PYRO_CLAW,x-35,y+12+arm_swing,pal)
        draw_indexed_sprite(surf,PYRO_CLAW,x+29,y+12-arm_swing,pal,flip_x=True)
        # Jaw / eye focal points make the creature's face readable instantly.
        eye_col=(170,235,255) if self.shell else WHITE
        safe_set(surf,x-4,head_y+6,eye_col); safe_set(surf,x+5,head_y+6,eye_col)
        pygame.draw.line(surf,(12,4,4),(x-4,head_y+12),(x+6,head_y+12),2)
        for tooth_x in (-2,2,6):
            safe_set(surf,x+tooth_x,head_y+13,(230,222,180))
        # Animated magma channels glow through the chest/arms. In shell mode
        # they contract and cool, visually communicating the resistance cycle.
        fissure=(122,213,232) if self.shell else (255,224,75)
        fissure2=(73,137,167) if self.shell else (255,92,16)
        channels=[(-7,-1,-3,7),(4,-2,8,6),(-1,7,2,14),(-21,4,-18,10),(22,3,25,10)]
        for i,(ax,ay,bx,by) in enumerate(channels):
            if self.shell and i%2: continue
            pygame.draw.line(surf,fissure2,(x+ax,y+ay+heave),(x+bx,y+by+heave),2)
            safe_set(surf,x+bx,y+by+heave,fissure)
        # Radiant core in the sternum rather than an ambiguous floating circle.
        core_r=4+int((math.sin(self.age*4.5)+1))
        pygame.draw.circle(surf,(35,8,5),(x,y+4+heave),core_r+3)
        pygame.draw.circle(surf,fissure2,(x,y+4+heave),core_r)
        safe_set(surf,x-1,y+3+heave,fissure)
        # Hardened-state outline reads as cooled obsidian armor.
        if self.shell:
            pygame.draw.arc(surf,(135,165,174),(x-20,y-13,41,40),.15,3.0,1)
            pygame.draw.arc(surf,(79,101,112),(x-20,y-13,41,40),3.2,6.0,1)
        self._damage_fx(surf,[(-15,-3),(13,12),(-2,-20),(22,3)])

    def draw_leviathan(self,surf):
        x,y=int(self.x),int(self.y)
        pal={'1':(1,19,31),'2':(4,43,58),'3':(8,77,91),'4':(14,116,124),
             '5':(33,163,161),'6':(72,211,199),'7':(137,255,230),'8':WHITE}
        # Segmented body travels behind the head with alternating pitch.
        for i in range(6,0,-1):
            sx=x+i*10
            sy=y+int(math.sin(self.age*3.0-i*.7)*9)
            draw_indexed_sprite(surf,LEVIATHAN_SEGMENT,sx-6,sy-4,pal)
            # dorsal bioluminescent node
            safe_set(surf,sx,sy-3,pal['7'])
        # Large predator head with an unmistakable snout/jaw.
        draw_indexed_sprite(surf,LEVIATHAN_HEAD,x-20,y-9,pal)
        # Swept fins are small authored-looking clusters attached to the body.
        fin=["...1...","..121..",".12321.","1234321","..121.."]
        draw_indexed_sprite(surf,fin,x+2,y-17,pal)
        draw_indexed_sprite(surf,fin,x+2,y+13,pal,flip_x=True)
        # Open black jaw with bright tooth pixels.
        pygame.draw.line(surf,pal['1'],(x-18,y),(x-7,y),4)
        for tx in (-16,-12,-8): safe_set(surf,x+tx,y-2,pal['8'])
        # Eye and lure.
        pygame.draw.circle(surf,pal['7'],(x-3,y-4),3)
        safe_set(surf,x-4,y-5,pal['8'])
        pygame.draw.line(surf,pal['4'],(x+7,y-8),(x+12,y-18),1)
        pygame.draw.circle(surf,pal['7'],(x+13,y-19),2)
        self._damage_fx(surf,[(-6,10),(11,-10),(-17,-5),(15,5)])

    def draw_sentinel(self,surf):
        x,y=int(self.x),int(self.y)
        # Modular rotating fortress.
        pygame.draw.circle(surf,(37,46,55),(x,y),27); pygame.draw.circle(surf,(90,102,108),(x,y),23,2)
        pygame.draw.circle(surf,(21,31,39),(x,y),13); pygame.draw.circle(surf,(54,207,220),(x,y),8)
        safe_set(surf,x-2,y-2,WHITE)
        # articulated turrets, visually damaged by phase.
        positions=[(-22,-16),(-22,16),(15,-22),(15,22)]
        for i,(ox,oy) in enumerate(positions):
            if self.component_state>=2 and i in (0,3): continue
            pygame.draw.rect(surf,(65,75,82),(x+ox-5,y+oy-4,10,8))
            pygame.draw.line(surf,(188,125,50),(x+ox-5,y+oy),(x+ox-13,y+oy),2)
        # shield ring phase 1
        if self.phase==1:
            pygame.draw.circle(surf,(76,220,234),(x,y),31,1)
            for a in range(0,360,45):
                aa=math.radians(a+self.age*20); safe_set(surf,x+int(math.cos(aa)*31),y+int(math.sin(aa)*31),WHITE)
        self._damage_fx(surf,[(-14,-11),(12,13),(-19,9),(16,-15)])

    def draw_mother(self,surf):
        x,y=int(self.x),int(self.y); pulse=2+int((math.sin(self.age*3)+1)*2)
        # Organic queen fused with machine ribs.
        pygame.draw.ellipse(surf,(50,12,45),(x-30,y-26,54,52))
        pygame.draw.ellipse(surf,(104,26,79),(x-23,y-21,40,42))
        pygame.draw.ellipse(surf,(36,11,35),(x-15,y-16,25,32))
        pygame.draw.circle(surf,(92,235,140),(x-4,y),7+pulse)
        pygame.draw.circle(surf,(205,255,210),(x-6,y-2),3)
        # limbs/cables
        for i in range(6):
            a=-1.6+i*.64; ex=x+int(math.cos(a)*36); ey=y+int(math.sin(a)*30)
            pygame.draw.line(surf,(82,26,70),(x-10,y), (ex,ey),4)
            pygame.draw.line(surf,(158,45,107),(x-10,y),(ex,ey),1)
        for oy in (-18,18):
            pygame.draw.rect(surf,(44,54,61),(x+12,y+oy-5,15,10)); pygame.draw.line(surf,GREEN,(x+14,y+oy),(x+25,y+oy),1)
        self._damage_fx(surf,[(-13,-15),(8,17),(-21,2),(14,-10)])

    def draw_ares(self,surf):
        x,y=int(self.x),int(self.y)
        # Humanoid siege cyborg upper body, intentionally cartoon-readable.
        pygame.draw.polygon(surf,(35,38,49),[(x-20,y-13),(x-8,y-26),(x+9,y-24),(x+20,y-10),(x+18,y+20),(x-16,y+22)])
        pygame.draw.polygon(surf,(88,73,70),[(x-15,y-10),(x-5,y-20),(x+7,y-18),(x+15,y-7),(x+12,y+15),(x-12,y+16)])
        # head
        pygame.draw.rect(surf,(45,47,55),(x-11,y-27,17,11)); pygame.draw.rect(surf,RED,(x-8,y-24,10,2)); safe_set(surf,x-7,y-24,YELLOW)
        # weapon arms
        pygame.draw.polygon(surf,(46,48,55),[(x-16,y-8),(x-37,y-13),(x-41,y-4),(x-20,y+3)])
        pygame.draw.rect(surf,(123,71,52),(x-42,y-10,19,6)); pygame.draw.line(surf,ORANGE,(x-42,y-7),(x-48,y-7),2)
        pygame.draw.polygon(surf,(46,48,55),[(x+14,y-6),(x+34,y-17),(x+40,y-9),(x+21,y+5)])
        pygame.draw.circle(surf,(221,144,56),(x+31,y-10),4)
        # spine/core
        pygame.draw.rect(surf,(24,31,38),(x-3,y-9,8,27)); pygame.draw.line(surf,(241,94,56),(x+1,y-6),(x+1,y+14),2)
        self._damage_fx(surf,[(-10,8),(10,-14),(-29,-8),(18,10)])

    def draw_wyrm(self,surf):
        x,y=int(self.x),int(self.y)
        # Segments form a dynamically undulating mechanical serpent.
        for i in range(6,0,-1):
            sx=x+i*9; sy=y+int(math.sin(self.age*4-i*.65)*10)
            pygame.draw.ellipse(surf,(35,79,112),(sx-9,sy-7,18,14))
            pygame.draw.arc(surf,ICE,(sx-8,sy-6,16,12),.2,2.9,1)
            safe_set(surf,sx-2,sy-3,WHITE)
        pygame.draw.polygon(surf,(29,66,101),[(x-28,y),(x-18,y-17),(x+8,y-20),(x+25,y),(x+8,y+20),(x-18,y+17)])
        pygame.draw.polygon(surf,(84,151,184),[(x-22,y),(x-12,y-12),(x+9,y-14),(x+19,y),(x+7,y+12),(x-12,y+11)])
        pygame.draw.polygon(surf,ICE,[(x-9,y-11),(x-2,y-24),(x+4,y-12)])
        pygame.draw.polygon(surf,(13,32,56),[(x-24,y),(x-10,y-5),(x-6,y),(x-10,y+5)])
        pygame.draw.circle(surf,(121,232,255),(x-5,y-5),3)
        self._damage_fx(surf,[(-10,12),(8,-13),(-19,-5),(15,8)])

    def draw_sovereign(self,surf):
        x,y=int(self.x),int(self.y)
        # Disconnected floating pieces around an impossible central face.
        rot=self.age*.8
        pygame.draw.polygon(surf,(39,17,71),[(x,y-18),(x+14,y),(x,y+18),(x-14,y)])
        pygame.draw.polygon(surf,(122,38,146),[(x,y-13),(x+10,y),(x,y+13),(x-10,y)])
        pygame.draw.circle(surf,(83,255,225),(x,y),5); safe_set(surf,x-1,y-1,WHITE)
        for i in range(6):
            a=rot+i*math.tau/6; rr=25+(i%2)*6; sx=x+int(math.cos(a)*rr); sy=y+int(math.sin(a)*rr)
            pygame.draw.polygon(surf,(73,31,112),[(sx,sy-6),(sx+5,sy),(sx,sy+6),(sx-5,sy)])
            safe_set(surf,sx,sy,MAGENTA if i%2 else GREEN)
        # impossible mirror line
        pygame.draw.line(surf,(207,58,220),(x-29,y+int(math.sin(rot)*5)),(x+29,y-int(math.sin(rot)*5)),1)
        self._damage_fx(surf,[(-8,-10),(10,8),(-17,11),(18,-9)])

    def draw_omega(self,surf):
        x,y=int(self.x),int(self.y); r=self.radius
        # Layered technological/organic super-entity. Each phase exposes more core.
        pygame.draw.polygon(surf,(22,9,24),[(x-r,y),(x-25,y-29),(x+8,y-r),(x+31,y-22),(x+r,y),(x+25,y+29),(x-8,y+r),(x-31,y+22)])
        pygame.draw.polygon(surf,(72,20,54),[(x-r+7,y),(x-19,y-24),(x+7,y-r+7),(x+25,y-17),(x+r-7,y),(x+18,y+23),(x-7,y+r-7),(x-25,y+17)])
        # armor petals
        for i in range(8):
            a=self.age*.12+i*math.tau/8; rr=25
            sx=x+int(math.cos(a)*rr); sy=y+int(math.sin(a)*rr)
            pygame.draw.rect(surf,(50,31,55),(sx-4,sy-4,8,8))
            safe_set(surf,sx,sy,(239,54,109))
        core_r=8+self.phase*3
        pygame.draw.circle(surf,(28,4,13),(x,y),core_r+6)
        pygame.draw.circle(surf,(230,42,98),(x,y),core_r)
        pygame.draw.circle(surf,(255,220,157),(x-3,y-3),max(2,core_r//3))
        if self.phase>=2:
            # organic inner tendrils exposed
            for i in range(6):
                a=i*math.tau/6+self.age*.4
                pygame.draw.line(surf,(144,29,76),(x,y),(x+int(math.cos(a)*34),y+int(math.sin(a)*26)),3)
        if self.phase==3:
            pygame.draw.circle(surf,(254,90,137),(x,y),r+8,1)
            pygame.draw.circle(surf,(255,224,160),(x,y),r+13,1)
        self._damage_fx(surf,[(-19,-15),(17,18),(-27,7),(21,-13),(0,24)])

# ---------------------------------------------------------------------------
# Main game state machine
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        # True stereo request. AudioSynth still adapts if the backend differs.
        pygame.mixer.pre_init(AUDIO_RATE,-16,2,512)
        pygame.init()

        self.data_dir=self._user_data_dir()
        self.save_path=os.path.join(self.data_dir,"campaign_save.json")
        self.settings_path=os.path.join(self.data_dir,"settings.json")
        self.settings={
            "music_volume":.80,
            "sfx_volume":.90,
            "fullscreen":False,
            "window_scale":4,
            "effects":2,
        }
        self._load_settings_file()

        pygame.display.set_caption(f"OMEGA HORIZON {BUILD_ID} - 16 BIT PSEUDO 3D SHMUP")
        self.window=None
        self.set_display_mode()
        self.canvas=pygame.Surface((NATIVE_W,NATIVE_H)).convert()
        self.clock=pygame.time.Clock(); self.running=True

        self.background=Background(); self.background.fx_level=int(self.settings["effects"])
        self.audio=AudioSynth(); self.audio.set_volumes(self.settings["music_volume"],self.settings["sfx_volume"])
        self.player=Player()

        self.stage=1; self.state="title"; self.state_timer=0.0
        self.score=0; self.stage_distance=0.0; self.stage_goal=self.stage_distance_goal()
        self.enemies=[]; self.player_bullets=[]; self.enemy_bullets=[]; self.pickups=[]; self.explosions=[]; self.hazards=[]
        self.boss=None; self.wave_serial=0; self.waves={}; self.spawn_timer=1.0; self.hazard_timer=3.0; self.boss_warning=0.0
        self.reward_pending=False; self.reward_timer=0.0; self.weapon_notice=""; self.notice_timer=0.0
        self.clean_waves=0; self.stage_deaths=0; self.last_enemy_label=""; self.health_drop_timer=10.0; self.health_pity=0

        # Menus / developer test tools.
        self.pause_index=0
        self.settings_index=0
        self.test_index=0
        self.test_stage=1
        self.menu_message=""
        self.menu_message_timer=0.0
        self.settings_return_state="pause"
        self.test_return_state="pause"
        self.test_code_buffer=""
        self.test_mode=False
        self.god_mode=False

    def stage_distance_goal(self): return 2200+(self.stage-1)*190

    # ------------------------ persistence / display --------------------

    @staticmethod
    def _user_data_dir():
        base=os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        path=os.path.join(base,"OmegaHorizon")
        try:
            os.makedirs(path,exist_ok=True)
        except Exception:
            path=os.getcwd()
        return path

    def _load_settings_file(self):
        try:
            with open(self.settings_path,"r",encoding="utf-8") as f:
                data=json.load(f)
            if isinstance(data,dict):
                self.settings["music_volume"]=clamp(float(data.get("music_volume",self.settings["music_volume"])),0,1)
                self.settings["sfx_volume"]=clamp(float(data.get("sfx_volume",self.settings["sfx_volume"])),0,1)
                self.settings["fullscreen"]=bool(data.get("fullscreen",False))
                self.settings["window_scale"]=int(clamp(int(data.get("window_scale",4)),2,5))
                self.settings["effects"]=int(clamp(int(data.get("effects",2)),0,2))
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(self.settings_path,"w",encoding="utf-8") as f:
                json.dump(self.settings,f,indent=2)
            return True
        except Exception:
            return False

    def set_display_mode(self):
        if self.settings.get("fullscreen",False):
            try:
                self.window=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
                return
            except Exception:
                self.settings["fullscreen"]=False
        scale=int(clamp(int(self.settings.get("window_scale",4)),2,5))
        self.settings["window_scale"]=scale
        self.window=pygame.display.set_mode((NATIVE_W*scale,NATIVE_H*scale))

    def apply_settings(self):
        self.background.fx_level=int(self.settings["effects"]) if hasattr(self,"background") else int(self.settings["effects"])
        if hasattr(self,"audio"):
            self.audio.set_volumes(self.settings["music_volume"],self.settings["sfx_volume"])
        self.set_display_mode()
        self.save_settings()

    def save_game(self):
        # Test-mode jumps must never contaminate normal campaign progression.
        if self.test_mode:
            self.menu_message="SAVE DISABLED IN TEST MODE"; self.menu_message_timer=2.2
            return False
        data={
            "version":1,
            "build":BUILD_ID,
            "stage":int(clamp(self.stage,1,10)),
            "score":int(max(0,self.score)),
            "lives":int(max(1,self.player.lives)),
            "health":float(clamp(self.player.health,1,self.player.max_health)),
            "max_health":float(self.player.max_health),
            "weapon":int(clamp(self.player.weapon,0,9)),
            "unlocked":[bool(v) for v in self.player.unlocked[:10]],
        }
        try:
            with open(self.save_path,"w",encoding="utf-8") as f:
                json.dump(data,f,indent=2)
            self.menu_message=f"SAVED STAGE {self.stage:02d} CHECKPOINT"; self.menu_message_timer=2.0
            return True
        except Exception:
            self.menu_message="SAVE FAILED"; self.menu_message_timer=2.0
            return False

    def load_game(self):
        try:
            with open(self.save_path,"r",encoding="utf-8") as f:
                data=json.load(f)
            stage=int(data.get("stage",1))
            if not 1<=stage<=10: raise ValueError("bad stage")
            unlocked=list(data.get("unlocked",[True]+[False]*9))
            if len(unlocked)!=10: raise ValueError("bad unlock list")
            unlocked=[bool(v) for v in unlocked]; unlocked[0]=True
            self.start_stage(stage)
            self.score=max(0,int(data.get("score",0)))
            self.player.lives=max(1,int(data.get("lives",3)))
            self.player.max_health=max(1,float(data.get("max_health",100)))
            self.player.health=clamp(float(data.get("health",self.player.max_health)),1,self.player.max_health)
            self.player.unlocked=unlocked
            weapon=int(clamp(int(data.get("weapon",0)),0,9))
            self.player.weapon=weapon if self.player.unlocked[weapon] else next(i for i,v in enumerate(self.player.unlocked) if v)
            self.menu_message=f"LOADED STAGE {stage:02d} CHECKPOINT"; self.menu_message_timer=2.2
            return True
        except Exception:
            self.menu_message="NO VALID SAVE FOUND"; self.menu_message_timer=2.2
            return False

    # ------------------------ menu / test mode -------------------------

    def pause_items(self):
        items=["RESUME","SAVE GAME","LOAD GAME","SETTINGS"]
        if self.test_mode: items.append("TEST MENU")
        items.append("QUIT TO TITLE")
        return items

    def open_pause(self):
        if self.state=="play":
            self.pause_index=0; self.state="pause"

    def open_settings(self,return_state="pause"):
        self.settings_return_state=return_state; self.settings_index=0; self.state="settings"

    def open_test_menu(self,return_state=None):
        if not self.test_mode:return
        self.test_return_state=return_state or self.state
        self.test_index=0; self.test_stage=int(clamp(self.stage,1,10)); self.state="test_menu"

    def activate_test_mode(self):
        self.test_mode=True
        self.test_stage=self.stage
        self.menu_message="TEST MODE ENABLED - F1"; self.menu_message_timer=3.0

    def prepare_test_loadout(self,stage):
        for i in range(10):
            self.player.unlocked[i]=(i<=stage-1)
        self.player.unlocked[0]=True
        if not self.player.unlocked[self.player.weapon]:
            self.player.weapon=max(i for i,v in enumerate(self.player.unlocked) if v)

    def test_jump_stage(self,stage):
        self.start_stage(stage)
        self.prepare_test_loadout(stage)
        self.player.health=self.player.max_health
        self.player.lives=max(self.player.lives,3)
        self.state="stage_intro"
        self.menu_message=f"TEST JUMP STAGE {stage:02d}"; self.menu_message_timer=2.0

    def test_spawn_boss(self,stage):
        self.start_stage(stage); self.begin_play(); self.prepare_test_loadout(stage)
        self.player.health=self.player.max_health; self.player.lives=max(self.player.lives,5)
        self.enemies.clear(); self.waves.clear(); self.enemy_bullets.clear(); self.hazards.clear(); self.pickups.clear()
        self.stage_distance=self.stage_goal; self.boss_warning=2.0
        self.boss=Boss(stage); self.boss.intro=.45
        self.weapon_notice=f"TEST BOSS: {STAGES[stage-1].boss_name}"; self.notice_timer=2.0
        self.audio.play_boss(stage-1)

    def unlock_all_test_weapons(self):
        self.player.unlocked=[True]*10
        self.weapon_notice="TEST: ALL WEAPONS UNLOCKED"; self.notice_timer=2.0

    def test_refill(self):
        self.player.health=self.player.max_health; self.player.lives=max(self.player.lives,9)
        self.weapon_notice="TEST: HEALTH AND LIVES REFILLED"; self.notice_timer=2.0

    def pause_action(self):
        items=self.pause_items(); choice=items[self.pause_index%len(items)]
        if choice=="RESUME": self.state="play"
        elif choice=="SAVE GAME": self.save_game()
        elif choice=="LOAD GAME": self.load_game()
        elif choice=="SETTINGS": self.open_settings("pause")
        elif choice=="TEST MENU": self.open_test_menu("pause")
        elif choice=="QUIT TO TITLE":
            self.audio.stop_music(); self.state="title"; self.boss=None; self.enemy_bullets.clear()

    def adjust_setting(self,direction):
        idx=self.settings_index
        if idx==0:
            self.settings["music_volume"]=round(clamp(self.settings["music_volume"]+direction*.1,0,1),2)
        elif idx==1:
            self.settings["sfx_volume"]=round(clamp(self.settings["sfx_volume"]+direction*.1,0,1),2)
        elif idx==2 and direction:
            self.settings["fullscreen"]=not self.settings["fullscreen"]
        elif idx==3:
            self.settings["window_scale"]=int(clamp(self.settings["window_scale"]+direction,2,5))
        elif idx==4:
            self.settings["effects"]=int(clamp(self.settings["effects"]+direction,0,2))
        self.apply_settings()

    def settings_action(self):
        if self.settings_index in (2,): self.adjust_setting(1)
        elif self.settings_index==5:
            self.state=self.settings_return_state

    def test_action(self):
        if self.test_index==0:return
        if self.test_index==1:self.test_jump_stage(self.test_stage)
        elif self.test_index==2:self.test_spawn_boss(self.test_stage)
        elif self.test_index==3:self.unlock_all_test_weapons()
        elif self.test_index==4:self.test_refill()
        elif self.test_index==5:
            self.god_mode=not self.god_mode
            self.menu_message="GOD MODE ON" if self.god_mode else "GOD MODE OFF"; self.menu_message_timer=2.0
        elif self.test_index==6:self.state=self.test_return_state


    def reset_new_game(self):
        self.player=Player(); self.score=0; self.stage=1; self.start_stage(1)

    def start_stage(self,stage):
        self.stage=stage; self.stage_distance=0; self.stage_goal=self.stage_distance_goal()
        self.enemies.clear(); self.player_bullets.clear(); self.enemy_bullets.clear(); self.pickups.clear(); self.explosions.clear(); self.hazards.clear()
        self.boss=None; self.waves.clear(); self.spawn_timer=.9; self.hazard_timer=2.5; self.boss_warning=0
        self.reward_pending=False; self.reward_timer=0; self.weapon_notice=""; self.notice_timer=0; self.stage_deaths=0; self.health_drop_timer=9.0; self.health_pity=0
        self.state="stage_intro"; self.state_timer=2.6; self.player.reset_position(); self.audio.play_stage(stage-1)

    def begin_play(self): self.state="play"; self.state_timer=0
    def game_over(self): self.state="game_over"; self.state_timer=0; self.audio.stop_music()
    def win_game(self): self.state="victory"; self.state_timer=0; self.audio.stop_music()

    def nearest_enemy(self,x,y):
        candidates=[e for e in self.enemies if not e.dead]
        if self.boss and not self.boss.dead and self.boss.intro<=0:candidates.append(self.boss)
        if not candidates:return None
        return min(candidates,key=lambda e:(e.x-x)**2+(e.y-y)**2)

    # ------------------------ spawn / waves ---------------------------

    def spawn_wave(self):
        if self.boss is not None or self.reward_pending:return
        self.wave_serial+=1; wid=self.wave_serial
        # All stages use the tactical roles, but the distribution changes.
        weights_by_stage=[
            [55,20,15,10],[40,28,20,12],[35,30,20,15],[40,18,22,20],[28,32,28,12],
            [28,27,22,23],[24,35,22,19],[33,28,23,16],[25,25,25,25],[20,30,25,25]
        ]
        weights=weights_by_stage[self.stage-1]
        count=min(8,4+self.stage//2+random.randint(0,1))
        formation=random.choice(["sine","chevron","tight"]+(["column"] if self.stage>=5 else []))
        center=random.randint(57,176); spacing=max(10,19-self.stage*.6)
        enemies=[]
        for i in range(count):
            archetype=random.choices(ARCHETYPES,weights=weights,k=1)[0]
            # Ambushers increasingly appear from behind, forcing Rear Guard value.
            rear=(archetype=="ambusher" and self.stage>=5 and random.random()<.42)
            if formation=="chevron": yy=center+(abs(i-(count-1)/2))*spacing*.55*(-1 if i%2 else 1)
            elif formation=="column": yy=center+(i-(count-1)/2)*max(8,spacing*.65)
            elif formation=="tight": yy=center+(i-(count-1)/2)*max(6,spacing*.50)
            else: yy=center+math.sin(i*1.35)*spacing
            yy=clamp(yy,34,NATIVE_H-24)
            xx=-18-i*8 if rear else NATIVE_W+14+i*10
            e=Enemy(xx,yy,self.stage,wid,i,archetype,formation,rear); enemies.append(e); self.enemies.append(e)
        self.waves[wid]={"total":count,"kills":0,"failed":False,"last":(NATIVE_W-20,112)}

    def spawn_boss_add(self,archetype,x,y):
        # Adds do not belong to a normal reward wave.
        self.wave_serial+=1; wid=self.wave_serial
        e=Enemy(x,y,self.stage,wid,0,archetype,"sine",False)
        e.health*=.72; e.max_health=e.health
        self.enemies.append(e); self.waves[wid]={"total":1,"kills":0,"failed":True,"last":(x,y)}

    def wave_enemy_destroyed(self,wid,x,y,archetype):
        data=self.waves.get(wid)
        if not data:return
        data["kills"]+=1; data["last"]=(x,y)
        if data["kills"]>=data["total"]:
            if not data["failed"]:
                self.clean_waves+=1
                self.health_pity+=1
                # Clean play can accelerate recovery and still produces rare
                # premium rewards, but normal health no longer depends on a
                # flawless wave.
                roll=random.random()
                if roll<.012:
                    self.pickups.append(Pickup(x,y,"life"))
                elif roll<.070:
                    self.pickups.append(Pickup(x,y,"major_health"))
                elif self.health_pity>=2 and self.player.health<82:
                    self.pickups.append(Pickup(x,y,"health")); self.health_pity=0; self.health_drop_timer=max(self.health_drop_timer,8.0)
            del self.waves[wid]

    def wave_enemy_escaped(self,wid):
        data=self.waves.get(wid)
        if data:data["failed"]=True

    def begin_boss_reward(self):
        if self.reward_pending:return
        self.reward_pending=True; self.reward_timer=5.0
        self.enemy_bullets.clear(); self.enemies.clear(); self.hazards.clear(); self.waves.clear()
        reward=STAGES[self.stage-1].reward_weapon
        if reward is None:
            self.state="stage_clear"; self.state_timer=2.8; return
        self.pickups.append(Pickup(clamp(self.boss.x,165,220),clamp(self.boss.y,55,180),"weapon",-25,0,8,reward))
        # Skill reward: a rare guaranteed 1UP opportunity for a no-death boss on stages 5/9.
        if self.stage in (5,9) and self.stage_deaths==0:
            self.pickups.append(Pickup(clamp(self.boss.x+12,170,230),clamp(self.boss.y+18,50,190),"life",-28,0,8))

    def collect_pickup(self,p):
        if p.kind=="health":
            self.player.health=min(self.player.max_health,self.player.health+30); self.audio.play_sfx("health",p.x,.85)
            self.explosions.append(Explosion(p.x,p.y,.28,.28,12,"green"))
        elif p.kind=="major_health":
            self.player.health=min(self.player.max_health,self.player.health+65); self.audio.play_sfx("major_health",p.x,.95)
            self.explosions.append(Explosion(p.x,p.y,.38,.38,17,"green")); self.weapon_notice="MAJOR HEALTH +65"; self.notice_timer=1.4
        elif p.kind=="life":
            self.player.lives+=1; self.audio.play_sfx("life",p.x,1.0)
            self.explosions.append(Explosion(p.x,p.y,.48,.48,20,"green")); self.weapon_notice="EXTRA LIFE"; self.notice_timer=1.6
        elif p.kind=="weapon":
            idx=p.weapon_index or 0
            fresh=self.player.unlock(idx); self.audio.play_sfx("weapon",p.x,1.0)
            self.explosions.append(Explosion(p.x,p.y,.55,.55,22,"void"))
            self.weapon_notice=f"WEAPON ACQUIRED: {WEAPON_NAMES[idx]}"; self.notice_timer=2.2
            if fresh:self.score+=750
            # Weapon module collection completes the stage.
            self.reward_pending=False; self.state="stage_clear"; self.state_timer=3.0
        p.life=0

    # ------------------------ damage / collisions ---------------------

    def splash_damage(self,x,y,radius,damage,weapon_index):
        for e in self.enemies:
            if not e.dead and (e.x-x)**2+(e.y-y)**2<=radius**2:e.hit(damage,self,weapon_index)
        if self.boss and not self.boss.dead and (self.boss.x-x)**2+(self.boss.y-y)**2<=(radius+self.boss.radius)**2:
            self.boss.hit(damage*.55,self,weapon_index)
        self.explosions.append(Explosion(x,y,.35,.35,radius*.72,"void"))

    @staticmethod
    def circle_rect_collision(b,rect):
        cx=clamp(b.x,rect.left,rect.right); cy=clamp(b.y,rect.top,rect.bottom)
        return (b.x-cx)**2+(b.y-cy)**2<=b.radius**2

    def handle_collisions(self):
        # Player shots.
        for b in list(self.player_bullets):
            if b.life<=0:continue
            for e in self.enemies:
                if e.dead:continue
                if b.rect().colliderect(e.rect()):
                    e.hit(b.damage,self,b.weapon_index)
                    if b.kind=="grenade":self.splash_damage(b.x,b.y,b.splash,b.damage*.55,b.weapon_index)
                    if b.pierce>0:b.pierce-=1
                    else:b.life=0
                    break
            if b.life>0 and self.boss and not self.boss.dead and self.boss.intro<=0 and b.rect().colliderect(self.boss.rect()):
                self.boss.hit(b.damage,self,b.weapon_index)
                if b.kind=="grenade":self.splash_damage(b.x,b.y,b.splash,b.damage*.45,b.weapon_index)
                if b.pierce>0:b.pierce-=1
                else:b.life=0

        pr=self.player.rect()
        # Enemy bullets.
        for b in self.enemy_bullets:
            if b.life>0 and self.circle_rect_collision(b,pr):b.life=0; self.player.hit(b.damage,self)
        # Enemy bodies.
        for e in self.enemies:
            if not e.dead and e.rect().colliderect(pr):
                e.dead=True; self.wave_enemy_escaped(e.wave_id); self.player.hit(18 if e.archetype!="heavy" else 24,self)
        if self.boss and not self.boss.dead and self.boss.intro<=0 and self.boss.rect().colliderect(pr):self.player.hit(25,self)
        # Environmental hazards.
        for h in self.hazards:
            if h.collides(pr):self.player.hit(14 if h.stage<7 else 18,self)
        # Pickups.
        for p in list(self.pickups):
            if p.life>0 and p.rect().colliderect(pr):self.collect_pickup(p)

    # ------------------------ gameplay update -------------------------

    def update_play(self,dt):
        keys=pygame.key.get_pressed(); self.player.update(dt,keys,self); self.background.update(dt,self.stage)
        self.notice_timer=max(0,self.notice_timer-dt)
        self.menu_message_timer=max(0,self.menu_message_timer-dt)

        # Recovery cadence / pity system. Standard +30 HP crosses periodically
        # enter from the right even if the player misses a perfect wave. Low HP
        # accelerates the cadence; existing recovery items suppress duplicates.
        if self.boss is None and self.stage_distance < self.stage_goal*.94:
            self.health_drop_timer-=dt
            active_recovery=any(p.life>0 and p.kind in ("health","major_health") for p in self.pickups)
            threshold=42 if self.player.health<=38 else 72 if self.player.health<=65 else 88
            if self.health_drop_timer<=0 and self.player.health<threshold and not active_recovery:
                kind="major_health" if self.player.health<=24 and random.random()<.30 else "health"
                self.pickups.append(Pickup(NATIVE_W+8,random.randint(55,185),kind,-28,0,10))
                self.health_drop_timer=random.uniform(11.0,15.0) if self.player.health>45 else random.uniform(7.5,10.5)
                self.health_pity=0
            elif self.health_drop_timer<=0:
                # Healthy players still get another check soon instead of losing
                # the recovery opportunity for the remainder of the stage.
                self.health_drop_timer=5.0

        if self.boss is None:
            self.stage_distance+=dt*(82+self.stage*4)
            self.spawn_timer-=dt
            interval=max(.70,2.10-(self.stage-1)*.115)
            if self.spawn_timer<=0 and self.stage_distance<self.stage_goal:
                self.spawn_wave(); self.spawn_timer=interval
            # Stage hazards only after stage 1 and outside final approach.
            if self.stage>=2 and self.stage_distance<self.stage_goal*.92:
                self.hazard_timer-=dt
                if self.hazard_timer<=0:
                    self.hazards.append(Hazard(self.stage)); self.hazard_timer=max(2.5,5.2-self.stage*.18)+random.random()*1.4
            if self.stage_distance>=self.stage_goal:
                self.boss_warning+=dt
                if self.boss_warning>1.35:
                    self.enemies.clear(); self.waves.clear(); self.enemy_bullets.clear(); self.hazards.clear()
                    self.boss=Boss(self.stage)
                    self.weapon_notice=f"BOSS: {STAGES[self.stage-1].boss_name}"
                    self.notice_timer=2.0
                    self.audio.play_boss(self.stage-1)
        elif not self.boss.dead:
            self.boss.update(dt,self)
        elif not self.reward_pending and self.state=="play":
            self.begin_boss_reward()

        # Reward safety: guaranteed boss weapon cannot be lost offscreen.
        if self.reward_pending:
            self.reward_timer-=dt
            if self.reward_timer<=0:
                wp=next((p for p in self.pickups if p.kind=="weapon" and p.life>0),None)
                if wp:self.collect_pickup(wp)

        for e in self.enemies:
            if not e.dead:e.update(dt,self)
        for b in self.player_bullets:b.update(dt,self)
        for b in self.enemy_bullets:
            if b.kind=="tracking":
                desired=angle_to(self.player.x-b.x,self.player.y-b.y); cur=math.atan2(b.vy,b.vx)
                delta=(desired-cur+math.pi)%(2*math.pi)-math.pi; cur+=clamp(delta,-1.25*dt,1.25*dt)
                sp=math.hypot(b.vx,b.vy); b.vx,b.vy=math.cos(cur)*sp,math.sin(cur)*sp
            b.update(dt,self)
        for p in self.pickups:p.update(dt,self)
        for ex in self.explosions:ex.update(dt)
        for h in self.hazards:h.update(dt,self)

        self.handle_collisions()
        self.enemies=[e for e in self.enemies if not e.dead]
        self.player_bullets=[b for b in self.player_bullets if b.alive()]
        self.enemy_bullets=[b for b in self.enemy_bullets if b.alive()]
        self.pickups=[p for p in self.pickups if p.life>0 and -15<p.x<NATIVE_W+30]
        self.explosions=[e for e in self.explosions if e.life>0]
        self.hazards=[h for h in self.hazards if h.life>0]

    def update(self,dt):
        if self.state=="play":self.update_play(dt)
        else:
            self.background.update(dt*.45,self.stage)
            self.notice_timer=max(0,self.notice_timer-dt)
            self.menu_message_timer=max(0,self.menu_message_timer-dt)
            for ex in self.explosions:ex.update(dt)
            self.explosions=[e for e in self.explosions if e.life>0]
            if self.state=="stage_intro":
                self.state_timer-=dt
                if self.state_timer<=0:self.begin_play()
            elif self.state=="stage_clear":
                self.state_timer-=dt
                if self.state_timer<=0:
                    if self.stage>=10:self.win_game()
                    else:self.start_stage(self.stage+1)

    # ------------------------ input -----------------------------------

    def handle_event(self,event):
        if event.type==pygame.QUIT:
            self.running=False; return
        if event.type!=pygame.KEYDOWN:
            return

        key=event.key

        # Global developer/test and checkpoint shortcuts.
        if key==pygame.K_F1 and self.test_mode and self.state not in ("settings",):
            if self.state=="test_menu": self.state=self.test_return_state
            else: self.open_test_menu(self.state)
            return
        if key==pygame.K_F5 and self.state in ("play","pause"):
            self.save_game(); return
        if key==pygame.K_F9 and self.state in ("title","play","pause"):
            self.load_game(); return

        if self.state=="title":
            if key==pygame.K_ESCAPE:
                self.running=False; return
            # Hidden deliberate cheat-code activation.
            ch=getattr(event,"unicode","")
            if ch and ch.isalpha():
                self.test_code_buffer=(self.test_code_buffer+ch.upper())[-16:]
                if self.test_code_buffer.endswith("TERMINUS"):
                    self.activate_test_mode()
            if key in (pygame.K_RETURN,pygame.K_SPACE):
                self.reset_new_game()
            elif key==pygame.K_l:
                self.load_game()
            elif key==pygame.K_F2:
                self.open_settings("title")
            return

        if self.state in ("game_over","victory"):
            if key in (pygame.K_RETURN,pygame.K_SPACE): self.reset_new_game()
            elif key==pygame.K_ESCAPE: self.state="title"
            return

        if self.state=="stage_intro":
            if key==pygame.K_RETURN:self.begin_play()
            elif key in (pygame.K_ESCAPE,pygame.K_p): self.begin_play(); self.open_pause()
            return

        if self.state=="play":
            if key==pygame.K_q:self.player.cycle_weapon(-1)
            elif key==pygame.K_e:self.player.cycle_weapon(1)
            elif key in (pygame.K_p,pygame.K_ESCAPE):self.open_pause()
            return

        if self.state=="pause":
            items=self.pause_items()
            if key in (pygame.K_p,pygame.K_ESCAPE):
                self.state="play"
            elif key==pygame.K_UP:
                self.pause_index=(self.pause_index-1)%len(items)
            elif key==pygame.K_DOWN:
                self.pause_index=(self.pause_index+1)%len(items)
            elif key in (pygame.K_RETURN,pygame.K_SPACE):
                self.pause_action()
            return

        if self.state=="settings":
            if key in (pygame.K_ESCAPE,pygame.K_p):
                self.state=self.settings_return_state
            elif key==pygame.K_UP:
                self.settings_index=(self.settings_index-1)%6
            elif key==pygame.K_DOWN:
                self.settings_index=(self.settings_index+1)%6
            elif key==pygame.K_LEFT:
                self.adjust_setting(-1)
            elif key==pygame.K_RIGHT:
                self.adjust_setting(1)
            elif key in (pygame.K_RETURN,pygame.K_SPACE):
                self.settings_action()
            return

        if self.state=="test_menu":
            if key in (pygame.K_ESCAPE,pygame.K_F1):
                self.state=self.test_return_state
            elif key==pygame.K_UP:
                self.test_index=(self.test_index-1)%7
            elif key==pygame.K_DOWN:
                self.test_index=(self.test_index+1)%7
            elif key==pygame.K_LEFT and self.test_index==0:
                self.test_stage=10 if self.test_stage<=1 else self.test_stage-1
            elif key==pygame.K_RIGHT and self.test_index==0:
                self.test_stage=1 if self.test_stage>=10 else self.test_stage+1
            elif key in (pygame.K_RETURN,pygame.K_SPACE):
                self.test_action()
            return

    # ------------------------ HUD / rendering -------------------------

    def draw_hud(self):
        s=self.canvas
        pygame.draw.rect(s,(5,9,22),(0,0,NATIVE_W,HUD_H)); pygame.draw.line(s,(52,130,170),(0,20),(NATIVE_W,20))
        draw_text(s,f"STAGE {self.stage:02d}",3,2,CYAN); draw_text(s,f"SCORE {self.score:07d}",65,2,WHITE); draw_text(s,f"LIVES {max(0,self.player.lives)}",183,2,YELLOW)
        name=WEAPON_NAMES[self.player.weapon]
        draw_text(s,f"WEAPON: {name}",3,11,(180,240,255))
        bx,by,bw,bh=180,11,71,7; draw_text(s,"HP",164,11,WHITE)
        pygame.draw.rect(s,(20,24,35),(bx,by,bw,bh)); pygame.draw.rect(s,GRAY,(bx,by,bw,bh),1)
        fill=int((bw-2)*max(0,self.player.health)/self.player.max_health); hpcol=GREEN if self.player.health>50 else YELLOW if self.player.health>25 else RED
        if fill>0:pygame.draw.rect(s,hpcol,(bx+1,by+1,fill,bh-2))
        if self.boss and not self.boss.dead:
            bw2=112; bx2=NATIVE_W//2-bw2//2
            pygame.draw.rect(s,(10,9,20),(bx2,23,bw2,6)); ratio=max(0,self.boss.health/self.boss.max_health)
            pygame.draw.rect(s,RED,(bx2+1,24,int((bw2-2)*ratio),4)); draw_text(s,"BOSS",bx2-29,23,MAGENTA)

    def draw_gameplay(self):
        self.background.draw(self.canvas,self.stage)
        for p in self.pickups:p.draw(self.canvas)
        for h in self.hazards:h.draw(self.canvas)
        for e in self.enemies:e.draw(self.canvas)
        if self.boss and not self.boss.dead:self.boss.draw(self.canvas)
        for b in self.player_bullets:b.draw(self.canvas)
        for b in self.enemy_bullets:b.draw(self.canvas)
        for i,ex in enumerate(self.explosions):
            fx=int(self.settings.get("effects",2))
            if fx==2 or (fx==1 and i%2==0) or (fx==0 and i%3==0):
                ex.draw(self.canvas)
        self.player.draw(self.canvas)

        if self.boss is None and self.stage_distance>=self.stage_goal and int(self.boss_warning*8)%2==0:
            pygame.draw.rect(self.canvas,(35,0,20),(58,96,140,18)); pygame.draw.rect(self.canvas,RED,(58,96,140,18),1)
            draw_text(self.canvas,"WARNING BOSS SIGNAL",67,102,YELLOW)

        if self.notice_timer>0 and self.weapon_notice:
            w=min(244,max(128,text_width(self.weapon_notice)+12)); x=(NATIVE_W-w)//2
            pygame.draw.rect(self.canvas,(4,9,18),(x,31,w,15)); pygame.draw.rect(self.canvas,(80,190,210),(x,31,w,15),1)
            tx=max(x+5,(NATIVE_W-text_width(self.weapon_notice))//2); draw_text(self.canvas,self.weapon_notice,tx,35,YELLOW)
        self.draw_hud()

    def draw_menu_box(self,title,items,selected,x=43,y=38,w=170):
        h=30+len(items)*15
        pygame.draw.rect(self.canvas,(4,7,17),(x,y,w,h))
        pygame.draw.rect(self.canvas,(62,125,157),(x,y,w,h),1)
        draw_text(self.canvas,title,(NATIVE_W-text_width(title))//2,y+7,CYAN)
        for i,label in enumerate(items):
            yy=y+23+i*15
            if i==selected:
                pygame.draw.rect(self.canvas,(26,43,58),(x+6,yy-3,w-12,12))
                pygame.draw.rect(self.canvas,(85,174,199),(x+6,yy-3,w-12,12),1)
            draw_text(self.canvas,label,x+12,yy,YELLOW if i==selected else WHITE)

    def draw_pause_menu(self):
        self.draw_menu_box("PAUSE MENU",self.pause_items(),self.pause_index,47,38,162)
        draw_text(self.canvas,"F5 SAVE  F9 LOAD",77,204,(119,178,197))

    def draw_settings_menu(self):
        fx_names=("LOW","MED","HIGH")
        items=[
            f"MUSIC {int(self.settings['music_volume']*100):03d}",
            f"SFX {int(self.settings['sfx_volume']*100):03d}",
            "FULLSCREEN "+("ON" if self.settings["fullscreen"] else "OFF"),
            f"WINDOW SCALE {int(self.settings['window_scale'])}X",
            "EFFECTS "+fx_names[int(self.settings["effects"])],
            "BACK",
        ]
        self.draw_menu_box("SETTINGS",items,self.settings_index,40,34,176)
        draw_text(self.canvas,"LEFT RIGHT ADJUST",76,198,(119,178,197))

    def draw_test_menu(self):
        items=[
            f"STAGE {self.test_stage:02d}",
            "JUMP TO STAGE",
            "SPAWN BOSS",
            "UNLOCK ALL WEAPONS",
            "REFILL HEALTH LIVES",
            "GOD MODE "+("ON" if self.god_mode else "OFF"),
            "BACK",
        ]
        self.draw_menu_box("TEST MODE",items,self.test_index,35,27,186)
        p=STAGES[self.test_stage-1]
        draw_text(self.canvas,p.title,(NATIVE_W-text_width(p.title))//2,157,MAGENTA)
        draw_text(self.canvas,"LEFT RIGHT CHOOSE STAGE",60,188,(119,178,197))
        draw_text(self.canvas,"F1 CLOSE",101,199,(119,178,197))

    def draw_menu_message(self):
        if self.menu_message_timer<=0 or not self.menu_message:return
        w=min(244,max(116,text_width(self.menu_message)+12)); x=(NATIVE_W-w)//2
        pygame.draw.rect(self.canvas,(5,8,18),(x,210-13,w,12))
        pygame.draw.rect(self.canvas,(80,160,180),(x,210-13,w,12),1)
        draw_text(self.canvas,self.menu_message,(NATIVE_W-text_width(self.menu_message))//2,200,YELLOW)

    def draw_overlay_center(self,title,subtitle=None,col=WHITE,subtitle2=None):
        w=max(166,text_width(title)+18,text_width(subtitle or "")+18,text_width(subtitle2 or "")+18)
        x=(NATIVE_W-w)//2; y=76; h=58 if subtitle2 else 48
        pygame.draw.rect(self.canvas,(6,7,18),(x,y,w,h)); pygame.draw.rect(self.canvas,(48,90,128),(x,y,w,h),1)
        for xx in range(x+2,x+w-2,4):safe_set(self.canvas,xx,y+2,(75,130,160)); safe_set(self.canvas,xx,y+h-3,(45,80,110))
        draw_text(self.canvas,title,(NATIVE_W-text_width(title))//2,y+9,col,shadow=True)
        if subtitle:draw_text(self.canvas,subtitle,(NATIVE_W-text_width(subtitle))//2,y+27,(175,210,235))
        if subtitle2:draw_text(self.canvas,subtitle2,(NATIVE_W-text_width(subtitle2))//2,y+41,(120,170,195))

    def draw_title(self):
        self.background.draw_space(self.canvas,1)
        hero_pal={'1':(8,23,50),'2':(22,57,99),'3':(41,105,151),'4':(76,176,202),
                  '5':(138,225,235),'6':WHITE,'7':ORANGE,'8':(124,240,255)}
        draw_indexed_sprite(self.canvas,PLAYER_PIXELS,53,100,hero_pal,scale=2)
        for i,col in enumerate(((255,229,91),ORANGE,(153,48,54),(76,35,70))):
            pygame.draw.line(self.canvas,col,(51-i*3,112),(44-i*5,112),max(1,4-i))
        draw_text(self.canvas,"OMEGA HORIZON",38,45,CYAN,2,True)
        draw_text(self.canvas,"V8.2 BOSS ART SYSTEMS",62,72,YELLOW)
        draw_text(self.canvas,"ENTER NEW GAME",84,154,WHITE)
        draw_text(self.canvas,"L LOAD  F2 SETTINGS",70,168,(170,210,230))
        draw_text(self.canvas,"MOVE WASD  FIRE Z",74,181,(170,210,230))
        draw_text(self.canvas,"WEAPON Q E  PAUSE P",67,192,(170,210,230))
        if self.test_mode:
            draw_text(self.canvas,"TEST MODE ENABLED  F1",68,204,MAGENTA)
        else:
            draw_text(self.canvas,"BUILD V8.2",100,207,(75,128,160))
        self.draw_menu_message()

    def draw(self):
        if self.state=="title":
            self.draw_title()
        elif self.state=="settings" and self.settings_return_state=="title":
            self.draw_title(); self.draw_settings_menu(); self.draw_menu_message()
        elif self.state=="test_menu" and self.test_return_state=="title":
            self.draw_title(); self.draw_test_menu(); self.draw_menu_message()
        else:
            self.draw_gameplay()
            if self.state=="stage_intro":
                p=STAGES[self.stage-1]
                self.draw_overlay_center(f"STAGE {self.stage:02d}",p.title,CYAN,p.subtitle)
            elif self.state=="stage_clear":
                reward=STAGES[self.stage-1].reward_weapon
                sub=f"SCORE {self.score:07d}" if reward is None else f"NEW: {WEAPON_NAMES[reward]}"
                self.draw_overlay_center("STAGE CLEAR",sub,GREEN)
            elif self.state=="pause":
                self.draw_pause_menu()
            elif self.state=="settings":
                self.draw_settings_menu()
            elif self.state=="test_menu":
                self.draw_test_menu()
            elif self.state=="game_over":
                self.draw_overlay_center("GAME OVER","ENTER TO RESTART",RED)
            elif self.state=="victory":
                self.draw_overlay_center("OMEGA DESTROYED",f"FINAL SCORE {self.score:07d}",GREEN,"THE TERMINUS IS SILENT")
            self.draw_menu_message()

        # Preserve the 256x224 native image under every display option.
        ww,wh=self.window.get_size()
        scale=max(1,min(ww//NATIVE_W,wh//NATIVE_H))
        tw,th=NATIVE_W*scale,NATIVE_H*scale
        scaled=pygame.transform.scale(self.canvas,(tw,th))
        self.window.fill(BLACK)
        self.window.blit(scaled,((ww-tw)//2,(wh-th)//2))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt=min(1/20,self.clock.tick(FPS)/1000.0)
            for event in pygame.event.get():self.handle_event(event)
            self.update(dt); self.draw()
        self.audio.stop_music(); pygame.quit()

# ---------------------------------------------------------------------------
# Packaged regression smoke-test entry point
# ---------------------------------------------------------------------------

def packaged_smoke_test():
    """Exercise V8.2 art, menus, saves, settings, all stages and stereo SFX."""
    g=Game()
    try:
        assert BUILD_ID=="V8.2-BOSS-ART-SYSTEMS"
        assert WEAPON_NAMES[4]=="HOMING ROCKET"
        assert g.player.unlocked==[True]+[False]*9
        assert len({(p.music_style,p.bpm,p.key) for p in STAGES})==10
        assert len(PYRO_HEAD)>=15 and len(PYRO_TORSO)>=18
        assert len(CARRIER_BODY)>=12 and len(LEVIATHAN_HEAD)>=16

        # Audio architecture remains truly stereo and volume-adjustable.
        if pygame.mixer.get_init() is not None and g.audio.enabled:
            assert len(g.audio.weapon_sfx)==10
            assert all(len(v)==3 for v in g.audio.weapon_sfx)
            g.audio.set_volumes(.5,.6)
            assert abs(g.audio.music_volume-.5)<.01 and abs(g.audio.sfx_volume-.6)<.01

        # Draw every campaign environment and all enemy/boss families.
        for stage in range(1,11):
            g.stage=stage; g.background.draw(g.canvas,stage)
            for i,arch in enumerate(ARCHETYPES):
                e=Enemy(155+i*18,65+i*27,stage,999+i,i,arch); e.draw(g.canvas)
            boss=Boss(stage); boss.intro=0; boss.draw(g.canvas)

        # Save/load checkpoint and developer tools.
        g.reset_new_game(); g.begin_play()
        g.stage=3; g.score=12345; g.player.health=61; g.player.lives=4
        g.player.unlocked[:4]=[True]*4; g.player.weapon=3
        assert g.save_game()
        g.score=0; g.player.health=5
        assert g.load_game()
        assert g.stage==3 and g.score==12345 and int(g.player.health)==61
        g.activate_test_mode(); assert g.test_mode
        g.test_spawn_boss(3); assert g.boss and g.boss.stage==3
        g.unlock_all_test_weapons(); assert all(g.player.unlocked)
        g.god_mode=True; hp=g.player.health; g.player.invuln=0; g.player.hit(99,g); assert g.player.health==hp

        # Menu render paths and one real gameplay frame.
        g.state="pause"; g.draw()
        g.open_settings("pause"); g.draw()
        g.open_test_menu("settings"); g.draw()
        g.state="play"; g.update(1/60); g.draw()
        g.audio.stop_music()
    finally:
        pygame.quit()
    return 0


if __name__=="__main__":
    if "--smoke-test" in sys.argv:raise SystemExit(packaged_smoke_test())
    Game().run()
