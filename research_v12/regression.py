import bootstrap
import unittest,json,io,os,time
from pathlib import Path
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def main():
    out=bootstrap.ROOT/'runs/regression';out.mkdir(parents=True,exist_ok=False);suite=unittest.TestSuite()
    for pattern in ['test_core.py','test_abstraction.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(bootstrap.ORIGINAL/'tests'),pattern=pattern))
    stream=io.StringIO();t=time.perf_counter();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (out/'raw.txt').write_text(stream.getvalue(),encoding='utf-8')
    obj={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'pass':result.wasSuccessful(),'seconds':time.perf_counter()-t,'scope':['preserved core','preserved abstraction'],'not_run':['full original exhaustive suite','native integration suite']}
    (out/'result.json').write_text(json.dumps(obj,indent=2),encoding='utf-8');print(obj)
if __name__=='__main__':main()
