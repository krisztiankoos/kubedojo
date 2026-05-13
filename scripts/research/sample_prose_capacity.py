#!/usr/bin/env python3
"""Run deterministic prose-capacity sampling for #388 rewrite cohort vs controls."""
from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "src/content/docs"
PIPELINE_DIR = REPO_ROOT / ".pipeline"
JSON_OUT = PIPELINE_DIR / "prose-capacity-sample.json"
HTML_OUT = REPO_ROOT / "docs/research/prose-capacity-sampling-2026-05-13.html"
TARGET_388 = 20
TARGET_CONTROL = 20
TRACKS = ("prerequisites", "k8s", "cloud", "platform")
FLOOR_MIN = 4900
FLOOR_MAX = 5100
BKT_WIDTH = 500

sys.path.insert(0, str(REPO_ROOT))
from scripts.quality.verify_module import density_metrics  # noqa: E402


def run_git(args: list[str]) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout


def git_log_388() -> list[tuple[str, str]]:
    raw = run_git(
        [
            "log",
            "--grep=#388",
            "--pretty=format:%H<<SEP>>%s",
            "--",
            str(DOCS_ROOT),
        ]
    )
    commits = []
    for line in raw.splitlines():
        if not line:
            continue
        if "<<SEP>>" not in line:
            continue
        sha, subject = line.split("<<SEP>>", 1)
        commits.append((sha.strip(), subject.strip()))
    return commits


def commit_md_paths(sha: str) -> list[str]:
    raw = run_git(["show", "--name-only", "--pretty=format:", sha])
    return [
        line.strip()
        for line in raw.splitlines()
        if line.strip().startswith("src/content/docs/")
        and line.strip().endswith(".md")
        and "/.pipeline/" not in line
        and "/.github/" not in line
    ]


def is_doc_file(path: str) -> bool:
    return path.startswith("src/content/docs/") and path.endswith(".md")


def is_module_file(path: str) -> bool:
    return is_doc_file(path) and Path(path).name.lower() != "index.md"


def track_of(path: str) -> str:
    parts = path.split("/")
    return parts[3] if len(parts) >= 4 else "unknown"


