# KubeDojo

**Free, comprehensive cloud native education.**

Kubernetes certifications. Platform engineering. SRE. DevSecOps. MLOps.

No paywalls. No upsells. Theory-first.

---

## 🇺🇦 Присвята

*Цей проєкт присвячується українським ІТ-інженерам, які віддали своє життя, захищаючи Батьківщину.*

*Вони були розробниками, DevOps-інженерами, системними адміністраторами. Вони будували системи, писали код, підтримували інфраструктуру. Коли прийшла війна, вони залишили клавіатури й взяли зброю.*

*Їхній код живе. Їхня жертва — вічна. Слава Україні.*

### Заповіт
*Тарас Шевченко, 1845*

> Як умру, то поховайте
> Мене на могилі,
> Серед степу широкого,
> На Вкраїні милій,
> Щоб лани широкополі,
> І Дніпро, і кручі
> Було видно, було чути,
> Як реве ревучий.
>
> Як понесе з України
> У синєє море
> Кров ворожу... отойді я
> І лани і гори —
> Все покину і полину
> До самого Бога
> Молитися... а до того
> Я не знаю Бога.
>
> Поховайте та вставайте,
> Кайдани порвіте
> І вражою злою кров'ю
> Волю окропіте.
> І мене в сем'ї великій,
> В сем'ї вольній, новій,
> Не забудьте пом'янути
> Незлим тихим словом.

---

## Learning Path

```
                              KUBEDOJO
    ═══════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   PREREQUISITES                        "Why Kubernetes?"│
    │   └── docs/prerequisites/                               │
    │       ├── Philosophy & Design          4 modules        │
    │       ├── Cloud Native 101             5 modules        │
    │       ├── Kubernetes Basics            8 modules        │
    │       └── Modern DevOps                6 modules        │
    │                                                         │
    └────────────────────────┬────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   CERTIFICATIONS                       Kubestronaut Path│
    │   └── docs/k8s/                                         │
    │       │                                                 │
    │       │  ENTRY LEVEL (multiple choice)                  │
    │       ├── KCNA    Kubernetes & Cloud Native Associate   │
    │       ├── KCSA    Security Associate                    │
    │       │                                                 │
    │       │  PRACTITIONER (hands-on lab)                    │
    │       ├── CKAD    Application Developer                 │
    │       ├── CKA     Administrator                         │
    │       └── CKS     Security Specialist                   │
    │                                                         │
    └────────────────────────┬────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   PLATFORM ENGINEERING              Beyond Certifications│
    │   └── docs/platform/                                    │
    │       │                                                 │
    │       ├── foundations/         Theory that doesn't change│
    │       │   Systems Thinking · Reliability · Distributed  │
    │       │   Systems · Observability Theory · Security     │
    │       │                                                 │
    │       ├── disciplines/         Applied practices        │
    │       │   SRE · Platform Engineering · GitOps ·         │
    │       │   DevSecOps · MLOps                             │
    │       │                                                 │
    │       └── toolkits/            Current tools (evolving) │
    │           Prometheus · ArgoCD · Vault · Backstage ·     │
    │           Kubeflow · and more...                        │
    │                                                         │
    └─────────────────────────────────────────────────────────┘

    ═══════════════════════════════════════════════════════════
```

---

## Status

| Track | Modules | Status |
|-------|---------|--------|
| [Prerequisites](docs/prerequisites/) | 23 | ✅ Complete |
| [Kubernetes Certifications](docs/k8s/) | 142 | ✅ Complete |
| [Platform Engineering](docs/platform/) | ~75 | 🚧 Planned |

---

## Where to Start

| You are... | Start here |
|------------|------------|
| New to containers/K8s | [Prerequisites](docs/prerequisites/) |
| Want certifications | [KCNA](docs/k8s/kcna/) (entry) or [CKA](docs/k8s/cka/) (admin) |
| Already certified | [Platform Engineering](docs/platform/) |

---

## Why This Exists

Cloud native education is fragmented. Certification courses charge $300-500+ for shallow content. Platform engineering knowledge lives in scattered blog posts. Tool documentation tells you *what*, not *why*.

KubeDojo is different:
- **Free forever** — No paid tiers, no premium content
- **Theory-first** — Understand principles before tools
- **Practitioner-built** — By people who run production systems
- **Complete path** — From beginner to platform engineer, not just cert prep

---

## Philosophy

**Theory before hands-on.** You can't troubleshoot what you don't understand.

**Speed is a skill.** CKA gives you ~7 minutes per question. We train speed explicitly.

**No memorization.** K8s docs are available during exams. We teach navigation, not YAML memorization.

**Principles over tools.** Tools change. Foundations don't. Learn both, in that order.

---

## Contributing

**What we need:**
- **Hands-on exercises** — Real scenarios, not toy examples
- **War stories** — Production incidents that teach lessons
- **Tool expertise** — Deep-dives on ArgoCD, Prometheus, Vault, etc.
- **Error fixes** — Typos, outdated commands, broken YAML

**What we don't build:**
- Exam simulators — Use [killer.sh](https://killer.sh) (included with exam purchase)
- Lab environments — Use [killercoda.com](https://killercoda.com) or local kind/minikube
- Video content — Text-first, searchable, version-controlled

**How to contribute:**
- Open an issue to discuss before large PRs
- Follow existing module structure
- Test all commands and YAML before submitting

---

## License

MIT License. Free to use, share, and modify.

---

*"In the dojo, everyone starts as a white belt. What matters is showing up to train."*
