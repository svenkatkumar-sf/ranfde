"""Generate source-system-specific synthetic rows and append to synthetic_v1.jsonl.

Four passes — one per source system — each with its own axes and seed example.
Appends to the existing file; does not overwrite.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

from helpers.config import from_env
from helpers.sdg import generate
from axes_v2 import (
    SALESFORCE_CASES_AXES,
    MULESOFT_ADMIN_AXES,
    CALENDAR_AXES,
    CORPORATE_NEWS_AXES,
)

cfg = from_env(ROOT)

import litellm
litellm.api_key = os.getenv("AZURE_API_KEY")


def validate(row: dict) -> bool:
    return bool(row.get("input")) and bool(row.get("output"))


seeds_path = ROOT / "use_case" / "evals" / "golden_v2.jsonl"
all_seeds = [json.loads(l) for l in seeds_path.read_text().splitlines() if l.strip()]

# One seed per source system — index matches the order in golden_v2.jsonl
SOURCE_SYSTEMS = [
    ("Salesforce Cases",  SALESFORCE_CASES_AXES, [all_seeds[0]]),
    ("Mulesoft Admin",    MULESOFT_ADMIN_AXES,   [all_seeds[1]]),
    ("Google Calendar",   CALENDAR_AXES,         [all_seeds[2]]),
    ("Corporate News",    CORPORATE_NEWS_AXES,   [all_seeds[3]]),
]

all_new_rows = []

for name, axes, seeds in SOURCE_SYSTEMS:
    print(f"\n=== {name} ===")
    rows, report = generate(
        cfg,
        seeds=seeds,
        axes=axes,
        per_combo=2,
        dedupe_threshold=0.7,
        validate=validate,
    )
    print(report)
    all_new_rows.extend(rows)

out = ROOT / "use_case" / "data" / "synthetic_v1.jsonl"
existing = out.read_text().rstrip("\n") if out.exists() else ""
new_lines = "\n".join(json.dumps(r, ensure_ascii=False) for r in all_new_rows)
out.write_text(existing + "\n" + new_lines + "\n")

total = sum(1 for l in out.read_text().splitlines() if l.strip())
print(f"\n✅ Appended {len(all_new_rows)} new rows → {total} total in {out.name}")
