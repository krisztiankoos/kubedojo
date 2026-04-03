#!/usr/bin/env python3
"""Score a module against the KubeDojo quality rubric.

Usage:
    python scripts/score_module.py 4 5 4 4 5 4 4
    python scripts/score_module.py 4 5 4 4 5 4 4 --json
    echo "4 5 4 4 5 4 4" | python scripts/score_module.py -

Dimensions (in order):
    D1: Learning Outcomes
    D2: Scaffolding & Structure
    D3: Active Learning
    D4: Real-World Connection
    D5: Assessment Alignment
    D6: Cognitive Load Management
    D7: Engagement & Motivation

Rules:
    - Every dimension must be >= 4 (a 3 anywhere = FAIL)
    - Sum must be >= 29 out of 35
    - Both conditions must pass
"""

import json
import sys

DIMENSIONS = [
    "Learning Outcomes",
    "Scaffolding & Structure",
    "Active Learning",
    "Real-World Connection",
    "Assessment Alignment",
    "Cognitive Load Management",
    "Engagement & Motivation",
]

RATINGS = [
    (29, 35, "Pass"),
    (22, 28, "Needs polish"),
    (15, 21, "Needs work"),
    (7, 14, "Rewrite"),
]


def score(values: list[int]) -> dict:
    if len(values) != 7:
        raise ValueError(f"Expected 7 scores, got {len(values)}")

    for i, v in enumerate(values):
        if not 1 <= v <= 5:
            raise ValueError(f"D{i+1} ({DIMENSIONS[i]}): score {v} out of range 1-5")

    total = sum(values)
    minimum = min(values)
    floor_pass = minimum >= 4
    sum_pass = total >= 29

    # Find rating tier by sum
    rating = "Unknown"
    for lo, hi, label in RATINGS:
        if lo <= total <= hi:
            rating = label
            break

    # Overall pass requires BOTH conditions
    passes = floor_pass and sum_pass

    # Find weak dimensions
    weak = [(DIMENSIONS[i], v) for i, v in enumerate(values) if v < 4]

    return {
        "scores": {DIMENSIONS[i]: v for i, v in enumerate(values)},
        "sum": total,
        "max": 35,
        "min_score": minimum,
        "floor_pass": floor_pass,
        "sum_pass": sum_pass,
        "passes": passes,
        "rating": rating if passes else f"FAIL ({rating} by sum, but floor violated)" if not floor_pass else f"FAIL ({rating})",
        "weak_dimensions": weak,
    }


def main():
    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]

    if not args or args[0] == "-":
        raw = sys.stdin.read().strip()
        values = [int(x) for x in raw.split()]
    else:
        values = [int(x) for x in args]

    try:
        result = score(values)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if use_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["passes"] else 1)

    # Pretty output
    print()
    for dim, val in result["scores"].items():
        marker = " " if val >= 4 else " <-- BELOW FLOOR"
        print(f"  D{list(result['scores'].keys()).index(dim)+1}: {val}/5  {dim}{marker}")

    print(f"\n  Sum: {result['sum']}/{result['max']}")
    print(f"  Min: {result['min_score']}")
    print(f"  Floor (all >= 4): {'PASS' if result['floor_pass'] else 'FAIL'}")
    print(f"  Sum (>= 29):      {'PASS' if result['sum_pass'] else 'FAIL'}")

    if result["passes"]:
        print(f"\n  RESULT: PASS ({result['sum']}/35)")
    else:
        print(f"\n  RESULT: FAIL")
        if result["weak_dimensions"]:
            print(f"  Fix: {', '.join(f'{d} ({v})' for d, v in result['weak_dimensions'])}")
        if not result["sum_pass"]:
            print(f"  Need {29 - result['sum']} more points to reach 29")

    print()
    sys.exit(0 if result["passes"] else 1)


if __name__ == "__main__":
    main()
