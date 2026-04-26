---
title: "Prerequisites & Environment Setup"
slug: ai-ml-engineering/prerequisites/module-1.1-prerequisites-environment-setup
sidebar:
  order: 101
---
> **AI/ML Engineering Track** | Complexity: `[QUICK]` | Time: 2-3
---
**Reading Time**: 2-3 hours
**Prerequisites**: A computer, internet access, and the willingness to type commands into a terminal
---

## Learning Outcomes

By the end of this module, you will be able to:
- Construct an isolated Python virtual environment that guarantees dependency separation across multiple artificial intelligence projects.
- Implement secure credential management practices by isolating application programming interface keys away from version control systems.
- Evaluate the execution costs and token utilization patterns of language model invocations using programmatic billing analysis.
- Debug common configuration mismatches involving system interpreters, package managers, and local environment variables.

## Why This Module Matters

A new software engineer joined an artificial intelligence team and immediately attempted to run a complex machine learning training script on their local workstation. Because they bypassed the standard virtual environment setup, the script installed conflicting versions of scientific libraries directly into their operating system's global Python interpreter. Two hours later, their entire operating system package manager stopped functioning, requiring a complete system rebuild that cost them two days of productivity. Their failure did not stem from a lack of programming knowledge, but rather from a fundamental misunderstanding of dependency isolation and environment management.

Professional software development requires treating your local workstation with the same architectural rigor as a production server. When developers construct explicit, reproducible environments, they eliminate the vast majority of configuration drift and dependency conflicts that plague modern application development. Establishing these foundations early ensures that when you encounter complex bugs later in the curriculum, you can confidently isolate the problem to your application logic rather than questioning whether your tools are configured correctly. A predictable environment transforms troubleshooting from a chaotic guessing game into a structured scientific process.

## Establishing Python Environment Isolation

The cornerstone of modern Python development is the virtual environment, a mechanism that provides independent execution contexts for different projects residing on the same machine. When developers install packages globally, they inevitably encounter version conflicts because different applications frequently require mutually exclusive versions of the same foundational libraries. Virtual environments solve this problem by creating an isolated directory structure containing a dedicated Python binary, a distinct package manager, and an independent repository for installed libraries.

### Constructing the Workspace

Creating a virtual environment requires explicit intention before installing any third-party dependencies. Modern Python distributions bundle the environment creation tool directly within the standard library, ensuring developers always have access to this critical isolation mechanism without requiring external package downloads. When you initialize a new workspace, the system constructs a mirrored directory tree that prioritizes local binaries over global system executables.

```bash
# Navigate to your dedicated projects directory and create a new workspace
mkdir -p ~/projects/ai-ml-lab
cd ~/projects/ai-ml-lab

# Initialize the virtual environment using the standard library module
python3.12 -m venv venv

# Activate the isolated context to redirect executable paths
source venv/bin/activate
```

Before proceeding, it is crucial to verify that your execution context has shifted from the global system to your isolated workspace. You can accomplish this by querying the active executable path, which should now point directly into your newly created project directory rather than a system-wide binary location. This verification step prevents the silent contamination of your global operating system packages and ensures that subsequent commands manipulate the correct dependency tree.

> **Active Learning Prompt:** Before running the `which python` command in your terminal, write down the exact file path you expect to see based on the directory structure where you initialized your project. What would it mean if the output displayed `/usr/bin/python` instead of your local workspace path, and how would that affect your next installation command?

### The Architecture of Isolation

Understanding the internal architecture of a virtual environment demystifies much of the behavior that confuses newer developers. The isolation mechanism relies primarily on manipulating your shell's execution path and utilizing symbolic links to reference the underlying Python binaries without duplicating large executable files across your filesystem. This approach allows you to instantiate hundreds of isolated environments without consuming massive amounts of storage.

```ascii
┌─────────────────────────────────────────────────────────┐
│ Virtual Environment Directory Structure                 │
│                                                         │
│ venv/                                                   │
│ ├── bin/                                                │
│ │   ├── activate      (Modifies your $PATH)             │
│ │   ├── pip           (Local package manager)           │
│ │   └── python        (Symlink to system python3.12)    │
│ ├── include/          (C headers for compiled modules)  │
│ ├── lib/                                                │
│ │   └── python3.12/                                     │
│ │       └── site-packages/                              │
│ │           ├── anthropic/    (Isolated dependencies)   │
│ │           └── pydantic/     (Live exclusively here)   │
│ └── pyvenv.cfg        (Configuration metadata)          │
└─────────────────────────────────────────────────────────┘
```

