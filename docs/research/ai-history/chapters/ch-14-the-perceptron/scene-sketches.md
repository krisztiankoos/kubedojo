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
- **Evidence Anchors:** `PsychRev58`, p. 386; `POND61`, pp. 79-92; `Smithsonian-MarkI` S/A/R object-record description.
- **Pedagogical Demonstration:** Use a small diagram-in-words: a sensory pattern activates S-units; selected signals move through A-units; R-units compete or fire; reinforcement changes later behavior. Avoid modern code.
- **Drafting Warning:** Do not say Rosenblatt invented the artificial neuron. Cross-link Ch5 for McCulloch-Pitts and Hebb.

## Scene 3: The Machine Learns by Moving Weights

- **Setting:** Mark I Perceptron as a physical cabinet: sensory input, plugboard, association circuitry, potentiometer array, response panel, meters, and a human trainer.
- **Beat:** The machine is trained on visible patterns. When it is wrong, the trainer forces the correct response; the system changes so the next encounter is different. This is the moment where "learning" becomes mechanical action, not a metaphor.
- **Narrative Use:** Make the analog hardware vivid and bounded. The chapter should let the reader feel the gap between a symbolic program manipulating lists and a machine whose memory lives in adjustable electrical settings.
- **Evidence Anchors:** `Smithsonian-MarkI`; `NavyPhoto60`; `POND61`, p. ix; `MarkI-Manual60` pending.
- **Pedagogical Demonstration:** Explain motorized potentiometers as physical weights once the operator manual is extracted. Until then, phrase the 400-photocell/motor-potentiometer detail with source caution in notes.
- **Drafting Warning:** Do not overclaim what Mark I recognized. It learned restricted pattern tasks, not open-world vision.

## Scene 4: The Theorem Under the Hype

- **Setting:** The mathematical chapters of *Principles of Neurodynamics*: solutions, separability, convergence, discrimination, detection, and generalization.
- **Beat:** Rosenblatt's serious claim is not "the machine is conscious." It is narrower and stronger: under stated conditions, a perceptron can learn a classification solution. The convergence theorem is the chapter's mathematical spine.
- **Narrative Use:** Use this scene to rescue Rosenblatt from both hype and dismissal. The theorem is real, but bounded. The limits are part of the science, not evidence that the program was fake.
- **Evidence Anchors:** `POND61`, pp. 97-117; `POND61`, pp. 153-193; `POND61`, p. 189 organized-environment limitation passage; `TwoTheorems59` pending.
- **Pedagogical Demonstration:** Teach linear separability without heavy equations: some classifications have a boundary the system can find; others do not. Then forward-link Ch15: later readers will recognize the learning rule as kin to stochastic gradient descent.
- **Drafting Warning:** Do not use the word "XOR" as the scene's center. That belongs to Ch17 unless used only as a one-sentence forward-link.

## Scene 5: Press, Controversy, and the Cybernetic Alternative

- **Setting:** The 1958 Navy/press announcement and Rosenblatt's 1961 preface looking back at the controversy.
- **Beat:** Public rhetoric made the perceptron sound like an embryo of a full artificial mind. Rosenblatt later complained that the press handled the announcement with destructive exuberance and emphasized that his research was a brain-modeling program.
- **Narrative Use:** The close separates rhetoric from capability, then returns to the chapter's axis: adaptive cybernetic learning versus symbolic AI. The perceptron was not a failed symbolic machine. It was a live alternative research program.
- **Evidence Anchors:** `NYT58` Yellow; `NavyPhoto60`; `POND61`, pp. vii-viii; `Olazaran96` pending.
- **Pedagogical Demonstration:** Show three columns in prose: "what the theorem supports," "what Mark I physically did," and "what the press imagined." This gives the reader an anti-myth tool.
- **Drafting Warning:** The 1969 Minsky-Papert story gets one forward-link only. Ch17 owns the fall.

## Optional Insert: The IBM 704 Shadow Machine

- **Setting:** The simulation layer at Cornell and NYU.
- **Beat:** Before and alongside Mark I, Rosenblatt's group used digital computers to simulate perceptual learning and classification. This means the perceptron program was simultaneously hardware, software, and theory.
- **Narrative Use:** Insert between Scenes 3 and 4 if the chapter needs a bridge from electromechanical hardware to mathematics.
- **Evidence Anchors:** `IRE60` abstract; `POND61`, p. ix and later experiment passage naming Burroughs 220 and IBM 704.
- **Drafting Warning:** Do not let this turn Mark I into a digital algorithm. It is a simulation layer, not a replacement for the hardware story.

## Anti-Padding Rule

If the final prose needs more length, expand only verified layers: the 1958 problem statement, the CAL/ONR setting, S/A/R unit architecture, Mark I's training workflow, IBM 704 simulations, the convergence/separability explanation, and Rosenblatt's own press-boundary comments. Do not add invented demonstrations, imagined Navy dialogue, hostile Minsky scenes, unverified rivalry drama, or the Ch17 demolition.
