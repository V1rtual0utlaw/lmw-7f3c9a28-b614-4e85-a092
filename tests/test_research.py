import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research import research, ResearchError
class ResearchTests(unittest.TestCase):
    def test_fetch_attribution_cache(self):
        def api(params):
            if params.get('list')=='search': return {'query':{'search':[{'pageid':1}]}}
            return {'query':{'pages':[{'title':'Bioluminescence','fullurl':'https://en.wikipedia.org/wiki/Bioluminescence','extract':'chemical light reaction. '*120}]}}
        with tempfile.TemporaryDirectory() as d, patch('research.fetch',side_effect=api) as f:
            notes=research('bioluminescence',d,lambda _:None)
            self.assertIn('[S1]',notes)
            self.assertTrue((Path(d)/'sources.txt').exists())
            n=f.call_count
            self.assertEqual(research('bioluminescence',d),notes)
            self.assertEqual(f.call_count,n)
            self.assertEqual(len(json.loads((Path(d)/'research.json').read_text())['sources']),1)
    def test_no_sources_stops(self):
        with tempfile.TemporaryDirectory() as d, patch('research.fetch',return_value={'query':{'search':[]}}):
            with self.assertRaises(ResearchError): research('unknown',d,lambda _:None)
            self.assertFalse((Path(d)/'research.json').exists())
    def test_disambiguation_rejected(self):
        def api(p):
            return {'query':{'search':[{'pageid':2}]}} if p.get('list') else {'query':{'pages':[{'title':'Ambiguous','extract':'word '*150,'pageprops':{'disambiguation':''}}]}}
        with tempfile.TemporaryDirectory() as d,patch('research.fetch',side_effect=api):
            with self.assertRaises(ResearchError): research('ambiguous',d,lambda _:None)
if __name__=='__main__': unittest.main()