When you execute the activation script, it modifies your current shell session by prepending the environment's binary directory to your system path. This path manipulation guarantees that subsequent invocations of Python or the package manager resolve to your local workspace rather than traversing up to the operating system's default utilities. Deactivating the environment simply reverses this path modification, returning your shell to its original configuration state and restoring access to the global tools without leaving permanent modifications on your system.

## Development Tooling and Editor Selection

Selecting the appropriate text editor or integrated development environment shapes your daily workflow and directly impacts your productivity when navigating complex codebases. While raw terminal editors offer unparalleled execution speed, modern development often benefits from rich visual interfaces that integrate syntax highlighting, type checking, and artificial intelligence completion systems. The goal is to choose a tool that minimizes friction between your mental model and the resulting source code, allowing you to focus entirely on architectural problem-solving.

### Evaluating Editor Capabilities

Different development environments prioritize different aspects of the programming experience, requiring engineers to balance raw performance against feature completeness. The table below outlines the primary considerations when selecting an editor for artificial intelligence engineering, focusing on the features that provide the highest return on investment for developers navigating this curriculum.

| Editor Application | Target Audience | Primary Advantages | Known Limitations | Built-in Intelligence |
|--------------------|-----------------|--------------------|-------------------|-----------------------|
| Visual Studio Code | General developers | Extensive plugin ecosystem and broad community support | Can consume significant memory with many extensions | Requires third-party plugin configuration |
| Cursor | AI-focused engineers | Deep integration with language models for code generation | Occasional synchronization bugs with underlying upstream features | Native context-aware generation |
| PyCharm Professional | Python specialists | Unparalleled refactoring capabilities and deep syntax analysis | Heavy resource footprint and extended startup duration | Proprietary assistant requiring subscription |
| Neovim / Emacs | Terminal purists | Zero latency editing and infinite customizability | Substantial initial learning investment | Requires manual language server setup |

For the majority of participants progressing through this curriculum, adopting a modern editor with integrated artificial intelligence features accelerates the learning process. These tools can automatically identify type inconsistencies, suggest idiomatic implementation patterns, and provide contextual documentation directly alongside your source code. You should configure your chosen editor to utilize the isolated virtual environment we established previously, ensuring that syntax analysis algorithms draw from your project-specific dependencies rather than system-wide libraries.

> **Active Learning Prompt:** Open your chosen integrated development environment and locate the configuration menu for selecting the Python interpreter. Does the editor currently point to your system installation, or has it successfully detected the local virtual environment directory? How would an incorrect selection impact the editor's ability to provide accurate auto-completion for third-party libraries?

### Standardizing the Toolchain

In addition to selecting a primary text editor, professional engineering environments rely on standardized command-line utilities to enforce code quality and consistency. By installing these tools into your virtual environment, you ensure that every collaborator working on the project adheres to identical stylistic and architectural rules.

| CLI Utility | Primary Function | Operational Necessity |
|-------------|------------------|-----------------------|
| pytest | Automated execution framework | Verifies that implementation logic satisfies the defined requirements without manual intervention. |
| pytest-cov | Execution path analysis | Quantifies the percentage of the codebase that receives validation during automated testing. |
| black | Deterministic code formatting | Eliminates subjective formatting disputes by enforcing a uniform syntactic structure across the repository. |
| isort | Dependency import organization | Automatically categorizes and alphabetizes module inclusions to maintain structural readability. |
| flake8 | Static syntax analysis | Identifies potential logical errors and stylistic violations before the code reaches execution. |
| mypy | Static type verification | Validates explicit type annotations to prevent runtime failures caused by unexpected data structures. |

Incorporating these utilities into your workflow from the beginning prevents the accumulation of technical debt. When you rely on automated systems to verify type definitions and enforce stylistic rules, you free your cognitive capacity to focus exclusively on solving the underlying business problem rather than debating structural formatting choices.

## Application Programming Interface Security

When developing applications powered by language models, your application programming interface keys serve as literal financial credentials that authorize consumption of expensive compute resources. Exposing these credentials in public version control repositories is equivalent to publishing your credit card details on the open internet, frequently resulting in thousands of dollars in unauthorized charges before automated safeguards trigger an account suspension. Professional developers mitigate this risk by strictly decoupling authentication secrets from their application source code.

