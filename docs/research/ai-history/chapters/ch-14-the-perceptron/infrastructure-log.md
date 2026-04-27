# Infrastructure Log: Chapter 14 - The Perceptron

## Infrastructure Thesis

The Perceptron story is infrastructure before it is mythology. Rosenblatt's program required an unusual bundle: a cybernetic theory of adaptive networks, Navy funding, Cornell Aeronautical Laboratory engineering, digital simulation time, and a physical electromechanical Mark I machine. The chapter should make readers see that the "learning machine" was not a metaphor. It moved through circuits, plugs, response panels, and adjustable analog weights.

## Cornell Aeronautical Laboratory, Buffalo

- **Verified setting:** `PsychRev58` p. 386 identifies Cornell Aeronautical Laboratory. `POND61` front matter gives Cornell Aeronautical Laboratory, Buffalo, New York. `Smithsonian-MarkI` records the machine as made at Cornell Aeronautical Laboratory in Buffalo.
- **Narrative function:** CAL is the chapter's first room. It locates Rosenblatt outside the Dartmouth/MIT symbolic-AI corridor and inside a defense-funded cybernetic engineering environment.
- **Boundary:** Do not relocate Mark I to Ithaca or MIT. Ithaca appears as Cornell University program support and computing context; Mark I is a CAL/Buffalo hardware story.

## Funding and Contracts

- **ONR:** `PsychRev58` p. 386 lists Office of Naval Research sponsorship under Contract Nonr-2381(00). `POND61` p. ix says the Information Systems Branch of ONR supported the Buffalo program from July 1957 and the Ithaca program from September 1959.
- **Rome Air Development Center:** `POND61` p. ix says RADC assisted the development of Mark I. `Smithsonian-MarkI` and `NavyPhoto60` also name RADC with ONR.
- **AEC / NYU computing:** `POND61` p. ix thanks the Atomic Energy Commission for NYU computing-center facilities. The later `POND61` experiment text says work used the Burroughs 220 at Cornell University and the IBM 704 at the AEC Applied Mathematics Center at NYU.
- **Ch16 handoff:** This chapter should point forward to Ch16 for the broader "Cold War Blank Check" funding pattern. Here, the funding story is restricted to why the perceptron could become hardware and large-scale simulation, not to a general defense-policy essay.

## Mark I Perceptron Hardware

### Green Anchors

- `Smithsonian-MarkI` describes Mark I as made in 1958, created at CAL in Buffalo with ONR/RADC funding, and arranged in S, A, and R units.
- `Smithsonian-MarkI` describes the cabinet layout: sensory unit, plugboard, potentiometer array, response panel, and meters.
- `NavyPhoto60` describes Mark I as an electromechanical device for identifying objects or patterns such as alphabet letters, trained by placing test patterns in the photoelectric cell "eye" and forcing correct response after errors.
- `POND61` p. ix credits Wightman and Martin with engineering work on Mark I and John Hay with the experimental program.

### Yellow Details Pending Operator Manual Extraction

- The 20x20 / 400-photocell input array.
- Motorized potentiometers as physical adjustable weights.
- Exact A-unit and R-unit counts in a particular Mark I configuration.
- Plugboard wiring and whether the relevant sensory-to-association connections were fixed, random, or experiment-configurable in a given run.
- Exact operator controls for forced correction and response display.

### Drafting Rule

Use the 400-photocell and motorized-potentiometer details because the task boundary requires them, but mark them in source notes as Yellow until `MarkI-Manual60` pages are extracted. Do not present those two details as Green page-anchored claims in prose review until the operator manual is verified directly.

## Digital Simulation Infrastructure

- **IBM 704:** `IRE60` abstract says Rosenblatt's simulation program used the IBM 704 to simulate perceptual learning, recognition, and classification of visual stimuli.
- **Burroughs 220:** `POND61` later experiment text identifies Burroughs 220 at Cornell University for some experiments.
- **NYU / AEC Applied Mathematics Center:** `POND61` identifies the IBM 704 at NYU's AEC Applied Mathematics Center.
- **Narrative function:** This prevents a false either/or. The perceptron was not "only hardware" and not "only software." The theory moved between mathematical proof, digital simulation, and electromechanical demonstration.
- **Supplementary-not-primary guardrail:** The simulations are explicitly *supplementary* to Mark I, not its substitute. The chapter must not say "the perceptron was a program running on the IBM 704" or describe the simulation work as Mark I's primary instantiation. If the simulation paragraph reads as if it could replace the hardware story, rewrite it. The simulations accelerated experimental iteration; Mark I is the chapter's primary engineering object.

## Stanford Cybernetic-Hardware Contemporary

