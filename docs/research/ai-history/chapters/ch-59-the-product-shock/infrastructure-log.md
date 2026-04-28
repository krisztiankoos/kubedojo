# Infrastructure Log: Chapter 59

## Technical Metrics & Constraints

- **Azure substrate:** OpenAI says ChatGPT/GPT-3.5 were trained on Azure AI supercomputing infrastructure; Microsoft says Azure powers OpenAI workloads and that Microsoft was building specialized supercomputing systems for OpenAI.
- **Consumer capacity pressure:** ChatGPT Plus promised access during peak times, faster responses, and priority access. Treat Plus as a capacity/productization response, not just a revenue story.
- **Cost compression:** OpenAI's GPT-3.5 Turbo API post says system-wide optimizations produced a 90% cost reduction for ChatGPT since December. This is a bridge to Ch63 inference economics.
- **Search integration:** Microsoft's Bing post describes search, browsing, chat, content generation, the Prometheus model, and a preview scaling to millions. Keep details brief; Ch60 handles retrieval/tool-use systems.
- **GPT-4 capacity:** OpenAI expected GPT-4 Plus access to be capacity constrained and used API waitlists/rate limits. Good anchor for the physical/inference constraints that later chapters expand.

## Adoption Metrics

- **100M MAU estimate:** Reuters/UBS estimated 100M monthly active users in January 2023, about two months after launch. Use as estimate, not audited company reporting.
- **1M in five days:** Attributed to Altman via contemporary reports; useful color but weaker than the Reuters/UBS estimate.
- **Record caveat:** Threads later reportedly reached 100M sign-ups in about five days. The chapter must phrase ChatGPT's record as time-bound.

## Prose Guardrails

- Separate monthly active users, sign-ups, API users, paid subscribers, and traffic. They are not interchangeable.
- Separate training infrastructure from serving infrastructure. Ch59 can introduce the issue; Ch63 owns the serving economics.
- Do not let Microsoft/Bing become Ch60. This chapter is about product shock and search response, not the architecture of retrieval/tool use.
