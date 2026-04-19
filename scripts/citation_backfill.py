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
DISPOSITIONS = {
    "supported",
    "weak_anchor",
    "needs_allowlist_expansion",
    "soften_to_illustration",
    "cannot_be_salvaged",
}

# Audience-level calibration (derived from module path) shapes how strict
# the research prompt is about rough numbers, illustrative framings, and
# lesson_point URLs. Foundational beginner content should not demand NIST
# citations for "browsers use memory" — the pipeline stays in service of
# teaching, not over-rigor.
_AUDIENCE_RULES: list[tuple[str, str]] = [
    ("prerequisites/zero-to-terminal/", "absolute_beginner"),
    ("prerequisites/", "beginner"),
    ("linux/foundations/", "beginner"),
    ("k8s/kcna/", "beginner"),
    ("ai/foundations/", "beginner"),
    ("linux/operations/", "intermediate"),
    ("cloud/", "intermediate"),
    ("k8s/cka/", "intermediate"),
    ("k8s/ckad/", "intermediate"),
    ("platform/foundations/", "intermediate"),
    ("ai/", "intermediate"),
    ("linux/security/", "advanced"),
    ("k8s/cks/", "advanced"),
    ("platform/", "advanced"),
    ("on-premises/", "advanced"),
]


def audience_level(module_key: str) -> str:
    for prefix, level in _AUDIENCE_RULES:
        if module_key.startswith(prefix):
            return level
    return "intermediate"


_AUDIENCE_GUIDANCE = {
    "absolute_beginner": (
        "AUDIENCE: absolute beginner (no technical background).\n"
        "Calibration for this tier:\n"
        "- Prefer `soften_to_illustration` or `weak_anchor` for rough "
        "  numbers. Round numbers and order-of-magnitude claims stand "
        "  on their own when framed as illustration.\n"
        "- `cannot_be_salvaged` only for harmful precision (dated "
        "  specific prices, causal overclaims) — NOT for pedagogically "
        "  useful rough numbers.\n"
        "- `lesson_point_url` is OPTIONAL (may be null) when the "
        "  teaching prose is self-evident.\n"
        "- Analogies and connective teaching prose produce NO claim "
        "  entries. If the module says 'the CPU is a chef', that is "
        "  not a factual claim."
    ),
    "beginner": (
        "AUDIENCE: beginner with some exposure to computing.\n"
        "Calibration for this tier:\n"
        "- Mix of `supported` and `soften_to_illustration` is normal.\n"
        "- Primary sources preferred; Wikipedia and MDN acceptable for "
        "  foundational concepts.\n"
        "- `cannot_be_salvaged` only for false precision (dated prices, "
        "  fabricated benchmarks) and opinion-as-fact."
    ),
    "intermediate": (
        "AUDIENCE: practitioner with working knowledge.\n"
        "Calibration for this tier:\n"
        "- Apply the standard disposition rules.\n"
        "- Prefer primary sources; `weak_anchor` only for genuinely "
        "  loose claims."
    ),
    "advanced": (
        "AUDIENCE: senior / exam-track practitioner.\n"
        "Calibration for this tier:\n"
        "- Every dated-specific number, vendor pricing, version-specific "
        "  behavior, or CVE reference → `supported` with a live primary "
        "  source (upstream docs, KEPs, RFCs, CVE DB, vendor pages).\n"
        "- `weak_anchor` is rare at this tier — either you have the "
        "  primary source or you don't."
    ),
}
# Dispositions whose claims get inline citation wraps in the inject step.
CITED_DISPOSITIONS = {"supported", "weak_anchor"}
# Dispositions that drive a prose rewrite of the claim's sentence.
REWRITE_DISPOSITIONS = {"soften_to_illustration", "cannot_be_salvaged"}
# Dispositions that take no action in the current pipeline but surface
# in a review queue for allowlist expansion.
DEFERRED_DISPOSITIONS = {"needs_allowlist_expansion"}
# Claim classes where soften/salvage is never acceptable — these refer
# to real-world events/specs and MUST cite a primary source (or go to
# allowlist expansion). "cannot_be_salvaged" is only valid if the claim
# is demonstrably fabricated and the rewrite REMOVES the claim entirely.
HARD_CITE_CLASSES = {
    "war_story", "incident", "standard", "security_claim", "statistic",
}


