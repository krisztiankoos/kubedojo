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
DISPOSITIONS = {"supported", "weak_anchor", "unciteable"}


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

## CRITICAL: disposition per claim — do not force weak anchors

Every claim gets a `disposition` field. This is the most important
judgment you make. Do not lie; do not fill a slot with a URL that
doesn't actually back the claim.

- **`supported`** — the URL's page directly discusses THIS specific
  claim. A K8s Windows-support statement cited to
  `kubernetes.io/docs/concepts/windows/` qualifies. An exact paper
  cited for the transformer architecture (arxiv.org/abs/1706.03762)
  qualifies. This is a primary or near-primary source. Strong
  support, not just thematic.

- **`weak_anchor`** — the URL is a category-page or topic-anchor
  on the allowlist that shares the same subject but does NOT
  directly confirm the specific number/event/claim. Acceptable
  ONLY when the claim itself is loose and generic ("browsers use
  memory"). NOT acceptable when the claim is specific.

- **`unciteable`** — NO URL on the allowlist honestly backs this
  claim. Set `proposed_url` and `proposed_tier` to null. Explain in
  `rationale` why nothing can back it. Examples that should be
  `unciteable`:
  - dated-specific prices ("$0.0928/hr on April 15 2026")
  - exact percentages at a single date when no source is on
    the allowlist
  - specific incident details whose primary postmortem is hosted
    off-allowlist (e.g., GitLab.com) and for which no neutral
    secondary source on the allowlist covers THOSE specifics
  - verbatim quotes from a named person without a cited interview
  - any claim that was likely fabricated by an LLM and has no
    real-world basis

Bias toward `unciteable` when in doubt. A truthful flag is better
than a forced weak anchor. The next step uses `unciteable` to route
the module to a content revision queue (claim gets softened or
removed), not a citation queue.

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
                    "disposition": "<supported | weak_anchor | unciteable>",
                    "proposed_url": "https://... or null if unciteable",
                    "proposed_tier": "<tier or null if unciteable>",
                    "rationale": "<one sentence — why URL supports, or why nothing can>",
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
        for f in ("claim_text", "claim_class", "disposition"):
            if f not in claim:
                issues.append(f"claim[{i}]:missing_{f}")
        disp = claim.get("disposition")
        if disp and disp not in DISPOSITIONS:
            issues.append(f"claim[{i}]:bad_disposition:{disp}")
        # URL/tier required when cited; must be null when unciteable.
        if disp in {"supported", "weak_anchor"}:
            if not claim.get("proposed_url"):
                issues.append(f"claim[{i}]:missing_proposed_url_for_{disp}")
            if not claim.get("proposed_tier"):
                issues.append(f"claim[{i}]:missing_proposed_tier_for_{disp}")
        elif disp == "unciteable":
            if claim.get("proposed_url"):
                issues.append(f"claim[{i}]:unciteable_must_have_null_url")
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
        disp = claim.get("disposition")
        # Unciteable claims bypass URL validation — they carry null URL.
        if disp == "unciteable":
            claim["proposed_url"] = None
            claim["proposed_tier"] = None
            kept_claims.append(claim)
            continue
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


# ---- inject step ---------------------------------------------------------


INJECT_PROMPT_TEMPLATE = """You are the inject step of the KubeDojo citation
backfill pipeline. Given the module body and the already-validated citation
seed (with dispositions), produce a STRUCTURED EDIT PLAN the orchestrator
will apply mechanically. Do NOT rewrite the module yourself.

## Rules

1. Only `supported` and `weak_anchor` claims produce inline insertions.
   Unciteable claims are skipped (the module will go to a revision queue
   after this step; your job is not to cite them).
2. Each inline insertion must be a pure WRAP: take an existing phrase in
   the module body and wrap it in `[phrase](url)`. The `original_phrase`
   MUST appear verbatim in `target_line`. The `replace_with` MUST equal
   `[original_phrase](url)`. No prose edits.
3. `target_line` MUST be a verbatim single line from the module body
   (copy the whole line so the orchestrator can locate it unambiguously).
4. The `sources_section` is a full `## Sources` markdown block. It
   becomes the last section in the module. Include:
   - every URL used in inline insertions (supported + weak_anchor)
   - every validated further_reading URL
   - short human-readable titles
   - do NOT list the same URL twice
5. Do not touch Mermaid, code blocks, tables, frontmatter, or quiz
   answers. If a claim's span_hint points at a code block or table row
   that cannot be wrapped in a markdown link, SKIP the inline insertion
   for that claim (still include the URL in sources_section).

## Output schema

Emit ONE JSON object. No preamble, no markdown fences.

{schema_block}

## Module to edit

Module key: `{module_key}`

```markdown
{module_body}
```

## Seed (already-validated citations)

```json
{seed_json}
```

Return ONLY the JSON object.
"""


INJECT_SCHEMA_EXAMPLE = json.dumps(
    {
        "module_key": "<string>",
        "inline_insertions": [
            {
                "claim_id": "C001",
                "target_line": "<verbatim single line from module body>",
                "original_phrase": "<substring of target_line to be wrapped>",
                "replace_with": "[<original_phrase>](<url>)",
            }
        ],
        "sources_section": "## Sources\n\n- [<title>](<url>) — <one-sentence annotation>\n- ...\n",
        "skipped_claims": [
            {"claim_id": "C002", "reason": "span_hint points at mermaid block; no wrapping target"}
        ],
    },
    indent=2,
)


def build_inject_prompt(module_key: str, module_body: str, seed: dict[str, Any]) -> str:
    # Trim seed to the fields the inject step cares about (keep bytes down).
    compact_seed = {
        "module_key": seed.get("module_key"),
        "claims": [
            {
                "claim_id": c.get("claim_id"),
                "claim_text": c.get("claim_text"),
                "span_hint": c.get("span_hint"),
                "disposition": c.get("disposition"),
                "proposed_url": c.get("proposed_url"),
            }
            for c in (seed.get("claims") or [])
        ],
        "further_reading": seed.get("further_reading") or [],
    }
    return INJECT_PROMPT_TEMPLATE.format(
        schema_block=INJECT_SCHEMA_EXAMPLE,
        module_key=module_key,
        module_body=module_body,
        seed_json=json.dumps(compact_seed, indent=2, ensure_ascii=False),
    )


def _validate_inline_insertion(ins: dict[str, Any], body: str) -> str | None:
    """Return a reason string if insertion is invalid, else None."""
    for f in ("target_line", "original_phrase", "replace_with"):
        if not ins.get(f):
            return f"missing_{f}"
    target = ins["target_line"]
    phrase = ins["original_phrase"]
    replace = ins["replace_with"]
    # target_line must appear verbatim in the module body.
    if target not in body:
        return "target_line_not_in_body"
    # phrase must appear in target_line.
    if phrase not in target:
        return "phrase_not_in_target_line"
    # replace_with must wrap original_phrase in a link: [phrase](url)
    expected_prefix = f"[{phrase}]("
    if not (replace.startswith(expected_prefix) and replace.endswith(")")):
        return "replace_with_not_pure_wrap"
    url = replace[len(expected_prefix):-1]
    if not url.startswith(("http://", "https://")):
        return "replace_with_url_not_http"
    if allowlist_tier(url) is None:
        return "replace_with_url_off_allowlist"
    return None


def apply_inject_plan(body: str, plan: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Apply inline insertions + append sources_section. Returns (new_body, applied)."""
    new_body = body
    applied: list[dict[str, Any]] = []
    for ins in plan.get("inline_insertions") or []:
        reason = _validate_inline_insertion(ins, new_body)
        if reason:
            applied.append({"claim_id": ins.get("claim_id"), "status": "rejected", "reason": reason})
            continue
        target = ins["target_line"]
        phrase = ins["original_phrase"]
        replace = ins["replace_with"]
        # Replace the phrase WITHIN the target line only — first occurrence.
        # We re-find the target line to preserve surrounding lines exactly.
        idx = new_body.find(target)
        if idx < 0:
            applied.append({"claim_id": ins.get("claim_id"), "status": "rejected",
                            "reason": "target_disappeared_after_prev_edits"})
            continue
        phrase_idx_in_target = target.find(phrase)
        abs_phrase_idx = idx + phrase_idx_in_target
        new_body = new_body[:abs_phrase_idx] + replace + new_body[abs_phrase_idx + len(phrase):]
        applied.append({"claim_id": ins.get("claim_id"), "status": "applied"})

    sources = (plan.get("sources_section") or "").strip()
    if sources:
        if not new_body.endswith("\n"):
            new_body += "\n"
        new_body += "\n" + sources + "\n"
    return new_body, applied


_INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(https?://[^)]+\)")


def _strip_sources_section(body: str) -> str:
    """Drop a trailing `## Sources` block, if present."""
    if "## Sources" not in body:
        return body
    pre, _, _ = body.rpartition("## Sources")
    return pre.rstrip()


def _verify_diff_is_additive(original: str, modified: str) -> list[str]:
    """Sanity-check that `modified` differs from `original` only by
    (a) new inline [phrase](url) wraps and (b) an appended Sources section.

    Both sides are unwrapped to bare text before compare so pre-existing
    inline links in the original are not flagged as prose changes. The
    test is: strip-Sources(modified) unwrapped == original unwrapped.
    """
    issues: list[str] = []
    modified_pre = _strip_sources_section(modified)
    orig_unwrapped = _INLINE_LINK_RE.sub(r"\1", original).rstrip()
    mod_unwrapped = _INLINE_LINK_RE.sub(r"\1", modified_pre).rstrip()
    if mod_unwrapped != orig_unwrapped:
        import difflib
        d = list(difflib.unified_diff(
            orig_unwrapped.splitlines(),
            mod_unwrapped.splitlines(),
            lineterm="", n=1,
        ))
        # Trim to the first few hunks so the issue message is useful.
        sample = "\n".join(d[:40])
        issues.append(f"prose_changed_outside_sources: {sample[:800]}")
    return issues


def run_inject(module_key: str, *, agent: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    module_path = resolve_module_path(module_key)
    normalized_key = module_path.relative_to(DOCS_ROOT).with_suffix("").as_posix()
    seed_path = seed_path_for(normalized_key)
    if not seed_path.exists():
        return {"module_key": normalized_key, "ok": False,
                "error": "no_seed_file", "detail": f"run research first: {seed_path}"}
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    supported = [c for c in (seed.get("claims") or [])
                 if c.get("disposition") in {"supported", "weak_anchor"}]
    if not supported and not (seed.get("further_reading") or []):
        return {"module_key": normalized_key, "ok": False,
                "error": "nothing_to_cite",
                "detail": "seed has no supported claims and no further_reading"}
    unciteable = [c for c in (seed.get("claims") or []) if c.get("disposition") == "unciteable"]

    module_body = module_path.read_text(encoding="utf-8")
    prompt = build_inject_prompt(normalized_key, module_body, seed)

    if dry_run:
        return {"module_key": normalized_key, "dry_run": True,
                "supported_count": len(supported), "unciteable_count": len(unciteable),
                "prompt_bytes": len(prompt)}

    task_id = f"citation-inject-{normalized_key.replace('/', '-')}-{_dt.datetime.now(_dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    if agent == "codex":
        ok, raw = dispatch_codex(prompt, task_id=task_id)
    elif agent == "gemini":
        ok, raw = dispatch_gemini(prompt)
    else:
        raise ValueError(f"unknown agent: {agent}")
    if not ok:
        return {"module_key": normalized_key, "ok": False,
                "error": "dispatch_failed", "detail": raw[-500:]}
    try:
        plan = parse_agent_response(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return {"module_key": normalized_key, "ok": False,
                "error": "parse_failed", "detail": str(exc),
                "raw_head": raw[:400], "raw_tail": raw[-400:]}

    new_body, applied = apply_inject_plan(module_body, plan)
    diff_issues = _verify_diff_is_additive(module_body, new_body)

    staging_path = module_path.with_suffix(".staging.md")
    staging_path.write_text(new_body, encoding="utf-8")

    # Write a revision record if there are unciteable claims.
    revision_record = None
    if unciteable:
        revision_path = REPO_ROOT / ".pipeline" / "citation-revisions" / f"{normalized_key.replace('/', '-')}.json"
        revision_path.parent.mkdir(parents=True, exist_ok=True)
        revision_record = {
            "module_key": normalized_key,
            "module_path": str(module_path.relative_to(REPO_ROOT)),
            "recorded_at": _iso_utc_now(),
            "unciteable_claims": [
                {
                    "claim_id": c.get("claim_id"),
                    "claim_text": c.get("claim_text"),
                    "span_hint": c.get("span_hint"),
                    "rationale": c.get("rationale"),
                }
                for c in unciteable
            ],
        }
        revision_path.write_text(
            json.dumps(revision_record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return {
        "module_key": normalized_key, "ok": len(diff_issues) == 0,
        "staging_path": str(staging_path.relative_to(REPO_ROOT)),
        "applied_count": sum(1 for a in applied if a.get("status") == "applied"),
        "rejected_count": sum(1 for a in applied if a.get("status") == "rejected"),
        "applied": applied,
        "diff_issues": diff_issues,
        "unciteable_count": len(unciteable),
        "revision_record": (f".pipeline/citation-revisions/"
                            f"{normalized_key.replace('/', '-')}.json")
                            if revision_record else None,
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

    ip = subs.add_parser("inject", help="Apply already-validated seed to one module")
    ip.add_argument("module_key", help="Module key under src/content/docs/")
    ip.add_argument("--agent", default="codex", choices=["codex", "gemini"])
    ip.add_argument("--dry-run", action="store_true",
                    help="Print prompt + exit; no dispatch, no writes")

    args = parser.parse_args(argv)

    if args.command == "research":
        result = run_research(args.module_key, agent=args.agent, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") or result.get("dry_run") else 1

    if args.command == "inject":
        result = run_inject(args.module_key, agent=args.agent, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") or result.get("dry_run") else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
