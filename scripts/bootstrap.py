"""Fetch the exact build dependencies declared in build-dependencies.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "build-dependencies.json"
DEPENDENCIES = ROOT / ".build-deps" / ("windows" if sys.platform == "win32" else "linux")


def run(*args: str, cwd: Path | None = None) -> None:
  subprocess.run(args, cwd=cwd, check=True)


def git(target: Path, *args: str) -> None:
  run("git", "-C", str(target), *args)


def sha256(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
      digest.update(chunk)
  return digest.hexdigest()


def checkout(name: str, spec: dict[str, str]) -> Path:
  target = DEPENDENCIES / name
  if not (target / ".git").is_dir():
    target.mkdir(parents=True, exist_ok=True)
    run("git", "init", str(target))
  probe = subprocess.run(
    ["git", "-C", str(target), "rev-parse", "--git-dir"],
    capture_output=True, text=True
  )
  if probe.returncode != 0 and "dubious ownership" in probe.stderr:
    run("git", "config", "--global", "--add", "safe.directory", str(target),
        cwd=Path(tempfile.gettempdir()))
  remote = subprocess.run(
    ["git", "-C", str(target), "remote", "get-url", "origin"],
    capture_output=True,
  )
  if remote.returncode != 0:
    git(target, "remote", "add", "origin", spec["url"])
  git(target, "fetch", "--depth", "1", "origin", spec["commit"])
  git(target, "checkout", "--detach", "--force", "FETCH_HEAD")
  detected = subprocess.check_output(
    ["git", "-C", str(target), "rev-parse", "HEAD"], text=True
  ).strip()
  if detected != spec["commit"]:
    raise RuntimeError(f"{name} resolved to {detected}, expected {spec['commit']}")
  return target


def install_vrf(manifest: dict[str, object], platform: str) -> None:
  vrf = manifest["vrf"]
  assert isinstance(vrf, dict)
  spec = vrf[platform]
  assert isinstance(spec, dict)
  version = str(vrf["version"])
  digest = str(spec["sha256"])
  archive_name = str(spec["archive"])
  expected = {str(name) for name in spec["files"]}
  output = ROOT / "tools" / "vrf" / ("win64" if platform == "windows" else "linux64")
  stamp = DEPENDENCIES / f"vrf-{platform}.stamp"
  stamp_value = f"{version} {digest}\n"
  if stamp.is_file() and stamp.read_text(encoding="utf-8") == stamp_value \
      and output.is_dir() and {path.name for path in output.iterdir() if path.is_file()} == expected:
    return

  url = (
    "https://github.com/ValveResourceFormat/ValveResourceFormat/releases/"
    f"download/{version}/{archive_name}"
  )
  with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    archive = temporary / archive_name
    urllib.request.urlretrieve(url, archive)
    actual = sha256(archive)
    if actual != digest:
      raise RuntimeError(f"VRF archive checksum mismatch: {actual}")
    with zipfile.ZipFile(archive) as package:
      package.extractall(temporary / "vrf")
    found = {
      path.name: path for path in (temporary / "vrf").rglob("*")
      if path.is_file() and path.name in expected
    }
    missing = expected - found.keys()
    if missing:
      raise RuntimeError(f"VRF archive is missing: {', '.join(sorted(missing))}")
    if output.exists():
      shutil.rmtree(output)
    output.mkdir(parents=True)
    for name in sorted(expected):
      shutil.copy2(found[name], output / name)
  if platform == "linux":
    (output / "Source2Viewer-CLI").chmod(0o755)
  stamp.write_text(stamp_value, encoding="utf-8")


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--platform", choices=("windows", "linux"), required=True)
  args = parser.parse_args()
  manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
  DEPENDENCIES.mkdir(parents=True, exist_ok=True)
  checkout("ambuild", manifest["ambuild"])
  checkout("metamod-source", manifest["metamod"])
  checkout("hl2sdk-manifests", manifest["hl2sdk_manifests"])
  checkout("hl2sdk-cs2", manifest["hl2sdk"])
  install_vrf(manifest, args.platform)


if __name__ == "__main__":
  main()
