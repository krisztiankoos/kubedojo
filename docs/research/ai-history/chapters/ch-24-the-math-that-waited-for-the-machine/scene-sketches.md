# Scene Sketches: Chapter 24 - The Math That Waited for the Machine

## Scene 1: The Frozen Hidden Layer

- **Setting:** The connectionist aftermath of the perceptron critique.
- **Beat:** A single-layer perceptron can be corrected when the output is wrong, but a hidden unit has no obvious teacher. The chapter should make this tangible: the machine fails, but the blame is distributed through invisible internal connections.
- **Evidence Needed:** Minsky/Papert source from Ch17 plus Rumelhart/Hinton/Williams 1986 contrast with perceptron-convergence learning.

## Scene 2: The Chain Rule Becomes Machinery

- **Setting:** A network as a ledger of intermediate numbers.
- **Beat:** Backpropagation is not magic. It is the chain rule turned into a repeatable accounting process: compute activations forward, cache them, compute sensitivities backward, update weights.
- **Pedagogical Demonstration:** Use a three-layer toy example with one input, one hidden unit, one output. Do not include equations unless the prose first explains what each quantity is doing.
- **Evidence Needed:** PDP chapter page anchors; Nielsen as teaching support only.

## Scene 3: The PDP Demonstration

- **Setting:** Mid-1980s connectionist research, where cognitive scientists are trying to recover learning from hand-coded symbolic systems.
- **Beat:** The Nature paper's dramatic claim is that hidden units learn internal features. This makes the network more than a curve-fitting shell: it can discover representations useful for a task.
- **Evidence Needed:** Nature abstract and examples; PDP chapter examples.

## Scene 4: The Algorithm Waiting for Machines

- **Setting:** Small simulations, not modern datacenters.
- **Beat:** Backpropagation wins historically because it has the right infrastructural shape. It is a procedure machines can repeat millions of times: multiply, sum, store activations, reuse derivatives, adjust weights.
- **Evidence Needed:** exact experiment scale from primary sources; later LeCun 1998 for why practical backprop still needed engineering tricks.

## Scene 5: The Honest Attribution

- **Setting:** A short narrative pause before the chapter moves toward the next chapter's theorem.
- **Beat:** Say plainly that 1986 was not the birth of the chain rule or even every form of backpropagation. It was the moment a dormant mathematical technique became a persuasive research program for learned representations.
- **Evidence Needed:** Werbos thesis, Linnainmaa source, and a secondary history.
