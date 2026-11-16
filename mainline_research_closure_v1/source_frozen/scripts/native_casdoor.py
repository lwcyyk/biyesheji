"""Explicitly authorized local Casdoor integration entry point."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.online_state.native_acceptance import run_native

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--authorization-id", required=True)
    parser.add_argument("--allow-native-casdoor", action="store_true", required=True)
    args = parser.parse_args()
    run_native(args.out, args.authorization_id, args.allow_native_casdoor)
