# Tier 3 Proposal — Chapter 13: The List Processor

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer: Codex (cross-family).

## Element 8 — Inline parenthetical definition (Starlight tooltip)

**SKIPPED** — universal default until a non-destructive tooltip component lands.

## Element 9 — Pull-quote (at most 1)

The chapter has zero verbatim quotes from primary sources — paraphrase throughout. Candidates surveyed:

### Candidate A — Russell `eval` realisation anecdote

The chapter (line 144) explicitly calls this out as Yellow-sourced: *"McCarthy's later retrospective includes the famous claim that Russell realized the `eval` definition could be implemented and hand-compiled it for the IBM 704. That anecdote rests on McCarthy's reminiscence rather than a paginated contemporary source, so the narrower and better-anchored claim is still the load-bearing one..."*

**Status: SKIPPED.** The contract (`brief.md`) and the chapter prose itself flag this as Yellow until HOPL page extraction lands. A pull-quote on a flagged-Yellow anecdote would override the chapter's own source-discipline. Wait for HOPL page anchors before reconsidering.

### Candidate B — McCarthy 1960 CACM opening

McCarthy, "Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I," *CACM* 3(4), April 1960, p. 184. The paper's opening sentence is widely reproduced; the chapter does not quote it directly.

**Status: PROPOSED**, *pending Codex verbatim verification against the CACM PDF (or the LISP 1.5 manual reproduction).* If the verbatim is reasonable, insert immediately after the "## `eval`, Lambda, `cond`, and Recursion" heading or after the line "The most compact way to see LISP's theory side is to follow `eval`" (whichever Codex judges better).

Working hypothesis for the verbatim (Codex to verify):

> "A programming system called LISP (for LISt Processor) has been developed for the IBM 704 computer by the Artificial Intelligence group at M.I.T."

If verbatim correct, an annotation could read: "The 1960 CACM paper formalised the language; the system itself had already been running for two years."

### Candidate C — McCarthy 1958 AIM-001 design rationale

The 1958 memo's opening articulates the FLPL boundary and the case for a new language. The chapter paraphrases this throughout the "IPL before LISP, FLPL before LISP Proper" section, but quotes nothing.

**Status: SKIPPED** in favour of Candidate B — the 1960 CACM paper is more iconic for LISP's public-canon moment, and the cap is one pull-quote. Codex may overrule if AIM-001 has a more quote-worthy sentence.

## Element 10 — Plain-reading asides (1–3 per chapter)

Chapter 13 is more technically dense than Ch10–Ch12. Survey:

### Candidate D — the S-expression-as-both-code-and-data paragraph (line 122)

> "That alignment is the heart of the chapter. In many languages, programs describe operations on data from a distance. In LISP, the program itself could be represented as a list. A conditional expression, a function application, a quoted symbol, or a function definition could be placed inside the same nested structure as the data it manipulated."

**Status: SKIPPED.** The paragraph is itself the plain-reading. The two paragraphs that follow (lines 124–126) further unpack the print-read-eval roundtrip. An aside would echo, not extend.

### Candidate E — the `eval`-as-bridge paragraph (line 160)

> "The important point is not that LISP was magic. It is that `eval` connected the two halves of the system. The theory of recursive symbolic functions became a machine process. The machine process operated over the same list structures that programmers could inspect and construct."

**Status: SKIPPED.** Already a plain-reading sentence-by-sentence. The chapter put the explanatory work in the prose itself.

### Candidate F — the mark-and-sweep paragraph (line 172)

> "Mark-and-sweep matched the way list structure worked. The system could begin from known roots: active variables, stacks, and structures still reachable by the running program. It could mark every cell reachable from those roots by following `car` and `cdr` links. Unmarked cells were no longer reachable by the program and could be swept back into available storage."

**Status: SKIPPED.** This *is* a plain-reading paragraph in form — the mark-and-sweep algorithm walked through in three sentences. An aside would replicate.

### Candidate G — the IBM 704 register etymology paragraph (line 92)

> "`cons` built a pair from two expressions. `car` selected the address part, the first side of the pair. `cdr` selected the decrement part, the rest of the pair…"

**Status: SKIPPED.** Already plain-read inline (the prose names "address part" and "decrement part" rather than just the opcodes).

## Summary verdict

- Element 8: SKIP.
- Element 9: 1 PROPOSED (Candidate B — 1960 CACM opening, verbatim TBD by Codex), 2 SKIPPED.
- Element 10: 0 PROPOSED, 4 SKIPPED.

**Total: 1 PROPOSED, 6 SKIPPED.** All four plain-reading candidates were skipped because the surrounding prose already does the plain-reading work.

Author asks Codex to:
1. Verify the verbatim wording of Candidate B against the CACM PDF or LISP 1.5 reproduction. APPROVE / REJECT / REVISE with corrected text.
2. Confirm the all-SKIP on plain-reading asides — is there a paragraph I'm misclassifying?
3. Identify any paraphrased-but-not-quoted primary-source sentence I missed (the pattern that caught the Turing child-mind sentence in Ch10).
