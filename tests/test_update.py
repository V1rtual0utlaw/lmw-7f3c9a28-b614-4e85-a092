import json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from update import apply_archive
class Updates(unittest.TestCase):
    def package(self,path,unsafe=False):
        with zipfile.ZipFile(path,'w') as z:
            for name,text in {'app.py':'value=1','factory.py':'value=2','index.html':'new','version.json':json.dumps({'app':'true-science-stories-factory','version':'0.4.0'}),'config.json':'overwrite'}.items():z.writestr('true-science-factory/'+name,text)
            if unsafe:z.writestr('../escape.py','bad')
    def test_preserves_assets_and_skips_repeat(self):
        with tempfile.TemporaryDirectory() as d,patch('update.running',return_value=False):
            root=Path(d); (root/'config.json').write_text('original');(root/'app.py').write_text('old');a=root/'new.zip';self.package(a)
            self.assertTrue(apply_archive(a,root));self.assertEqual((root/'config.json').read_text(),'original')
            self.assertFalse(apply_archive(a,root));self.assertTrue(list((root/'runtime/update-backups').glob('*/app.py')))
    def test_unsafe_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=root/'new.zip';self.package(a,True)
            with self.assertRaises(ValueError):apply_archive(a,root)
            self.assertFalse((root/'app.py').exists())
    def test_running_blocks_update(self):
        with tempfile.TemporaryDirectory() as d,patch('update.running',return_value=True):
            root=Path(d);a=root/'new.zip';self.package(a)
            with self.assertRaises(RuntimeError):apply_archive(a,root)
if __name__=='__main__':unittest.main()
