#!/usr/bin/env python3
"""Evaluate frozen AMR alert rules on countries held out before threshold review."""
import argparse, csv, json
from pathlib import Path
from biosignal.country_evaluation import evaluate_country_holdout

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labelled_csv", type=Path, help="CSV with independent reference outcomes and provenance")
    parser.add_argument("--protocol", required=True, type=Path, help="expert-approved frozen JSON protocol")
    args = parser.parse_args()
    with args.labelled_csv.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_country_holdout(rows, protocol), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
