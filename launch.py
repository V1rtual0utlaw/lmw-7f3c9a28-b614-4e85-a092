"""Start only local endpoints, then the production interface."""
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def ready(url):
    try:
        with urllib.request.urlopen(url,timeout=2) as r: return r.status==200
    except OSError: return False

def wait(url,process,seconds=180):
    for _ in range(seconds):
        if ready(url): return
        if process.poll() is not None: raise RuntimeError('Local service exited. See logs folder; ComfyUI may need a newer NVIDIA driver.')
        time.sleep(1)
    raise RuntimeError('Local service startup timed out. See logs folder.')

def start():
    installed=json.loads((ROOT/'runtime/installed.json').read_text(encoding='utf-8-sig'))
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
    os.environ['PATH']=str(Path(installed['ffmpeg']).parent)+os.pathsep+os.environ['PATH']
    logs=ROOT/'logs'; logs.mkdir(exist_ok=True)
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    if not ready(cfg['ollama']+'/api/tags'):
        env=os.environ.copy(); env['OLLAMA_HOST']='127.0.0.1:11434'
        with (logs/'ollama.log').open('ab') as f:
            p=subprocess.Popen([installed['ollama'],'serve'],stdout=f,stderr=f,env=env,creationflags=flags)
        wait(cfg['ollama']+'/api/tags',p)
    if not ready(cfg['comfy']+'/system_stats'):
        base=Path(installed['comfy'])
        with (logs/'comfy.log').open('ab') as f:
            p=subprocess.Popen([str(base/'python_embeded/python.exe'),'-s',str(base/'ComfyUI/main.py'),'--windows-standalone-build','--listen','127.0.0.1','--port','8188','--lowvram'],cwd=base,stdout=f,stderr=f,creationflags=flags)
        wait(cfg['comfy']+'/system_stats',p,300)
    if '--prepare' in sys.argv: return
    if ready('http://127.0.0.1:8765/api/jobs'):
        import webbrowser
        webbrowser.open('http://127.0.0.1:8765'); return
    subprocess.run([installed['python'],str(ROOT/'app.py')],cwd=ROOT,check=True)

if __name__=='__main__':
    try: start()
    except Exception as e:
        print(f'Launch failed: {e}'); sys.exit(1)
