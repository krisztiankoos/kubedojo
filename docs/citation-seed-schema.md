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
  "disposition": "supported | weak_anchor | unciteable",
  "proposed_url": "https://..." | null,   // required for supported/weak_anchor; null for unciteable
  "proposed_tier": "standards | upstream | vendor | incidents | general" | null,
  "rationale": "why this URL supports this claim, 1 sentence (for supported/weak_anchor) OR why no URL can honestly back the claim (for unciteable)"
}
```

### Disposition rules (critical — calibrated 2026-04-19)

The first calibration run on ZTT 0.1 showed Codex will force a weak
anchor for EVERY claim if not told otherwise, masking the fact that
some module claims are hallucinated fabrications that nothing can
honestly cite. The three dispositions exist to surface that:

- **`supported`** — the proposed URL's page content genuinely
  discusses THIS SPECIFIC claim. A K8s Windows-support claim cited
  to `kubernetes.io/docs/concepts/windows/` qualifies. A primary
  source, not just a thematic anchor.
- **`weak_anchor`** — the URL is a category-page or thematic-anchor
  that touches the same topic but doesn't directly confirm the
  specific number/event/claim. Acceptable when the claim is loose
  ("browsers use memory"). NOT acceptable when the claim is
  specific ("30 tabs use 4-6GB").
- **`unciteable`** — NO honest URL on the allowlist backs this
  claim; it likely originates from the module writer's parametric
  knowledge, not evidence. Do NOT force a URL. Set `proposed_url`
  and `proposed_tier` to null. The module will be flagged for
  content revision — the claim should be softened, made generic,
  or removed — instead of citation.

Pattern: dated-specific prices, exact percentages at a single date,
verbatim quotes without source, very specific incident details
are high-probability `unciteable`.

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
