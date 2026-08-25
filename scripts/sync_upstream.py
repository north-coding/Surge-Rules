#!/usr/bin/env python3
"""Mirror selected Loyalsoldier Surge rule sets with conservative validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = ROOT / "upstream"

SOURCES = {
    "proxy.txt": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/proxy.txt",
    "direct.txt": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/direct.txt",
    "cncidr.txt": "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/cncidr.txt",
}

MIN_RULE_LINES = {
    "proxy.txt": 500,
    "direct.txt": 1000,
    "cncidr.txt": 100,
}

# Large legitimate upstream changes should be reviewed manually rather than silently accepted.
MIN_SIZE_RATIO = 0.50
MAX_SIZE_RATIO = 2.00


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "north-coding/surge-rules upstream sync"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    return data.decode("utf-8")


def rule_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def validate(name: str, text: str, current: Path) -> None:
    lowered = text[:4096].lower()
    if "<!doctype html" in lowered or "<html" in lowered:
        raise ValueError(f"{name}: received HTML instead of a rule file")

    rules = rule_lines(text)
    if len(rules) < MIN_RULE_LINES[name]:
        raise ValueError(
            f"{name}: suspiciously few rules: {len(rules)} "
            f"(minimum {MIN_RULE_LINES[name]})"
        )

    if name == "cncidr.txt":
        invalid = [
            line for line in rules
            if not line.startswith(("IP-CIDR,", "IP-CIDR6,", "IP6-CIDR,"))
        ]
        if invalid:
            sample = invalid[:3]
            raise ValueError(f"{name}: unexpected rule syntax, sample={sample!r}")

    if current.exists():
        old_size = current.stat().st_size
        new_size = len(text.encode("utf-8"))
        if old_size:
            ratio = new_size / old_size
            if not MIN_SIZE_RATIO <= ratio <= MAX_SIZE_RATIO:
                raise ValueError(
                    f"{name}: size changed too much ({old_size} -> {new_size}, "
                    f"ratio={ratio:.2f}); review upstream manually"
                )


def main() -> int:
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in SOURCES.items():
        destination = UPSTREAM_DIR / name
        text = fetch(url)
        validate(name, text, destination)

        if not text.endswith("\n"):
            text += "\n"

        destination.write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(
            f"{name}: {len(rule_lines(text))} rules, "
            f"{destination.stat().st_size} bytes, sha256={digest}"
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
