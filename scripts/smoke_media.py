"""Real local narration and word-timing smoke test on the Windows release runner."""
import sys,wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import ROOT,Narrator,write_captions
folder=ROOT/'runtime/media-smoke';folder.mkdir(parents=True,exist_ok=True)
text="Some deep ocean animals make their own light. It's called bioluminescence. A chemical reaction turns energy into a glow."
narrator=Narrator(ROOT)
audio=folder/'narration.wav';narrator.synthesize(text,audio)
with wave.open(str(audio)) as w:
    assert w.getnframes()/w.getframerate()>3
words=narrator.timings(audio,text)
assert len(words)==len(text.split())
assert all(x['end']>=x['start'] for x in words)
write_captions(words,folder/'captions.ass',True)
print('Real Windows Kokoro voice + Whisper word timing + highlighted caption assets passed.')
