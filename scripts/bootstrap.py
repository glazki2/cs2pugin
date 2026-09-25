"""Fetch the exact build dependencies declared in build-dependencies.json."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "build-dependencies.json"
DEPENDENCIES = ROOT / ".build-deps" / ("windows" if sys.platform == "win32" else "linux")


def run(*args: str, cwd: Path | None = None) -> None:
  subprocess.run(args, cwd=cwd, check=True)


def git(target: Path, *args: str) -> None:
  run("git", "-C", str(target), *args)


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


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--platform", choices=("windows", "linux"), required=True)
  args = parser.parse_args()
  manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
  DEPENDENCIES.mkdir(parents=True, exist_ok=True)
  checkout("ambuild", manifest["ambuild"])
  metamod = checkout("metamod-source", manifest["metamod"])
  # Metamod:Source API 18 plugins include khook.hpp from this submodule.
  git(metamod, "submodule", "update", "--init", "--depth", "1", "third_party/khook")
  checkout("hl2sdk-manifests", manifest["hl2sdk_manifests"])
  checkout("hl2sdk-cs2", manifest["hl2sdk"])


if __name__ == "__main__":
  main()
