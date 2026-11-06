"""Iola on a list's full lines. Takes a JSON file of {text: rate}, renders only what
clips.json does not have, and MERGES, so older lists keep their clips. Bare words and
syllables come out poor this way: run iola_short.py on those afterwards. Run with
while-you-live/audio/.venv, python -I."""
import json, hashlib, pathlib, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from kokoro import KPipeline
out = pathlib.Path(__file__).parent / 'iola'
man = json.load(open(out / 'clips.json'))
said = json.load(open(sys.argv[1]))
P = KPipeline(lang_code='a', device='mps')
tmp = tempfile.mktemp(suffix='.wav')
for text, rate in said.items():
    if text in man: continue
    speed = 0.72 if rate < 0.65 or len(text) < 16 else 0.85
    res = list(P(text.replace(' ... ', ', , '), voice='af_heart', speed=speed))
    wav = np.concatenate([r.audio.detach().cpu().numpy() for r in res])
    name = hashlib.md5(text.encode()).hexdigest()[:10] + '.mp3'
    sf.write(tmp, wav, 24000)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-af', 'apad=pad_dur=0.1', '-ac', '1', '-b:a', '48k', str(out / name)], check=True)
    man[text] = name
    print(round(len(wav) / 24000, 2), repr(text[:60]), r'/', ' '.join(r.phonemes for r in res)[:70])
json.dump(man, open(out / 'clips.json', 'w'), indent=0, ensure_ascii=False)
