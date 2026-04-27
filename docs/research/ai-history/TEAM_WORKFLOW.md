# AI History Team Workflow

This is a living operating document for the AI History book. Update it when the team learns a better practice. Do not treat it as frozen policy.

## Operating Principle

Honesty over output is the highest rule. A chapter should be shorter if verified research cannot support the desired length. Agents must not invent scenes, dialogue, institutional motives, deployment numbers, hardware details, or causal links to satisfy a word target.

## Roles

- Human editor: sets ambition, accepts scope tradeoffs, resolves taste and book-level direction.
- Primary researcher: owns the chapter contract and keeps claims tied to evidence.
- Gemini reviewer: stress-tests research completeness, source choice, word-count honesty, and prose readiness.
- Claude reviewer: when available, provides cross-family review for narrative coherence, overclaiming, and final prose quality.
- Codex reviewer/writer: may research, implement docs, draft prose after gates, and maintain workflow artifacts.

Agents should help each other by naming gaps plainly. A useful refusal or downgrade is better than a confident but unsupported expansion.

## Chapter Lifecycle

### 1. Research Contract

Create or fill the standard chapter files:

- `brief.md`
- `sources.md`
- `timeline.md`
- `people.md`
- `infrastructure-log.md`
- `scene-sketches.md`
- `open-questions.md`
- `status.yaml`

The contract must include:

- thesis and scope
- boundary contract for what not to overclaim
- primary and secondary source table
- scene-level claim table with Green/Yellow/Red status
- timeline and people map
- infrastructure constraints
- open questions
- honest prose-capacity estimate

Research-contract approval means the structure and source plan are good enough to continue research. It does not mean prose drafting may begin.

### 2. Research Gap Analysis

After research-contract approval, request or create a gap analysis before prose readiness. The gap analysis should answer:

- Which claims remain Yellow or Red?
- Which page, section, figure, table, or archival anchors are missing?
- Which sources are primary, secondary, tertiary, or merely convenient?
- Which narrative scenes are strong enough to draft?
- Which scenes are too thin or speculative?
- What word count is naturally supported by verified evidence?
- Which chapter ambitions should be reduced?
- What should Gemini, Claude, Codex, or the human editor help source?

Gap analysis should be concrete. "Need more sources" is weak. "Need Pearl 1986 page anchor for local propagation in singly connected networks" is useful.

### 3. Anchor Extraction

Before prose readiness, extract exact anchors for high-value claims:

- page numbers for books and PDFs
- section names for HTML sources
- theorem, figure, table, or equation identifiers where useful
- DOI, stable URL, archival URL, or bibliographic identifier

Do not upgrade a claim to Green just because a source is famous. Upgrade it only when the specific claim is anchored.

### 4. Prose-Readiness Review

Ask Gemini to review the full contract plus gap analysis. The expected verdicts are:

- `READY_TO_DRAFT`: page anchors and gaps are sufficient for a faithful chapter.
- `READY_TO_DRAFT_WITH_CAP`: draft, but cap the word count below the target.
- `NEEDS_ANCHORS`: source list is good, but page/section anchors are missing.
- `NEEDS_RESEARCH`: source list or scope is inadequate.
- `SCOPE_DOWN`: the chapter should be shorter or narrower.

Only `READY_TO_DRAFT` and `READY_TO_DRAFT_WITH_CAP` unlock prose drafting.

### 5. Drafting

Draft only from verified evidence. Use Yellow claims only with explicit caution and never as structural load-bearing claims. Red claims stay out of prose except as clearly labeled open questions.

If a chapter cannot honestly reach 4,000 words, write the natural chapter length and document why. The target is quality, not padding.

### 6. Prose Review

Ask Gemini to review the drafted chapter for:

- factual overclaims
- unsupported scenes
- missing citations
- source misuse
- narrative coherence
- word-count inflation
- book-level continuity

Do not merge prose on tests alone. Cross-family review remains required.

### 7. Claude / Cross-Family Review

When Claude is available, ask for an independent-family review before final acceptance. Claude should especially check:

- whether the prose outpaced the research contract
- whether the story is compelling without fabrication
- whether chapter transitions and part-level arcs work

### 8. Human Final Pass

The human editor decides:

- whether the chapter's natural length is acceptable
- whether to source more material or scope down
- whether tone and pacing match the book
- whether unresolved questions can remain as future work

## Status Terms

- `researching`: contract or anchors are still incomplete.
- `research_contract_approved`: reviewer approved the research plan, but prose is not unlocked.
- `gap_analysis_requested`: reviewer has been asked to identify missing anchors and weak scenes.
- `anchors_in_progress`: exact page/section anchors are being extracted.
- `prose_ready`: reviewer says drafting may begin.
- `drafting`: prose is being written.
- `prose_review`: draft is under cross-family review.
- `accepted`: human/cross-family review has cleared the chapter.

## Word Count Discipline

Word count must follow evidence. Use these labels in briefs and gap analyses:

- `4k-7k supported`: verified sources can support a long narrative without padding.
- `3k-5k likely`: chapter has enough evidence, but some scenes should stay compact.
- `2k-4k natural`: conceptually important but structurally compact.
- `short chapter recommended`: expansion would require filler or unrelated material.

When in doubt, lower the target and ask for help sourcing the missing layer.

## Review Request Template

Use this shape when asking for gap analysis or prose readiness:

```text
Please review Chapter N as [gap analysis / prose-readiness review].

Focus files:
- docs/research/ai-history/chapters/ch-XX-.../brief.md
- docs/research/ai-history/chapters/ch-XX-.../sources.md
- docs/research/ai-history/chapters/ch-XX-.../open-questions.md

Questions:
1. Which claims remain Yellow/Red and why?
2. Which exact page/section anchors are required before prose?
3. Which scenes are strong enough to draft, and which are thin?
4. What natural word-count range is supported by verified evidence?
5. What should another agent or the human editor help source?

Please post a structured comment with concrete gaps and a verdict:
- READY_TO_DRAFT
- READY_TO_DRAFT_WITH_CAP
- NEEDS_ANCHORS
- NEEDS_RESEARCH
- SCOPE_DOWN
```

## Change Rule

This document should evolve through small PRs. When the team discovers a repeatable failure mode, add a rule here and cite the chapter or PR that exposed it.
