import shutil,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import animation_indices,wan_workflow,Factory,run,duration
class Animation(unittest.TestCase):
    def test_three_distinct_scenes(self):
        for count in range(1,30):
            chosen=animation_indices(count)
            self.assertEqual(len(chosen),min(3,count));self.assertTrue(all(0<=x<count for x in chosen))
    def test_native_wan_graph(self):
        graph=wan_workflow('A calf walking slowly',123)
        self.assertEqual(graph['6']['inputs']['length'],65)
        self.assertEqual(graph['2']['inputs']['device'],'cpu')
        self.assertEqual(graph['10']['class_type'],'VAEDecodeTiled')
        for node in graph.values():
            for value in node['inputs'].values():
                if isinstance(value,list):self.assertIn(value[0],graph)
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg is required for mixed render verification')
    def test_actual_mixed_render_preserves_narration_length(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);image=root/'still.png';animation=root/'motion.mp4';audio=root/'voice.wav';out=root/'mixed.mp4'
            run(['ffmpeg','-y','-f','lavfi','-i','color=c=blue:s=320x180','-frames:v','1',image])
            run(['ffmpeg','-y','-f','lavfi','-i','testsrc2=s=320x180:r=16:d=1','-c:v','libx264','-pix_fmt','yuv420p',animation])
            run(['ffmpeg','-y','-f','lavfi','-i','sine=frequency=220:duration=2',audio])
            Factory({'captions':False},lambda _:None).render(image,audio,out,animation=animation)
            self.assertLess(abs(duration(out)-2),.15)
if __name__=='__main__':unittest.main()