### Implementing Secure Credential Storage

The industry standard methodology for managing sensitive configuration values relies on environmental variables injected during the application startup phase. Instead of embedding keys directly within your Python scripts, you construct a dedicated local configuration file that remains completely isolated from your version control tracking system. This approach ensures that your codebase can be shared safely while individual developers maintain their own distinct authorization credentials.

```bash
# Generate a hidden configuration file in your project root
touch .env

# Verify that your version control system will ignore this file
echo ".env" >> .gitignore

# Add your proprietary credentials using standard variable assignment
echo "ANTHROPIC_API_KEY=sk-ant-your-secure-key-here" >> .env
echo "OPENAI_API_KEY=sk-proj-your-secure-key-here" >> .env
```

Once the physical file exists, your Python application must parse these values and inject them into the active execution context. The `python-dotenv` package provides a standardized utility for loading these local files into memory, allowing your application logic to retrieve the keys as if they were provisioned by the host operating system. This mechanism bridges the gap between local development convenience and production deployment security without requiring complex infrastructure orchestration.

```python
import os
import logging
from dotenv import load_dotenv

# Initialize the logging framework for structured output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_credentials() -> None:
    """Validate the presence of required authentication tokens."""
    # Populate the environmental context from the local file
    load_dotenv()
    
    # Retrieve the key without providing a fallback default
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        logger.error("Authentication failure: API key is absent from the environment.")
        raise ValueError("Missing critical configuration. Check your .env file.")
        
    logger.info("Authentication success: Credentials successfully injected.")

if __name__ == "__main__":
    verify_credentials()
```

### Analyzing Provider Alternatives

While the curriculum heavily utilizes the Anthropic ecosystem for its strong contextual analysis capabilities, developers should understand the broader landscape of artificial intelligence providers. Selecting the appropriate vendor often depends on balancing requirements for latency, reasoning depth, and financial constraints.

| Provider Platform | Typical Use Case | Access Mechanism | Pricing Model | Noteworthy Advantages |
|-------------------|------------------|------------------|---------------|-----------------------|
| Anthropic Claude | Complex logical reasoning and secure coding | Direct API integration | Usage-based per token | Massive context window capacity |
| OpenAI Platform | General purpose instruction following | Direct API integration | Usage-based per token | Broad ecosystem compatibility |
| Groq | Rapid iterative testing and low latency | Specialized endpoints | Generous free allocations | Exceptionally fast inference speeds |
| Hugging Face | Open-source model experimentation | Inference API | Tiered access limits | Wide variety of model architectures |
| Local Execution | High privacy environments | Direct hardware execution | Zero marginal cost | Complete data confidentiality |

By maintaining awareness of multiple providers, you avoid vendor lock-in and retain the flexibility to migrate your applications when pricing structures or technical capabilities inevitably shift. Your architectural logic should ideally abstract the specific provider implementation behind a unified interface, allowing you to substitute alternative language models seamlessly without requiring substantial codebase refactoring.

## Invoking the Language Model Architecture

Communicating with a modern artificial intelligence service involves translating your human instructions into a highly structured programmatic request that the vendor's servers can process efficiently. Rather than sending raw text strings across the network, your application must package the prompt alongside specific metadata defining the desired model version, the maximum allowable response length, and the structural format of the conversation history.

### The Request Lifecycle

Understanding the lifecycle of an invocation request provides necessary context for interpreting latency issues and network failures. When your application initiates a call, it performs a serialized handshake with the provider's infrastructure, exchanging authentication tokens before negotiating the token processing parameters. This sequential process dictates the minimum response time you can expect from any synchronous architecture and highlights areas where asynchronous optimization becomes mandatory.

```ascii
┌───────────────────────────────────────────────────────────────┐
│ The Language Model Request Lifecycle                          │
│                                                               │
│ Local Application                Vendor Infrastructure        │
│ ─────────────────                ─────────────────────        │
│                                                               │
│ 1. Construct Message Array ──┐                                │
│ 2. Apply Authentication      │                                │
│ 3. Serialize to JSON       ──┴──> Network Transmission ────┐  │
│                                                            │  │
│                              ┌──< Load Balancer Routing <──┘  │
│                              │                                │
│                              └──> 4. Tokenize Input Text      │
│                                   5. Execute Inference        │
│                              ┌──< 6. Assemble Output Tokens   │
│                              │                                │
│ 7. Parse HTTP Response     <─┴──< Network Transmission ────┘  │
│ 8. Extract Target Text       │                                │
│ 9. Record Billing Metrics  ──┘                                │
└───────────────────────────────────────────────────────────────┘
```

