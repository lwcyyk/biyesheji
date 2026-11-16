"""Download official, pinned native distributions into an isolated local runtime."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime/l1"
ASSETS = {
    "keycloak-26.8.1.zip": "https://github.com/keycloak/keycloak/releases/download/26.8.1/keycloak-26.8.1.zip",
    "keycloak-26.8.1.zip.sha1": "https://github.com/keycloak/keycloak/releases/download/26.8.1/keycloak-26.8.1.zip.sha1",
    "casdoor_Windows_x86_64.zip": "https://github.com/casdoor/casdoor/releases/download/v4.25.0/casdoor_Windows_x86_64.zip",
    "casdoor_4.25.0_checksums.txt": "https://github.com/casdoor/casdoor/releases/download/v4.25.0/casdoor_4.25.0_checksums.txt",
    "OpenJDK21U-jre_x64_windows_hotspot_21.0.9_10.zip": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.9%2B10/OpenJDK21U-jre_x64_windows_hotspot_21.0.9_10.zip",
    "OpenJDK21U-jre_x64_windows_hotspot_21.0.9_10.zip.sha256.txt": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.9%2B10/OpenJDK21U-jre_x64_windows_hotspot_21.0.9_10.zip.sha256.txt",
}


def download(item):
    name, url = item; path = RUNTIME / "downloads" / name
    if not path.exists():
        part = path.with_name(path.name + ".part")
        # Certificate verification remains enabled; Windows offline CRL lookup
        # may fail, so unavailable revocation information is best-effort only.
        subprocess.run(["curl.exe", "--ssl-revoke-best-effort", "-fLsS", "--connect-timeout", "20", "--max-time", "600", url, "-o", str(part)], check=True)
        assert part.resolve().is_relative_to(RUNTIME.resolve()) and path.resolve().is_relative_to(RUNTIME.resolve())
        part.replace(path)
    record = {"name": name, "url": url, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    print(json.dumps({"downloaded": name, "bytes": record["bytes"]}), flush=True)
    return record


def main():
    (RUNTIME / "downloads").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:records = list(pool.map(download, ASSETS.items()))
    downloads = RUNTIME / "downloads"
    kc = downloads / "keycloak-26.8.1.zip"
    expected = (downloads / (kc.name + ".sha1")).read_text().split()[0].lower()
    if hashlib.sha1(kc.read_bytes()).hexdigest() != expected:raise ValueError("Keycloak upstream checksum mismatch")
    jre = downloads / "OpenJDK21U-jre_x64_windows_hotspot_21.0.9_10.zip"
    expected = (downloads / (jre.name + ".sha256.txt")).read_text().split()[0].lower()
    if hashlib.sha256(jre.read_bytes()).hexdigest() != expected:raise ValueError("JRE checksum mismatch")
    cas = downloads / "casdoor_Windows_x86_64.zip"
    lines = (downloads / "casdoor_4.25.0_checksums.txt").read_text().splitlines()
    expected = next(line.split()[0] for line in lines if line.split()[-1].lstrip("*") == cas.name)
    if hashlib.sha256(cas.read_bytes()).hexdigest() != expected:raise ValueError("Casdoor checksum mismatch")
    for path, name in [(kc, "keycloak"), (jre, "java"), (cas, "casdoor")]:
        destination = RUNTIME / "dist" / name
        if destination.exists():continue
        with zipfile.ZipFile(path) as z:
            for member in z.infolist():
                if not (destination / member.filename).resolve().is_relative_to(destination.resolve()):raise ValueError("archive path escape")
            z.extractall(destination)
    target = ROOT / "experiments/l1/distributions.json"; target.parent.mkdir(parents=True, exist_ok=True)
    record={"status": "CHECKSUM_VERIFIED", "artifacts": records,
        "transport": "TLS certificate verification; Windows unavailable CRL best effort", "scope": "deployment versions; not confirmation of study thresholds"}
    if target.exists():
        if json.loads(target.read_text(encoding="utf-8"))!=record:raise ValueError("existing distribution lock differs; do not overwrite evidence")
    else:
        with target.open("x", encoding="utf-8") as f:json.dump(record, f, indent=2)
    print("Official distribution checksums verified; extracted under .runtime/l1", flush=True)


if __name__ == "__main__":main()
