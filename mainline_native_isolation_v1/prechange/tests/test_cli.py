from pathlib import Path
import json,subprocess,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def call(self,*args):
        return subprocess.run([sys.executable,str(ROOT/'scripts/cli.py'),*args],cwd=ROOT,
                              capture_output=True,text=True,encoding='utf-8',timeout=30)

    def test_reference_and_certificate_commands(self):
        result=self.call('solve','examples/stay_finish.json','--engine','reference')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'FEASIBLE')
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'proof.json')
            created=self.call('certificate','examples/three_worlds.json','--out',path)
            self.assertEqual(created.returncode,0,created.stderr)
            checked=self.call('check','examples/three_worlds.json',path,'--kind','impossibility')
            self.assertEqual(checked.returncode,0,checked.stderr)
            self.assertEqual(json.loads(checked.stdout)['verdict'],'ACCEPTED')
            original=Path(path).read_bytes()
            repeated=self.call('certificate','examples/three_worlds.json','--out',path)
            self.assertNotEqual(repeated.returncode,0)
            self.assertEqual(Path(path).read_bytes(),original)


if __name__=='__main__':unittest.main()
