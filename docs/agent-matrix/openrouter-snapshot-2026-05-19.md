# OpenRouter Model Catalog Snapshot — 2026-05-19

**Source**: `https://openrouter.ai/api/v1/models` (no auth needed for the list).
**Catalog size at fetch**: 356 models. **This file**: filtered to families relevant to the KubeDojo agent matrix.

## ⚠ Prices are point-in-time

These numbers are correct as of 2026-05-19. **Re-snapshot before any routing or budget decision** — OpenRouter pricing changes without notice as upstream providers shift rates and new variants land. To refresh, see the *Refresh procedure* at the bottom of this file.

## Why filter at all

OpenRouter offers ~356 models. KubeDojo only routes opens-source / non-Western families through OpenRouter (Western families — Claude, GPT, Gemini — go via subscription per `reference_provider_routing_economics`). Excluding Western models from this snapshot drops ~half the catalog and surfaces the *actually-decision-relevant* rows.

## Currency / unit

All prices are USD per **1 million tokens**, computed from OpenRouter's per-token `pricing.prompt` / `pricing.completion` fields × 1e6.

`Ctx` is the OpenRouter-reported `context_length`.

---

## Tables

### Qwen 3.6 family (research / open generation)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `qwen/qwen3.6-35b-a3b` | 262,144 | 0.15 | 1.00 |
| `qwen/qwen3.6-flash` | 1,000,000 | 0.19 | 1.12 |
| `qwen/qwen3.6-plus` | 1,000,000 | 0.33 | 1.95 |
| `qwen/qwen3.6-27b` | 262,144 | 0.32 | 3.20 |
| `qwen/qwen3.6-max-preview` | 262,144 | 1.04 | 6.24 |

### Qwen commercial line (older arch, NOT 3.6 generation — naming collision risk)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `qwen/qwen-plus-2025-07-28:thinking` | 1,000,000 | 0.26 | 0.78 |
| `qwen/qwen-plus-2025-07-28` | 1,000,000 | 0.26 | 0.78 |
| `qwen/qwen-plus` | 1,000,000 | 0.26 | 0.78 |

### Qwen 3.5 and other Qwen

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `qwen/qwen3-235b-a22b-2507` | 262,144 | 0.07 | 0.10 |
| `qwen/qwen-2.5-7b-instruct` | 131,072 | 0.04 | 0.10 |
| `qwen/qwen3.5-9b` | 262,144 | 0.04 | 0.15 |
| `qwen/qwen3-14b` | 131,702 | 0.10 | 0.24 |
| `qwen/qwen3.5-flash-02-23` | 1,000,000 | 0.07 | 0.26 |
| `qwen/qwen3-32b` | 131,072 | 0.08 | 0.28 |
| `deepseek/deepseek-r1-distill-qwen-32b` | 128,000 | 0.29 | 0.29 |
| `qwen/qwen3-30b-a3b-instruct-2507` | 262,144 | 0.09 | 0.30 |
| `qwen/qwen3-30b-a3b-thinking-2507` | 131,072 | 0.08 | 0.40 |
| `qwen/qwen3-8b` | 131,072 | 0.05 | 0.40 |
| `qwen/qwen-2.5-72b-instruct` | 131,072 | 0.36 | 0.40 |
| `qwen/qwen3-30b-a3b` | 131,072 | 0.09 | 0.45 |
| `qwen/qwen3-next-80b-a3b-thinking` | 262,144 | 0.10 | 0.78 |
| `qwen/qwen3.5-35b-a3b` | 262,144 | 0.14 | 1.00 |
| `qwen/qwen-2.5-coder-32b-instruct` | 128,000 | 0.66 | 1.00 |
| `qwen/qwen3-next-80b-a3b-instruct` | 262,144 | 0.09 | 1.10 |
| `qwen/qwen3-235b-a22b-thinking-2507` | 262,144 | 0.15 | 1.50 |
| `qwen/qwen3.5-27b` | 262,144 | 0.20 | 1.56 |
| `qwen/qwen3.5-plus-02-15` | 1,000,000 | 0.26 | 1.56 |
| `qwen/qwen3.5-plus-20260420` | 1,000,000 | 0.30 | 1.80 |
| `qwen/qwen3-235b-a22b` | 131,072 | 0.45 | 1.82 |
| `qwen/qwen3.5-122b-a10b` | 262,144 | 0.26 | 2.08 |
| `qwen/qwen3.5-397b-a17b` | 262,144 | 0.39 | 2.34 |
| `qwen/qwen3-max-thinking` | 262,144 | 0.78 | 3.90 |
| `qwen/qwen3-max` | 262,144 | 0.78 | 3.90 |

