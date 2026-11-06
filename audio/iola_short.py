"""Iola on a bare word or a syllable. Kokoro is poor on a tiny input, so each one is
said inside a sentence and cut back out on the token timestamps. Full lines are not
touched. Run with while-you-live/audio/.venv, python -I."""
import json, hashlib, pathlib, re
import numpy as np
from kokoro import KPipeline
import soundfile as sf, subprocess, sys, tempfile
SR = 24000
TMP = tempfile.mktemp(suffix='.wav')
out = pathlib.Path(__file__).parent / 'iola'
man = json.load(open(out / 'clips.json'))
P = KPipeline(lang_code='a', device='mps')

def cut(phrase, tries=('The word is {}, and that is all.', 'Now say {}, and then stop.')):
    want = re.findall(r"[a-z']+", phrase.lower())
    for tmpl in tries:
        for r in P(tmpl.format(phrase), voice='af_heart', speed=0.82):
            toks = [t for t in r.tokens if re.search(r'[a-z]', t.text.lower())]
            words = [t.text.lower().strip(",.") for t in toks]
            for i in range(len(words) - len(want) + 1):
                if words[i:i + len(want)] == want:
                    a, b = toks[i].start_ts, toks[i + len(want) - 1].end_ts
                    if a is None or b is None: continue
                    aud = r.audio.detach().cpu().numpy()
                    s = max(0, int((a - 0.02) * SR)); e = min(len(aud), int((b + 0.05) * SR))
                    clip = aud[s:e].copy(); f = min(int(0.012 * SR), len(clip) // 4)
                    clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
                    return clip
    raise RuntimeError('no cut: ' + phrase)

rows = []; parts = {}
def write(text, wav):
    name = hashlib.md5(('v2' + text).encode()).hexdigest()[:10] + '.mp3'
    old = man.get(text)
    sf.write(TMP, np.concatenate([wav, np.zeros(int(0.08 * SR))]), SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', TMP, '-ac', '1', '-b:a', '48k', str(out / name)], check=True)
    if old and old != name: (out / old).unlink(missing_ok=True)
    man[text] = name; rows.append((round(len(wav) / SR, 2), text))

short = [t for t in man if '.' not in t]
# A JSON list of texts, to do one list's words and leave the older lists' clips alone.
if len(sys.argv) > 1:
    only = set(json.load(open(sys.argv[1]))); short = [t for t in short if t in only]
for t in [t for t in short if ', ' not in t]:
    parts[t] = cut(t); write(t, parts[t])
for t in [t for t in short if ', ' in t]:
    gap = np.zeros(int(0.32 * SR)); seq = []
    for p in t.split(', '):
        c = parts.get(p)
        if c is None: c = parts[p] = cut(p)
        seq += [c, gap]
    write(t, np.concatenate(seq[:-1]))
json.dump(man, open(out / 'clips.json', 'w'), indent=0, ensure_ascii=False)
for d, t in sorted(rows): print(d, repr(t))
