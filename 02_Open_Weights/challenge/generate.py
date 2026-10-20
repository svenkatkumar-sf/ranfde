import json
import os
import sys
from pathlib import Path

# repo root is three levels up from this file
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

from helpers.config import from_env
from helpers.sdg import generate
from axes import AXES

cfg = from_env(ROOT)

# Load golden examples as seeds
seeds = [
    json.loads(line)
    for line in (ROOT / "use_case" / "evals" / "golden.jsonl").read_text().splitlines()
    if line.strip()
]

def validate(row: dict) -> bool:
    return bool(row.get("input")) and bool(row.get("output"))

# Azure needs api_key passed explicitly
import litellm
litellm.api_key = os.getenv("AZURE_API_KEY")

rows, report = generate(
    cfg,
    seeds=seeds,
    axes=AXES,
    per_combo=3,
    dedupe_threshold=0.7,
    validate=validate,
)

print(report)

out = ROOT / "use_case" / "data" / "synthetic_v1.jsonl"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
print(f"Saved {len(rows)} rows to {out}")
