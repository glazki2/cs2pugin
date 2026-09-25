"""Run the SDK-independent Runtime Visibility Studio checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "tools" / "visibility_point_editor"


def run(*args: str) -> None:
  subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
  run(sys.executable, str(STUDIO / "check_runtime_alignment.py"))
  for name in ("capsule_visibility.js", "bvh8.js", "bvh8_worker.js",
               "fps_runtime.js", "viewer.js"):
    run("node", "--check", str(STUDIO / name))
  run("node", str(STUDIO / "check_bvh8.mjs"))
  run("node", str(STUDIO / "check_fps.mjs"))


if __name__ == "__main__":
  main()
