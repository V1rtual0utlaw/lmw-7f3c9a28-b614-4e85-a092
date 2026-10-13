import json,sys,tempfile,threading,unittest,urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import Factory
from app import Handler,APP_VERSION
class DevelopmentPreview(unittest.TestCase):
    def test_preview_renders_captioned_documentary_and_short(self):
        f=Factory({'voice_id':'am_michael','captions':True},lambda _:None)
        with tempfile.TemporaryDirectory() as d,patch('factory.run'),patch('factory.duration',return_value=22),patch.object(f,'voice'),patch.object(f,'render') as render:
            report=f.preview(d)
            self.assertTrue(report['documentary_captions'])
            self.assertEqual(render.call_count,2)
            self.assertIn('text',render.call_args_list[0].kwargs)
            self.assertEqual(render.call_args_list[0].args[2].name,'documentary.mp4')
            self.assertTrue(render.call_args_list[1].args[3])
            self.assertTrue((Path(d)/'review.json').exists())
    def test_info_exposes_running_version_and_no_cache(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/info') as r:
                data=json.load(r);self.assertIn('no-store',r.headers['Cache-Control'])
            self.assertEqual(data['version'],APP_VERSION);self.assertTrue(data['documentary_captions']);self.assertEqual(data['voice_engine'],'kokoro')
        finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
