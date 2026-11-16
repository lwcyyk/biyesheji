"""Explicitly authorized M4 dedicated-scope acceptance."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.online_state.unidentified_acceptance import run

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--authorization-id',required=True)
    parser.add_argument('--allow-native-casdoor',required=True,action='store_true')
    args=parser.parse_args()
    run(args.out,args.authorization_id,args.allow_native_casdoor)