### Qwen coder variants

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `qwen/qwen3-coder-30b-a3b-instruct` | 160,000 | 0.07 | 0.27 |
| `qwen/qwen3-coder-next` | 262,144 | 0.11 | 0.80 |
| `qwen/qwen3-coder-flash` | 1,000,000 | 0.20 | 0.97 |
| `qwen/qwen3-coder` | 1,048,576 | 0.22 | 1.80 |
| `qwen/qwen3-coder-plus` | 1,000,000 | 0.65 | 3.25 |

### Qwen VL (vision)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `qwen/qwen3-vl-32b-instruct` | 262,144 | 0.10 | 0.42 |
| `qwen/qwen3-vl-8b-instruct` | 256,000 | 0.08 | 0.50 |
| `qwen/qwen3-vl-30b-a3b-instruct` | 262,144 | 0.13 | 0.52 |
| `qwen/qwen2.5-vl-72b-instruct` | 131,072 | 0.25 | 0.75 |
| `qwen/qwen3-vl-235b-a22b-instruct` | 262,144 | 0.20 | 0.88 |
| `qwen/qwen3-vl-8b-thinking` | 256,000 | 0.12 | 1.36 |
| `qwen/qwen3-vl-30b-a3b-thinking` | 131,072 | 0.13 | 1.56 |
| `qwen/qwen3-vl-235b-a22b-thinking` | 131,072 | 0.26 | 2.60 |

### DeepSeek (via OpenRouter — compare to hermes-native pricing)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `deepseek/deepseek-v4-flash` | 1,048,576 | 0.11 | 0.22 |
| `deepseek/deepseek-v3.2` | 131,072 | 0.25 | 0.38 |
| `deepseek/deepseek-v3.2-exp` | 163,840 | 0.27 | 0.41 |
| `deepseek/deepseek-v3.2-speciale` | 163,840 | 0.29 | 0.43 |
| `nex-agi/deepseek-v3.1-nex-n1` | 131,072 | 0.14 | 0.50 |
| `deepseek/deepseek-chat-v3-0324` | 163,840 | 0.20 | 0.77 |
| `deepseek/deepseek-chat-v3.1` | 163,840 | 0.21 | 0.79 |
| `deepseek/deepseek-r1-distill-llama-70b` | 131,072 | 0.70 | 0.80 |
| `deepseek/deepseek-v4-pro` | 1,048,576 | 0.43 | 0.87 |
| `deepseek/deepseek-chat` | 163,840 | 0.32 | 0.89 |
| `deepseek/deepseek-v3.1-terminus` | 163,840 | 0.27 | 0.95 |
| `deepseek/deepseek-r1-0528` | 163,840 | 0.50 | 2.15 |
| `deepseek/deepseek-r1` | 163,840 | 0.70 | 2.50 |

### Kimi (Moonshot AI)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `moonshotai/kimi-k2.5` | 262,144 | 0.40 | 1.90 |
| `moonshotai/kimi-k2` | 131,072 | 0.57 | 2.30 |
| `moonshotai/kimi-k2-thinking` | 262,144 | 0.60 | 2.50 |
| `moonshotai/kimi-k2-0905` | 262,144 | 0.60 | 2.50 |
| `~moonshotai/kimi-latest` | 262,144 | 0.73 | 3.49 |
| `moonshotai/kimi-k2.6` | 262,144 | 0.73 | 3.49 |

### Z-AI / GLM (Zhipu)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `z-ai/glm-4-32b` | 128,000 | 0.10 | 0.10 |
| `z-ai/glm-4.7-flash` | 202,752 | 0.06 | 0.40 |
| `z-ai/glm-4.5-air` | 131,072 | 0.13 | 0.85 |
| `z-ai/glm-4.6v` | 131,072 | 0.30 | 0.90 |
| `z-ai/glm-4.6` | 202,752 | 0.43 | 1.74 |
| `z-ai/glm-4.7` | 202,752 | 0.40 | 1.75 |
| `z-ai/glm-4.5v` | 65,536 | 0.60 | 1.80 |
| `z-ai/glm-5` | 202,752 | 0.60 | 1.92 |
| `z-ai/glm-4.5` | 131,072 | 0.60 | 2.20 |
| `z-ai/glm-5.1` | 202,752 | 0.98 | 3.08 |
| `z-ai/glm-5v-turbo` | 202,752 | 1.20 | 4.00 |
| `z-ai/glm-5-turbo` | 202,752 | 1.20 | 4.00 |