# ---- prompt --------------------------------------------------------------


RESEARCH_PROMPT_TEMPLATE = """You are the research step of the KubeDojo citation backfill pipeline.

Your job: read the module below and return a JSON seed file that identifies
every factual claim that requires an inline citation, plus a short Further
Reading list. You do NOT rewrite the module. You do NOT add citations. You
only produce the JSON seed.

## HARD RULE: factual claims about real events MUST be cited

This rule is NON-NEGOTIABLE and overrides every audience calibration
below. The following claim classes MUST be `supported` OR
`needs_allowlist_expansion`. They CANNOT be `soften_to_illustration`
or `cannot_be_salvaged` unless the claim is provably fabricated
(in which case `cannot_be_salvaged` with a rewrite that REMOVES the
false claim entirely, not softens it):

- `war_story` — any anecdote naming a real company, person, date, or
  event. "GitLab's 2017 outage" MUST cite the postmortem (via
  `supported` if the host is allowlisted, else
  `needs_allowlist_expansion`). Never soften a named-event anecdote
  into "a company once had an outage" — that is lying with teaching
  flavor.
- `incident` — same rule. Real outages, real breaches, real CVEs get
  primary-source citations or go to allowlist expansion.
- `standard` — named specifications, regulations, RFCs. Cite the spec.
- `security_claim` — claims about real vulnerabilities, real attacks,
  real defenses in the wild. Must cite.
- `statistic` — specific statistics attributed to a real source
  ("StatCounter says Windows is X%"). Cite the source.

Claims that MAY be softened (audience calibration applies):
- `vendor_capability` — IF presented as illustrative ("AWS
  instances can cost a few cents per hour"). SPECIFIC vendor
  behavior statements ("kubelet uses X by default since 1.27") must
  be cited.
- `benchmark`, `pricing` — IF illustrative teaching numbers. Dated
  specific quotes must cite or be removed.

## Universal citation discipline (NOT a prose-style mandate)

IMPORTANT: this section governs CITATION patterns only. It does NOT
tell you to rewrite the module's voice, pacing, or teaching style.
The module's voice is preserved by the inject step (which swaps only
specific sentences, never freely rewrites). Your job here is the
citation layer underneath whatever voice the author chose.

Citation discipline (applies at every audience tier):
- Target density: kubernetes.io/docs. They cite RFCs, KEPs, CVEs,
  upstream design docs — NOT every sentence. Worked examples and
  connective prose carry themselves.
- Cite specifics (dated numbers, CVEs, version-specific behavior,
  vendor capability statements). Do NOT cite teaching flow,
  analogies, or pedagogical framing.
- Prefer one authoritative reference over three adjacent weak anchors.
- Hedging prose ("may", "sometimes", "depending on") is a yellow flag:
  if load-bearing, the specific case should be citable or softened.

What this does NOT mean:
- Do NOT demand the module read like a k8s reference doc. Absolute-
  beginner modules legitimately use warm analogies, longer paragraphs,
  and slower pacing. That's correct for their audience.
- Do NOT flag analogies ("the CPU is a chef") as unciteable. Analogies
  are teaching tools, not factual claims. They produce NO seed entry.

{audience_guidance}

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

## CRITICAL: disposition per claim — 5 states, pick the right one

Every claim gets exactly one `disposition`. This is the most
important judgment you make. Do not force URLs that don't honestly
back the claim, but also do not dump teaching examples into an
unfixable bucket — good pedagogy uses grounded hypotheticals.

- **`supported`** — URL's page directly discusses THIS specific
  claim. K8s Windows-support → `kubernetes.io/docs/concepts/windows/`.
  Transformer paper → `arxiv.org/abs/1706.03762`. Primary source.

- **`weak_anchor`** — URL is a category/topic page that touches the
  subject but doesn't confirm the specific number/event. Acceptable
  ONLY for loose claims ("browsers use memory"); never for specific
  ones.

- **`needs_allowlist_expansion`** — the claim is REAL and
  VERIFIABLE, but its primary source is NOT on the allowlist.
  Set `proposed_url` to the URL you WOULD have used (the off-list
  primary source). Set `proposed_tier` to null. The claim stays in
  the module unchanged for now; a separate allowlist-review process
  decides whether to add that domain.
  Example: GitLab 2017 outage → `about.gitlab.com/.../postmortem/`.
  If that host is not in the allowlist below, this is the right
  disposition.

- **`soften_to_illustration`** — the module uses a SPECIFIC number
  or scenario as a TEACHING EXAMPLE for a real underlying principle.
  The number itself isn't citable (it's illustrative), but the
  LESSON POINT is. Supply TWO things:
  1. `suggested_rewrite`: the sentence rewritten with explicit
     framing: "for instance,", "imagine", "a typical case", or an
     approximate form ("roughly"). Keep the pedagogical force.
  2. `lesson_point_url`: an allowlisted URL citing the GENERAL
     principle the example teaches (e.g. over-provisioning is
     common, browser memory varies widely).
  `proposed_url` / `proposed_tier` null.
  Example: "a team might pay $400/month for a 32GB server when
  they only use 2GB" → rewrite as "a team might easily pay
  hundreds of dollars per month for a server they only use a
  fraction of" + lesson_point_url to a FinOps / right-sizing doc.

- **`cannot_be_salvaged`** — false precision, verbatim quotes
  without a source, or opinions dressed as measurements. Rewrite
  the sentence to remove the false claim while preserving the
  teaching intent. Supply `suggested_rewrite`; `proposed_url`,
  `proposed_tier`, `lesson_point_url` all null.
  Examples:
  - "AWS listed t2.large at $0.0928/hr on April 15 2026" →
    rewrite: "a small AWS VM typically costs a few cents per
    hour, depending on region and instance type."
  - "OrbStack is the fastest, lightest, best-UX option" →
    rewrite: "OrbStack is a popular option known for speed and
    polished UX."

Decision rules (strict):
- Dated historical price with an exact amount (e.g. "$0.0928/hr on
  April 15 2026") → `cannot_be_salvaged` ALWAYS. Vendor pricing
  pages change; a URL for the instance family does NOT back the
  historical snapshot. Rewrite to "a few cents per hour, depending
  on region and instance type" or similar.
- Illustrative dollar amount in teaching prose ("a team might pay
  $400/month for a 32GB server") → `soften_to_illustration`.
- Specific percentage at a specific date (e.g. "60.8% in March
  2026") → `supported` ONLY if the live dashboard shows roughly
  that figure; else `soften_to_illustration` ("most common",
  "roughly X%").
- Real outage / incident with primary source off-allowlist →
  `needs_allowlist_expansion`.
- Superlative without benchmark ("fastest", "best UX") →
  `cannot_be_salvaged`.
- Exact quote / verbatim claim without interview source →
  `cannot_be_salvaged`.
- Back-of-envelope calculations presented as facts (e.g. "AGC had
  74 KB") → `soften_to_illustration` with the primary source as
  lesson_point, and a rewrite that rounds or qualifies the number.

Bias toward honesty. A truthful disposition is better than a
forced weak anchor.

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
                    "disposition": "<one of 5 dispositions — see rules above>",
                    "proposed_url": "https://... (required for supported/weak_anchor/needs_allowlist_expansion; null for soften/salvage)",
                    "proposed_tier": "<tier, or null if off-allowlist or rewrite disposition>",
                    "suggested_rewrite": "<rewritten sentence for soften/salvage; null otherwise>",
                    "lesson_point_url": "<allowlisted URL for lesson principle, soften only; null otherwise>",
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
    level = audience_level(module_key)
    guidance = _AUDIENCE_GUIDANCE.get(level, _AUDIENCE_GUIDANCE["intermediate"])
    return RESEARCH_PROMPT_TEMPLATE.format(
        audience_guidance=guidance,
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
        # Per-disposition field requirements.
        if disp in CITED_DISPOSITIONS:
            if not claim.get("proposed_url"):
                issues.append(f"claim[{i}]:missing_proposed_url_for_{disp}")
            if not claim.get("proposed_tier"):
                issues.append(f"claim[{i}]:missing_proposed_tier_for_{disp}")
        elif disp == "needs_allowlist_expansion":
            # URL optional but if present MUST be off-allowlist (that's
            # the whole point — we're asking for expansion).
            url = claim.get("proposed_url")
            if url and allowlist_tier(url) is not None:
                issues.append(f"claim[{i}]:needs_allowlist_expansion_but_url_is_already_allowlisted")
        elif disp in REWRITE_DISPOSITIONS:
            if claim.get("proposed_url"):
                issues.append(f"claim[{i}]:{disp}_must_have_null_proposed_url")
            if not claim.get("suggested_rewrite"):
                issues.append(f"claim[{i}]:missing_suggested_rewrite_for_{disp}")
            if disp == "soften_to_illustration" and not claim.get("lesson_point_url"):
                issues.append(f"claim[{i}]:missing_lesson_point_url_for_soften")
        cc = claim.get("claim_class")
        if cc and cc not in CLAIM_CLASSES:
            issues.append(f"claim[{i}]:bad_class:{cc}")
        tier = claim.get("proposed_tier")
        if tier and tier not in TIER_NAMES:
            issues.append(f"claim[{i}]:bad_tier:{tier}")
        # HARD RULE: war stories, incidents, standards, security claims,
        # and statistics cannot be softened. They must cite or defer.
        if cc in HARD_CITE_CLASSES and disp == "soften_to_illustration":
            issues.append(
                f"claim[{i}]:hard_cite_class_cannot_soften:"
                f"{cc}/{disp} — must be supported, weak_anchor, or needs_allowlist_expansion"
            )
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

        # Rewrite-bucket claims: no URL fetch needed; they carry a
        # suggested_rewrite and possibly a lesson_point_url. The
        # lesson_point_url MUST be on-allowlist and reachable.
        if disp in REWRITE_DISPOSITIONS:
            claim["proposed_url"] = None
            claim["proposed_tier"] = None
            lp_url = (claim.get("lesson_point_url") or "").strip() or None
            if lp_url:
                lp_tier = allowlist_tier(lp_url)
                if lp_tier is None:
                    rejected.append({
                        "url": lp_url, "reason": "lesson_point_off_allowlist",
                        "at_step": "research_validation",
                        "claim_id": claim.get("claim_id"),
                    })
                    claim["lesson_point_url"] = None
                else:
                    result = fetch(lp_url)
                    status = int(result.get("status") or 0)
                    if not (status and status < 400):
                        rejected.append({
                            "url": lp_url,
                            "reason": f"lesson_point_http_{status}" if status else "lesson_point_network_failure",
                            "at_step": "research_validation",
                            "claim_id": claim.get("claim_id"),
                        })
                        claim["lesson_point_url"] = None
            kept_claims.append(claim)
            continue

        # Allowlist-expansion-request claims: URL is optional CONTEXT
        # (the off-list source we'd use if allowlist grew). Don't
        # fetch — we're deliberately pointing at unknown hosts.
        if disp == "needs_allowlist_expansion":
            claim["proposed_tier"] = None  # by definition
            kept_claims.append(claim)
            continue

        # Cited dispositions: URL must be on-allowlist AND reachable.
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
will apply mechanically. You do NOT rewrite the module freely — every edit
is either an inline citation wrap or an authorized prose rewrite tied to a
specific claim_id.

## MANDATORY per-disposition actions

For EACH claim in the seed, you MUST emit the action its disposition
requires. A claim with a rewrite disposition that is not emitted as a
`prose_rewrite` in your output is a BUG in your output — the pipeline
will FAIL the module. Do not treat rewrites as optional.

- `supported` | `weak_anchor` → REQUIRED: one `inline_insertion` (pure
  wrap of an existing phrase in `[phrase](url)`). The URL is the one
  in the seed. If a supported-claim's span_hint points at a mermaid/
  code block/table row that cannot carry a markdown link, put the URL
  in `sources_section` instead and record the skip in
  `skipped_claims` with reason `span_not_wrappable`.

- `soften_to_illustration` → REQUIRED: one `prose_rewrite` entry.
  You ONLY identify the `target_line` — the verbatim line from the
  module body that contains the claim_text. The orchestrator does
  the actual sentence swap using the seed's `suggested_rewrite` and
  `claim_text`, so you do NOT need to construct the replacement
  string. Just tell us which line to target.
  If the seed has a `lesson_point_url`, add it to `sources_section`
  as a Further Reading-style entry (do NOT try to inline-wrap inside
  the rewritten sentence — that's brittle at scale).

- `cannot_be_salvaged` → REQUIRED: one `prose_rewrite` entry. Same
  shape as above — target_line only. Orchestrator handles the swap.
  No citation added.

- `needs_allowlist_expansion` → DO NOTHING. Add the claim_id to
  `skipped_claims` with reason `awaiting_allowlist_review`. Do not
  edit the module; do not add a citation.

Before returning your JSON, count: the number of rewrite-disposition
claims in the seed must equal the number of entries in
`prose_rewrites` OR appear in `skipped_claims`. If not, revise.

## Edit discipline

1. `target_line` MUST be a verbatim single line copied from the module
   body — the WHOLE line, untrimmed, exactly as it appears. Line
   boundaries are \\n. Copy once, don't edit.
2. For `inline_insertion`: `original_phrase` must appear verbatim in
   `target_line`; `replace_with` must equal `[original_phrase](url)`.
3. For `prose_rewrite`: just identify the `target_line` and the
   `claim_id`. The orchestrator constructs the actual replacement by
   finding the seed's `claim_text` inside target_line and swapping it
   for the seed's `suggested_rewrite`. If `claim_text` does not appear
   in `target_line` you picked the wrong line — revise.
4. Never modify frontmatter, Mermaid blocks, code blocks, quiz answers,
   or exercise steps. If a claim's span_hint points into one of those,
   skip it (add to `skipped_claims` with a reason).
5. `sources_section` is appended last. Include:
   - every URL used in inline_insertions
   - every validated `further_reading` URL from the seed
   - every `lesson_point_url` used by soften claims (as Further Reading
     style entries)
   - do NOT list duplicate URLs
   - short human-readable titles + one-sentence annotations

## Output schema

Emit ONE JSON object. No preamble, no markdown fences.

{schema_block}

## Module to edit

Module key: `{module_key}`

```markdown
{module_body}
```

## Seed (already-validated)

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
        "prose_rewrites": [
            {
                "claim_id": "C002",
                "target_line": "<verbatim single line from module body that contains claim_text>",
            }
        ],
        "sources_section": "## Sources\n\n- [<title>](<url>) — <one-sentence annotation>\n- ...\n",
        "skipped_claims": [
            {"claim_id": "C003", "reason": "awaiting_allowlist_review | span_in_code_block | ..."}
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
                "suggested_rewrite": c.get("suggested_rewrite"),
                "lesson_point_url": c.get("lesson_point_url"),
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


def _authorized_rewrites(seed: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Map claim_id → {claim_text, suggested_rewrite} for each rewrite-
    disposition claim in the seed. The orchestrator performs the actual
    sentence swap; Codex only picks the target_line.
    """
    out: dict[str, dict[str, str]] = {}
    for c in seed.get("claims") or []:
        if c.get("disposition") in REWRITE_DISPOSITIONS and c.get("suggested_rewrite") and c.get("claim_text"):
            out[str(c.get("claim_id") or "")] = {
                "claim_text": str(c["claim_text"]),
                "suggested_rewrite": str(c["suggested_rewrite"]),
            }
    return out