This structural flow illustrates why error handling must extend beyond simple syntax verification. A failure could originate from an unauthorized token during step two, a network timeout during transmission, or an inference rejection if the requested prompt violates the provider's internal safety guidelines. Robust applications anticipate failures at every transition boundary in this architecture, incorporating graceful degradation pathways rather than terminating abruptly.

### Implementing the Invocation Logic

To demonstrate this lifecycle in practice, we construct a concrete script that establishes a verified connection to the Anthropic service. Notice how the implementation utilizes explicit type annotations and clearly separates the configuration logic from the functional execution, demonstrating professional coding standards from the very beginning of the curriculum.

```python
import os
from typing import Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, RateLimitError

def invoke_language_model(prompt_text: str, token_limit: int = 100) -> str:
    """
    Transmit a structured prompt to the remote language model service.
    
    This function demonstrates secure initialization, explicit limit controls,
    and foundational error handling required for reliable infrastructure.
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise EnvironmentError("Cannot invoke model: missing API configuration.")
        
    client = Anthropic(api_key=api_key)
    
    try:
        # Construct the structured payload requested by the API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=token_limit,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        
        # Isolate and return only the generated string
        return response.content[0].text
        
    except RateLimitError:
        return "Failure: The vendor's concurrency limits were exceeded."
    except APIError as error:
        return f"Failure: The vendor returned a processing error: {error}"

if __name__ == "__main__":
    sample_prompt = "Explain the importance of virtual environments in one sentence."
    print("Initiating remote invocation...")
    result = invoke_language_model(sample_prompt)
    print(f"Vendor response: {result}")
```

### Analyzing Token Economics

Every execution incurs a minor financial cost calculated against the precise volume of tokenized data processed during the request and the response phases. A token roughly correlates to a distinct syllable or short word segment, meaning complex source code often generates a higher token density than plain conversational English. Organizations monitor these metrics diligently because unchecked recursive loops can generate thousands of automated requests, accumulating massive bills before administrative personnel notice the anomaly.

| Metric Category | Standard Measurement | Operational Impact | Monitoring Strategy |
|-----------------|----------------------|--------------------|---------------------|
| Input Processing | Measured per million submitted tokens | Dictates the baseline cost of contextualizing large documents | Implement request length validation logic |
| Output Generation | Measured per million generated tokens | Often represents the most significant financial expenditure | Mandate absolute upper boundaries |
| System Overheads | Measured in raw temporal latency | Determines the interactive responsiveness of the application | Track execution duration percentiles |
| Concurrency Limits | Measured in concurrent active connections | Governs how many simultaneous users the application supports | Utilize exponential backoff algorithms |

By enforcing strict token limits on every request, you constrain your maximum financial exposure. If an application enters an infinite loop, a low token boundary ensures each mistaken invocation only consumes fractions of a cent rather than accumulating substantial output generation charges over an extended duration.

```python
def calculate_execution_cost(input_count: int, output_count: int) -> float:
    """
    Evaluate the financial impact of a discrete model execution.
    
    The pricing structures reflect hypothetical baseline averages where
    output generation typically costs significantly more than input parsing.
    """
    input_rate_per_million = 3.00
    output_rate_per_million = 15.00
    
    input_cost = (input_count / 1_000_000) * input_rate_per_million
    output_cost = (output_count / 1_000_000) * output_rate_per_million
    
    return input_cost + output_cost

# Example calculation for a moderately sized document processing task
projected_cost = calculate_execution_cost(input_count=2500, output_count=850)
print(f"Projected transaction fee: ${projected_cost:.4f}")
```

### Worked Example: Debugging a Connection Failure

Consider a scenario where your application attempts to invoke the language model but immediately throws a cryptic authentication error. The ability to systematically isolate the root cause distinguishes senior engineers from junior practitioners.

**The Problem:** The developer runs their Python script from the terminal, but the program terminates with an `AuthenticationError: Invalid API Key`. The developer verifies that their `.env` file exists and contains the correct string, yet the application continues to fail on every invocation.

