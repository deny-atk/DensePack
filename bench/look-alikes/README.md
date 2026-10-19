# Look-alike benchmark: images (2.0.3) against exact text (PR #5)

Ran on 2026-10-16 with Claude Code 2.1.299, `claude-sonnet-5-5` and `claude-opus-5-5`, 3 runs per cell, 36 sessions, $11.44 in total. It uses one synthetic file and one kind of data, so it shows what can happen, not how often it happens in real projects.

## What it tests

`make_data.py` writes `units.md`, a Markdown table of 120 synthetic Russian units, and `key.json`, the right answers. Codes such as `ОС-4741` use Cyrillic letters that look Latin, and 29 codes have a Latin twin in another row. Areas use NBSP, and negative balances use the minus sign U+2212. The random seed is fixed, so the file is the same on every machine.

`tasks.json` has 3 tasks:

1. `extract` writes the codes of all free units to `codes.json`.
2. `debts` writes the code and balance of each unit with a negative balance to `debts.txt`.
3. `edit` changes the status of the unit with the largest area.

Both arms run the same build, DensePack 2.0.3 plus PR #5. The `images` arm sets `"exacttext": "off"`, which skips every line the PR adds, so it behaves as 2.0.3. The `text` arm keeps the default `on`.

## How to run it again

1. Install DensePack from the PR branch `exact-text-for-look-alikes` as your user plugin.
2. In `run.py`, change `SETTINGS` so it turns off the plugins of your own setup. Only DensePack should load.
3. Move the `runs` folder away, because `run.py` skips runs that already have a `result.json`.
4. Run `python3 run.py 3 sonnet opus`, then `python3 score.py`.

`run.py` starts each session with `claude -p` in `auto` permission mode, in its own folder under `runs/`.

## Files

- `results.md` is the table that `score.py` prints from `runs/`.
- `runs/<arm>-<model>-<task>-<run>/` holds each session's `result.json` from `claude -p --output-format json`, the file it wrote, and `tools.json`, its tool calls counted from the session transcript.

## Results

| Task | Model | Exact, images | Exact, text | Cost, images | Cost, text | Turns, images | Turns, text |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extract | Sonnet | 71%, plus 9 wrong codes per run | 100% | $0.245 | $0.154 | 3.0 | 3.0 |
| extract | Opus | 100% | 100% | $0.493 | $0.318 | 7.3 | 3.0 |
| debts | Sonnet | 83% | 100% | $0.212 | $0.150 | 8.3 | 3.0 |
| debts | Opus | 100% | 100% | $0.458 | $0.349 | 20.0 | 6.0 |
| edit | Sonnet | 100% | 100% | $0.214 | $0.225 | 11.0 | 15.0 |
| edit | Opus | 100% | 100% | $0.395 | $0.389 | 12.0 | 9.0 |

"Exact" counts a normal space for NBSP as right, because no model in either arm wrote an NBSP back.

Mean tool calls per run, from `tools.json`:

| Task | Model | Searches, images | Searches, text | Partial Reads, images | Partial Reads, text |
| --- | --- | --- | --- | --- | --- |
| extract | Sonnet | 0 | 0 | 0 | 0 |
| extract | Opus | 4.3 | 0 | 0 | 0 |
| debts | Sonnet | 4.3 | 0 | 0 | 0 |
| debts | Opus | 8.3 | 2.7 | 8.0 | 0 |
| edit | Sonnet | 3.0 | 8.0 | 1.0 | 0.7 |
| edit | Opus | 5.7 | 2.0 | 0.7 | 1.0 |
