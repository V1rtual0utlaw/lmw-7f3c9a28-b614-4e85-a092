import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from factory import Factory
class Scripts(unittest.TestCase):
    def test_sections_and_schema(self):
        f=Factory({},lambda _:None)
        scene={'narration':' '.join(['Organisms produce light using chemical reactions inside specialized cells.']*7),'image_prompt':'Scientific illustration','claims':['Chemical light'],'source_ids':['S1']}
        with patch.object(f,'llm',side_effect=[json.dumps({'title':'Ocean light','sections':['Chemistry','Ecology']}),json.dumps(scene),json.dumps(scene)]) as m:
            p=f.plan('Ocean light',1,'[S1] Ocean light source')
            self.assertEqual(len(p['scenes']),2)
            self.assertIsInstance(m.call_args.args[1],dict)
    def test_invalid_source_retries_with_reason(self):
        f=Factory({},lambda _:None)
        bad={'narration':'word '*40,'image_prompt':'image','claims':[],'source_ids':['S99']}
        good={**bad,'source_ids':['S1']}
        with patch.object(f,'llm',side_effect=[json.dumps({'title':'Ocean','sections':['A','B']}),json.dumps(bad),json.dumps(good),json.dumps(good)]) as m:
            f.plan('Ocean',1,'[S1] source text')
            self.assertIn('source_ids must use supplied IDs',m.call_args_list[2].args[0])
    def test_diagnostics_saved(self):
        f=Factory({},lambda _:None)
        with tempfile.TemporaryDirectory() as d,patch.object(f,'llm',return_value='{}'):
            f.debugdir=Path(d)
            with self.assertRaisesRegex(RuntimeError,'title must be nonempty'): f.plan('Ocean',1,'notes')
            self.assertEqual(len(list((Path(d)/'script-diagnostics').glob('*.json'))),3)
if __name__=='__main__':unittest.main()
