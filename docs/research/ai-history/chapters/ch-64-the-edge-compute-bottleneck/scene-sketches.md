# Scene Sketches: Chapter 64 - The Edge Compute Bottleneck

## Scene 1: The Phone Learns To See

- **Action:** Start before LLMs. MobileNets and the iPhone X Neural Engine show
  the old edge bargain: redesign the model and add dedicated silicon because
  mobile latency, size, heat, and power are not datacenter constraints.
- **Evidence Layer:** MobileNets p.1/pp.2-4; Apple iPhone X lines 162-167.
- **Narrative Job:** Establish that edge AI is a lineage of compromises, not a
  sudden 2024 marketing invention.
- **Guardrail:** Do not imply MobileNets were generative AI.

## Scene 2: Privacy Becomes A Compute Argument

- **Action:** Face ID and Gemini Nano make "where the computation runs" part of
  the user promise. If data stays local, features can work offline and avoid
  some server calls.
- **Evidence Layer:** Apple iPhone X lines 81-83; Google Pixel lines 278-289;
  Android docs lines 394-396.
- **Narrative Job:** Turn privacy from a slogan into an architecture choice:
  local execution changes what data has to move.
- **Guardrail:** Say "can reduce" and "for features that run locally," not
  universal privacy.

## Scene 3: The Small Model Is Not A Toy

- **Action:** Explain Gemini Nano, MobileLLM, Qualcomm's phone NPU framing, and
  Apple AFM-on-device as deliberate small-model engineering. Small does not mean
  unserious; it means the task envelope is narrower.
- **Evidence Layer:** Google Pixel lines 278-289; Android blog lines 38-39;
  Qualcomm brief p.1; MobileLLM p.1; Apple ML lines 17-20.
- **Narrative Job:** Show that the edge pushes model design toward compact,
  specialized, quantized, and task-specific systems.
- **Guardrail:** Qualcomm claims stay Yellow product framing.

## Scene 4: The Bottleneck Is Memory

- **Action:** Move from model size to memory hierarchy. AFM-on-device uses GQA
  and quantization; LLM-in-a-flash shows what happens when the model exceeds
  DRAM and weights must move from slower flash.
- **Evidence Layer:** Apple AFM paper architecture/deployment sections;
  LLM-in-a-flash p.1/pp.2-3.
- **Narrative Job:** Make DRAM, flash bandwidth, KV cache, and quantization as
  visible to the reader as battery and heat.
- **Guardrail:** Do not claim LLM-in-a-flash proves arbitrary frontier models can
  run on phones.

## Scene 5: The Cloud Comes Back

- **Action:** Apple and Google both expose the hybrid truth. Apple routes larger
  requests to Private Cloud Compute; Google's Pixel Video Boost uploads video for
  cloud processing.
- **Evidence Layer:** Apple Newsroom lines 58-60; Google Pixel lines 296-297.
- **Narrative Job:** Show why edge AI does not eliminate datacenters. It creates
  a router between local, private/cloud, and unavailable.
- **Guardrail:** Keep full datacenter and grid consequences for Ch70/72.

## Scene 6: Edge AI Becomes A Design Discipline

- **Action:** Close by naming the discipline: choose local model, local
  accelerator, quantization, memory strategy, app API, cloud fallback, and user
  privacy boundary together.
- **Evidence Layer:** Synthesize from cited sources only.
- **Narrative Job:** Handoff to Ch65 and Ch70/72: open weights matter because
  deployable models matter; datacenters still matter because the edge is bounded.
- **Guardrail:** No unsourced claims about market share or future device specs.
