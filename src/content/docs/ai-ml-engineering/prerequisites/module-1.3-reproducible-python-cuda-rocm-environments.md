---
revision_pending: true
title: "Reproducible Python, CUDA, and ROCm Environments"
slug: ai-ml-engineering/prerequisites/module-1.3-reproducible-python-cuda-rocm-environments
sidebar:
  order: 103
---
> **AI/ML Engineering Track** | Complexity: `[MEDIUM]` | Time: 2-3
---
**Reading Time**: 2-3 hours
**Prerequisites**: Modules 1.1 and 1.2 complete
---

## What You'll Be Able to Do

By the end of this module, you will:
- understand the layers of a local AI environment instead of treating setup as magic
- build one reproducible Python environment per project
- reason about driver, toolkit, and framework compatibility
- choose when to use plain virtual environments and when containers are worth it
- diagnose the most common CUDA, ROCm, and Python drift failures

**Why this matters**: environment failures waste more learner time than most actual coding errors. If your setup is unreliable, every module after this becomes harder than it should be.

---

## Why AI Environments Break So Often

In web development, many learners can get away with:
- one Python install
- one Node install
- lots of trial and error

In AI work, the stack is tighter and less forgiving.

You are often combining:
- Python packages
- compiled native extensions
- deep learning frameworks
- GPU drivers
- CUDA or ROCm runtime expectations
- operating system behavior

If you do not understand the stack boundaries, you end up debugging by superstition.

---

## The Four Layers of the Stack

Think about your environment in layers:

1. **Operating system and kernel**
2. **GPU driver layer**
3. **Compute runtime layer** such as CUDA or ROCm
4. **Python and framework layer** such as PyTorch, TensorFlow, tokenizers, and app dependencies

Most failures happen when learners confuse these layers.

Examples:
- reinstalling Python when the real problem is the GPU driver
- changing the driver when the real problem is an incompatible wheel
- blaming PyTorch when the real issue is environment mixing between projects

---

## The Reproducibility Rule That Prevents Most Pain

Use this baseline rule:

**One project, one isolated environment, one documented setup path.**

That means:
- a dedicated project directory
- a dedicated Python environment
- a dependency file tracked in Git
- one short verification sequence

Do not share one giant global Python environment across AI projects.

That approach often looks efficient for two days and chaotic by week three.

---

## The Baseline Workflow

For most learners, this is the correct starting workflow:

1. install a supported Python version
2. create one directory per project
3. create a virtual environment inside or adjacent to that project
4. install only what the project needs
5. record dependencies
6. run a short verification script

Example shape:

```text
my-ai-project/
├── .venv/
├── src/
├── notebooks/
├── data/
├── outputs/
├── requirements.txt
└── README.md
```

This is deliberately boring. Boring is what you want from environments.

---

## Python Isolation Choices

### Option 1: `venv` as the Default Baseline

For this curriculum, plain Python virtual environments are the safest baseline.

Why:
- built into Python
- simple mental model
- minimal hidden behavior
- portable enough for solo work
- easy to debug

If a learner cannot keep a `venv` workflow healthy, adding more tooling usually makes the problem harder, not easier.

### Option 2: Higher-Level Environment Managers

You may later choose tools that manage Python versions, lock files, or binary packages more aggressively.

These can be useful, but they are not the baseline skill.

You should first understand:
- what Python version is active
- where packages are being installed
- which environment is currently activated

Without that, better tools just hide confusion.

### Option 3: Containers

Containers are valuable when:
- your host machine is already messy
- you need stronger reproducibility
- your team needs the same setup
- you are preparing code for deployment anyway

Containers are not automatically simpler for beginners. They add another layer. Use them when the added control is worth it.

---

## CUDA and ROCm: What You Actually Need to Understand

You do not need to memorize every toolkit version. You do need the right mental model.

### CUDA

