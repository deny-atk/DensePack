"""Scores bench runs: right and wrong answers, cost, turns and tokens."""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY = json.loads((HERE / "key.json").read_text(encoding="utf-8"))
ORIGINAL = (HERE / "units.md").read_text(encoding="utf-8")
# SPACES forgives only a normal space for NBSP. FOLD also forgives Latin look-alikes and "-" for the minus sign.
SPACES = str.maketrans("\u00a0", " ")
FOLD = str.maketrans("\u0410\u0412\u0415\u041a\u041c\u041d\u041e\u0420\u0421\u0422\u0425\u00a0\u2212",
                     "ABEKMHOPCTX -")


def score(task, run):
    """Returns the share of right answers exactly, except NBSP and after folding, and the wrong entries."""
    try:
        if task == "extract":
            got, want = json.loads((run / "codes.json").read_text(encoding="utf-8")), KEY["free"]
        elif task == "debts":
            got = (run / "debts.txt").read_text(encoding="utf-8").strip().splitlines()
            want = KEY["debts"]
        else:
            want = [KEY["biggest_line"].replace("\u0437\u0430\u043d\u044f\u0442\u043e", "\u043f\u0440\u043e\u0434\u0430\u043d\u043e")]
            got = sorted(set((run / "units.md").read_text(encoding="utf-8").splitlines()) - set(ORIGINAL.splitlines()))
    except (OSError, ValueError):
        return 0.0, 0.0, 0.0, 0
    share = lambda table: len({g.translate(table) for g in got} & {w.translate(table) for w in want}) / len(want)
    return share({}), share(SPACES), share(FOLD), len(set(got) - set(want))


rows = defaultdict(list)
for run in sorted((HERE / "runs").glob("*-*-*-*")):
    arm, model, task, rep = run.name.split("-")
    if rep == "0":
        continue
    result = json.loads((run / "result.json").read_text())
    usage = result.get("usage", {})
    exact, spaces, folded, wrong = score(task, run)
    rows[(task, model, arm)].append({
        "exact": exact, "spaces": spaces, "folded": folded, "wrong": wrong,
        "cost": result.get("total_cost_usd", 0), "turns": result.get("num_turns", 0),
        "input": sum(usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
        "output": usage.get("output_tokens", 0), "seconds": result.get("duration_ms", 0) / 1000,
    })

print("| Task | Model | Arm | Runs | Exact | Exact except NBSP | Right after folding | Wrong entries "
      "| Cost USD | Turns | Input tokens | Output tokens | Seconds |")
print("| --- " * 13 + "|")
for (task, model, arm), runs in sorted(rows.items()):
    mean = lambda k: statistics.mean(r[k] for r in runs)
    print(f"| {task} | {model} | {arm} | {len(runs)} | {mean('exact'):.0%} | {mean('spaces'):.0%} | "
          f"{mean('folded'):.0%} | {mean('wrong'):.1f} | {mean('cost'):.3f} | {mean('turns'):.1f} | "
          f"{mean('input'):,.0f} | {mean('output'):,.0f} | {mean('seconds'):.0f} |")
if "--json" in sys.argv:
    print(json.dumps({"|".join(k): v for k, v in rows.items()}, indent=1))
