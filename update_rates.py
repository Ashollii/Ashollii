#!/usr/bin/env python3
"""Refresh the live-rates table inside this profile README from the
Nerkh market.json. Stdlib only; run by the update-rates workflow."""
import json
import re
import urllib.request

MARKET_URL = ("https://raw.githubusercontent.com/Ashollii/Nerkh/main/"
              "market.json")
README = "README.md"


def fmt(v):
    try:
        return f"{int(v):,}"
    except Exception:
        return "—"


def main():
    req = urllib.request.Request(MARKET_URL,
                                 headers={"User-Agent": "profile-rates/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        m = json.loads(r.read().decode("utf-8"))

    table = "\n".join([
        "| | Rate (Toman) |",
        "|---|---|",
        f"| 💵 US Dollar | {fmt(m.get('usd'))} |",
        f"| 💶 Euro | {fmt(m.get('eur'))} |",
        f"| ✨ Gold 18k (per gram) | {fmt(m.get('gold_18k'))} |",
        f"| 🪙 Emami Coin | {fmt(m.get('coin_emami'))} |",
        "",
        f"<sub>⏰ Last update: {m.get('updated_at', '—')} (Tehran) · "
        "Source: [Nerkh](https://github.com/Ashollii/Nerkh)</sub>",
    ])

    with open(README, encoding="utf-8") as f:
        text = f.read()
    new = re.sub(r"(<!-- RATES:START -->).*?(<!-- RATES:END -->)",
                 lambda mo: f"{mo.group(1)}\n{table}\n{mo.group(2)}",
                 text, flags=re.S)
    if new != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print("README updated")
    else:
        print("No change")


if __name__ == "__main__":
    main()
