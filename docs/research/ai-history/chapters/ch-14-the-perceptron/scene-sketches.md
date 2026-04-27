# Scene Sketches: Chapter 14 - The Perceptron

## Scene 1: Not Dartmouth, Buffalo

- **Setting:** Cornell Aeronautical Laboratory, Buffalo, 1957-1958, under ONR sponsorship. This is a different institutional world from Dartmouth, RAND, and MIT symbolic AI.
- **Beat:** Rosenblatt is asking how organisms sense, store, and use information, not how to write a theorem-proving program or list-processing language. The scene positions the perceptron as a cybernetic research program before the reader encounters Mark I or press hype.
- **Narrative Use:** Establish the chapter's central boundary: Rosenblatt was not at Dartmouth, and the perceptron line is not a footnote to symbolic AI. It is a competing research style with its own institutions, machines, and funding logic.
- **Evidence Anchors:** `PsychRev58`, p. 386; `POND61`, pp. vii-ix; Ch11 local boundary.
- **Pedagogical Demonstration:** Contrast a symbolic-AI question ("What rules search a proof space?") with Rosenblatt's question ("How can a network change after experience so later stimuli evoke different responses?"). Keep this conceptual, not polemical.

## Scene 2: The Paper Perceptron

- **Setting:** The 1958 *Psychological Review* paper and the theoretical vocabulary later consolidated in *Principles of Neurodynamics*.
- **Beat:** The perceptron is introduced as a hypothetical nervous system and a theory of storage and organization, not as a finished robot. S-units, A-units, R-units, response thresholds, and reinforcement become the reader's basic vocabulary.
- **Narrative Use:** This scene prevents modern flattening. The perceptron was not just a one-line classifier; it was a theory of signal-generating units, networks, environments, response functions, and reinforcement systems.
- **Evidence Anchors:** `PsychRev58`, p. 386; `POND61`, pp. 79-92; `Smithsonian-MarkI` S/A/R object-record description; `HubelWiesel59-62` for V1 receptive-field hierarchies.
- **Pedagogical Demonstration:** Use a small diagram-in-words: a sensory pattern activates S-units; selected signals move through A-units; R-units compete or fire; reinforcement changes later behavior. Avoid modern code.
- **Novel-Contribution Beat:** State precisely what is Rosenblatt's *new* idea here. The threshold-logic neuron is McCulloch-Pitts 1943 (Ch5). The "neurons that wire together fire together" learning intuition is Hebb 1949 (Ch5). The cybernetic feedback frame is Wiener 1948 (Ch6). Rosenblatt's contribution is narrower: a supervised error-correction learning procedure that adjusts weights on the random A-layer connections after a wrong response, plus a convergence theorem that bounds when that procedure terminates with a solution. Get this distinction in front of the reader before the convergence-theorem scene.
- **Physiological Resonance Beat:** Note that Rosenblatt's S/A/R hierarchy is structurally similar to the V1 receptive-field hierarchies that David Hubel and Torsten Wiesel began publishing in 1959 and through 1962. The chapter should flag the resonance without claiming a settled influence direction; Rosenblatt's program ran in parallel with, not downstream of, the early Hubel-Wiesel papers.
- **Drafting Warning:** Do not say Rosenblatt invented the artificial neuron. Cross-link Ch5 for McCulloch-Pitts and Hebb.

## Scene 3: The Machine the Engineering Team Built

