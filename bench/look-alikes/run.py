"""Runs one headless Claude Code session per arm, model, task and repeat.

Arm "images" sets exacttext off, which is the DensePack 2.0.3 behaviour.
Arm "text" keeps exacttext on, the fork's behaviour. Usage: python3 run.py REPEATS MODEL...
"""
import itertools
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = json.loads((HERE / "tasks.json").read_text(encoding="utf-8"))
# Only DensePack loads, so other plugins add no hooks or tokens.
SETTINGS = json.dumps({"enabledPlugins": {"trekker@trekker-marketplace": False,
                                          "agent-mail@osteele-local": False,
                                          "cc-plugin-you-should-know@builtin": False}})


def run(arm, model, task, rep):
    out = HERE / "runs" / f"{arm}-{model}-{task}-{rep}"
    if (out / "result.json").is_file():
        return
    shutil.rmtree(out, ignore_errors=True)
    (out / ".claude" / "tmp").mkdir(parents=True)
    shutil.copy(HERE / "units.md", out)
    (out / ".claude" / "tmp" / "densepack-settings.json").write_text(
        json.dumps({"exacttext": "on" if arm == "text" else "off"}))
    proc = subprocess.run(
        ["claude", "-p", TASKS[task], "--model", model, "--output-format", "json",
         "--permission-mode", "auto", "--strict-mcp-config", "--settings", SETTINGS,
         "--allowedTools", "Read", "Write", "Edit", "Grep", "Glob", "--max-turns", "25"],
        cwd=out, capture_output=True, text=True, timeout=600)
    (out / "result.json").write_text(proc.stdout or json.dumps({"error": proc.stderr[-2000:]}))
    print(out.name, "exit", proc.returncode, flush=True)


if __name__ == "__main__":
    reps, models = int(sys.argv[1]), sys.argv[2:]
    jobs = list(itertools.product(["images", "text"], models, TASKS, range(1, reps + 1)))
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(lambda job: run(*job), jobs))