_MD_NOISE_RE = re.compile(r"[`*_\\]")


def _normalize_for_match(s: str) -> str:
    """Strip markdown formatting noise that the research step drops when
    paraphrasing claim_text. The module body keeps backticks around
    `t2.large` etc.; the seed's claim_text strips them. We normalize
    both sides before substring-checking."""
    return re.sub(r"\s+", " ", _MD_NOISE_RE.sub("", s)).strip()


def _find_claim_span_in_line(line: str, claim_text: str) -> tuple[int, int] | None:
    """Find where `claim_text` lives inside `line` after normalization.
    Returns (start, end) byte offsets IN THE ORIGINAL line, or None.

    We walk the original line and accumulate a mapping from normalized
    chars → original indices; then locate the normalized claim_text in
    the normalized line and translate back."""
    orig_norm_chars: list[str] = []
    orig_indices: list[int] = []
    for i, ch in enumerate(line):
        if _MD_NOISE_RE.match(ch):
            continue
        if ch.isspace():
            if orig_norm_chars and orig_norm_chars[-1] == " ":
                continue
            orig_norm_chars.append(" ")
            orig_indices.append(i)
        else:
            orig_norm_chars.append(ch)
            orig_indices.append(i)
    normalized_line = "".join(orig_norm_chars).strip()
    # Recompute indices after strip — if we stripped leading whitespace
    # the indices list needs the same trim.
    lead = len(normalized_line) and "".join(orig_norm_chars)[0] == " "
    if lead:
        orig_indices = orig_indices[1:]
        orig_norm_chars = orig_norm_chars[1:]
    normalized_claim = _normalize_for_match(claim_text)
    if not normalized_claim:
        return None
    pos = "".join(orig_norm_chars).find(normalized_claim)
    if pos < 0:
        return None
    end = pos + len(normalized_claim)
    if end - 1 >= len(orig_indices) or pos >= len(orig_indices):
        return None
    return orig_indices[pos], orig_indices[end - 1] + 1