**The Solution Process:**
1. The developer first checks if the `.env` file is located in the current working directory from which they are executing the script. The script was invoked from a nested subdirectory (`src/scripts/run.py`), but the `.env` file was actually placed at the repository root.
2. The developer updates their application logic to specify the exact absolute path to the configuration file using `load_dotenv(dotenv_path="/full/path/to/.env")`.
3. The script still fails. The developer then inspects the literal contents of the `.env` file using a raw text editor and notices unintended spaces around the assignment operator: `ANTHROPIC_API_KEY = sk-ant-12345`.
4. After removing the spaces so the line reads `ANTHROPIC_API_KEY=sk-ant-12345`, the parsing utility extracts the key correctly, and the script successfully establishes a network connection.

> **Active Learning Prompt:** Suppose you want to write a script that processes a massive directory of text files by sending each one to the language model sequentially. Based on the error handling concepts discussed earlier, what specific failure mode should you anticipate happening frequently during a large batch processing job, and how might you architect your code to recover from it without crashing?

## Did You Know?

1. The concept of software dependency isolation gained significant traction in the late 1990s as application complexity outgrew traditional system-wide installations, leading to the colloquial term "dependency hell" among systems administrators trying to reconcile version conflicts.
2. Modern virtual environments manipulate the execution context without duplicating core binaries, utilizing clever symbolic links to reference the original interpreter, which keeps the total storage footprint of an isolated workspace remarkably small and efficient.
3. The underlying tokenization algorithms utilized by modern language models are heavily influenced by Byte Pair Encoding, a data compression technique originally developed in the 1990s to replace frequently occurring byte pairs with unused sequence markers for transmission efficiency.
4. Security researchers frequently deploy automated scanning bots across public source code repositories to detect exposed authentication credentials, often identifying and revoking leaked application programming interface keys within minutes of the initial repository commit.

## Common Mistakes

| Mistake | Description | Consequence | Prevention Strategy |
|---------|-------------|-------------|---------------------|
| Installing packages globally | Running package manager commands without activating the local workspace. | Global system dependencies become polluted, potentially breaking operating system utilities. | Always verify the active shell prompt displays the virtual environment prefix before executing installation commands. |
| Committing configuration files | Tracking the hidden `.env` file in the version control repository. | Sensitive credentials are exposed to unauthorized individuals, leading to potential financial exploitation. | Immediately append the configuration filename to the version control ignore list upon repository creation. |
| Ignoring response token limits | Omitting the maximum token boundary parameter during model invocation requests. | The remote service may generate exceptionally long responses, accumulating unexpected billing charges. | Mandate strict upper boundaries on all programmatic requests to constrain maximum financial exposure. |
| Bypassing local error handlers | Assuming remote network calls will always succeed without interruption. | Temporary network latency or concurrency throttling will crash the entire application process. | Implement robust exception handling specifically targeting rate limits and endpoint unavailability. |
| Syntactic formatting errors | Placing spaces around the assignment operator within local configuration files. | The parsing utility fails to extract the credential, returning empty values to the application logic. | Strictly adhere to the standard key-value formatting convention without interstitial whitespace. |
| Interpreter path mismatch | Pointing the integrated development editor at the global system executable instead of the workspace binary. | The editor displays false syntax warnings indicating that successfully installed dependencies cannot be located. | Manually configure the editor's execution path to target the isolated binary directory. |
| Missing dependency lockfiles | Failing to generate a requirements document representing the exact library versions installed in the environment. | Collaborators construct conflicting environments because the package manager defaults to resolving the newest versions available. | Routinely execute the freeze command to explicitly document the tested versions of all external libraries. |
| Outdated package managers | Executing installations using legacy versions of the package management utility. | The utility fails to interpret modern package distribution formats, resulting in complex compilation errors during installation. | Systematically upgrade the installation utility as the very first command executed within a newly activated workspace. |

## Quiz

**Q1.** An engineer on your team pushes a new artificial intelligence application to the main repository. Another developer clones the code, creates their virtual environment, and runs the script. The application immediately terminates with a message stating that the required authentication token is absent. What is the most appropriate architectural solution to resolve this for the second developer?

<details>
<summary>Answer</summary>
The second developer must create their own local configuration file in their workspace and populate it with their unique credentials. The original developer correctly excluded their secret file from the repository to prevent credential leakage, meaning new collaborators must provision their own environment variables locally before executing the code.
</details>

