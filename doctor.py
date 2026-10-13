import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
    installed=json.loads((ROOT/'runtime/installed.json').read_text(encoding='utf-8-sig'))
    ffmpeg=Path(installed['ffmpeg']); probe=ffmpeg.with_name('ffprobe.exe')
    for exe in [ffmpeg,probe]: subprocess.run([str(exe),'-version'],check=True,stdout=subprocess.DEVNULL)
    with urllib.request.urlopen(cfg['ollama']+'/api/tags',timeout=10) as r: models=json.load(r)
    if cfg['model'] not in {m['name'] for m in models['models']}: raise RuntimeError('Ollama script model missing')
    with urllib.request.urlopen(cfg['comfy']+'/object_info/CheckpointLoaderSimple',timeout=10) as r: info=json.load(r)
    w=json.loads((ROOT/'workflow.json').read_text(encoding='utf-8-sig'))
    if w['4']['inputs']['ckpt_name'] not in info['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]: raise RuntimeError('ComfyUI checkpoint missing')
    with urllib.request.urlopen(cfg['comfy']+'/system_stats',timeout=10) as r: stats=json.load(r)
    if not any('cuda' in str(d.get('type','')).lower() for d in stats.get('devices',[])): raise RuntimeError('ComfyUI has not detected NVIDIA CUDA. Update the NVIDIA driver and re-run setup.')
    if not (ROOT/'runtime/voice-test.wav').is_file(): raise RuntimeError('Voice smoke test missing')
    print('Ready: FFmpeg, Ollama model, ComfyUI CUDA + image checkpoint, and Piper test voice.')
if __name__=='__main__':
    try: main()
    except Exception as e: print(f'Dependency check failed: {e}'); sys.exit(1)
