"""Original synthesized Christmas music, sleigh jingle, and bells.

Melodies are the public-domain tunes Jingle Bells (1857) and a short
Westminster-like toll. No commercial recording is copied.
"""
import math
import random
import struct
import wave
from pathlib import Path

random.seed(25)
ROOT = Path(__file__).resolve().parents[1] / 'halloween_hub/static/assets/sneak-peek'
RATE = 22050

PITCH = {
    'G3': 196.00, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25, 'D5': 587.33,
    'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'C6': 1046.50,
}


def music_box(samples, start, frequency, duration, level):
    for i in range(int(duration * RATE)):
        t = i / RATE
        if start + i >= len(samples):
            break
        edge = math.exp(-3.2 * t) * min(1, t * 80)
        tone = math.sin(2 * math.pi * frequency * t)
        shimmer = math.sin(2 * math.pi * frequency * 2.01 * t) * 0.18
        samples[start + i] += (tone + shimmer) * edge * level


def write(name, samples):
    peak = max(1e-6, max(abs(v) for v in samples))
    scale = 0.82 / peak
    frames = b''.join(struct.pack('<h', max(-32767, min(32767, int(v * scale * 32767)))) for v in samples)
    with wave.open(str(ROOT / name), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(frames)


def christmas_music():
    beat = 0.26
    # Jingle Bells chorus, then the verse tag, played twice.
    phrase = [
        ('E5', 1), ('E5', 1), ('E5', 2),
        ('E5', 1), ('E5', 1), ('E5', 2),
        ('E5', 1), ('G5', 1), ('C5', 1.5), ('D5', 0.5), ('E5', 2.5), (None, 0.5),
        ('F5', 1), ('F5', 1), ('F5', 1), ('F5', 1),
        ('F5', 1), ('E5', 1), ('E5', 1), ('E5', 0.5), ('E5', 0.5),
        ('E5', 1), ('D5', 1), ('D5', 1), ('E5', 1), ('D5', 2), ('G5', 2),
        ('E5', 1), ('E5', 1), ('E5', 2),
        ('E5', 1), ('E5', 1), ('E5', 2),
        ('E5', 1), ('G5', 1), ('C5', 1.5), ('D5', 0.5), ('E5', 2.5), (None, 0.5),
        ('F5', 1), ('F5', 1), ('F5', 1), ('F5', 1),
        ('F5', 1), ('E5', 1), ('E5', 1), ('E5', 1),
        ('G5', 1), ('G5', 1), ('F5', 1), ('D5', 1), ('C5', 3), (None, 1),
    ]
    total_beats = sum(length for _, length in phrase) * 2
    samples = [0.0] * int((total_beats * beat + 1.2) * RATE)
    cursor = 0.15
    for _ in range(2):
        for name, length in phrase:
            if name:
                music_box(samples, int(cursor * RATE), PITCH[name], length * beat + 0.35, 0.55)
                if length >= 1:
                    music_box(samples, int(cursor * RATE), PITCH[name] / 2, length * beat, 0.16)
            cursor += length * beat
    write('christmas-music.wav', samples)


def sleigh_jingle():
    seconds = 3.2
    samples = [0.0] * int(seconds * RATE)
    rng = random.Random(9)
    t = 0.05
    while t < seconds - 0.2:
        start = int(t * RATE)
        for i in range(int(0.045 * RATE)):
            if start + i >= len(samples):
                break
            env = math.exp(-i / RATE / 0.012)
            noise = rng.uniform(-1, 1)
            ring = math.sin(2 * math.pi * (1800 + rng.randrange(0, 900)) * i / RATE)
            samples[start + i] += (noise * 0.35 + ring * 0.65) * env * 0.45
        t += 0.07 + rng.random() * 0.04
    # A short public-domain Jingle Bells tag on top of the shake.
    tag = [('E5', 0.16), ('E5', 0.16), ('E5', 0.32), ('E5', 0.16), ('E5', 0.16), ('E5', 0.45)]
    cursor = 0.35
    for name, length in tag:
        music_box(samples, int(cursor * RATE), PITCH[name], length + 0.2, 0.7)
        cursor += length
    write('sleigh-jingle.wav', samples)


def church_bells():
    seconds = 9.0
    samples = [0.0] * int(seconds * RATE)
    tolls = [(0.2, 'E5'), (1.7, 'C5'), (3.3, 'G4'), (5.1, 'E5'), (6.8, 'C5')]
    partials = (1, 2.0, 2.76, 3.4, 4.2)
    weights = (1, 0.45, 0.28, 0.14, 0.08)
    for start, name in tolls:
        base = PITCH[name] * 0.5
        begin = int(start * RATE)
        for i in range(int(3.4 * RATE)):
            if begin + i >= len(samples):
                break
            t = i / RATE
            env = math.exp(-1.15 * t) * min(1, t * 40)
            tone = sum(math.sin(2 * math.pi * base * part * t) * weight for part, weight in zip(partials, weights))
            samples[begin + i] += tone * env * 0.7
    write('christmas-bells.wav', samples)


if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    christmas_music()
    sleigh_jingle()
    church_bells()
    for name in ('christmas-music.wav', 'sleigh-jingle.wav', 'christmas-bells.wav'):
        print(name, (ROOT / name).stat().st_size)
