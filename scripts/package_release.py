"""Create a release archive from this source tree; models/media are excluded."""
import argparse,json,zipfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',default='dist/True-Science-Stories-Factory.zip');a=p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',a.repository):raise SystemExit('Invalid repository')
files=[x for x in ROOT.iterdir() if x.is_file() and x.suffix in {'.py','.ps1','.bat','.html','.json','.md'}]
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:
  if f.name=='update-channel.json':continue
  z.write(f,'true-science-factory/'+f.name)
 z.writestr('true-science-factory/update-channel.json',json.dumps({'repository':a.repository,'enabled':True},indent=2))
print(out)
