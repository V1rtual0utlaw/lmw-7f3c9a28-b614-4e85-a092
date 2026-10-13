import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from launch import repair_paths,executable,spawn
class Launcher(unittest.TestCase):
    def test_moved_install_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ['runtime/venv/Scripts/python.exe','runtime/ComfyUI_windows_portable/python_embeded/python.exe','runtime/ComfyUI_windows_portable/ComfyUI/main.py']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('placeholder')
            fixed=repair_paths({'python':'missing/python.exe','comfy':'missing/comfy'},root)
            self.assertEqual(fixed['python'],str((root/'runtime/venv/Scripts/python.exe').resolve()))
            self.assertEqual(fixed['comfy'],str((root/'runtime/ComfyUI_windows_portable').resolve()))
    def test_missing_tool_names_path(self):
        with self.assertRaisesRegex(RuntimeError,'Ollama executable is missing'):executable('Ollama',['nonexistent.exe'])
    def test_spawn_error_names_component(self):
        with patch('launch.subprocess.Popen',side_effect=FileNotFoundError()):
            with self.assertRaisesRegex(RuntimeError,'ComfyUI could not start'):spawn('ComfyUI',['missing/python.exe'])
if __name__=='__main__':unittest.main()