- **Setting:** Mark I Perceptron as a physical cabinet: sensory input, plugboard, association circuitry, potentiometer array, response panel, meters, and a human trainer.
- **Beat:** The machine is trained on visible patterns. When it is wrong, the trainer forces the correct response; the system changes so the next encounter is different. This is the moment where "learning" becomes mechanical action, not a metaphor.
- **Narrative Use:** Make the analog hardware vivid and bounded. The chapter should let the reader feel the gap between a symbolic program manipulating lists and a machine whose memory lives in adjustable electrical settings.
- **Evidence Anchors:** `Smithsonian-MarkI`; `NavyPhoto60`; `POND61`, p. ix; `MarkI-Manual60` pending.
- **Pedagogical Demonstration:** Explain motorized potentiometers as physical weights once the operator manual is extracted. Until then, phrase the 400-photocell/motor-potentiometer detail with source caution in notes.
- **Engineering-Team Beat:** Name the people who built and operated the machine. `POND61` p. ix credits Charles Wightman and Francis Martin with the engineering work and John Hay with the experimental program. `MarkI-Manual60` adds Albert E. Murray as Hay's co-author of the *Mark I Perceptron Operators' Manual (Project PARA)*. This is the chapter's hedge against the lone-genius myth: Mark I is a CAL engineering-culture object, not a Rosenblatt sketch made physical. The 1971 boating death of Rosenblatt has the historiographic side-effect that Wightman and the engineering team became the program's continuity in projects like Tobermory; record their agency early enough that the reader understands that.
- **Drafting Warning:** Do not overclaim what Mark I recognized. It learned restricted pattern tasks, not open-world vision. A second drafting risk lives here: the "over-curated demo" question. Some of the reported successes may have been highly curated closed-world demos selected to support the public release. The chapter should keep enough humility about the public-demonstration record to honor that conflict without taking the over-curation claim as proven.

## Scene 4: The Theorem Under the Hype

- **Setting:** The mathematical chapters of *Principles of Neurodynamics*: solutions, separability, convergence, discrimination, detection, and generalization.
- **Beat:** Rosenblatt's serious claim is not "the machine is conscious." It is narrower and stronger: under stated conditions, a perceptron can learn a classification solution. The convergence theorem is the chapter's mathematical spine.
- **Narrative Use:** Use this scene to rescue Rosenblatt from both hype and dismissal. The theorem is real, but bounded. The limits are part of the science, not evidence that the program was fake.
- **Evidence Anchors:** `POND61`, pp. 97-117; `POND61`, pp. 153-193; `POND61`, p. 189 organized-environment limitation passage; `TwoTheorems59` and `MTP59-NPL` pending; `Block62-RMP` and `Novikoff62` pending.
- **Independent-Legitimacy Beat:** Anchor the program's mathematical seriousness in 1962 sources that are not Rosenblatt's own voice. H. D. Block's "The Perceptron: A Model for Brain Functioning" in *Reviews of Modern Physics* (1962) is a careful exposition by an outside reviewer; A. B. J. Novikoff's "On Convergence Proofs on Perceptrons" in the 1962 *Symposium on the Mathematical Theory of Automata* tightened the convergence theorem under a cleaner assumption set. Together they place perceptron mathematics inside a recognized 1962 scientific record, not a Navy-press one.
- **Pedagogical Demonstration:** Teach linear separability without heavy equations: some classifications have a boundary the system can find; others do not. Then forward-link Ch15: later readers will recognize the learning rule as kin to stochastic gradient descent.
- **Drafting Warning:** Do not use the word "XOR" as the scene's center. That belongs to Ch17 unless used only as a one-sentence forward-link.

## Scene 5: The 1958 Collision, the Cybernetic Family, and the Historiographic Fade

