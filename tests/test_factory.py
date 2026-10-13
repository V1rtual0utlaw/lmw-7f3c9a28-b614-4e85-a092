import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import skim, groups
class Checks(unittest.TestCase):
    def test_duplicate(self):
        seen=set(); t='Ocean animals can produce light through chemical reactions inside specialized cells within their bodies.'
        self.assertEqual(skim(t,25,seen),[])
        self.assertIn('NC: duplicate narration',skim(t,25,seen))
    def test_short_and_context(self):
        r=skim('And it glows',4,set()); self.assertEqual(len(r),4)
    def test_complete_grouping(self):
        t=' '.join(['Animals produce light through chemical reactions inside special cells in their bodies.']*12)
        g=groups(t); self.assertEqual(' '.join(g),t); self.assertTrue(all(x.endswith('.') for x in g))
if __name__=='__main__': unittest.main()
