# Tier 3 proposal — Chapter 9: The Memory Miracle

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer: Codex (cross-family adversarial).

## Element 1 — Pull-quote (`:::note`, ≤1 per chapter)

**Status: SKIPPED**

Rationale: Rule (b). Every quote-worthy sentence in Ch09 is already inside a prose paragraph that introduces and contextualises it. Candidates considered:

- Williams & Kilburn (1948 *Nature* Letter): "purely experimental, and is on too small a scale to be of mathematical value." Already in-prose with framing about the Manchester rig's limitations.
- Kilburn 1947 report: "of the order of 0.2 seconds … by the insulating properties of the screen material" + "regenerating the charge pattern at a frequency greater than 5 cycles/second" + the "600 microseconds" hypothetical-machine instruction-time figure. Already quoted at full length with the report's full encoding-scheme list (dot-dash, dash-dot, defocus-focus, focus-defocus, anticipation).
- Forrester on the mercury delay line: "It worked. But it was slow." Already in-prose, in-line.
- Forrester on Williams-tube reliability: "expensive and short-lived and not very reliable." Already in-prose, used twice.
- Forrester on Project Whirlwind's reliability emphasis: "were devoted to scientific computation where if the machine stopped working, you could begin over or do the job tomorrow." Already in-prose with the air-defence contrast immediately following.
- Forrester on the desperation of the era: "people were desperate for memory for computers. All kinds of things were being tried." Already in-prose, two sentences.
- Forrester on the Boston-to-Buffalo television-link idea: "seriously considered renting a television link from Boston to Buffalo and back so that we could store binary digits in the transit time that it would take to make the round-trip on the television channel." Already in-prose at full length, with a substantial follow-up paragraph that does the interpretive work ("It was a poor answer, but it located the problem exactly").
- Forrester on the 3D geometry insight: "if we had one-dimensional storage and two-dimensional storage, what's the possibility of a three-dimensional storage." Already in-prose with full attribution.
- Forrester on the coincident-current selection trick (1947 glow tubes): "You could activate a wire say in the 'x' axis and another one crossing in the 'y' axis and only the glow tube at the intersection would have enough voltage on it to break down and begin to discharge." Already in-prose at full length, with the next paragraph plain-reading the threshold logic.
- Forrester on the magnetic-material substitution (1949): "over a period of two or three months we developed how that could be done and then over the next three years or so, we in fact brought it to the point where it was a working, permanently reliable system." Already in-prose with full attribution.
- Forrester's January 1951 *J. Appl. Phys.* abstract: "tests show that most existing metallic magnetic materials switch in 20 to 10,000 microseconds and are too slow" and "nonmetallic magnetic materials … switch in less than a microsecond." Already in-prose with the 2:1 ratio framing.
- Forrester's patent 2,736,880: "of magnetic material, each having substantially rectangular hysteresis properties … the several rings being arranged in rows and columns" + "3 ∛number of cores" input leads. Already in-prose with the cube-root scaling argument.
- Wang's patent 2,708,722: "at least 0.4-0.5, preferably greater than 0.80" residual flux density + "involves no mechanical movement … hence, its speed is not limited by mechanical considerations." Already in-prose with the next paragraph plain-reading the remanence point.
- Forrester on the Memory Test Computer: "I must say I doubted that they could do it and certainly not in the nine months they said it would take, but they came very close." Already in-prose with full attribution and the next-paragraph hinge framing.
- Forrester on choosing IBM: "to a substantial number of companies, probably 15 or so" + "it was clear that IBM was far ahead of any of the others as a possible company to do the work, so we recommended them to the Air Force." Already in-prose at full length.
- Forrester on the SAGE 1956 cast: "By 1956, the SAGE air defense system was essentially cast in its direction. The first of 30-some computer centers was nearing completion in New Jersey." Already in-prose.

Pull-quote: SKIP per (b). Every candidate is already quoted in-prose with framing that does the work a callout would otherwise do.

## Element 2 — Plain-reading aside on a dense paragraph (`:::tip[Plain reading]`)

**Status: SKIPPED**

Rationale: `READER_AIDS.md` item 10 reserves plain-reading callouts for *symbolically* dense paragraphs (mathematical formulas, derivations, abstract definitions stacked) — explicitly *not* narratively dense paragraphs. Ch09 is mostly narrative (institutional history, biography, oral-history quotation), with a handful of symbolic moments — but each is already plain-read in the same paragraph or the immediately following one. Candidates:

- **The 2:1 discrimination ratio paragraph.** REJECTED — the paragraph itself contains its own plain reading: "A current in one coordinate line alone had to remain below the switching threshold; simultaneous currents in the crossing lines had to exceed it. The selected core changed state, while the many half-selected cores on the same row or column remained unchanged. In practical terms, the array was a field of tiny magnetic decisions, each decision made only when two coordinates agreed on the same location." A callout would only restate this.
- **The "3 ∛number of cores" scaling formula paragraph.** REJECTED — the paragraph's last sentence already plain-reads it: "If the memory grew by volume while the wiring grew by edge length, memory could scale without drowning the machine in connections." That is the gist; a callout would duplicate.
- **The Wang patent residual-flux-density paragraph.** REJECTED — the next paragraph already plain-reads it: "The patent language about residual flux density was not decorative physics. It specified how strongly the material should remember after the applied pulse ended. In a memory technology, remanence was the point: the device had to retain a distinction without continuous power or mechanical motion."
- **The Kilburn report 0.2-second-retention / 5-Hz refresh / 600-μs instruction-time paragraph.** REJECTED — the next paragraph plain-reads the encoding-scheme list (dot-dash, defocus-focus): "Kilburn was not describing a settled component to be dropped into an engineering design. He was comparing ways to make a visible electrical trace on a cathode-ray screen stand for a stable binary state."
- **The 1947 glow-tube coincident-current paragraph.** REJECTED — the next paragraph plain-reads the threshold logic: "Coincident selection depends on a threshold. Each selected coordinate contributes only part of the force needed to change a state; only at the addressed intersection do the contributions add up to enough."
- **The Forrester 1951 *J. Appl. Phys.* abstract paragraph (20–10,000 μs vs. <1 μs).** REJECTED — the next paragraph already plain-reads the magnitude difference: "the claim that a nonmetallic magnetic material could switch in less than a microsecond was not a marginal improvement. It was the difference between memory as an unstable timing trick and memory as an addressable component."

No paragraph in Ch09 satisfies the symbolic-density criterion in a way that is not already plain-read in the same or next paragraph. SKIP per item 10's explicit permission to refuse.

## Element 3 — Inline parenthetical definition (Starlight tooltip)

**Status: SKIPPED**

Rationale: `READER_AIDS.md` item 8 — universal SKIP across every chapter until a non-destructive tooltip component lands. Ch09's specialist terms (Williams tube, mercury delay line, rectangular hysteresis loop, coincident-current selection, magnetic-core memory, Project Whirlwind / SAGE, Memory Test Computer) are covered by the Plain-words glossary above.

---

## Author's prediction

Calibration: Ch01 2/5; Ch02 0/4; Ch03 1/3; Ch04 0/3; Ch05 0/3; Ch06 0/3; Ch07 0/3; Ch08 0/3. Ch09 has the same shape as the 0/3 group — every quote-worthy sentence already in-prose, every symbolically dense paragraph already plain-read by the same or next paragraph. Predicting **0/3** with all-AGREE from Codex. Open to a counter-proposal, especially if Codex sees a paragraph that a callout would genuinely *add* to.
