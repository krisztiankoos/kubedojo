# Open Questions: Chapter 64 - The Edge Compute Bottleneck

## Resolved For This Contract

- **Is this Apple-only?** No. Apple is central because the roadmap names Neural
  Engine, but Google/Android, Qualcomm, MobileNets, MobileLLM, and LLM-in-flash
  keep the chapter from becoming a single-vendor story.
- **Do we need live TOPS comparisons?** No. Vendor TOPS/token claims age quickly
  and are not directly comparable. Use them only as dated product framing.
- **Should privacy be a legal claim?** No. Treat privacy as an architecture and
  product promise: local processing can reduce server calls and data movement,
  but this chapter is not a compliance audit.
- **Should edge replace cloud in the narrative?** No. Apple PCC and Pixel Video
  Boost show hybrid routing is the honest conclusion.
- **Do we include edge servers/Jetson?** Not in this pass. Ch64 is focused on
  personal devices and phone-class constraints; Ch72 can pick up datacenter/edge
  infrastructure if needed.

## Still Needed Before Prose Drafting

- Claude source-fidelity review of all line/page anchors.
- Gemini gap/capacity audit of the 4,000-5,000 word plan.
- Optional: add an official Apple Neural Engine spec page for a 2024/2025 chip
  only if prose needs a modern NPU comparison. Current contract avoids direct
  cross-generation TOPS comparisons.
