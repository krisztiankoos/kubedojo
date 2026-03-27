#!/usr/bin/env python3
"""Batch Gemini adversary review for multiple modules.

Usage:
    python scripts/batch-gemini-review.py [--dry-run] [--batch on-prem|disciplines|all]
    python scripts/batch-gemini-review.py --files file1.md file2.md ...
"""

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from dispatch import dispatch_gemini_with_retry

RESULTS_DIR = REPO_ROOT / ".review-results"

ON_PREM_MODULES = sorted(
    p for p in (REPO_ROOT / "src/content/docs/on-premises").rglob("module-*.md")
)

DISCIPLINE_DIRS = [
    "release-engineering", "chaos-engineering", "finops", "data-engineering",
    "networking", "ai-gpu-infrastructure", "leadership",
]
DISCIPLINE_MODULES = sorted(
    p for d in DISCIPLINE_DIRS
    for p in (REPO_ROOT / "src/content/docs/platform/disciplines" / d).rglob("module-*.md")
    if p.exists()
)

ALL_MODULES = ON_PREM_MODULES + DISCIPLINE_MODULES


def review_module(path: Path, timeout: int = 900) -> dict:
    """Send a single module to Gemini for adversary review."""
    content = path.read_text()
    rel_path = path.relative_to(REPO_ROOT)

    prompt = f"""Review this KubeDojo module for technical accuracy and quality.

FILE: {rel_path}

```markdown
{content}
```

Focus on:
1. Technical accuracy — are commands, YAML, version numbers correct?
2. Factual claims — dates, statistics, company references accurate?
3. Completeness — exercises runnable? Quiz answers correct?
4. Quality — war stories realistic? "Did You Know?" facts verifiable?

Verdict: APPROVE / NEEDS CHANGES
If NEEDS CHANGES, list each issue with:
- Line/section reference
- What's wrong
- What it should be
"""

    print(f"\n{'='*60}")
    print(f"Reviewing: {rel_path}")
    print(f"{'='*60}")

    ok, output = dispatch_gemini_with_retry(prompt, review=True, timeout=timeout)

    result = {
        "file": str(rel_path),
        "success": ok,
        "verdict": _extract_verdict(output) if ok else "ERROR",
        "output": output if ok else "",
    }
    return result


def _extract_verdict(output: str) -> str:
    """Extract APPROVE/NEEDS CHANGES from review output."""
    upper = output.upper()
    if "NEEDS CHANGES" in upper or "NEEDS_CHANGES" in upper:
        return "NEEDS CHANGES"
    if "REJECT" in upper:
        return "REJECT"
    if "APPROVE" in upper:
        return "APPROVE"
    return "UNKNOWN"


def main():
    parser = argparse.ArgumentParser(description="Batch Gemini adversary review")
    parser.add_argument("--dry-run", action="store_true", help="List modules without reviewing")
    parser.add_argument("--batch", choices=["on-prem", "disciplines", "all"], default="all")
    parser.add_argument("--files", nargs="+", help="Specific files to review")
    parser.add_argument("--timeout", type=int, default=900, help="Per-module timeout (default: 900s)")
    parser.add_argument("--start", type=int, default=0, help="Start from module N (for resuming)")
    args = parser.parse_args()

    if args.files:
        modules = [Path(f) for f in args.files]
    elif args.batch == "on-prem":
        modules = ON_PREM_MODULES
    elif args.batch == "disciplines":
        modules = DISCIPLINE_MODULES
    else:
        modules = ALL_MODULES

    modules = modules[args.start:]

    print(f"Modules to review: {len(modules)}")
    for i, m in enumerate(modules):
        print(f"  [{i}] {m.relative_to(REPO_ROOT)}")

    if args.dry_run:
        return

    RESULTS_DIR.mkdir(exist_ok=True)
    results = []
    approved = 0
    needs_changes = 0
    errors = 0

    for i, module in enumerate(modules):
        print(f"\n[{i+1}/{len(modules)}] ", end="")
        result = review_module(module, args.timeout)
        results.append(result)

        if result["verdict"] == "APPROVE":
            approved += 1
        elif result["verdict"] in ("NEEDS CHANGES", "REJECT"):
            needs_changes += 1
        else:
            errors += 1

        # Save incremental results
        results_file = RESULTS_DIR / f"review-{time.strftime('%Y%m%d-%H%M%S')}-batch.json"
        results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))

        # Rate limit buffer
        if i < len(modules) - 1:
            time.sleep(5)

    # Final summary
    print(f"\n{'='*60}")
    print(f"REVIEW COMPLETE")
    print(f"{'='*60}")
    print(f"  Approved:      {approved}")
    print(f"  Needs Changes: {needs_changes}")
    print(f"  Errors:        {errors}")
    print(f"  Total:         {len(results)}")

    if needs_changes > 0:
        print(f"\nModules needing changes:")
        for r in results:
            if r["verdict"] in ("NEEDS CHANGES", "REJECT"):
                print(f"  - {r['file']}")

    # Save final results
    final_file = RESULTS_DIR / f"review-final-{time.strftime('%Y%m%d-%H%M%S')}.json"
    final_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to: {final_file}")


if __name__ == "__main__":
    main()
