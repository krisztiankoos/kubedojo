# Infrastructure Log: Chapter 69 - The Data Exhaustion Limit

- **Token accounting:** Ch69 must distinguish dataset size, unique tokens, and
  tokens seen during training. Villalobos lines 120-132 explicitly warn that
  training tokens can exceed dataset size under multi-epoch training.
- **Common Crawl as bounded substrate:** FineWeb and Villalobos both use Common
  Crawl/open web as a large but bounded source. Treat it as infrastructure that
  requires extraction, filtering, deduplication, and licensing/legal context
  from Ch68.
- **Dataset refinery:** FineWeb's contribution is not just a 15T-token dump. It
  documents extraction choices, filtering heuristics, deduplication strategy,
  ablation models, and model-evaluation loops.
- **Repeated-data economics:** Data-constrained scaling says repeated data has
  value for a few epochs and then diminishing returns. This is an engineering
  lever, not a permanent escape from scarcity.
- **Audio/video as convertible data:** Epoch treats images and video as data
  stocks, and Whisper shows internet audio paired with transcripts becoming
  multilingual speech-recognition and translation supervision. Keep this as a
  conversion path, not a claim about any private LLM training run.
- **Synthetic-data factory:** Self-Instruct and phi-1 show two synthetic-data
  styles: instruction/task generation and textbook/exercise generation.
- **Distribution anchor:** Model collapse introduces the requirement for real
  distributional grounding. If synthetic data recursively replaces human data,
  rare tails can disappear.
- **Evaluation freshness:** GPT-4 and LiveBench show benchmark data also needs
  freshness controls. Public tests can become training data; dynamic benchmarks
  are a data pipeline for evaluation, not just a leaderboard.
