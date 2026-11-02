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


HARVEST_FILES = {
    "README.md": ("🌾 **SubHarvest pulse** — **{c}** configs & **{p}** proxies "
                  "ready to use{when}"),
    "README.fa.md": ("🌾 **نبض ساب‌هاروست** — **{c}** کانفیگ و **{p}** پروکسی "
                     "آماده‌ی استفاده{when}"),
}
HARVEST_WHEN = {
    "README.md": " · last harvest: {t} (Tehran)",
    "README.fa.md": " · آخرین برداشت: {t} (تهران)",
}
SUBHARVEST_RAW = ("https://raw.githubusercontent.com/Ashollii/SubHarvest/main/"
                  "output/{name}.txt")
SUBHARVEST_COMMITS = ("https://api.github.com/repos/Ashollii/SubHarvest/"
                      "commits?per_page=1")


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-rates/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def harvest_line(path):
    try:
        configs = fetch_text(SUBHARVEST_RAW.format(name="configs"))
        proxies = fetch_text(SUBHARVEST_RAW.format(name="proxies"))
        c = sum(1 for ln in configs.splitlines() if "://" in ln)
        p = sum(1 for ln in proxies.splitlines() if "://" in ln)
    except Exception:
        return None
    when = ""
    try:
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo
        data = json.loads(fetch_text(SUBHARVEST_COMMITS))
        stamp = data[0]["commit"]["committer"]["date"]
        t = (datetime.fromisoformat(stamp.replace("Z", "+00:00"))
             .astimezone(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M"))
        when = HARVEST_WHEN[path].format(t=t)
    except Exception:
        when = ""
    return HARVEST_FILES[path].format(c=f"{c:,}", p=f"{p:,}", when=when)


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
        line = harvest_line(path)
        if line:
            new = re.sub(r"(<!-- HARVEST:START -->).*?(<!-- HARVEST:END -->)",
                         lambda mo: f"{mo.group(1)}\n{line}\n{mo.group(2)}",
                         new, flags=re.S)
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"updated: {path}")
        else:
            print(f"no change: {path}")


if __name__ == "__main__":
    main()
