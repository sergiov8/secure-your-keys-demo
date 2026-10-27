"""Finds Google API keys and hardcoded api_key= arguments in a directory.

Run it on your repo before cutover day, and again in CI after it:

    python -m step1_keyless_auth.scan_for_keys .

Exits 1 if anything is found. This is a quick local check, not a
replacement for a real secret scanner on your Git host.
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass

# Google API keys, including AI Studio keys, start with "AIza".
GOOGLE_KEY = re.compile(r"AIza[0-9A-Za-z_\-]{35}")
# An api_key argument set to a quoted literal instead of an env lookup.
LITERAL_API_KEY_ARG = re.compile(r"""api_key\s*=\s*["'][^"']+["']""")

SKIP_DIRS = frozenset({".git", ".venv", "venv", "node_modules", "__pycache__"})
MAX_FILE_BYTES = 2_000_000


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str


def scan_text(text: str, path: str = "<text>") -> list[Finding]:
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        if GOOGLE_KEY.search(line):
            findings.append(Finding(path, number, "google-api-key"))
        elif LITERAL_API_KEY_ARG.search(line):
            findings.append(Finding(path, number, "hardcoded-api-key-argument"))
    return findings


def scan_tree(root: str) -> list[Finding]:
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
                with open(path, encoding="utf-8", errors="ignore") as f:
                    findings.extend(scan_text(f.read(), path))
            except OSError:
                continue
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Find Google API keys in a directory.")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    findings = scan_tree(args.root)
    for f in findings:
        # Print the location only. Never echo the key itself.
        print(f"{f.path}:{f.line}: {f.kind}")
    if findings:
        print(f"\n{len(findings)} finding(s). Rotate any real key that appears above.")
        sys.exit(1)
    print("No keys found.")


if __name__ == "__main__":
    main()
