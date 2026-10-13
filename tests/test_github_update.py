import hashlib,io,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from update import github_update
class GitHubUpdates(unittest.TestCase):
    def fixture(self,root,bad=False):
        (root/'version.json').write_text(json.dumps({'version':'0.4.1'}))
        (root/'update-channel.json').write_text(json.dumps({'repository':'owner/factory','enabled':True}))
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for name,text in {'app.py':'value=1','factory.py':'value=2','index.html':'new','version.json':json.dumps({'app':'true-science-stories-factory','version':'0.5.0'}),'update-channel.json':json.dumps({'repository':'owner/factory','enabled':True})}.items():z.writestr('true-science-factory/'+name,text)
        data=b.getvalue()
        asset={'name':'True-Science-Stories-Factory.zip','browser_download_url':'https://github.com/owner/factory/releases/download/v0.5.0/True-Science-Stories-Factory.zip','size':len(data),'digest':'sha256:'+('0'*64 if bad else hashlib.sha256(data).hexdigest())}
        return [io.BytesIO(json.dumps({'tag_name':'v0.5.0','assets':[asset]}).encode()),io.BytesIO(data)]
    def test_verified_online_update(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);responses=self.fixture(root)
            with patch('update.urllib.request.urlopen',side_effect=responses),patch('update.running',return_value=False):self.assertTrue(github_update(root))
            self.assertEqual(json.loads((root/'version.json').read_text())['version'],'0.5.0')
    def test_bad_digest_keeps_installed_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);responses=self.fixture(root,True)
            with patch('update.urllib.request.urlopen',side_effect=responses):
                with self.assertRaisesRegex(ValueError,'checksum'):github_update(root)
            self.assertEqual(json.loads((root/'version.json').read_text())['version'],'0.4.1')
    def test_unconfigured_no_network(self):
        with tempfile.TemporaryDirectory() as d,patch('update.urllib.request.urlopen') as request:
            self.assertFalse(github_update(Path(d)));request.assert_not_called()
if __name__=='__main__':unittest.main()