def _authorized_replacement_lines(seed: dict[str, Any], body: str) -> set[str]:
    """Precompute the SET of replacement lines the orchestrator may
    emit — one per rewrite-disposition claim whose claim_text can be
    located in the body after markdown normalization. Used by the
    diff linter."""
    out: set[str] = set()
    for info in _authorized_rewrites(seed).values():
        claim_text = info["claim_text"]
        suggested = info["suggested_rewrite"]
        for line in body.splitlines():
            span = _find_claim_span_in_line(line, claim_text)
            if span is None:
                continue
            start, end = span
            new_line = line[:start] + suggested + line[end:]
            out.add(new_line.strip())
    return out


def _validate_prose_rewrite(rw: dict[str, Any], body: str,
                            authorized: dict[str, dict[str, str]]) -> str | None:
    for f in ("claim_id", "target_line"):
        if not rw.get(f):
            return f"missing_{f}"
    claim_id = str(rw["claim_id"])
    if claim_id not in authorized:
        return "rewrite_not_authorized_by_seed"
    target = rw["target_line"]
    if target not in body:
        return "target_line_not_in_body"
    claim_text = authorized[claim_id]["claim_text"]
    if _find_claim_span_in_line(target, claim_text) is None:
        return "claim_text_not_in_target_line"
    return None


