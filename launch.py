"""Start only local endpoints, then the production interface."""
import json, os, shutil, subprocess, sys, time, urllib.request
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

def executable(label, candidates):
    for value in candidates:
        if value and Path(value).is_file(): return str(Path(value).resolve())
    paths=', '.join(str(x) for x in candidates if x)
    raise RuntimeError(f'{label} executable is missing. Checked: {paths}. No software was reinstalled.')

def repair_paths(installed, root=ROOT):
    root=Path(root); fixed=dict(installed)
    fixed['python']=executable('Factory Python',[root/'runtime/venv/Scripts/python.exe',installed.get('python'),sys.executable])
    candidates=[root/'runtime/ComfyUI_windows_portable',Path(installed['comfy']) if installed.get('comfy') else None]
    base=next((x for x in candidates if x and (x/'python_embeded/python.exe').is_file() and (x/'ComfyUI/main.py').is_file()),None)
    if base: fixed['comfy']=str(base.resolve())
    local=Path(os.environ.get('LOCALAPPDATA',str(Path.home())))
    ollama_candidates=[installed.get('ollama'),shutil.which('ollama'),local/'Programs/Ollama/ollama.exe']
    found=next((str(Path(x).resolve()) for x in ollama_candidates if x and Path(x).is_file()),None)
    if found:fixed['ollama']=found
    ffmpeg_candidates=[installed.get('ffmpeg'),shutil.which('ffmpeg')]
    found=next((str(Path(x).resolve()) for x in ffmpeg_candidates if x and Path(x).is_file()),None)
    if found:fixed['ffmpeg']=found
    return fixed

def spawn(label,args,**kwargs):
    print(f'Starting {label}: {args[0]}')
    try:return subprocess.Popen(args,**kwargs)
    except FileNotFoundError as e:raise RuntimeError(f'{label} could not start. Missing executable or working folder: {args[0]}; folder: {kwargs.get("cwd","current folder")}') from e

def start():
    installed_path=ROOT/'runtime/installed.json'
    installed=json.loads(installed_path.read_text(encoding='utf-8-sig'))
    fixed=repair_paths(installed)
    if fixed!=installed:
        print('Repairing saved installation paths for this factory folder.')
        installed_path.with_suffix('.json.backup').write_text(json.dumps(installed,indent=2),encoding='utf-8')
        installed_path.write_text(json.dumps(fixed,indent=2),encoding='utf-8')
    installed=fixed
    cfg_path=ROOT/'config.json'
    cfg=json.loads(cfg_path.read_text(encoding='utf-8-sig'))
    if cfg.get('piper_python') and not Path(cfg['piper_python']).is_file():
        cfg['piper_python']=installed['python']
        cfg_path.write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    ffmpeg=installed.get('ffmpeg')
    if ffmpeg and Path(ffmpeg).is_file():os.environ['PATH']=str(Path(ffmpeg).parent)+os.pathsep+os.environ['PATH']
    logs=ROOT/'logs';logs.mkdir(exist_ok=True)
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    if not ready(cfg['ollama']+'/api/tags'):
        exe=executable('Ollama',[installed.get('ollama'),shutil.which('ollama')])
        env=os.environ.copy();env['OLLAMA_HOST']='127.0.0.1:11434'
        with (logs/'ollama.log').open('ab') as f:p=spawn('Ollama',[exe,'serve'],stdout=f,stderr=f,env=env,creationflags=flags)
        wait(cfg['ollama']+'/api/tags',p)
    if not ready(cfg['comfy']+'/system_stats'):
        if not installed.get('comfy'):raise RuntimeError('ComfyUI installation folder is not configured in runtime/installed.json.')
        base=Path(installed['comfy'])
        exe=executable('ComfyUI Python',[base/'python_embeded/python.exe'])
        main=base/'ComfyUI/main.py'
        if not main.is_file():raise RuntimeError(f'ComfyUI main.py is missing: {main}. No files were reinstalled.')
        with (logs/'comfy.log').open('ab') as f:
            p=spawn('ComfyUI',[exe,'-s',str(main),'--windows-standalone-build','--listen','127.0.0.1','--port','8188','--lowvram'],cwd=base,stdout=f,stderr=f,creationflags=flags)
        wait(cfg['comfy']+'/system_stats',p,300)
    if '--prepare' in sys.argv:return
    if ready('http://127.0.0.1:8765/api/jobs'):
        import webbrowser
        webbrowser.open('http://127.0.0.1:8765');return
    app=ROOT/'app.py'
    if not app.is_file():raise RuntimeError(f'Factory app.py is missing: {app}')
    p=spawn('factory',[installed['python'],str(app)],cwd=ROOT)
    if p.wait():raise RuntimeError('Factory exited with an error. See the message printed above.')

if __name__=='__main__':
    try:start()
    except Exception as e:
        print(f'Launch failed: {e}')
        try:
            (ROOT/'logs').mkdir(exist_ok=True)
            (ROOT/'logs/launch-error.txt').write_text(str(e),encoding='utf-8')
        except OSError:pass
        sys.exit(1)
