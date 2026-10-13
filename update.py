"""Apply downloaded factory ZIPs without extracting or replacing user assets."""
import argparse, datetime, hashlib, json, os, re, shutil, sys, tempfile, urllib.request, urllib.parse, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALLOWED={'media.py','app.py','factory.py','research.py','index.html','launch.py','doctor.py','update.py','README.md','version.json','update-channel.json','START_WINDOWS.bat','UPDATE_FACTORY.bat','SETUP_AND_START.bat','SETUP.ps1','BOOTSTRAP.ps1'}
REQUIRED={'app.py','factory.py','index.html','version.json'}

def version_tuple(value): return tuple(int(x) for x in value.split('.'))
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def running():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8765/api/jobs',timeout=2) as r: return r.status==200
    except OSError: return False

def apply_archive(archive, root=ROOT):
    root=Path(root); runtime=root/'runtime'; runtime.mkdir(exist_ok=True)
    state=runtime/'update-state.json'
    fingerprint=digest(archive)
    if state.exists() and json.loads(state.read_text()).get('sha256')==fingerprint: return False
    with zipfile.ZipFile(archive) as z:
        entries={}
        for entry in z.infolist():
            name=entry.filename.replace('\\','/')
            parts=name.split('/')
            if name.startswith('/') or '..' in parts or ':' in name: raise ValueError('Unsafe archive path')
            if len(parts)==2 and parts[0]=='true-science-factory' and parts[1] in ALLOWED and not entry.is_dir():
                if parts[1] in entries: raise ValueError('Duplicate update file')
                if entry.file_size>2_000_000: raise ValueError('Unexpectedly large update file')
                entries[parts[1]]=entry
        if not REQUIRED.issubset(entries): raise ValueError('Not a supported factory update ZIP')
        version=json.loads(z.read(entries['version.json']))
        if version.get('app')!='true-science-stories-factory': raise ValueError('Wrong application package')
        new=version_tuple(version['version'])
        current=root/'version.json'
        if current.exists() and new<=version_tuple(json.loads(current.read_text())['version']):
            print('Already running this version or a newer one.'); return False
        if running(): raise RuntimeError('Close the factory command window before updating. Active production will not be interrupted.')
        stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup=runtime/'update-backups'/stamp; backup.mkdir(parents=True)
        prior={}; changed=[]
        with tempfile.TemporaryDirectory(dir=runtime) as temp:
            stage=Path(temp)
            for name,entry in entries.items():
                content=z.read(entry)
                if name.endswith('.py'): compile(content,name,'exec')
                (stage/name).write_bytes(content)
            try:
                for name in entries:
                    target=root/name
                    if target.is_symlink(): raise ValueError('Refusing to replace a symbolic link')
                    prior[name]=target.exists()
                    if target.exists(): shutil.copy2(target,backup/name)
                    os.replace(stage/name,target); changed.append(name)
            except Exception:
                for name in reversed(changed):
                    if prior[name]: shutil.copy2(backup/name,root/name)
                    else: (root/name).unlink(missing_ok=True)
                raise
        state.write_text(json.dumps({'version':version['version'],'sha256':fingerprint,'archive':str(archive),'backup':str(backup)},indent=2))
    print('Updated to '+version['version']+'. Settings, models and outputs preserved.')
    return True

def github_update(root=ROOT):
    root=Path(root)
    channel=root/'update-channel.json'
    if not channel.exists(): return False
    settings=json.loads(channel.read_text(encoding='utf-8-sig'))
    repo=settings.get('repository')
    if not repo or not settings.get('enabled',True): return False
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo): raise ValueError('Invalid configured GitHub repository')
    req=urllib.request.Request('https://api.github.com/repos/'+repo+'/releases/latest',headers={'User-Agent':'TrueScienceStoriesFactoryUpdater/0.5','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=8) as r: release=json.loads(r.read(1_000_000))
    if release.get('draft') or release.get('prerelease'): return False
    current=json.loads((root/'version.json').read_text())['version']
    version=release['tag_name'].removeprefix('v')
    if version_tuple(version)<=version_tuple(current): return False
    asset=next((x for x in release.get('assets',[]) if x.get('name')=='True-Science-Stories-Factory.zip'),None)
    if not asset: raise ValueError('Release does not include the factory archive')
    url=asset['browser_download_url']
    expected='https://github.com/'+repo+'/releases/download/'
    if not url.startswith(expected): raise ValueError('Release asset came from an unexpected repository')
    checksum=asset.get('digest','')
    if not re.fullmatch(r'sha256:[0-9a-fA-F]{64}',checksum): raise ValueError('Release asset is missing its GitHub SHA-256 digest')
    if not 0<asset.get('size',0)<=10_000_000: raise ValueError('Release archive size is unexpected')
    cache=root/'runtime'/'update-downloads';cache.mkdir(parents=True,exist_ok=True)
    archive=cache/('factory-'+version+'.zip');part=archive.with_suffix('.partial')
    print('Downloading factory '+version+' from GitHub...')
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'TrueScienceStoriesFactoryUpdater/0.5'})
        with urllib.request.urlopen(req,timeout=15) as response,part.open('wb') as out:
            size=0
            while True:
                chunk=response.read(65536)
                if not chunk:break
                size+=len(chunk)
                if size>10_000_000:raise ValueError('Release download exceeded size limit')
                out.write(chunk)
        if size!=asset['size'] or digest(part).lower()!=checksum[7:].lower(): raise ValueError('Release checksum or size verification failed')
        with zipfile.ZipFile(part) as z:
            manifest=json.loads(z.read('true-science-factory/version.json'))
            if manifest['version']!=version:raise ValueError('Archive version differs from release tag')
            incoming=json.loads(z.read('true-science-factory/update-channel.json'))
            if incoming.get('repository')!=repo:raise ValueError('Update would change the configured repository')
        os.replace(part,archive)
        return apply_archive(archive,root)
    finally:
        part.unlink(missing_ok=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('archive',nargs='?');p.add_argument('--auto',action='store_true');a=p.parse_args()
    if a.auto:
        try:
            if github_update(): return
        except Exception as e:
            print('Online update unavailable; continuing with installed version: '+str(e))
    if a.archive: candidates=[Path(a.archive)]
    else:
        folders=[Path.home()/'Downloads']
        if os.environ.get('USERPROFILE'): folders.append(Path(os.environ['USERPROFILE'])/'Downloads')
        candidates=list({x for f in folders if f.exists() for x in f.glob('True-Science-Stories-Factory*.zip')})
        candidates.sort(key=lambda x:x.stat().st_mtime,reverse=True)
    if not candidates:
        print('No downloaded factory update found.' if not a.auto else 'No new update downloaded.');return
    apply_archive(candidates[0])
if __name__=='__main__':
    try: main()
    except Exception as e: print('Update stopped: '+str(e));sys.exit(1)
