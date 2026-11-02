"""Generate Signature Success adoption rows and append to synthetic_v1.jsonl."""

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
from axes_v2 import SIGNATURE_SUCCESS_AXES

cfg = from_env(ROOT)

import litellm
litellm.api_key = os.getenv("AZURE_API_KEY")


def validate(row: dict) -> bool:
    return bool(row.get("input")) and bool(row.get("output"))


seeds_path = ROOT / "use_case" / "evals" / "golden_v2.jsonl"
all_seeds = [json.loads(l) for l in seeds_path.read_text().splitlines() if l.strip()]
sig_seed = [all_seeds[4]]  # fifth seed — the Signature Success one

rows, report = generate(
    cfg,
    seeds=sig_seed,
    axes=SIGNATURE_SUCCESS_AXES,
    per_combo=3,
    dedupe_threshold=0.7,
    validate=validate,
)
print(report)

out = ROOT / "use_case" / "data" / "synthetic_v1.jsonl"
existing = out.read_text().rstrip("\n")
new_lines = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
out.write_text(existing + "\n" + new_lines + "\n")

total = sum(1 for l in out.read_text().splitlines() if l.strip())
print(f"\n✅ Appended {len(rows)} Signature Success rows → {total} total")
print("\nNew rows:")
for r in rows:
    print(f"  [{total - len(rows) + rows.index(r)}] {r['input'][:80]}")
