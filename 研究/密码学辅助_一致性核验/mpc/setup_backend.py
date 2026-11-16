"""Fetch one pinned official MP-SPDZ release into this research directory only."""
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
URL = "https://github.com/data61/MP-SPDZ/releases/download/v0.4.4/mp-spdz-0.4.4.tar.xz"
EXPECTED = "73d6473526101b4433999fc4f7521fdfdc53ddf018e5f64480518d6293f62760"


def main():
    VENDOR.mkdir(exist_ok=True)
    archive = VENDOR / "mp-spdz-0.4.4.tar.xz"
    if not archive.exists():
        print("Downloading pinned official MP-SPDZ v0.4.4 archive", flush=True)
        request = urllib.request.Request(URL, headers={"User-Agent": "auth-lifecycle-research"})
        with urllib.request.urlopen(request, timeout=45) as response, archive.open("xb") as output:
            while chunk := response.read(1 << 20): output.write(chunk)
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != EXPECTED: raise ValueError("Archive hash mismatch; retained without extraction")
    marker = VENDOR / "backend_release.json"
    if marker.exists():
        print(marker.read_text()); return
    with tarfile.open(archive) as source:
        tops = sorted({Path(m.name).parts[0] for m in source.getmembers() if Path(m.name).parts})
        for member in source.getmembers():
            dest = (VENDOR / member.name).resolve()
            if not dest.is_relative_to(VENDOR.resolve()): raise ValueError("archive path escapes vendor")
        source.extractall(VENDOR, filter="data")
    metadata = {"url": URL, "version": "0.4.4", "sha256": actual,
                "archive_bytes": archive.stat().st_size, "top_level_paths": tops,
                "status": "UPSTREAM_DISTRIBUTION_NOT_OUR_CRYPTOGRAPHIC_CONTRIBUTION"}
    marker.write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__": main()