[CUDA is the NVIDIA compute stack](https://github.com/NVIDIA/cuda-python) used by many deep learning frameworks.

For learners, the important idea is:

**driver compatibility and framework build compatibility must agree.**

If they do not, you often see:
- GPU not detected
- runtime initialization errors
- unsupported binary or kernel errors
- silent fallback to CPU

### ROCm

[ROCm plays a similar role for AMD GPUs](https://github.com/ROCm/ROCm), but the ecosystem and [supported combinations can be less forgiving depending on hardware and distro choice](https://github.com/ROCm/ROCm).

That does not make it unusable. It means you should be stricter about:
- using supported operating systems
- using documented framework builds
- avoiding random package mixing

### The Wrong Mental Model

"I installed the newest thing, so it should work."

Wrong.

The correct model is:

"I installed a compatible set of things."

That is how reproducible environments are built.

---

## A Compatibility Checklist That Ages Well

Before installing frameworks, verify:

1. what GPU you have
2. whether your OS is appropriate for the stack
3. whether the driver is installed and visible
4. which compute runtime family you are targeting
5. [which framework build matches that target](https://github.com/pytorch/pytorch)

Only then install the framework.

If you reverse that order, you end up debugging the entire stack at once.

---

## Verification Beats Hope

Every environment should have a short smoke test.

Examples of what you want to verify:
- Python version
- active environment path
- package install sanity
- framework import
- GPU visibility
- simple tensor operation on the intended backend

A successful smoke test gives you a checkpoint. Without it, you do not know whether the system was ever healthy.

---

## When to Use Containers Instead of Host Python

Use host Python plus `venv` when:
- you are learning
- the project is solo
- setup is straightforward
- you want the simplest debugging path

Use containers when:
- onboarding must be repeatable
- host dependencies are unstable
- you are mixing multiple incompatible stacks
- the project is moving toward deployment

Do not containerize everything by reflex. But do not resist containers once host drift becomes the actual problem.

---

## Common Failure Modes

### Failure 1: Wrong Python, Right Packages

You installed dependencies into one interpreter and ran another.

Symptoms:
- package not found
- command works in one terminal but not another
- notebook and CLI disagree

Fix:
- check active interpreter
- recreate the environment cleanly
- stop guessing which Python is being used

### Failure 2: Driver and Framework Mismatch

Symptoms:
- GPU not available
- import succeeds but device use fails
- framework falls back to CPU

Fix:
- verify the driver layer first
- verify the intended compute runtime
- install a framework build that matches it

### Failure 3: Mixed Package Managers Without a Plan

Symptoms:
- inconsistent behavior across machines
- difficult upgrades
- unclear source of installed binaries

Fix:
- choose a primary environment strategy per project
- keep the project setup documented

### Failure 4: "It Works on My Notebook"

The notebook kernel, shell environment, and project directory are not actually aligned.

Fix:
- make the environment explicit
- make the project root explicit
- verify imports from both notebook and CLI

---

## Recommended Team Habits Even for Solo Learners

Even if you work alone, behave like someone who may need to recreate the project in two months.

Track:
- dependency file
- Python version
- short setup steps
- smoke test
- GPU or CPU assumptions

That habit is the bridge from hobby setup to professional reproducibility.

---

## Common Mistakes

| Mistake | What Goes Wrong | Better Move |
|---|---|---|
| One global Python environment for everything | dependency collisions and mystery imports | one environment per project |
| Installing frameworks before checking driver/runtime assumptions | hard-to-read failures | verify stack layers first |
| Mixing tools without understanding the active interpreter | shell and notebook mismatch | always know which interpreter is active |
| Trusting a setup because one import worked once | hidden drift remains | use a repeatable smoke test |
| Treating containers as magic | extra complexity with no model | use containers intentionally, not reflexively |

---

## Check Your Understanding

1. Why is "compatible set" a better mindset than "latest version" for AI environments?
2. What problem does one-project-one-environment solve?
3. When should a learner choose containers over plain virtual environments?
4. Why is a smoke test more valuable than assuming a successful install means the system is healthy?

---

<!-- v4:generated type=no_quiz model=codex turn=1 -->
## Quiz


**Q1.** Your team starts a new local LLM project, and one developer suggests reusing the same global Python environment they already use for three other AI experiments to save time. Two weeks later, package versions conflict and nobody can reproduce the same setup. What project setup should you have used from day one, and why?

<details>
<summary>Answer</summary>
Use the module's baseline rule: one project, one isolated environment, and one documented setup path. That means a dedicated project directory, a dedicated `venv`, a tracked dependency file such as `requirements.txt`, and a short verification sequence. This prevents dependency collisions and makes it possible to recreate the same environment later instead of relying on a shared global Python install.
</details>

**Q2.** Your teammate sees that PyTorch imports correctly, but when they try to run a tensor operation on the GPU, the framework falls back to CPU. They immediately propose reinstalling Python. Based on the stack model from the module, what is the more likely problem area to investigate first?

<details>
<summary>Answer</summary>
The driver and compute runtime compatibility should be checked before touching Python. The module explains that many failures happen when people confuse stack layers. If import works but GPU use fails, the likely issue is a driver/framework/runtime mismatch rather than Python itself. The right approach is to verify the driver layer first, confirm the intended CUDA or ROCm target, and then ensure the installed framework build matches that target.
</details>

**Q3.** You are setting up an AMD GPU workstation for model training on Linux. A colleague says, "Just install the newest packages from wherever you find them and it should work." Why is that a risky approach for ROCm, and what should you do instead?

<details>
<summary>Answer</summary>
It is risky because ROCm can be less forgiving about supported hardware, operating systems, and framework builds. The module's correct mental model is not "install the newest thing" but "install a compatible set of things." You should verify that the OS is appropriate, confirm the GPU and driver are supported, choose ROCm as the target runtime family deliberately, and then install a documented framework build that matches that setup instead of mixing random packages.
</details>

**Q4.** A notebook on your machine can import a library successfully, but the same import fails from the command line in the project directory. What failure mode does this suggest, and how should you fix it?

<details>
<summary>Answer</summary>
This suggests an environment mismatch between the notebook kernel, shell interpreter, and possibly the project root. The module calls this a common "it works on my notebook" problem. The fix is to make the environment explicit, make the project root explicit, verify which interpreter is active, and confirm imports from both the notebook and CLI so they are using the same project environment.
</details>

**Q5.** You are helping a small team onboard to a project that mixes several incompatible AI stacks, and different laptops keep drifting into different states. The code may later be deployed in production. Should you stay with host Python plus `venv`, or is this a case for containers?

<details>
<summary>Answer</summary>
This is a case where containers are worth using. The module recommends host Python plus `venv` for learning, solo work, and straightforward setups, but containers become the better choice when onboarding must be repeatable, host dependencies are unstable, multiple incompatible stacks are involved, or the project is moving toward deployment. Here, the added control of containers is justified.
</details>

**Q6.** A developer installs framework packages first and only afterward checks whether the machine's GPU driver and runtime stack are appropriate. They now face hard-to-read errors across multiple layers. What installation order would have reduced this confusion?

<details>
<summary>Answer</summary>
They should have followed the compatibility checklist before installing frameworks. The module's order is: verify what GPU is present, confirm the OS is appropriate, check that the driver is installed and visible, choose the compute runtime family such as CUDA or ROCm, and then install the framework build that matches that target. Reversing that order makes the whole stack harder to debug.
</details>

**Q7.** Your project setup guide currently says only, "Install dependencies and start working." A new teammate asks how they can tell whether the environment was ever healthy in the first place. What should you add to the project, and what should it verify?

<details>
<summary>Answer</summary>
Add a short smoke test as part of the documented setup path. The module recommends verifying the Python version, active environment path, package install sanity, framework import, GPU visibility, and a simple tensor operation on the intended backend. This gives the team a known-good checkpoint instead of assuming that installation output means the environment actually works.
</details>

<!-- /v4:generated -->
<!-- v4:generated type=no_exercise model=codex turn=1 -->
## Hands-On Exercise


Goal: build a fresh project environment that is isolated, documented, and easy to verify on CPU, CUDA, or ROCm hardware.

- [ ] Create a new project directory with a dedicated virtual environment and activate it.

  ```bash
  mkdir -p reproducible-ai-env/{src,notebooks,data,outputs}
  cd reproducible-ai-env
  python3 -m venv .venv
  source .venv/bin/activate
  python --version
  which python
  ```

- [ ] Record the active interpreter and package tool versions so the environment state is explicit from the start.

  ```bash
  python --version
  python -m pip --version
  which python
  which pip
  ```

- [ ] Create a minimal dependency file and install only the packages this project needs.

  ```bash
  cat > requirements.txt <<'EOF'
  pip
  setuptools
  wheel
  numpy
  EOF

  python -m pip install --upgrade pip setuptools wheel
  python -m pip install -r requirements.txt
  python -m pip freeze > requirements.lock.txt
  ```

- [ ] Inspect the machine's GPU stack before installing any framework-specific CUDA or ROCm build.

  ```bash
  uname -a
  lspci | grep -Ei 'vga|3d|display'
  ```

  ```bash
  nvidia-smi
  ```

  ```bash
  rocminfo
  ```

- [ ] Add a smoke test script that reports Python details, package import health, and whether PyTorch can see CUDA or ROCm if it is installed later.

  ```bash
  cat > verify_env.py <<'EOF'
  import os
  import platform
  import sys

  print("python:", sys.version.split()[0])
  print("executable:", sys.executable)
  print("platform:", platform.platform())
  print("venv:", os.environ.get("VIRTUAL_ENV", "not set"))

  import numpy
  print("numpy:", numpy.__version__)

  try:
      import torch
      print("torch:", torch.__version__)
      print("cuda_available:", torch.cuda.is_available())
      print("cuda_version:", getattr(torch.version, "cuda", None))
      print("hip_version:", getattr(torch.version, "hip", None))
      if torch.cuda.is_available():
          x = torch.tensor([1.0, 2.0]).to("cuda")
          print("tensor_device:", x.device)
  except ImportError:
      print("torch: not installed")
  EOF

  python verify_env.py
  ```

- [ ] Create a short setup note so another person can reproduce the same environment without guessing.

  ```bash
  cat > README.md <<'EOF'
  # Reproducible AI Environment

  ## Setup
  1. Create the virtual environment: `python3 -m venv .venv`
  2. Activate it: `source .venv/bin/activate`
  3. Install dependencies: `python -m pip install -r requirements.txt`

  ## Verify
  Run: `python verify_env.py`
  EOF

  cat README.md
  ```

- [ ] Recreate the environment from scratch and confirm the same verification path still works.

  ```bash
  deactivate
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -r requirements.txt
  python verify_env.py
  ```

Success criteria:
- The project has its own `.venv`, `requirements.txt`, `requirements.lock.txt`, `README.md`, and `verify_env.py`.
- `which python` points to the project's virtual environment after activation.
- `python -m pip freeze` produces a repeatable dependency snapshot.
- Hardware inspection identifies whether the machine should follow a CPU, CUDA, or ROCm path.
- `python verify_env.py` runs successfully and reports a clear, reproducible environment state.

<!-- /v4:generated -->
## Next Modules

- [Notebooks, Scripts, and Project Layouts](./module-1.4-notebooks-scripts-project-layouts/)
- [PyTorch Fundamentals](../deep-learning/module-1.2-pytorch-fundamentals/)
- [Home AI Workstation Fundamentals](./module-1.2-home-ai-workstation-fundamentals/)

## Sources

- [NVIDIA cuda-python](https://github.com/NVIDIA/cuda-python) — Useful for understanding CUDA's platform/runtime surface from the Python side of local AI environments.
- [ROCm Official Repository](https://github.com/ROCm/ROCm) — Useful for ROCm overview, supported hardware and OS guidance, and links to the official compatibility matrix.
- [PyTorch Official Repository](https://github.com/pytorch/pytorch) — Useful for seeing how a major framework distinguishes CPU, CUDA, and ROCm installation and build paths.
