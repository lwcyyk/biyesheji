"""Create example inputs in a new directory (no overwrite)."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.fixtures import stay_finish,named_three_worlds,conflict_worlds,response_loss
p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
dest=Path(args.out);dest.mkdir(parents=True,exist_ok=False)
for name,model in {'stay_finish':stay_finish(horizon=8),'three_worlds':named_three_worlds(),
                   'adaptive_probe':conflict_worlds(informative_probe=True),'response_loss':response_loss()}.items():
 (dest/(name+'.json')).write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