### MiniMax

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `minimax/minimax-m2.1` | 204,800 | 0.29 | 0.95 |
| `minimax/minimax-m2` | 204,800 | 0.26 | 1.00 |
| `minimax/minimax-01` | 1,000,192 | 0.20 | 1.10 |
| `minimax/minimax-m2.5` | 204,800 | 0.15 | 1.15 |
| `minimax/minimax-m2.7` | 204,800 | 0.28 | 1.20 |
| `minimax/minimax-m2-her` | 65,536 | 0.30 | 1.20 |
| `minimax/minimax-m1` | 1,000,000 | 0.40 | 2.20 |

### NVIDIA Nemotron

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `nvidia/nemotron-nano-9b-v2` | 131,072 | 0.04 | 0.16 |
| `nvidia/nemotron-3-nano-30b-a3b` | 262,144 | 0.05 | 0.20 |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | 131,072 | 0.10 | 0.40 |
| `nvidia/nemotron-3-super-120b-a12b` | 1,000,000 | 0.09 | 0.45 |

### Mistral / Cohere / Other

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `mistralai/mistral-nemo` | 131,072 | 0.02 | 0.03 |
| `mistralai/mistral-small-24b-instruct-2501` | 32,768 | 0.05 | 0.08 |
| `mistralai/ministral-3b-2512` | 131,072 | 0.10 | 0.10 |
| `mistralai/ministral-8b-2512` | 262,144 | 0.15 | 0.15 |
| `cohere/command-r7b-12-2024` | 128,000 | 0.04 | 0.15 |
| `mistralai/mistral-7b-instruct-v0.1` | 4,096 | 0.11 | 0.19 |
| `mistralai/ministral-14b-2512` | 262,144 | 0.20 | 0.20 |
| `mistralai/mistral-small-3.2-24b-instruct` | 128,000 | 0.07 | 0.20 |
| `mistralai/voxtral-small-24b-2507` | 32,000 | 0.10 | 0.30 |
| `mistralai/devstral-small` | 131,072 | 0.10 | 0.30 |
| `alibaba/tongyi-deepresearch-30b-a3b` | 131,072 | 0.09 | 0.45 |
| `mistralai/mistral-small-3.1-24b-instruct` | 128,000 | 0.35 | 0.55 |
| `mistralai/mistral-small-2603` | 262,144 | 0.15 | 0.60 |
| `mistralai/mistral-saba` | 32,768 | 0.20 | 0.60 |
| `cohere/command-r-08-2024` | 128,000 | 0.15 | 0.60 |
| `mistralai/codestral-2508` | 256,000 | 0.30 | 0.90 |
| `mistralai/mistral-large-2512` | 262,144 | 0.50 | 1.50 |
| `mistralai/devstral-2512` | 262,144 | 0.40 | 2.00 |
| `mistralai/mistral-medium-3.1` | 131,072 | 0.40 | 2.00 |
| `mistralai/devstral-medium` | 131,072 | 0.40 | 2.00 |
| `mistralai/mistral-medium-3` | 131,072 | 0.40 | 2.00 |
| `mistralai/mistral-large-2411` | 131,072 | 2.00 | 6.00 |
| `mistralai/mistral-large-2407` | 131,072 | 2.00 | 6.00 |
| `mistralai/pixtral-large-2411` | 131,072 | 2.00 | 6.00 |
| `mistralai/mixtral-8x22b-instruct` | 65,536 | 2.00 | 6.00 |
| `mistralai/mistral-large` | 128,000 | 2.00 | 6.00 |
| `mistralai/mistral-medium-3-5` | 262,144 | 1.50 | 7.50 |
| `cohere/command-a` | 256,000 | 2.50 | 10.00 |
| `cohere/command-r-plus-08-2024` | 128,000 | 2.50 | 10.00 |

### Free tiers (rate-limited, NOT for production calibration)