**Q2.** Your continuous integration pipeline executes a daily batch job that summarizes thousands of customer feedback reports using a language model. Recently, the job has started failing halfway through with an error indicating that the server is refusing connections due to excessive concurrency. How should you modify the application logic to address this specific failure pattern?

<details>
<summary>Answer</summary>
You should wrap the invocation logic in an exception handling block that specifically catches rate limit errors, and then implement a proportional backoff strategy. When the vendor's infrastructure signals that the application is transmitting requests too rapidly, the script should pause execution temporarily before attempting the transmission again, rather than crashing the entire batch job.
</details>

**Q3.** You are reviewing a pull request where a junior developer has implemented a new feature that generates creative marketing copy. The code successfully establishes a connection and retrieves a response, but you notice they have hardcoded a large array of configuration parameters directly into the invocation payload while omitting any constraints on the response length. What specific risk does this introduce, and what recommendation should you provide?

<details>
<summary>Answer</summary>
Omitting a constraint on the response length exposes the project to runaway token generation costs. If the model behaves unexpectedly or enters a recursive pattern, it could consume an enormous amount of output tokens. You should recommend that they explicitly define a maximum token boundary parameter to cap the financial exposure of each individual request.
</details>

**Q4.** A team member is struggling to understand why their integrated development environment highlights every imported scientific library with a red underline, indicating that the modules cannot be found. However, when they execute their script from the terminal interface within the same window, the program runs flawlessly. What configuration discrepancy is causing this visual inconsistency?

<details>
<summary>Answer</summary>
The integrated development environment is currently analyzing the code using the global system interpreter, which lacks the required dependencies. Meanwhile, the terminal session has the virtual environment activated, allowing the script to execute successfully. The developer needs to update the editor's internal settings to point toward the isolated binary directory.
</details>

**Q5.** Your infrastructure team provisions a dedicated server for hosting an internal application. When the deployment script runs, it installs several updated machine learning packages using elevated system privileges. Shortly after, an unrelated background service on the server stops functioning because a shared library was overwritten. How could the deployment script be modified to prevent this cross-application interference?

<details>
<summary>Answer</summary>
The deployment script should construct and activate a discrete virtual environment for the new application before running any package installation commands. This ensures all specific library versions are sandboxed within the project directory, protecting the underlying operating system and other background services from dependency conflicts.
</details>

**Q6.** During a code review, you notice a colleague has written a script that calculates the operational cost of processing documents by tracking the total character count of the input text and the resulting output text. They multiply this character count by the vendor's published pricing metric to project the monthly budget. Why will this calculation produce inaccurate financial projections?

<details>
<summary>Answer</summary>
Language models process text based on tokens, not distinct characters. A token often represents a segment of a word or a common syllable, meaning the character count does not directly translate to the billed volume. The calculation must rely on the explicit token usage metrics returned by the vendor's application programming interface to accurately project costs.
</details>

## Hands-On Exercise

This exercise requires you to construct a completely isolated workspace from scratch and execute a secure, authenticated request to a language model without exposing your credentials.

- [ ] Create a dedicated project directory and navigate into it using your terminal interface.
- [ ] Initialize a new virtual environment using the standard library module and activate it for your current session.
- [ ] Verify the activation by confirming that the active executable path resolves to your local workspace directory.
- [ ] Install the required vendor software development kit and the environment variable loading utility using the local package manager.
- [ ] Construct a hidden configuration file and append the necessary exclusion rule to your local version control configuration.
- [ ] Add a valid authentication token to your configuration file following standard environmental variable syntax.
- [ ] Write a Python script that loads the local configuration, establishes a verified connection to the vendor, and transmits a brief prompt.
- [ ] Execute the script and confirm that it prints the language model's response alongside the explicit token utilization metrics.

## Next Steps

Now that you have established a secure and isolated foundation, you are prepared to advance to **Module 1.2: Foundations of AI-Driven Development**. The environment you configured in this module serves as the reliable execution platform for all subsequent exercises, ensuring you can focus on building intelligent applications rather than fighting configuration drift and unpredictable dependency conflicts.

## Sources

- [CPython venv docs](https://github.com/python/cpython/blob/3.12/Doc/library/venv.rst) — Primary reference for how Python virtual environments work and what isolation they provide.
- [Anthropic Pricing](https://www.anthropic.com/pricing) — Useful for checking current Claude API costs instead of relying on stale course estimates.
