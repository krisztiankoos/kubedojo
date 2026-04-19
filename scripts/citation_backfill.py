#!/usr/bin/env python3
"""Citation backfill orchestrator — research → inject → verify → diff-lint.

Session 5 (2026-04-19): only the `research` subcommand is implemented.
Inject / verify / diff-lint ship in follow-up sessions once research is
calibrated on the 4 pilot modules.

Usage:
    # Research phase — dispatch Codex, validate URLs, write seed JSON.
    python scripts/citation_backfill.py research <module-key>
    python scripts/citation_backfill.py research --agent gemini <module-key>
    python scripts/citation_backfill.py research --dry-run <module-key>
        # emits the Codex prompt to stdout, no dispatch, no writes

    # Other subcommands land later:
    #   inject <module-key>
    #   verify <module-key>
    #   run <module-key>       — all four phases in order
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Re-use the fetcher (sibling module; static tools may not see the path prepend).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_citation import allowlist_tier, fetch  # type: ignore[import-not-found]  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "src" / "content" / "docs"
SEED_DIR = REPO_ROOT / "docs" / "citation-seeds"
SCHEMA_VERSION = 1

CLAIM_CLASSES = {
    "war_story", "incident", "statistic", "standard",
    "vendor_capability", "pricing", "benchmark", "security_claim",
}
TIER_NAMES = {"standards", "upstream", "vendor", "incidents", "general"}


# ---- prompt --------------------------------------------------------------


RESEARCH_PROMPT_TEMPLATE = """You are the research step of the KubeDojo citation backfill pipeline.

Your job: read the module below and return a JSON seed file that identifies
every factual claim that requires an inline citation, plus a short Further
Reading list. You do NOT rewrite the module. You do NOT add citations. You
only produce the JSON seed.

## What MUST be cited (inline in a later step)

- war stories, incident timelines, legal cases
- specific statistics, benchmarks, pricing
- standards, regulations, curricula references by name
- vendor capability claims ("X supports Y since version Z")
- security or safety claims tied to a real incident

## What must NOT produce a claim entry

- teaching analogies ("the CPU is like a chef")
- connective instructor prose ("this matters because...")
- questions, quiz items, exercise steps
- Mermaid diagrams, code blocks, tables (unless the table row is itself a
  factual vendor/statistic claim)

If the module is purely pedagogical with zero hard claims, return an empty
`claims` array and 2–3 Further Reading entries appropriate to the topic.
This is a legitimate, expected output for intro modules.

## Trusted-domain allowlist

URLs you propose MUST resolve to hosts on this allowlist (tiered by claim
class). Pick the tier that best matches the claim. Do NOT invent URL paths
you are unsure about — prefer a well-known top-level doc page over a
hallucinated deep link.

{allowlist_block}

## Output schema

Emit ONE JSON object, no preamble, no markdown fences, no trailing commas.
Schema:

{schema_block}

Claim class enum: {claim_classes}
Tier enum: {tiers}

## Module to research

Module key: `{module_key}`
Module path: `{module_path}`

```markdown
{module_body}
```