| Model | Ctx | $in/M | $out/M |
|---|---:|---:|---:|
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 256,000 | 0.00 | 0.00 |
| `deepseek/deepseek-v4-flash:free` | 1,048,576 | 0.00 | 0.00 |
| `nvidia/nemotron-3-super-120b-a12b:free` | 1,000,000 | 0.00 | 0.00 |
| `minimax/minimax-m2.5:free` | 204,800 | 0.00 | 0.00 |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256,000 | 0.00 | 0.00 |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128,000 | 0.00 | 0.00 |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262,144 | 0.00 | 0.00 |
| `nvidia/nemotron-nano-9b-v2:free` | 128,000 | 0.00 | 0.00 |
| `z-ai/glm-4.5-air:free` | 131,072 | 0.00 | 0.00 |
| `qwen/qwen3-coder:free` | 1,048,576 | 0.00 | 0.00 |
| `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 32,768 | 0.00 | 0.00 |

---

## Naming-collision warning

**Qwen has two product lines that both use "Plus / Max" suffixes.** Don't conflate them:

- **Qwen 3.6 generation** (research-style / open arch): `qwen3.6-35b-a3b`, `qwen3.6-flash`, `qwen3.6-plus`, `qwen3.6-27b`, `qwen3.6-max-preview`.
- **Qwen commercial line** (Alibaba's hosted production models, older arch): `qwen-plus`, `qwen-plus-2025-07-28`, `qwen-turbo`, `qwen-max` (when present), etc.

Commercial `qwen-plus` is *cheaper on output* than `qwen3.6-plus` ($0.78 vs $1.95) but uses older architecture. Whether 3.6-plus's quality justifies 2.5× cost is the empirical question of any calibration round.

Likely similar naming pitfalls exist for other vendors as new generations land — treat the prefix string as opaque; verify against vendor docs when picking.

---

## Calibration test set proposed for review-lane (2026-05-19)

Subject to user green-light. Ground truth: codex `gpt-5.5` APPROVE verdict on PR #1333 round-2 (after the round-1 NEEDS_CHANGES at SHA `6f541af2` with three findings).

| # | Model | $in/M | $out/M | Hypothesis |
|---|---|---:|---:|---|
| 1 | `qwen/qwen3.6-35b-a3b` | 0.15 | 1.00 | The base 3.6 — cheapest, the floor of the "qwen3.6 reviewer" claim |
| 2 | `qwen/qwen3.6-plus` | 0.33 | 1.95 | Mid-tier 3.6; tests whether the quality jump over base is worth ~2× output cost |
| 3 | `qwen/qwen-plus-2025-07-28` | 0.26 | 0.78 | Commercial-line **outside** the 3.6 generation; tests whether 3.6 actually beats the older commercial line |
| 4 | `moonshotai/kimi-k2.6` | 0.73 | 3.49 | Different vendor, long-context reputation; one outsider data point so we're not all-in on qwen |

**Explicitly NOT in this round** (and why):
- `qwen3.6-max-preview` — too expensive per user 2026-05-19.
- `qwen3.6-27b` — dense 27B is *more* expensive than the 35B-MoE base; skip.
- All `:free` tiers — rate-limited, not honest cost comparison.
- `deepseek/*` — covered by a separate calibration goal (hermes-native vs OpenRouter cost compare), not the review-lane question.
- Coder variants — `qwen3-coder-*` is for `edit`/`draft` task class, not review.
- Vision (VL) — out of scope for review task class.

**Per-PR cost ceiling for this test set**: PR #1333 round-1 codex review was ~370s wall and ~1972 chars output. Open-model dispatches are usually shorter latency but more verbose. Worst case: 4 models × ~4k output tokens × $3.49/M (most expensive = kimi-k2.6) ≈ $0.06. Single-PR calibration is negligible cost.

---

## Refresh procedure

```bash
# 1. Fetch raw catalog
curl -s "https://openrouter.ai/api/v1/models" -o /tmp/openrouter-models.json

# 2. Eyeball total count
python3 -c "import json; print(len(json.load(open('/tmp/openrouter-models.json'))['data']))"

# 3. Spot-check a specific family
python3 <<'EOF'
import json
data = json.load(open("/tmp/openrouter-models.json"))
target = "qwen3.6"  # change as needed
for m in data["data"]:
    if target in m["id"].lower():
        p = m.get("pricing", {}) or {}
        pin = float(p.get("prompt") or 0) * 1e6
        pout = float(p.get("completion") or 0) * 1e6
        print(f"{m['id']:<50} ${pin:.2f}/M in   ${pout:.2f}/M out   ctx={m.get('context_length'):,}")
EOF
```

When prices have meaningfully moved (>10% on any model we route to, or a new model variant appears that displaces a calibrated winner), generate a new dated snapshot in this folder rather than editing this one. Snapshots are immutable.
