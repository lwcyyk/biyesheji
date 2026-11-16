"""Read-only imports of the preserved finite-model baseline."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
OLD = WORKSPACE / '研究/算法机制重构与原创性验证_2026-11-03'
ORIGINAL = WORKSPACE / 'auth-lifecycle'
sys.path[:0] = [str(ORIGINAL/'src'), str(OLD/'prototype'), str(OLD), str(OLD/'.deps')]

