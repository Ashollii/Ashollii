#!/usr/bin/env python3
"""Refresh the live-rates table inside this profile README (English and
Persian editions) from the Nerkh market.json. Stdlib only; run by the
update-rates workflow."""
import json
import os
import re
import urllib.request

MARKET_URL = ("https://raw.githubusercontent.com/Ashollii/Nerkh/main/"
              "market.json")

FILES = {
    "README.md": {
        "header": "| | Rate (Toman) |",
        "rows": [
            ("💵 US Dollar", "usd"),
            ("💶 Euro", "eur"),
            ("✨ Gold 18k (per gram)", "gold_18k"),
            ("🪙 Emami Coin", "coin_emami"),
        ],
        "footer": ("<sub>⏰ Last update: {upd} (Tehran) · "
                   "Source: [Nerkh](https://github.com/Ashollii/Nerkh)</sub>"),
    },
    "README.fa.md": {
        "header": "| | نرخ (تومان) |",
        "rows": [
            ("💵 دلار آمریکا", "usd"),
            ("💶 یورو", "eur"),
            ("✨ طلای ۱۸ عیار (هر گرم)", "gold_18k"),
            ("🪙 سکه امامی", "coin_emami"),
        ],
        "footer": ("<sub>⏰ آخرین به‌روزرسانی: {upd} (تهران) · "
                   "منبع: [نرخ](https://github.com/Ashollii/Nerkh)</sub>"),
    },
}


def fmt(v):
    try:
        return f"{int(v):,}"
    except Exception:
        return "—"


def build_table(spec, m):
    lines = [spec["header"], "|---|---|"]
    for label, key in spec["rows"]:
        lines.append(f"| {label} | {fmt(m.get(key))} |")
    lines.append("")
    lines.append(spec["footer"].format(upd=m.get("updated_at", "—")))
    return "\n".join(lines)


def main():
    req = urllib.request.Request(MARKET_URL,
                                 headers={"User-Agent": "profile-rates/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        m = json.loads(r.read().decode("utf-8"))

    for path, spec in FILES.items():
        if not os.path.exists(path):
            print(f"skip (missing): {path}")
            continue
        table = build_table(spec, m)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"(<!-- RATES:START -->).*?(<!-- RATES:END -->)",
                     lambda mo: f"{mo.group(1)}\n{table}\n{mo.group(2)}",
                     text, flags=re.S)
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"updated: {path}")
        else:
            print(f"no change: {path}")


if __name__ == "__main__":
    main()