Return ONLY the JSON object. Do not include any other text.
"""


def _format_allowlist_block(allowlist: dict[str, Any]) -> str:
    lines: list[str] = []
    for tier in ("standards", "upstream", "vendor", "incidents", "general"):
        domains = allowlist.get("tiers", {}).get(tier) or []
        if not domains:
            continue
        lines.append(f"- **{tier}**: {', '.join(str(d) for d in domains)}")
    return "\n".join(lines)


def _format_schema_block() -> str:
    return json.dumps(
        {
            "module_key": "<string>",
            "module_path": "<string>",
            "research_run_id": "<ISO-8601-UTC>-<agent>-<model>",
            "schema_version": SCHEMA_VERSION,
            "claims": [
                {
                    "claim_id": "C001",
                    "claim_text": "<verbatim-or-tight-paraphrase>",
                    "claim_class": "<one-of-enum>",
                    "span_hint": "<line N | section: X | paragraph after diagram 2>",
                    "proposed_url": "https://...",
                    "proposed_tier": "<one-of-enum>",
                    "rationale": "<one sentence>",
                }
            ],
            "further_reading": [
                {
                    "url": "https://...",
                    "title": "<short title>",
                    "tier": "<one-of-enum>",
                    "why_relevant": "<one sentence>",
                }
            ],
            "notes": "<optional free text>",
        },
        indent=2,
    )


def build_research_prompt(module_key: str, module_path: Path, module_body: str) -> str:
    from fetch_citation import _load_allowlist  # type: ignore[import-not-found]
    allowlist = _load_allowlist()
    return RESEARCH_PROMPT_TEMPLATE.format(
        allowlist_block=_format_allowlist_block(allowlist),
        schema_block=_format_schema_block(),
        claim_classes=", ".join(sorted(CLAIM_CLASSES)),
        tiers=", ".join(sorted(TIER_NAMES)),
        module_key=module_key,
        module_path=str(module_path.relative_to(REPO_ROOT)),
        module_body=module_body,
    )


# ---- module lookup -------------------------------------------------------


def resolve_module_path(module_key: str) -> Path:
    """Accepts 'prereqs/.../module-0.1-...' or a bare filename stem."""
    rel = module_key.strip().removesuffix(".md")
    candidate = DOCS_ROOT / f"{rel}.md"
    if candidate.exists():
        return candidate
    # Fallback: search by stem (useful when user types just the stem).
    matches = list(DOCS_ROOT.glob(f"**/{rel}.md"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"No module found for key: {module_key}")
    raise ValueError(
        f"Ambiguous module key {module_key}; matched {len(matches)} files"
    )


def seed_path_for(module_key: str) -> Path:
    flat = module_key.replace("/", "-")
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    return SEED_DIR / f"{flat}.json"


# ---- dispatch ------------------------------------------------------------


def dispatch_codex(prompt: str, *, task_id: str) -> tuple[bool, str]:
    """Send the prompt through scripts/ab ask-codex; return (ok, response_text)."""
    cmd = [
        "scripts/ab", "ask-codex",
        "--task-id", task_id,
        "--from", "claude",
        "--new-session",
        "-",
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout_after_900s"
    if proc.returncode != 0:
        return False, proc.stderr or proc.stdout
    return _extract_bridge_response(proc.stdout)


_BRIDGE_MSG_RE = re.compile(r"Message sent to Claude \(ID: (\d+)\)")


def _extract_bridge_response(stdout: str) -> tuple[bool, str]:
    match = _BRIDGE_MSG_RE.search(stdout)
    if not match:
        return False, f"no_response_message_id_in_bridge_stdout:\n{stdout[-400:]}"
    msg_id = match.group(1)
    read = subprocess.run(
        ["scripts/ab", "read", msg_id],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if read.returncode != 0:
        return False, read.stderr
    body = read.stdout
    # Strip the bridge envelope header — everything before the 60-char rule.
    parts = body.split("=" * 60, 1)
    return True, (parts[1] if len(parts) == 2 else body).strip()


def dispatch_gemini(prompt: str) -> tuple[bool, str]:
    cmd = [
        "scripts/dispatch.py" if Path("scripts/dispatch.py").exists() else "dispatch.py",
        "gemini", "-", "--timeout", "900",
    ]
    # Prefer the .venv python if present.
    if Path(".venv/bin/python").exists():
        cmd = [".venv/bin/python", *cmd]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout_after_900s"
    if proc.returncode != 0:
        return False, proc.stderr or proc.stdout
    return True, proc.stdout


# ---- validation ----------------------------------------------------------


def _stable_claim_id(claim_text: str) -> str:
    return "C" + hashlib.sha1(claim_text.encode("utf-8")).hexdigest()[:7]


def parse_agent_response(raw: str) -> dict[str, Any]:
    """Strip common wrappers (code fences, preamble) and json.loads."""
    text = raw.strip()
    # Remove ```json fences if present.
    if text.startswith("```"):
        # drop first line
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[:-3]
    # Find the first { and last } to be robust to stray prose.
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("no_json_object_in_response")
    return json.loads(text[first:last + 1])


def validate_seed(seed: dict[str, Any]) -> list[str]:
    """Schema-only validation (no network). Returns list of issues."""
    issues: list[str] = []
    for field in ("module_key", "module_path", "claims", "further_reading"):
        if field not in seed:
            issues.append(f"missing_field:{field}")
    for i, claim in enumerate(seed.get("claims") or []):
        if not isinstance(claim, dict):
            issues.append(f"claim[{i}]:not_dict")
            continue
        for f in ("claim_text", "claim_class", "proposed_url", "proposed_tier"):
            if f not in claim:
                issues.append(f"claim[{i}]:missing_{f}")
        cc = claim.get("claim_class")
        if cc and cc not in CLAIM_CLASSES:
            issues.append(f"claim[{i}]:bad_class:{cc}")
        tier = claim.get("proposed_tier")
        if tier and tier not in TIER_NAMES:
            issues.append(f"claim[{i}]:bad_tier:{tier}")
    for i, link in enumerate(seed.get("further_reading") or []):
        if not isinstance(link, dict):
            issues.append(f"further_reading[{i}]:not_dict")
            continue
        for f in ("url", "tier"):
            if f not in link:
                issues.append(f"further_reading[{i}]:missing_{f}")
    return issues


def validate_urls(seed: dict[str, Any]) -> dict[str, Any]:
    """Network pass: fetch every URL, move rejects into rejected_urls."""
    rejected: list[dict[str, Any]] = list(seed.get("rejected_urls") or [])
    kept_claims: list[dict[str, Any]] = []
    for claim in seed.get("claims") or []:
        url = (claim.get("proposed_url") or "").strip()
        if not url:
            rejected.append({
                "url": "", "reason": "empty_url", "at_step": "research_validation",
                "agent_proposed_tier": claim.get("proposed_tier"),
            })
            continue
        tier = allowlist_tier(url)
        if tier is None:
            rejected.append({
                "url": url, "reason": "off_allowlist",
                "at_step": "research_validation",
                "agent_proposed_tier": claim.get("proposed_tier"),
            })
            continue
        result = fetch(url)
        status = int(result.get("status") or 0)
        issues = result.get("issues") or []
        if status and status < 400 and "pdf_needs_adapter" not in issues:
            # Correct the tier if agent mislabeled.
            claim["proposed_tier"] = tier
            kept_claims.append(claim)
        else:
            reason = "pdf_no_adapter" if "pdf_needs_adapter" in issues else \
                     "network_failure" if not status else f"http_{status}"
            rejected.append({
                "url": url, "reason": reason, "at_step": "research_validation",
                "agent_proposed_tier": claim.get("proposed_tier"),
            })

    kept_fr: list[dict[str, Any]] = []
    for link in seed.get("further_reading") or []:
        url = (link.get("url") or "").strip()
        if not url:
            continue
        tier = allowlist_tier(url)
        if tier is None:
            rejected.append({
                "url": url, "reason": "off_allowlist",
                "at_step": "research_validation", "agent_proposed_tier": link.get("tier"),
            })
            continue
        result = fetch(url)
        status = int(result.get("status") or 0)
        if status and status < 400:
            link["tier"] = tier
            kept_fr.append(link)
        else:
            rejected.append({
                "url": url, "reason": f"http_{status}" if status else "network_failure",
                "at_step": "research_validation", "agent_proposed_tier": link.get("tier"),
            })

    seed["claims"] = kept_claims
    seed["further_reading"] = kept_fr
    seed["rejected_urls"] = rejected
    return seed


# ---- research orchestration ---------------------------------------------


def _iso_utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds")


def run_research(module_key: str, *, agent: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    module_path = resolve_module_path(module_key)
    module_body = module_path.read_text(encoding="utf-8")
    normalized_key = module_path.relative_to(DOCS_ROOT).with_suffix("").as_posix()
    prompt = build_research_prompt(normalized_key, module_path, module_body)

    if dry_run:
        return {
            "module_key": normalized_key,
            "dry_run": True,
            "prompt_bytes": len(prompt),
            "prompt_preview": prompt[:600],
            "prompt_tail": prompt[-400:],
        }

    task_id = f"citation-research-{normalized_key.replace('/', '-')}-{_dt.datetime.now(_dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    if agent == "codex":
        ok, raw = dispatch_codex(prompt, task_id=task_id)
        model = "gpt-5.3-codex-spark"  # codex default; bridge may override
    elif agent == "gemini":
        ok, raw = dispatch_gemini(prompt)
        model = "gemini-3-pro-preview"
    else:
        raise ValueError(f"unknown agent: {agent}")

    if not ok:
        return {
            "module_key": normalized_key, "ok": False,
            "error": "dispatch_failed", "detail": raw[-600:],
        }

    try:
        seed = parse_agent_response(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return {
            "module_key": normalized_key, "ok": False,
            "error": "parse_failed", "detail": str(exc),
            "raw_head": raw[:400], "raw_tail": raw[-400:],
        }

    seed.setdefault("module_key", normalized_key)
    seed.setdefault("module_path", str(module_path.relative_to(REPO_ROOT)))
    seed["schema_version"] = SCHEMA_VERSION
    seed["research_run_id"] = f"{_iso_utc_now()}-{agent}-{model}"
    # Stabilize claim IDs.
    for claim in seed.get("claims") or []:
        if isinstance(claim, dict) and claim.get("claim_text") and not claim.get("claim_id"):
            claim["claim_id"] = _stable_claim_id(str(claim["claim_text"]))

    schema_issues = validate_seed(seed)
    seed["_schema_issues"] = schema_issues
    seed = validate_urls(seed)

    out_path = seed_path_for(normalized_key)
    out_path.write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "module_key": normalized_key, "ok": True,
        "seed_path": str(out_path.relative_to(REPO_ROOT)),
        "claims_kept": len(seed.get("claims") or []),
        "further_reading_kept": len(seed.get("further_reading") or []),
        "rejected": len(seed.get("rejected_urls") or []),
        "schema_issues": schema_issues,
    }


# ---- CLI -----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Citation backfill orchestrator")
    subs = parser.add_subparsers(dest="command", required=True)

    rp = subs.add_parser("research", help="Run the research step on one module")
    rp.add_argument("module_key", help="Module key under src/content/docs/")
    rp.add_argument("--agent", default="codex", choices=["codex", "gemini"])
    rp.add_argument("--dry-run", action="store_true",
                    help="Print prompt + exit; no dispatch, no writes")

    args = parser.parse_args(argv)

    if args.command == "research":
        result = run_research(args.module_key, agent=args.agent, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") or result.get("dry_run") else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