def apply_inject_plan(body: str, plan: dict[str, Any], seed: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Apply inline insertions + authorized prose rewrites + append sources_section.
    Returns (new_body, applied).

    Prose rewrites: Codex identifies the target_line; the orchestrator
    constructs the replacement deterministically by substring-swapping
    the seed's claim_text for the seed's suggested_rewrite inside that
    line. Codex cannot inject arbitrary prose via this path.
    """
    new_body = body
    applied: list[dict[str, Any]] = []
    authorized = _authorized_rewrites(seed)

    # Prose rewrites FIRST so inline_insertions applied afterwards can't
    # accidentally target a phrase that's about to be rewritten.
    for rw in plan.get("prose_rewrites") or []:
        reason = _validate_prose_rewrite(rw, new_body, authorized)
        if reason:
            applied.append({"claim_id": rw.get("claim_id"), "kind": "prose_rewrite",
                            "status": "rejected", "reason": reason})
            continue
        claim_id = str(rw["claim_id"])
        target = rw["target_line"]
        claim_text = authorized[claim_id]["claim_text"]
        suggested = authorized[claim_id]["suggested_rewrite"]
        # Locate the claim span inside target_line via markdown-aware
        # substring search — we may be swapping into `t2.large` backtick
        # territory that the seed's claim_text dropped.
        span = _find_claim_span_in_line(target, claim_text)
        if span is None:
            applied.append({"claim_id": rw.get("claim_id"), "kind": "prose_rewrite",
                            "status": "rejected",
                            "reason": "claim_text_span_not_findable"})
            continue
        start, end = span
        new_line = target[:start] + suggested + target[end:]
        idx = new_body.find(target)
        if idx < 0:
            applied.append({"claim_id": rw.get("claim_id"), "kind": "prose_rewrite",
                            "status": "rejected",
                            "reason": "target_disappeared_after_prev_edits"})
            continue
        new_body = new_body[:idx] + new_line + new_body[idx + len(target):]
        applied.append({"claim_id": rw.get("claim_id"), "kind": "prose_rewrite",
                        "status": "applied"})

    for ins in plan.get("inline_insertions") or []:
        reason = _validate_inline_insertion(ins, new_body)
        if reason:
            applied.append({"claim_id": ins.get("claim_id"), "kind": "inline",
                            "status": "rejected", "reason": reason})
            continue
        target = ins["target_line"]
        phrase = ins["original_phrase"]
        replace = ins["replace_with"]
        idx = new_body.find(target)
        if idx < 0:
            applied.append({"claim_id": ins.get("claim_id"), "kind": "inline",
                            "status": "rejected",
                            "reason": "target_disappeared_after_prev_edits"})
            continue
        phrase_idx_in_target = target.find(phrase)
        abs_phrase_idx = idx + phrase_idx_in_target
        new_body = new_body[:abs_phrase_idx] + replace + new_body[abs_phrase_idx + len(phrase):]
        applied.append({"claim_id": ins.get("claim_id"), "kind": "inline",
                        "status": "applied"})

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


def _verify_diff_is_additive(original: str, modified: str,
                             authorized_rewrites: dict[str, str] | None = None) -> list[str]:
    """Sanity-check that `modified` differs from `original` only by
    (a) new inline [phrase](url) wraps, (b) authorized prose rewrites
    (each full-line replacement must match a seed-authorized target),
    and (c) an appended Sources section.

    Strategy: unwrap inline links on both sides, strip the new Sources
    block, then diff line-by-line. Any changed line must appear as a
    value in `authorized_rewrites` (the seed's suggested_rewrite set).
    """
    issues: list[str] = []
    authorized_values = set((authorized_rewrites or {}).values())
    modified_pre = _strip_sources_section(modified)
    orig_unwrapped = _INLINE_LINK_RE.sub(r"\1", original).rstrip()
    mod_unwrapped = _INLINE_LINK_RE.sub(r"\1", modified_pre).rstrip()
    if mod_unwrapped == orig_unwrapped:
        return issues

    # Not identical; find which lines changed and check each against the
    # authorized-rewrite set.
    import difflib
    orig_lines = orig_unwrapped.splitlines()
    mod_lines = mod_unwrapped.splitlines()
    matcher = difflib.SequenceMatcher(a=orig_lines, b=mod_lines, autojunk=False)
    unauthorized: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        # replace / insert / delete hunks
        removed = orig_lines[i1:i2]
        added = mod_lines[j1:j2]
        # 1-to-1 substitutions are the only allowed form (paired rewrite).
        if len(removed) == len(added):
            for old_line, new_line in zip(removed, added, strict=False):
                if new_line.strip() not in authorized_values:
                    unauthorized.append((old_line, new_line))
        else:
            # Asymmetric change — never allowed outside of Sources.
            unauthorized.append(("\n".join(removed)[:200], "\n".join(added)[:200]))
    if unauthorized:
        sample_lines: list[str] = []
        for old_line, new_line in unauthorized[:5]:
            sample_lines.append(f"-{old_line[:140]}")
            sample_lines.append(f"+{new_line[:140]}")
        issues.append("unauthorized_prose_change:\n" + "\n".join(sample_lines))
    return issues


def run_inject(module_key: str, *, agent: str = "codex", dry_run: bool = False) -> dict[str, Any]:
    module_path = resolve_module_path(module_key)
    normalized_key = module_path.relative_to(DOCS_ROOT).with_suffix("").as_posix()
    seed_path = seed_path_for(normalized_key)
    if not seed_path.exists():
        return {"module_key": normalized_key, "ok": False,
                "error": "no_seed_file", "detail": f"run research first: {seed_path}"}
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    claims = seed.get("claims") or []
    cited = [c for c in claims if c.get("disposition") in CITED_DISPOSITIONS]
    rewrites = [c for c in claims if c.get("disposition") in REWRITE_DISPOSITIONS]
    deferred = [c for c in claims if c.get("disposition") in DEFERRED_DISPOSITIONS]
    has_fr = bool(seed.get("further_reading") or [])
    if not cited and not rewrites and not has_fr:
        return {"module_key": normalized_key, "ok": False,
                "error": "nothing_to_do",
                "detail": "seed has no cited, rewrite, or further_reading actions"}

    module_body = module_path.read_text(encoding="utf-8")
    prompt = build_inject_prompt(normalized_key, module_body, seed)

    if dry_run:
        return {"module_key": normalized_key, "dry_run": True,
                "cited_count": len(cited),
                "rewrite_count": len(rewrites),
                "deferred_count": len(deferred),
                "further_reading_count": len(seed.get("further_reading") or []),
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

    new_body, applied = apply_inject_plan(module_body, plan, seed)
    diff_issues = _verify_diff_is_additive(
        module_body, new_body,
        authorized_rewrites={k: v for k, v in (
            (line_key, line_key) for line_key in _authorized_replacement_lines(seed, module_body)
        )},
    )
    # Coverage gate — every rewrite-disposition claim must appear in
    # either the applied rewrites set OR the skipped_claims list.
    expected_rewrite_ids = {
        str(c.get("claim_id")) for c in (seed.get("claims") or [])
        if c.get("disposition") in REWRITE_DISPOSITIONS
    }
    applied_rewrite_ids = {
        str(a.get("claim_id")) for a in applied
        if a.get("kind") == "prose_rewrite" and a.get("status") == "applied"
    }
    skipped_ids = {str(s.get("claim_id")) for s in (plan.get("skipped_claims") or [])}
    missing = expected_rewrite_ids - applied_rewrite_ids - skipped_ids
    if missing:
        diff_issues.append(
            f"rewrite_dispositions_not_addressed: {sorted(missing)[:5]}"
        )
    # Coverage gate — every cited-disposition claim must appear in
    # applied inlines OR skipped_claims. (supported+weak_anchor)
    expected_cited_ids = {
        str(c.get("claim_id")) for c in (seed.get("claims") or [])
        if c.get("disposition") in CITED_DISPOSITIONS
    }
    applied_inline_ids = {
        str(a.get("claim_id")) for a in applied
        if a.get("kind") == "inline" and a.get("status") == "applied"
    }
    missing_cited = expected_cited_ids - applied_inline_ids - skipped_ids
    if missing_cited:
        diff_issues.append(
            f"cited_dispositions_not_addressed: {sorted(missing_cited)[:5]}"
        )

    staging_path = module_path.with_suffix(".staging.md")
    staging_path.write_text(new_body, encoding="utf-8")

    # Write a deferred-claims record so allowlist-expansion review has
    # the full list. Rewrites are applied in-place; no revision record
    # needed for them any more.
    deferred_record_path = None
    if deferred:
        rp = REPO_ROOT / ".pipeline" / "citation-revisions" / f"{normalized_key.replace('/', '-')}.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(
            json.dumps({
                "module_key": normalized_key,
                "module_path": str(module_path.relative_to(REPO_ROOT)),
                "recorded_at": _iso_utc_now(),
                "needs_allowlist_expansion": [
                    {
                        "claim_id": c.get("claim_id"),
                        "claim_text": c.get("claim_text"),
                        "span_hint": c.get("span_hint"),
                        "off_allowlist_url": c.get("proposed_url"),
                        "rationale": c.get("rationale"),
                    }
                    for c in deferred
                ],
            }, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        deferred_record_path = str(rp.relative_to(REPO_ROOT))

    return {
        "module_key": normalized_key, "ok": len(diff_issues) == 0,
        "staging_path": str(staging_path.relative_to(REPO_ROOT)),
        "inline_applied": sum(1 for a in applied if a.get("kind") == "inline" and a.get("status") == "applied"),
        "rewrite_applied": sum(1 for a in applied if a.get("kind") == "prose_rewrite" and a.get("status") == "applied"),
        "rejected_count": sum(1 for a in applied if a.get("status") == "rejected"),
        "applied": applied,
        "diff_issues": diff_issues,
        "deferred_count": len(deferred),
        "deferred_record": deferred_record_path,
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
