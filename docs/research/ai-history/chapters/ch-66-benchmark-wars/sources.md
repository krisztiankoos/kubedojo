# Sources: Chapter 66 - Benchmark Wars

## Status Legend

- Green: claim has direct primary support from a benchmark paper, technical
  report, or first-party methodology source.
- Yellow: claim is usable only with a caveat: release-report/product framing,
  time-sensitive leaderboard meaning, or synthesis from multiple sources.
- Red: do not draft without new verification.

## Primary Source Spine

| Source | Use In Chapter | Anchor Notes |
|---|---|---|
| Dan Hendrycks et al., "Measuring Massive Multitask Language Understanding," arXiv:2009.03300. PDF: https://arxiv.org/pdf/2009.03300 | MMLU as the frontier scorecard for broad academic/professional knowledge. | Green: PDF downloaded 2026-04-28. Abstract/page 1 says MMLU covers 57 tasks including math, US history, computer science, law, and more; models need broad world knowledge/problem solving; largest GPT-3 reaches 43.9%; and models remain below expert-level accuracy. Body reports 15,908 questions, 5-shot dev set, and expert/human baselines. |
| BIG-bench authors, "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models," arXiv:2206.04615. PDF: https://arxiv.org/pdf/2206.04615 | Broad benchmark expansion; benchmark saturation and short useful lifespan; leakage caveats. | Green: PDF downloaded 2026-04-28. Abstract says BIG-bench has 204 tasks by 450 authors across 132 institutions; covers linguistics, reasoning, math, commonsense, biology, physics, social bias, software development, etc.; human expert raters provide baselines; performance/calibration improve with scale but remain poor. Section 1.2 discusses restricted benchmark scope and short useful lifespans. Section 2 says tasks were contributed openly on GitHub and notes direct leakage impossible for the reported models but indirect leakage possible. |
| Percy Liang et al., "Holistic Evaluation of Language Models," arXiv:2211.09110. PDF: https://arxiv.org/pdf/2211.09110 | HELM as a transparency/multi-metric response to single-score benchmark culture. | Green: PDF downloaded 2026-04-28. Abstract says HELM taxonomizes scenarios/metrics, measures 7 metrics across 16 core scenarios where possible, performs targeted evaluations across 26 scenarios, evaluates 30 prominent models on 42 scenarios, and improves scenario overlap from 17.9% to 96.0%. Body argues accuracy-only evaluation treats other desiderata as second-class. |
| OpenAI, "GPT-4 Technical Report," arXiv:2303.08774. PDF: https://arxiv.org/pdf/2303.08774 | Benchmarks as release/product evidence; contamination disclosure; OpenAI Evals as infrastructure. | Green/Yellow: PDF downloaded 2026-04-28. Abstract and intro claim GPT-4 human-level performance on professional/academic benchmarks and simulated bar exam top 10%. Section 4 reports exam and benchmark tables including MMLU 86.4%, states contamination checks were run, and discloses GSM-8K training-set inclusion. Lines around 461-464 say OpenAI is open-sourcing Evals for creating/running benchmarks and tracking deployed models. Use as OpenAI release-report framing, not neutral proof of intelligence. |
| Lianmin Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," arXiv:2306.05685. PDF: https://arxiv.org/pdf/2306.05685 | Preference arenas and LLM-as-judge as public comparison infrastructure. | Green: PDF downloaded 2026-04-28. Abstract says existing benchmarks are inadequate for open-ended human preferences, introduces MT-Bench and Chatbot Arena, and reports GPT-4 judge agreement over 80%, similar to human-human agreement. Body defines MT-Bench as 80 high-quality multi-turn questions, Chatbot Arena as anonymous pairwise crowdsourcing, and documents position, verbosity, self-enhancement, and math/reasoning judge failures. |
| Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770. PDF: https://arxiv.org/pdf/2310.06770 | Harder, real-world benchmark design and moving-target evaluation. | Green: PDF downloaded 2026-04-28. Abstract says SWE-bench has 2,294 software engineering problems from GitHub issues and pull requests across 12 Python repos; models edit a codebase and pass tests; Claude 2 solves 1.96% in initial setup. Body says existing benchmarks are saturated, construction filters PRs from about 90,000 to 2,294 tasks, and training data repositories are disjoint to reduce contamination risk. |
| David Manheim and Scott Garrabrant, "Categorizing Variants of Goodhart's Law," arXiv:1803.04585. PDF: https://arxiv.org/pdf/1803.04585 | Conceptual anchor for metrics becoming targets and overoptimization failure. | Green: PDF downloaded 2026-04-28. Abstract defines Goodhart-like failures as overoptimization on metrics until further optimization becomes ineffective or harmful; body defines regressional, extremal, causal, and adversarial variants. |
| Wikipedia pages for MMLU, BIG-bench, HELM, Chatbot Arena, and Goodhart's law. | Source-discovery only. | Yellow: useful for locating primary links and chronology; not evidence for prose claims. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Confirmation | Status | Notes |
|---|---|---|---|---|---|
| Modern foundation-model releases use benchmark tables as capability claims, not merely scientific appendices. | Table In Model Card | GPT-4 Technical Report Section 4 | MMLU/HELM/BIG-bench papers | Yellow | Synthesis; keep release-report framing. |
| MMLU covers 57 academic/professional subjects and was designed to test broad world knowledge/problem solving. | Frontier Scorecard | MMLU p.1 and dataset section | GPT-4 report MMLU usage | Green | Strong scorecard anchor. |
| MMLU authors report largest GPT-3 at 43.9% and below expert-level accuracy, showing the benchmark initially exposed gaps. | Frontier Scorecard | MMLU p.1/results | MMLU Table 1 | Green | Historical, not current ranking. |
| BIG-bench broadened evaluation to 204 tasks by 450 authors across 132 institutions. | Frontier Scorecard | BIG-bench abstract | BIG-bench Section 2 | Green | Use to show expansion pressure. |
| BIG-bench authors argued many benchmarks had restricted scope and short useful lifespans. | Contamination / Goodhart | BIG-bench Section 1.2 | SuperGLUE saturation figure | Green | Good bridge to benchmark arms race. |
| HELM explicitly targets transparency, multi-metric measurement, and standardized model comparison. | Frontier Scorecard | HELM abstract | HELM Sections 1.1 / multi-metric | Green | Avoid reducing HELM to leaderboard. |
| HELM evaluates beyond accuracy: calibration, robustness, fairness, bias, toxicity, and efficiency. | Frontier Scorecard | HELM abstract/body | HELM Figure 3 discussion | Green | Important anti-single-score scene. |
| GPT-4 report uses professional/academic exams, MMLU, HumanEval, and other benchmarks as release evidence. | Table In Model Card | GPT-4 Technical Report Section 4 | GPT-4 abstract | Yellow | First-party technical report. |
| GPT-4 report discloses contamination checks and notes GSM-8K training-set inclusion. | Contamination / Goodhart | GPT-4 Section 4 footnotes/table notes | Appendix references | Green | Do not overstate beyond report. |
| OpenAI Evals is presented as a framework for creating/running benchmarks and tracking model performance in deployment. | Evaluation As Power | GPT-4 report lines around Evals | OpenAI Evals footnote in report | Green | Infrastructure anchor. |
| MT-Bench and Chatbot Arena were introduced because conventional benchmarks missed open-ended human preferences. | Arena Courtroom | Zheng et al. abstract/introduction | MT-Bench/Chatbot Arena sections | Green | Core public-comparison scene. |
| Chatbot Arena uses anonymous pairwise voting and public preference data to compare models. | Arena Courtroom | Zheng et al. Section 2.3 | Abstract release note | Green | Date-bound methodology. |
| GPT-4-as-judge can align with human preferences at over 80% agreement, but judge bias/failure modes are documented. | Arena Courtroom | Zheng et al. abstract + limitations | Position/verbosity/self-bias sections | Green | Balanced claim. |
| Goodhart effects explain why optimizing a proxy benchmark can degrade its relation to the real goal. | Contamination / Goodhart | Manheim/Garrabrant abstract | Goodhart variant sections | Green | Conceptual, not benchmark-specific accusation. |
| BIG-bench and SWE-bench both treat leakage/contamination as a design problem rather than a rumor. | Contamination / Goodhart | BIG-bench leakage note; SWE-bench disjoint repos | GPT-4 contamination checks | Green | Good no-accusation guardrail. |
| SWE-bench was built from real GitHub issues/PRs and execution tests to make software evaluation less toy-like. | Harder Tests | SWE-bench abstract/Sections 2-3 | SWE-bench construction pipeline | Green | Handoff to agentic coding but not Ch60. |
| SWE-bench initial results showed models solved only a small fraction of tasks, keeping the benchmark useful at release. | Harder Tests | SWE-bench abstract/results | SWE-bench tables | Green | Date-bound. |
| Public leaderboards and arena scores shape product perception, procurement, and open-vs-closed narratives. | Evaluation As Power | GPT-4 release framing + Arena public ranking + HELM transparency | Ch65 open weights context | Yellow | Institutional synthesis; do not invent specific decisions. |
| Benchmark scores are time-sensitive and do not settle model quality. | Close | HELM multi-metric argument; Zheng judge limitations; Goodhart | MMLU/BIG-bench saturation discussion | Green | Core moral. |

## Conflict Notes

- Benchmark scores are time-sensitive. Always date them.
- Do not imply one benchmark settles model quality.
- Do not draft until source anchors are extracted.
- Do not accuse a model/lab of contamination unless the source itself reports a
  contamination check or discloses overlap.
