"""Run the isolated ONLINE_TRUSTED_STATE_V1 runtime from a source checkout."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from auth_lifecycle.online_state.cli import main

if __name__ == "__main__":
    main()
