# Citation Seed JSON Schema

Contract for per-module citation seed files written by
`scripts/citation_backfill.py research`. Frozen this session per
Codex's "contract first" consult.

## File path

```
docs/citation-seeds/{module-key-with-slashes-replaced-by-dashes}.json
```

Example:
`docs/citation-seeds/prerequisites-zero-to-terminal-module-0.1-what-is-a-computer.json`

One file per module. Supersedes the legacy per-track
`docs/citation-seeds-{track}.md` format (which remains readable by
v1_pipeline.py's `_citation_seed_path` fallback for any drafts
already in flight).

## Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `module_key` | string | yes | Matches the module path under `src/content/docs/` without `.md`. |
| `module_path` | string | yes | Relative to repo root. |
| `research_run_id` | string | yes | `{ISO-8601-utc}-{agent}-{model}` — traceability. |
| `schema_version` | integer | yes | Starts at `1`. Bump on breaking changes. |
| `claims` | array[Claim] | yes | Zero-length means "no hard claims in this module"; fine. |
| `further_reading` | array[Link] | yes | At least 1 entry if `claims` is empty. |
| `notes` | string | no | Free-text agent notes for the next step. |
| `rejected_urls` | array[RejectedURL] | no | URLs the validator dropped (allowlist miss, 4xx/5xx). |

## Claim object

```json
{
  "claim_id": "C001",
  "claim_text": "verbatim or tightly-paraphrased sentence from the module",
  "claim_class": "war_story | incident | statistic | standard | vendor_capability | pricing | benchmark | security_claim",
  "span_hint": "line 74" or "section: RAM" or "paragraph after diagram 2",
  "disposition": "supported | weak_anchor | needs_allowlist_expansion | soften_to_illustration | cannot_be_salvaged",
  "proposed_url": "https://..." | null,   // required for supported/weak_anchor; optional for needs_allowlist_expansion (context); null for soften/salvage
  "proposed_tier": "standards | upstream | vendor | incidents | general" | null,
  "suggested_rewrite": "for soften_to_illustration and cannot_be_salvaged: the new sentence text",  // null for other dispositions
  "lesson_point_url": "https://... for soften_to_illustration: URL citing the general principle the example teaches",  // null for others
  "rationale": "why this URL supports this claim, or why no URL can, or why rewrite is needed"
}
```

### Disposition rules (calibrated 2026-04-19, refined same-session)

The first calibration on ZTT 0.1/0.2/0.11 revealed that lumping
every non-citable claim into one bucket loses the signal. There are
five distinct states a claim can be in, each with a different
downstream action. Codex must pick exactly one:

- **`supported`** — the proposed URL's page content genuinely
  discusses THIS SPECIFIC claim. A K8s Windows-support claim cited
  to `kubernetes.io/docs/concepts/windows/` qualifies. Primary or
  near-primary source. Downstream: inline-wrap at the claim's span.

- **`weak_anchor`** — URL is a category/topic page touching the
  same subject but doesn't directly confirm the specific
  number/event. Acceptable for loose claims ("browsers use
  memory"), unacceptable for specific ones ("30 tabs use 4-6GB").
  Downstream: inline-wrap; flagged for a future semantic-verify
  pass.

- **`needs_allowlist_expansion`** — a REAL, verifiable claim whose
  primary source is NOT on the allowlist. Downstream: NO inline
  citation; module's claim stays unchanged for now; the claim goes
  to a review list for allowlist expansion. Codex MAY include the
  URL it would have used so the expansion review has context
  (stored in `proposed_url`; `proposed_tier` is null because the
  domain isn't tiered).
  Example: GitLab 2017 outage — primary postmortem is
  `about.gitlab.com`, which may or may not be on the current
  allowlist.

- **`soften_to_illustration`** — a grounded PEDAGOGICAL example
  where a specific number or scenario is used to teach a real
  principle. The number itself isn't citable (it's illustrative),
  but the LESSON POINT is real and citable. Downstream: rewrite
  the sentence with explicit framing ("for instance,", "imagine",
  "a typical case would be"), AND add a citation for the general
  principle the example teaches. Codex must supply both the
  rewritten sentence AND the citation URL for the lesson point.
  Example: "a team might pay $400/month for a 32GB server when
  they only use 2GB" — specific number is fake, but
  over-provisioning is a real documented phenomenon.

- **`cannot_be_salvaged`** — false precision, verbatim quotes
  with no source, or opinions stated as fact. Downstream: rewrite
  the sentence to remove the false precision/opinion, preserving
  the teaching intent. No citation needed. Set `proposed_url` and
  `proposed_tier` to null.
  Examples: "AWS listed t2.large at $0.0928/hr on April 15 2026"
  (fake specificity); "OrbStack is the fastest, lightest option"
  (subjective dressed as measurement).

Pattern matching:
- Dated-specific prices → `cannot_be_salvaged` (or `supported` if a
  real current pricing page backs it).
- Specific outage details → `supported` if on allowlist, else
  `needs_allowlist_expansion`.
- Illustrative numbers in teaching prose → `soften_to_illustration`.
- Superlatives without benchmark → `cannot_be_salvaged`.

Rules:
- `claim_id` is stable across research runs for the same module
  (use sha1 of `claim_text` truncated to 7 chars, prefixed `C`).
- `claim_class` must match the taxonomy in
  `docs/citation-trusted-domains.yaml :: claim_class_priority`.
- `proposed_tier` MUST be one of the allowlist tiers when set. If
  the URL's host matches a different tier, the validator
  auto-corrects and records a note.
- Teaching prose (analogies, connective tissue, instructor framing)
  must NOT produce claims. Zero-claim output is legitimate.

## Link object (further_reading)

```json
{
  "url": "https://...",
  "title": "Plain-English title",
  "tier": "standards | upstream | vendor | incidents | general",
  "why_relevant": "1 sentence on why a learner would click this"
}
```

## RejectedURL object

```json
{
  "url": "https://...",
  "reason": "off_allowlist | http_403 | http_404 | network_failure | pdf_no_adapter",
  "at_step": "research_validation",
  "agent_proposed_tier": "standards"
}
```

## Validation pipeline

After the agent emits its JSON, `citation_backfill.py` performs:

1. **Schema check** — all required fields present, enums valid.
2. **Allowlist check** — every URL's host resolves to a tier in
   `docs/citation-trusted-domains.yaml`. Mismatches go to
   `rejected_urls`.
3. **Fetch check** — each remaining URL is fetched via
   `scripts/fetch_citation.py`. Non-2xx/3xx or PDF (MVP: no adapter
   yet) go to `rejected_urls`.
4. **Minimum-output check** — if `claims` is empty AND
   `further_reading` has fewer than 1 validated link, the module
   goes to `review_needed` state (seed file written but marked
   incomplete). No inject step runs.
5. **Write** — validated seed written to disk; rejected URLs kept
   in `rejected_urls` for the next retry to avoid repeating
   hallucinations.

## Examples

See calibration outputs under `docs/citation-seeds/` after the
first research runs ship.
