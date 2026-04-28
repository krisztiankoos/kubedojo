# People: Chapter 64 - The Edge Compute Bottleneck

## Research And Product Actors

- **Andrew G. Howard et al. / MobileNets team:** Use for the efficient mobile
  model lineage before LLMs.
- **Apple hardware/software teams:** Use institutionally for A11 Neural Engine,
  Face ID on-device processing, Apple Intelligence, AFM-on-device, and Private
  Cloud Compute. Avoid individual hero framing unless quoting official roles.
- **Google Pixel / Android / Gemini Nano teams:** Use for Gemini Nano, AICore,
  and the explicit statement that on-device models are smaller and less
  generalized than cloud models.
- **Qualcomm Snapdragon team:** Use for phone NPU product framing only. Keep
  token/sec and 10B-parameter claims marked as vendor claims.
- **Keivan Alizadeh et al. / Apple LLM-in-a-flash team:** Use for DRAM/flash
  constraints and model-larger-than-memory inference.
- **Zechun Liu et al. / MobileLLM team:** Use for sub-billion model design aimed
  at common on-device tasks.

## Guardrail

Do not write this as a device-launch recap. The protagonist is the resource
envelope: model size, memory, battery, accelerators, operating-system model
services, and cloud fallback.
