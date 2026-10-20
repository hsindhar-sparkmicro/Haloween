"""Deterministic original ambience; no external audio rights required."""
import math
import random
import struct
import wave
from pathlib import Path
random.seed(31)
root = Path(__file__).resolve().parents[1] / 'halloween_hub/static/assets'
for name, duration in [('midnight', 12), ('whisper', 3)]:
    rate = 22050
    samples = bytearray()
    previous = 0
    for i in range(rate * duration):
        t = i / rate
        previous = .96 * previous + .04 * random.uniform(-1, 1)
        edge = min(1, t * 2, (duration - t) * 2)
        wind = previous * .7
        tone = math.sin(2 * math.pi * 110 * t) * .05 + math.sin(2 * math.pi * 165 * t) * .025
        chime = math.sin(2 * math.pi * 660 * t) * math.exp(-4 * (t % 4)) * .08
        value = (wind + tone + chime) * edge
        samples.extend(struct.pack('<h', int(value * 26000)))
    with wave.open(str(root / (name + '.wav')), 'wb') as output:
        output.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        output.writeframes(samples)
for name, notes in [('quiet-scene',[110,146.8,130.8,110]),('mist-scene',[174.6,164.8,155.6,146.8]),('pumpkin-scene',[261.6,329.6,392,523.2]),('vampire-scene',[98,116.5,110,73.4]),('buster-scene',[196,246.9,293.7,392]),('witch-scene',[220,207.7,261.6,174.6]),('graveyard-scene',[65.4,77.8,82.4,65.4]),('train-scene',[146.8,196,174.6,130.8])]:
    rate=22050
    samples=bytearray()
    for i in range(rate*3):
        t=i/rate
        frequency=notes[min(3,int(t/.75))]
        pulse=t%.75
        envelope=min(1,t*3,(3-t)*3)*math.exp(-pulse*2)
        value=(math.sin(2*math.pi*frequency*t)*.13+math.sin(2*math.pi*frequency*2*t)*.035)*envelope
        samples.extend(struct.pack('<h',int(value*24000)))
    with wave.open(str(root/(name+'.wav')),'wb') as output:
        output.setparams((1,2,rate,0,'NONE','not compressed'))
        output.writeframes(samples)
