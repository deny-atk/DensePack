"""Writes units.md, a synthetic register of Russian units, and key.json, the right answers.

Codes use Cyrillic letters that look Latin, and some codes have a Latin twin in another row.
Areas use NBSP before the unit, and negative balances use the minus sign U+2212.
"""
import json
import random
from pathlib import Path

rng = random.Random(4)
CYR, LAT = "АВЕКМНОРСТХ", "ABEKMHOPCTX"
STREETS = ["ул. Лесная", "ул. Садовая", "пр. Мира", "ул. Заречная", "пер. Тихий", "ул. Победы"]
STATUSES = ["свободно", "занято"]
NBSP, MINUS = "\u00a0", "\u2212"


def money(value):
    whole, cents = divmod(abs(value), 100)
    text = f"{whole:,}".replace(",", NBSP) + f",{cents:02d}"
    return (MINUS if value < 0 else "") + text


rows, seen = [], set()
while len(rows) < 120:
    letters = "".join(rng.choice(CYR) for _ in range(2))
    code = f"{letters}-{rng.randrange(10000):04d}"
    if code in seen:
        continue
    seen.add(code)
    rows.append(code)
    # Every fourth code gets a Latin twin in a later row.
    if len(rows) % 4 == 0 and len(rows) < 120:
        twin = code.translate(str.maketrans(CYR, LAT))
        seen.add(twin)
        rows.append(twin)

table = []
for n, code in enumerate(rows, 1):
    area = rng.randrange(250, 1500)
    table.append({
        "n": n, "code": code, "address": f"{rng.choice(STREETS)}, д. {rng.randrange(1, 90)}",
        "area": f"{area // 10},{area % 10}{NBSP}м²", "area_value": area,
        "status": rng.choice(STATUSES), "balance": money(rng.randrange(-300000, 900000)),
    })
# One unit, a Cyrillic code with a Latin twin, gets the largest area.
biggest = next(r for r in table if r["code"][0] in CYR and r["code"].translate(str.maketrans(CYR, LAT)) in seen)
biggest["area"], biggest["area_value"] = f"199,9{NBSP}м²", 1999

lines = ["# Реестр помещений", "", "| № | Код | Адрес | Площадь | Статус | Баланс, руб. |",
         "| --- | --- | --- | --- | --- | --- |"]
lines += [f"| {r['n']} | {r['code']} | {r['address']} | {r['area']} | {r['status']} | {r['balance']} |"
          for r in table]
Path("units.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
Path("key.json").write_text(json.dumps({
    "free": [r["code"] for r in table if r["status"] == "свободно"],
    "debts": [f"{r['code']}\t{r['balance']}" for r in table if r["balance"].startswith(MINUS)],
    "biggest_line": next(lines[i + 4] for i, r in enumerate(table) if r is biggest),
}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(table), "rows,", sum(r["code"][0] in LAT for r in table), "Latin twins")