def exists_on_head(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def read_current_text(path: str) -> str:
    return run_git(["show", f"HEAD:{path}"])


def collect_388_touched() -> set[str]:
    touched: set[str] = set()
    for sha, _ in git_log_388():
        for path in commit_md_paths(sha):
            if is_module_file(path):
                touched.add(path)
    return touched


def sample_388_commits(limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for sha, subject in git_log_388():
        for path in commit_md_paths(sha):
            if not is_module_file(path) or path in seen:
                continue
            if not exists_on_head(path):
                continue
            seen.add(path)
            metrics = density_metrics(read_current_text(path))
            rows.append(
                {
                    "path": path,
                    "commit": sha,
                    "subject": subject,
                    "track": track_of(path),
                    **metrics,
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def collect_track_control_pool(track: str, excluded: set[str]) -> list[str]:
    prefix = f"src/content/docs/{track}/"
    raw = run_git(
        [
            "log",
            "--name-only",
            "--pretty=format:%H<<SEP>>%s",
            "--",
            str(DOCS_ROOT / track),
        ]
    )
    seen: set[str] = set()
    ordered: list[str] = []
    for line in raw.splitlines():
        if not line or "<<SEP>>" in line:
            continue
        path = line.strip()
        if not path.startswith(prefix) or not is_module_file(path):
            continue
        if path in excluded or path in seen:
            continue
        if not exists_on_head(path):
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def sample_control(limit: int, excluded: set[str]) -> list[dict[str, object]]:
    per_track = limit // len(TRACKS)
    remainder = limit % len(TRACKS)
    quotas = {
        track: per_track + (1 if i < remainder else 0)
        for i, track in enumerate(TRACKS)
    }
    pools = {track: collect_track_control_pool(track, excluded) for track in TRACKS}
    selected: list[str] = []
    for track in TRACKS:
        quota = quotas[track]
        pool = pools[track]
        selected.extend(pool[:quota])

    selected = selected[:limit]
    positions = {track: quotas[track] for track in TRACKS}

    # Deterministic top-up from the aggregate, round-robin by track when any
    # track had an unavailable quota (including zero-availability tracks).
    if len(selected) < limit:
        while len(selected) < limit:
            progressed = False
            for track in TRACKS:
                pool = pools[track]
                idx = positions[track]
                if idx >= len(pool):
                    continue
                selected.append(pool[idx])
                positions[track] = idx + 1
                progressed = True
                if len(selected) >= limit:
                    break
            if not progressed:
                break

    rows: list[dict[str, object]] = []
    for path in selected[:limit]:
        metrics = density_metrics(read_current_text(path))
        rows.append({"path": path, "track": track_of(path), **metrics})
    return rows


def bucket_labels(values: list[float | int], width: int = BKT_WIDTH) -> list[str]:
    if not values:
        return []
    min_val = int(min(values))
    max_val = int(max(values))
    start = (min_val // width) * width
    end = ((max_val // width) + 1) * width
    return [f"{left}-{left + width - 1}" for left in range(start, end, width)]


def histogram(values: list[float | int], width: int = BKT_WIDTH) -> list[dict[str, float | int]]:
    labels = bucket_labels(values, width)
    if not labels:
        return []
    counts = OrderedDict((label, 0) for label in labels)
    min_val = (int(min(values)) // width) * width
    for value in values:
        v = int(value)
        idx = (v - min_val) // width
        keys = list(counts.keys())
        if idx >= len(keys):
            idx = len(keys) - 1
        if idx < 0:
            idx = 0
        counts[keys[idx]] += 1
    total = len(values)
    return [
        {
            "range": label,
            "count": count,
            "share": round(count / total, 3) if total else 0.0,
        }
        for label, count in counts.items()
    ]


def floor_cluster_fraction(rows: list[dict[str, object]]) -> float:
    if not rows:
        return 0.0
    hit = sum(1 for r in rows if FLOOR_MIN <= int(r["body_words"]) <= FLOOR_MAX)
    return round(hit / len(rows), 3)


def recommend(fraction: float) -> tuple[str, str]:
    if fraction > 0.20:
        return (
            "BUILD F NOW",
            "More than 20% of sampled #388 modules are inside the 4900-5100 band, so "
            "the static 5000-word floor is likely creating recurrent failures and should be "
            "replaced with dynamic per-module budgets.",
        )
    if fraction >= 0.10:
        return (
            "BUILD VERIFIER-ONLY",
            "Near-floor clustering is material but not above 20%; validate verifier behavior "
            "first before switching gating to dynamic budgets.",
        )
    return (
        "DEFER",
        "Less than 10% of sampled #388 modules sit near the fixed floor, so there is "
        "insufficient evidence to justify immediate Option F changes.",
    )


def build_sample_rows_html(rows: list[dict[str, object]]) -> str:
    lines = [
        "<table>",
        "<thead><tr><th>Path</th><th>Body words</th><th>mean_wpp</th><th>median_wpp</th><th>short_paragraph_rate</th></tr></thead>",
        "<tbody>",
    ]
    for row in rows:
        lines.append(
            "<tr>"
            f"<td><code>{html.escape(str(row['path']))}</code></td>"
            f"<td>{int(row['body_words'])}</td>"
            f"<td>{row['mean_wpp']}</td>"
            f"<td>{row['median_wpp']}</td>"
            f"<td>{row['short_paragraph_rate']}</td>"
            "</tr>"
        )
    lines.append("</tbody>")
    lines.append("</table>")
    return "\n".join(lines)


def build_histogram_html(
    rows_388: list[dict[str, object]],
    rows_control: list[dict[str, object]],
) -> str:
    h388 = histogram([r["body_words"] for r in rows_388])
    hctrl = histogram([r["body_words"] for r in rows_control])
    ranges = sorted(set(item["range"] for item in (h388 + hctrl)))
    bucket_map_388 = {item["range"]: item for item in h388}
    bucket_map_control = {item["range"]: item for item in hctrl}

    lines = [
        "<table>",
        "<thead><tr><th>Body-word bucket</th><th>#388 count</th><th>Control count</th><th>Gap</th></tr></thead>",
        "<tbody>",
    ]
    for label in ranges:
        row_388 = bucket_map_388.get(label, {"count": 0, "share": 0.0})
        row_ctl = bucket_map_control.get(label, {"count": 0, "share": 0.0})
        gap = row_388["count"] - row_ctl["count"]
        lines.append(
            "<tr>"
            f"<td>{html.escape(str(label))}</td>"
            f"<td>{row_388['count']} ({row_388['share']:.1%})</td>"
            f"<td>{row_ctl['count']} ({row_ctl['share']:.1%})</td>"
            f"<td>{gap:+d}</td>"
            "</tr>"
        )
    lines.append("</tbody>")
    lines.append("</table>")
    return "\n".join(lines)


def build_html(summary: dict[str, object]) -> str:
    c388 = summary["cohorts_388"]
    cctl = summary["cohorts_control"]
    meta = summary["sample_metadata"]
    metrics = summary["decision_metrics"]
    decision, rationale = recommend(metrics["floor_cluster_fraction_388"])
    floor_query = f"{FLOOR_MIN} <= body_words <= {FLOOR_MAX}"
    generated_at = summary["generated_at"]
    bucket_width = summary["bucket_width"]

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
<title>Prose Capacity — #388 sampling vs control (2026-05-13)</title>
<style>
  :root {{
    --bg: #fafbfc; --fg: #1a1d23; --muted: #5b6573; --accent: #0057B7;
    --good: #0d8a4a; --partial: #b45c00; --gap: #b8001f; --card: #ffffff;
    --border: #e2e6eb; --mono: ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 0; background: var(--bg); color: var(--fg);
         font: 15px/1.55 system-ui, -apple-system, \"Segoe UI\", Roboto, sans-serif; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1 {{ margin: 0 0 8px; font-size: 28px; }}
  h2 {{ margin: 40px 0 12px; padding-bottom: 8px; border-bottom: 2px solid var(--accent);
       font-size: 22px; }}
  h3 {{ margin: 24px 0 8px; font-size: 17px; }}
  .meta {{ color: var(--muted); margin: 0 0 24px; font-size: 14px; }}
  .tldr {{ background: var(--card); border-left: 4px solid var(--accent);
          padding: 14px 18px; margin: 16px 0 28px; border-radius: 0 6px 6px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0;
          background: var(--card); border: 1px solid var(--border); }}
  th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--border);
           text-align: left; vertical-align: top; }}
  th {{ background: #eef2f6; font-weight: 600; font-size: 13px; }}
  td {{ font-size: 14px; }}
  code {{ background: #eef2f6; padding: 1px 6px; border-radius: 3px;
         font-family: var(--mono); font-size: 13px; }}
  .decision {{ font-size: 18px; color: var(--good); font-weight: 700; }}
  .risk {{ background: #fff7e6; border: 1px solid #f0d9a8; padding: 12px 16px;
            border-radius: 6px; margin: 12px 0; font-size: 14px; }}
  .warning {{ background: #fff7e6; border: 1px solid #f0d9a8; padding: 12px 16px;
              border-radius: 6px; margin: 12px 0; font-size: 14px; }}
</style>
</head>
<body>
<main>

<h1>Option F Prose Capacity Sampling (388 vs control)</h1>
<p class=\"meta\">
  Captured 2026-05-13. Dataset: git main at {generated_at}.
  Source of truth: <code>src/content/docs/**/*.md</code>. Output summary file:
  <code>.pipeline/prose-capacity-sample.json</code>.
</p>

<div class=\"tldr\">
  <strong>Recommendation:</strong> <span class=\"decision\">{html.escape(decision)}</span>.
  {html.escape(rationale)}
</div>

<section id=\"methodology\">
  <h2>Methodology</h2>
  <p>
    Git was queried with:
    <code>git log --grep=\"#388\" --pretty=format:%H%x00%s -- src/content/docs</code>,
    then each commit SHA was resolved via
    <code>git show --name-only --pretty=format: &lt;sha&gt;</code> to extract changed
    Markdown files under <code>src/content/docs/</code>. Deleted files on HEAD were skipped.
  </p>
  <p>
    Sampling rule (deterministic):
  </p>
  <ul>
    <li>#388 cohort: first {TARGET_388} unique markdown paths in git log order.</li>
    <li>Control cohort: {TARGET_CONTROL} recent non-#388 modules with balanced track quotas.
      Requested quotas were distributed across <code>prerequisites</code>, <code>k8s</code>, <code>cloud</code>, <code>platform</code>;
      actual selections are shown as <code>{meta["actual_track_balance"]}</code>.</li>
    <li>Density metrics were computed from the current <code>HEAD</code> file content with
      <code>density_metrics()</code> imported from <code>scripts/quality/verify_module.py</code>.</li>
  </ul>
  <p>
    Required exact fields for this decision: <code>body_words</code>, <code>mean_wpp</code>,
    <code>median_wpp</code>, and <code>short_paragraph_rate</code>.
  </p>
  <ul>
    <li>n_388 = {len(c388)}</li>
    <li>n_control = {len(cctl)}</li>
    <li>Bucket width = {bucket_width}</li>
  </ul>
</section>

<section id=\"distributions\">
  <h2>Body-word distribution</h2>
  <h3>#388 cohort</h3>
  <p>Each row counts body-word buckets and share within the #388 sample.</p>
  {build_histogram_html(c388, cctl)}
</section>

<section id=\"samples\">
  <h2>Module samples</h2>
  <h3>#388 sample (first {TARGET_388})</h3>
  {build_sample_rows_html(c388)}

  <h3>Control sample (track-balanced)</h3>
  {build_sample_rows_html(cctl)}
</section>

<section id=\"decision\">
  <h2>Key decision metric</h2>
  <p>
    Cluster condition: {floor_query}. Fraction in #388 sample =
    <strong>{metrics['floor_cluster_fraction_388']:.1%}</strong>.
    Threshold rule from issue: <strong>build Option F now only if fraction &gt; 20%</strong>.
  </p>
  <p class=\"risk\">
    Computed recommendation: <strong>{html.escape(decision)}</strong>.
  </p>
</section>

<section id=\"threats\">
  <h2>Limitations and threats to validity</h2>
  <ul>
    <li>Deterministic sample excludes non-#388 modules that were touched by #388 then later changed
      but now equalized by post-#388 edits.</li>
    <li>Only one density summary axis is tested; short-paragraph dynamics may mask semantic depth or
      conceptual density, especially for concept-heavy AI modules.</li>
    <li>Control pooling is recency-weighted and track-stratified; it does not match a full bootstrap sample
      over all non-#388 modules.</li>
    <li>All results are point estimates from current HEAD only; changing file history or markdown structure will
      alter recomputed density values.</li>
    <li>No claim about verifier behavior is made beyond this prose corpus signal.</li>
  </ul>
</section>

</main>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-388", type=int, default=TARGET_388)
    parser.add_argument("--target-control", type=int, default=TARGET_CONTROL)
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--no-html", action="store_true")
    args = parser.parse_args(argv)

    all_388_touched = collect_388_touched()
    rows_388 = sample_388_commits(args.target_388)
    rows_control = sample_control(args.target_control, all_388_touched)

    buckets_388 = histogram([int(row["body_words"]) for row in rows_388])
    buckets_control = histogram([int(row["body_words"]) for row in rows_control])

    fraction = floor_cluster_fraction(rows_388)
    rec, rationale = recommend(fraction)

    control_counts = Counter([row["path"].split("/")[3] for row in rows_control])

    summary = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sample_metadata": {
            "github_query_388": 'git log --grep="#388" --pretty=format:%H%x00%s -- src/content/docs',
            "commit_file_query": "git show --name-only --pretty=format: <sha>",
            "requested_track_balance": dict.fromkeys(TRACKS, args.target_control // len(TRACKS)),
            "actual_track_balance": dict(control_counts),
            "n_388": len(rows_388),
            "n_control": len(rows_control),
            "bucket_width": BKT_WIDTH,
        },
        "cohorts_388": rows_388,
        "cohorts_control": rows_control,
        "distributions": {
            "body_words_bucket_width": BKT_WIDTH,
            "cohort_388": buckets_388,
            "cohort_control": buckets_control,
        },
        "bucket_width": BKT_WIDTH,
        "decision_metrics": {
            "floor_window": {"min": FLOOR_MIN, "max": FLOOR_MAX},
            "floor_cluster_fraction_388": fraction,
            "decision": rec,
            "rationale": rationale,
        },
    }

    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not args.no_html and not args.json_only:
        HTML_OUT.write_text(build_html(summary), encoding="utf-8")
    else:
        print("Note: HTML generation skipped (--json-only or --no-html).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