- **Setting:** Three concentric framings closing the chapter — the November 1958 NPL *Mechanisation of Thought Processes* symposium at Teddington; the 1958 Navy/press announcement and Rosenblatt's 1961 preface looking back at the controversy; the post-1969/post-1971 historiographic settlement.
- **Beat — The 1958 Collision:** The HMSO *Mechanisation of Thought Processes* proceedings volume contains Rosenblatt's "Two Theorems of Statistical Separability in the Perceptron," Oliver Selfridge's "Pandemonium: A Paradigm for Learning," and John McCarthy's "Programs with Common Sense" within a single 1958 NPL symposium. This is the documented historical moment when cybernetic learning and symbolic reasoning were placed side by side on a single program. It is the chapter's strongest evidence that the "rivalry" was not a retrospective reconstruction.
- **Beat — Press and Rosenblatt's Pushback:** Public rhetoric made the perceptron sound like an embryo of a full artificial mind. Rosenblatt later complained that the press handled the announcement with destructive exuberance and emphasized that his research was a brain-modeling program. Use `POND61` pp. vii-viii to anchor his own pushback.
- **Beat — The Cybernetic Family:** The perceptron was not an isolated Buffalo project. Bernard Widrow and Marcian E. (Ted) Hoff at Stanford built the contemporaneous ADALINE/MADALINE analog-hardware learning system in 1960 (`WidrowHoff60`). Selfridge's Pandemonium (1959) is a cybernetic cousin in the same NPL volume. Wightman's Tobermory project at CAL extended Mark I's pattern logic into auditory perception after 1960. This shows the chapter that "learning machines" were a 1958-1962 movement, not a single-lab anomaly.
- **Beat — Historiographic Fade:** Rosenblatt died in a sailing accident on Chesapeake Bay on 11 July 1971, two years after the Minsky-Papert *Perceptrons* book. The connectionist counter-narrative did not have its primary defender available in print between 1971 and the late-1970s revival. This is a load-bearing historiographic note for why the post-1969 narrative was settled the way it was, without importing Ch17's content. Treat the precise date and birthday-coincidence framing as Yellow until `Rosenblatt71` is page-anchored.
- **Narrative Use:** The close separates rhetoric from capability, places Rosenblatt inside a documented 1958 collision and a recognizable cybernetic-hardware family, and explains why the historiographic record was not contested in real time after the late 1960s. The perceptron was not a failed symbolic machine. It was a live alternative research program inside a cybernetic-learning movement that was muted by its primary defender's death and only fully recovered in the 1980s.
- **Evidence Anchors:** `MTP59-NPL` (proceedings of the 1958 NPL symposium, including `TwoTheorems59`); `NYT58` Yellow with attribution-direction Red; `NavyPhoto60`; `POND61`, pp. vii-viii; `Olazaran96` pending; `WidrowHoff60` pending; `Tobermory62-65` pending; institutional records of Rosenblatt's 1971 death.
- **Pedagogical Demonstration:** Show three columns in prose: "what the theorem supports," "what Mark I physically did," and "what the press imagined." This gives the reader an anti-myth tool.
- **Drafting Warning:** The 1969 Minsky-Papert story gets one forward-link only. Ch17 owns the fall. Do not turn the 1971 death into a melodramatic close — it is one paragraph of historiographic context, not a tragic coda.

## Optional Insert: The IBM 704 Shadow Machine

- **Setting:** The simulation layer at Cornell and NYU.
- **Beat:** Before and alongside Mark I, Rosenblatt's group used digital computers to simulate perceptual learning and classification. This means the perceptron program was simultaneously hardware, software, and theory.
- **Narrative Use:** Insert between Scenes 3 and 4 if the chapter needs a bridge from electromechanical hardware to mathematics.
- **Evidence Anchors:** `IRE60` abstract; `POND61`, p. ix and later experiment passage naming Burroughs 220 and IBM 704.
- **Drafting Warning:** Do not let this turn Mark I into a digital algorithm. It is a simulation layer, not a replacement for the hardware story.

## Anti-Padding Rule

If the final prose needs more length, expand only verified layers: the 1958 problem statement, the CAL/ONR setting, S/A/R unit architecture, Mark I's training workflow, IBM 704 simulations as supplementary work, the convergence/separability explanation, the 1958 NPL symposium collision, the Block 1962 / Novikoff 1962 mathematical legitimacy, the Widrow-Hoff ADALINE parallel, and Rosenblatt's own press-boundary comments. Do not add invented demonstrations, imagined Navy dialogue, hostile Minsky scenes, unverified rivalry drama, melodramatic 1971-death codas, or the Ch17 demolition.