- **ADALINE / MADALINE (Widrow-Hoff, 1960):** Bernard Widrow and Marcian E. Hoff at Stanford Electrical Engineering built ADALINE (Adaptive Linear Neuron) and MADALINE (Many ADALINEs) as a contemporaneous analog-hardware learning system using least-mean-squares weight adjustment (`WidrowHoff60`).
- **Narrative function:** Mark I was not an isolated Buffalo quirk; it was part of a broader 1960 cybernetic-hardware movement that included Stanford. The chapter should anchor this in one paragraph in Scene 5 without expanding into a parallel ADALINE history.
- **Boundary:** This is a parallel, not a rivalry. Do not stage ADALINE as a competitor to Mark I; both programs existed inside the same cybernetic-learning lineage and shared funding patterns through Navy/ONR-adjacent channels.

## Tobermory Continuity Project

- **Setting:** Cornell Aeronautical Laboratory, after the 1960 Mark I demonstration.
- **Verified anchors:** `Tobermory62-65` worklist; secondary references and Cornell records.
- **Narrative function:** Wightman's Tobermory project extended Mark I's pattern-recognition logic into auditory perception, providing program-continuity evidence beyond the 1960 demonstration. Use as a brief Scene-5 beat to show the perceptron line did not stop with Mark I.
- **Boundary:** Do not turn Tobermory into its own chapter; it is a continuity beat that prepares the reader for the post-1969 historiographic question.

## NPL 1958 Symposium Infrastructure

- **Setting:** National Physical Laboratory, Teddington, UK, 24-27 November 1958.
- **Verified anchors:** `MTP59-NPL` proceedings table of contents; Rosenblatt's "Two Theorems," Selfridge's "Pandemonium," and McCarthy's "Programs with Common Sense" co-presence.
- **Narrative function:** This is the primary historical infrastructure evidence that the cybernetic-vs-symbolic split was a 1958 documentary fact, not a retrospective reconstruction. The proceedings volume is itself the infrastructure: a single HMSO publication that co-stages all three traditions.
- **Boundary:** Do not turn the symposium into a deep dive on Selfridge or McCarthy; their full scenes belong elsewhere. Use it as the documented stage where the rivalry is visible.

## Unit Architecture

- **S-units:** Sensory units receive stimuli. `Smithsonian-MarkI` gives S-unit functional description; `POND61` table of contents anchors elementary units and signals at pp. 79-83.
- **A-units:** Association units receive and transmit signals among units. `Smithsonian-MarkI` describes their role; `POND61` provides the theoretical vocabulary.
- **R-units:** Response units transmit signals to the outside and display/express recognition behavior. `Smithsonian-MarkI` gives the public object description.
- **Reinforcement systems:** `POND61` table of contents places reinforcement systems at p. 88; `NavyPhoto60` describes forced correction in training.
- **Drafting use:** Explain the architecture as a signal-transmission and reinforcement system, not as a modern multilayer neural-network tutorial.

## Mathematics Infrastructure

- `POND61` table of contents puts the existence and attainability of solutions in elementary perceptrons at pp. 97-117, including the principal convergence theorem.
- `POND61` organizes discrimination experiments, error-correction procedures, detection, and generalization at pp. 153-193.
- `POND61` discusses completely linear perceptrons at p. 245 and onward.
- **Ch15 handoff:** The perceptron learning rule can be made legible later as a stochastic-gradient method on linear classifiers, but that is a retrospective bridge. Ch14 should use Rosenblatt's own language: solutions, separability, reinforcement, convergence, discrimination, detection, and generalization.

## Media and Public Demonstration Infrastructure

- **New York Times:** `NYT58` is the key press article, but original scan is pending. Treat the famous "walk, talk, see, write..." sentence as Yellow.
- **Navy release:** `NavyPhoto60` is a public-domain Navy image record with detailed description and release date. It is useful for public framing and training procedure, but not as rigorous performance validation.
- **Rosenblatt's own pushback:** `POND61` pp. vii-viii says the popular press contributed to controversy and that his program was not primarily about inventing AI devices.
- **Drafting rule:** Put press after hardware and theory. If press comes first, it will distort the chapter.

## Object Afterlife

- `Smithsonian-MarkI` records that Mark I came to the Smithsonian in 1967 from Cornell University as a transfer from ONR.
- **Narrative use:** A short close or caption can note that the physical machine survived as an object, which helps readers remember that this was real hardware.
- **Boundary:** Do not build a museum-afterlife scene unless additional archival material appears.

## Infrastructure Gaps Before Prose

- Extract `MarkI-Manual60` pages for hardware counts, component diagram, potentiometer mechanism, and operator workflow.
- Extract full `IRE60` pages for simulation experiment details.
- Extract original `NYT58` article scan for exact attribution and page.
- Extract `TwoTheorems59` and `VG1196G1` for the theorem lineage before the 1961/1962 consolidation.
