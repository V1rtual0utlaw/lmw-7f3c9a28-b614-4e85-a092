import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import align_script,write_captions,caption_groups,stamp,safe_text
class Captions(unittest.TestCase):
    def test_exact_words_keep_script_and_audio_times(self):
        words=[{'text':'Deep','start':0,'end':.3},{'text':'ocean','start':.3,'end':.7},{'text':'animals','start':.7,'end':1.1},{'text':'glow','start':1.1,'end':1.5}]
        aligned=align_script('Deep ocean animals glow.',words)
        self.assertEqual(aligned[-1]['text'],'glow.');self.assertEqual(aligned[-1]['end'],1.5)
    def test_mismatch_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'NC:'):align_script('Deep ocean animals glow.',[{'text':'unrelated','start':0,'end':1}])
    def test_phrase_highlight_safe_area_and_sidecar(self):
        words=[{'text':x,'start':i*.4,'end':(i+1)*.4} for i,x in enumerate('Deep ocean animals make their own light.'.split())]
        with tempfile.TemporaryDirectory() as d:
            p=write_captions(words,Path(d)/'captions.ass',True);s=p.read_text(encoding='utf-8-sig')
            self.assertIn('PlayResY: 1280',s);self.assertIn('\\pos(360,850)',s)
            self.assertIn('\\c&H0000D5FF&',s);self.assertEqual(s.count('Dialogue:'),len(words))
            self.assertTrue(p.with_suffix('.srt').exists());self.assertTrue(all(len(x)<=3 for x in caption_groups(words)))
    def test_times_and_escape(self):
        self.assertEqual(stamp(61.23,True),'0:01:01.23');self.assertEqual(stamp(61.234),'00:01:01,234')
        self.assertNotIn('{',safe_text('{\\pos(1,1)}'))
if __name__=='__main__':unittest.main()
