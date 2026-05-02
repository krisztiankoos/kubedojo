---
revision_pending: false
title: "Module 7.1: Bash Fundamentals"
slug: linux/operations/shell-scripting/module-7.1-bash-fundamentals
sidebar:
  order: 2
lab:
  id: linux-7.1-bash-fundamentals
  url: https://killercoda.com/kubedojo/scenario/linux-7.1-bash-fundamentals
  duration: "35 min"
  difficulty: intermediate
  environment: ubuntu
---

# Module 7.1: Bash Fundamentals

> **Shell Scripting** | Complexity: `[MEDIUM]` | Time: 30-35 min | Focus: safe command orchestration, readable control flow, and defensive automation habits.

## Prerequisites

Before starting this module, make sure you can navigate a Linux shell, run commands with arguments, and recognize when a command succeeds or fails from its visible output and exit status.

- **Required**: [Module 1.1: Kernel Architecture](/linux/foundations/system-essentials/module-1.1-kernel-architecture/) for understanding commands
- **Required**: Basic command line experience
- **Helpful**: Any programming experience

## What You'll Be Able to Do

After this module, you will be able to apply Bash fundamentals to scripts that other operators can run, inspect, and debug without relying on hidden terminal state.

- **Implement** bash scripts with variables, conditionals, loops, and functions that behave correctly when inputs contain spaces or missing values.
- **Diagnose** error handling failures by evaluating exit codes, pipelines, `set -euo pipefail`, and `trap` behavior.
- **Design** argument processing and input validation so scripts fail clearly before they damage files, clusters, or deployment state.
- **Debug** failing scripts with tracing, ShellCheck, and small repeatable tests instead of guessing at command output.

## Why This Module Matters

In 2021, a payments platform running a routine maintenance window lost several hours of transaction processing because a shell script treated an empty variable as a valid target directory. The cleanup job was intended to rotate temporary export files before a database migration, but one missing environment value changed the meaning of the command line. Engineers recovered from backups and internal queues, yet the incident still consumed an overnight response bridge, delayed settlements, and cost the company more in remediation than the original migration project.

That story is not dramatic because Bash is exotic; it is dramatic because Bash is ordinary. The shell sits between humans, operating systems, CI pipelines, package managers, Kubernetes clients, and production automation. A small script can be the safest tool in the room when it validates assumptions, preserves arguments, and reports failures honestly. The same script can become dangerous when it relies on unquoted variables, ignores exit codes, or keeps running after a pipeline has already failed.

This module teaches Bash as operational engineering, not as trivia about syntax. You will write scripts that use variables, conditionals, loops, functions, input, output, and error handling, but the deeper goal is judgment: recognizing when Bash is enough, when it needs guardrails, and when the job deserves a richer language. When Kubernetes examples appear later in the Linux and platform tracks, assume the exam-friendly shortcut `alias k=kubectl` is available, and target Kubernetes 1.35 or newer behavior when a command interacts with cluster resources.

## The Shell Script Contract

A Bash script is a contract between the person who writes it, the shell that interprets it, and the system state it changes. The first line chooses the interpreter, the permission bit decides whether the kernel can execute the file directly, and every command after that inherits a working directory, environment variables, file descriptors, and arguments. Treating those pieces as a contract helps you avoid the beginner mistake of thinking a script is just a saved terminal transcript.

The shebang line is the first visible part of that contract. `#!/bin/bash` says the script intentionally uses Bash, while `#!/bin/sh` promises a smaller POSIX feature set that may be interpreted by `dash`, `ash`, or another shell. `#!/usr/bin/env bash` finds Bash through `PATH`, which can help on systems where Bash is installed outside `/bin`, but it also means the calling environment influences which binary is selected. None of these choices is universally best; the right choice depends on whether portability or Bash-specific safety features matter more for the job.

```bash
#!/bin/bash
# This is a comment
echo "Hello, World!"
```

A first script looks simple because the shell does a lot of work before your code runs. It opens the file, chooses the interpreter, passes the script path as `$0`, and passes the remaining words as positional arguments. That setup means the same text can behave differently depending on whether you execute it directly, run it through `bash script.sh`, or source it into your current shell with `source script.sh`.

```bash
# Create and run
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, World!"
EOF

chmod +x hello.sh
./hello.sh
# Hello, World!
```

Executable scripts are usually easier to reason about in operations because they behave like commands: they receive arguments, return exit codes, and do not unexpectedly modify the caller's shell. Sourced scripts are useful for profile files and shared helper definitions, but they run in the current shell process, so changing a variable or directory inside the file changes the caller as well. Before running this, what output and side effects do you expect from `./script.sh` compared with `source script.sh`?

```bash
#!/bin/bash          # Use Bash
#!/bin/sh            # Use system shell (more portable)
#!/usr/bin/env bash  # Find bash in PATH (most portable)

# The shebang must be the first line, no spaces before #!
```

The mechanics of running a script also affect debugging. If you type `bash script.sh`, the executable bit does not matter because you are explicitly launching Bash and giving it a file to read. If you type `./script.sh`, the executable bit and shebang both matter because the kernel is asked to execute that path. If you source the file, there is no child process boundary, which is powerful for loading functions but risky for general automation.

```bash
# Method 1: Make executable
chmod +x script.sh
./script.sh

# Method 2: Run with interpreter
bash script.sh

# Method 3: Source (runs in current shell)
source script.sh
. script.sh  # Same as source
```

Operational scripts should make their expectations visible. Put the interpreter decision at the top, keep setup close to the entry point, and avoid relying on interactive shell aliases unless the script defines them itself. In an exam shell you might define `alias k=kubectl` for speed, but a script that controls a cluster should either call the binary it needs or document the dependency with a clear command check before it tries to use it.

A helpful way to review any shell script is to ask what promise each line makes. The shebang promises an interpreter, each assignment promises a value, each branch promises a decision rule, and each command promises a side effect or a piece of output. When those promises are implicit, the script may still work for the author, but it becomes hard for another engineer to determine whether a later change is safe. Making the contract explicit is what turns a short script into shared infrastructure.

There is also a security angle to this contract. A script that inherits arbitrary environment values, runs in an unexpected directory, or expands untrusted input without quotes can become an accidental command builder. You do not need to turn every basic script into a hardened security appliance, but you should know which values came from the caller and which values the script created itself. The moment a value crosses that boundary, validation and quoting become part of the design rather than cleanup work.

## Variables, Arguments, and Quoting

Variables in Bash are not typed containers in the way Python or Go variables are. They are mostly strings that the shell expands into command words before a command runs. That expansion step is why assignment has no spaces around `=`, why `${name}` can be clearer than `$name`, and why quoting is not cosmetic. If the expansion produces two words where you expected one path, the command receives two arguments and may do something very different from what the script author intended.

```bash
# Assignment (no spaces around =)
name="John"
count=42

# Using variables
echo "Hello, $name"
echo "Count: ${count}"

# ${} is clearer and required for some cases
file="log"
echo "${file}s"   # logs
echo "$files"     # Empty (no variable named files)

# Read-only
readonly PI=3.14159
PI=3  # Error: PI: readonly variable
```

The most important habit in this section is quoting expansions that should remain a single value. `"$name"` tells Bash to preserve the value as one argument even if it contains spaces, tabs, or wildcard characters. `${file}s` tells Bash where the variable name ends, which prevents accidental lookup of a different variable. `readonly` is useful for constants because it turns accidental reassignment into an immediate error instead of a quiet change in behavior.

```bash
$0          # Script name
$1, $2...   # Positional arguments
$#          # Number of arguments
$@          # All arguments (as separate strings)
$*          # All arguments (as single string)
$?          # Exit code of last command
$$          # Current process ID
$!          # PID of last background command
```

Special variables are the script's view of its calling context. `$#` tells you how many arguments arrived, `$?` reports the last command's exit code, and `"$@"` preserves the original argument boundaries when you need to forward or loop over user input. The difference between `"$@"` and `$*` is not academic when file names contain spaces, Kubernetes resource names are generated by tools, or a CI job passes a flag value that happens to include shell metacharacters.

```bash
# Indexed array
fruits=("apple" "banana" "cherry")
echo ${fruits[0]}      # apple
echo ${fruits[@]}      # All elements
echo ${#fruits[@]}     # Length: 3

# Add element
fruits+=("date")

# Associative array (Bash 4+)
declare -A colors
colors[red]="#FF0000"
colors[green]="#00FF00"
echo ${colors[red]}
```

Arrays let Bash carry a list without flattening it into one string. That matters when you build argument vectors for commands, because each array element remains one word when expanded as `"${array[@]}"`. Associative arrays add named keys, which can be helpful for small lookup tables, but remember that they require Bash 4 or newer. If portability to older macOS system Bash matters, either install a newer Bash or avoid associative arrays in shared scripts.

Command substitution runs a command and replaces the substitution with its standard output. Standard error is not captured unless you redirect it, and the trailing newlines in standard output are removed. Pause and predict: what happens if you run `files=$(ls -l /nonexistent)`? The error message is printed to standard error, the variable receives only standard output, and the assignment's success behavior depends on how you use the command substitution afterward.

```bash
# Modern syntax (preferred)
now=$(date)
files=$(ls -1 | wc -l)

# Old syntax (still works)
now=`date`

# Use in strings
echo "Current time: $(date +%H:%M)"
echo "You have $(ls | wc -l) files"
```

Use `$()` for command substitution because it nests cleanly and is easier to read during reviews. Backticks still work, and you will see them in legacy scripts, but nested backticks require escaping that makes failure modes harder to spot. When command substitution becomes complex, consider whether a named function or temporary variable would make the script easier to test. The goal is not to compress every operation into one line; the goal is to make the data flow obvious.

Quoting deserves repetition because it is the difference between a script that works with the sample input and a script that works with real input. A path copied from a desktop can contain spaces, a generated filename can contain brackets, and an operator can pass an empty string while testing a failure case. Quoting does not make values trusted, but it does preserve their boundaries so the receiving command sees the same argument the caller intended. Once you build that habit, many shell bugs simply stop appearing.

When you need a default, be precise about what "missing" means. `${value:-default}` uses the default when the variable is unset or empty, while other parameter expansion forms distinguish unset from empty. That distinction matters in scripts where an empty value can be intentional, such as clearing a label or disabling an optional field. Beginners often reach for defaults to avoid errors, but experienced operators use them only when the fallback is a genuine part of the workflow.

## Decisions with Conditionals

Conditionals turn shell scripts from command lists into automation that can inspect state and choose a path. The `if` statement itself is simple: it runs a command and checks that command's exit code. In Bash, tests such as `[ "$a" = "$b" ]` and `[[ "$a" = "$b" ]]` are commands or language constructs that return success or failure, so the same mental model applies whether you are checking a string, a file, or a real command.

```bash
# Basic if
if [ condition ]; then
    echo "true"
fi

# If-else
if [ condition ]; then
    echo "true"
else
    echo "false"
fi

# If-elif-else
if [ condition1 ]; then
    echo "first"
elif [ condition2 ]; then
    echo "second"
else
    echo "else"
fi
```

The shape of an `if` block should reveal the decision being made. A script that checks whether a configuration file exists before reading it is not merely avoiding a crash; it is protecting the next command from receiving nonsense input. Good conditionals fail close to the bad assumption and report the value that caused the failure. That habit saves time when a script runs unattended in CI and the only evidence you get is a log file.

```bash
# String comparisons
[ "$a" = "$b" ]     # Equal
[ "$a" != "$b" ]    # Not equal
[ -z "$a" ]         # Empty
[ -n "$a" ]         # Not empty

# Number comparisons
[ "$a" -eq "$b" ]   # Equal
[ "$a" -ne "$b" ]   # Not equal
[ "$a" -lt "$b" ]   # Less than
[ "$a" -le "$b" ]   # Less than or equal
[ "$a" -gt "$b" ]   # Greater than
[ "$a" -ge "$b" ]   # Greater than or equal

# File tests
[ -e "$file" ]      # Exists
[ -f "$file" ]      # Is regular file
[ -d "$dir" ]       # Is directory
[ -r "$file" ]      # Is readable
[ -w "$file" ]      # Is writable
[ -x "$file" ]      # Is executable
[ -s "$file" ]      # Has size > 0
```

The test operators are small, but the distinction between string, number, and file checks is large. `-eq` compares integers, while `=` compares strings, and using the wrong one produces misleading errors when a value is empty or nonnumeric. File tests are often the best defense before a destructive command because they let the script explain what is wrong before attempting the operation. A clear `[[ ! -r "$config_file" ]]` branch is better than letting the next command fail several lines later.

`[[ ]]` is Bash-specific, while `[ ]` is the portable test command. In a Bash script, `[[ ]]` is usually safer because it does not perform word splitting or pathname expansion on unquoted variable expansions, and it supports pattern and regular expression matching. Stop and think: why is `[[ ]]` considered safer than `[ ]`? If `$name` is completely empty and unquoted in `[ $name = "John" ]`, Bash effectively hands `[` a malformed argument list.

```bash
# [[ ]] is Bash-specific but safer
[[ "$name" = "John" ]]      # Works even if $name is empty
[[ "$file" = *.txt ]]       # Pattern matching
[[ "$a" =~ ^[0-9]+$ ]]      # Regex matching

# [ ] is POSIX, more portable
# But requires more quoting
[ "$name" = "John" ]

# Recommendation: Use [[ ]] in Bash scripts
```

Logical operators let you combine decisions, but they can also hide intent if the condition grows too wide. A useful rule is to keep the condition readable enough that a tired reviewer can name the failure case. If the check requires several business rules, split the validation into a function with a meaningful name and return an exit code. That keeps the top-level script focused on control flow while the function owns the details.

```bash
# AND
if [[ condition1 && condition2 ]]; then
    echo "both true"
fi

# OR
if [[ condition1 || condition2 ]]; then
    echo "at least one true"
fi

# NOT
if [[ ! condition ]]; then
    echo "not true"
fi

# With [ ] syntax
if [ condition1 ] && [ condition2 ]; then
    echo "both true"
fi
```

The practical takeaway is that conditionals should document operational intent. A backup script should say whether a target directory is missing, unreadable, or empty. A deployment helper should distinguish "tool missing" from "cluster returned an error" instead of printing one vague failure line. These details feel verbose while writing, but they turn a production page from a mystery into a checklist.

Conditionals also help you separate expected alternatives from exceptional failures. A missing optional report file might be a normal branch, while a missing destination directory might be a hard stop. If both cases are handled with the same generic `echo failed`, the script loses information that could have guided the next action. Write branches that reflect the operational meaning of the condition, not just the mechanical result of a test expression.

For scripts that will be reviewed by teammates, prefer clear positive checks at important boundaries. `if [[ -r "$config_file" ]]; then load_config; else ...` often reads better than deeply nested negative logic, especially when several conditions interact. Negative checks are still useful for early exits, but they should fail with a specific reason. A reviewer should be able to trace the path from input validation to work execution without mentally simulating every possible value.

## Repetition with Loops

Loops are where shell scripts become powerful and where many shell scripts become fragile. The shell's default behavior is to split words and expand globs before the loop body runs, so you need to know whether you are iterating over a literal list, an array, a pathname pattern, or command output. The safest loop is the one that preserves the shape of the data it was given and handles the empty case explicitly.

```bash
# List iteration
for fruit in apple banana cherry; do
    echo "$fruit"
done

# Array iteration
fruits=("apple" "banana" "cherry")
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

# Range
for i in {1..5}; do
    echo "$i"
done

# C-style
for ((i=0; i<5; i++)); do
    echo "$i"
done

# Files
for file in *.txt; do
    echo "Processing $file"
done

# Command output
for pod in $(kubectl get pods -o name); do
    echo "Pod: $pod"
done
```

The final example shows a common trap: command substitution followed by a `for` loop splits on whitespace, so it is safe only when the output format cannot contain spaces and you accept the parsing tradeoff. Kubernetes object names returned by `kubectl get pods -o name` are typically safe enough for quick terminal work, especially if you use `k get pods -o name` after defining `alias k=kubectl`, but scripts should prefer structured output or line-oriented reads when correctness matters. Pause and predict: if you loop over `*.txt` in a directory with no text files, does the loop skip, or does it process the literal string `*.txt`?

```bash
# Basic while
count=0
while [ $count -lt 5 ]; do
    echo "$count"
    ((count++))
done

# Read file line by line
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt

# Read command output
kubectl get pods -o name | while read pod; do
    echo "Pod: $pod"
done

# Infinite loop
while true; do
    echo "Running..."
    sleep 5
done
```

`while IFS= read -r line` is the standard pattern for reading text without trimming leading whitespace or treating backslashes as escapes. It is longer than a naive `for line in $(cat file)` loop, but it preserves the data instead of letting the shell reinterpret it. In operational scripts, preserving the data is almost always worth the extra characters. A log line, path, or JSON fragment can contain spaces that are meaningful to the program reading it.

```bash
# Break
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break
    fi
    echo "$i"
done

# Continue
for i in {1..5}; do
    if [ $i -eq 3 ]; then
        continue
    fi
    echo "$i"
done
```

Loop control is useful when the script has a clear reason to stop early or skip one item. `break` communicates that continuing would be wasteful or unsafe, while `continue` communicates that the current item is not eligible for the remaining work. If either command appears deep inside nested logic, consider moving the loop body into a function. Named functions make it easier to test the decision separately and keep the loop's purpose visible.

Be especially careful when a loop performs side effects. Printing names is harmless, but deleting files, restarting services, or updating cluster resources changes the cost of a bad iteration. A practical pattern is to first write the loop so it prints the exact commands or targets, then replace the print with the real operation only after the target list looks correct. This dry-run mindset catches glob surprises, whitespace bugs, and unexpected empty matches before they become state changes.

Line-oriented loops should also make failure behavior visible. If one item fails, should the script stop, skip the item, retry, or record the failure and continue? There is no universal answer, but there should be an answer in the code. Batch scripts that silently continue after partial failure are painful because the final success message hides the list of items that were never processed correctly.

## Functions and Script Shape

Functions are how Bash scripts become maintainable programs instead of long scrolls of commands. A function packages a decision or operation behind a name, receives arguments through `$1`, `$2`, and friends, and reports success or failure through its return code. It can also print data for command substitution, but that technique works best when the function's standard output is reserved for data and diagnostic messages go to standard error.

```bash
# Definition
greet() {
    echo "Hello, $1!"
}

# Call
greet "World"
# Hello, World!

# Alternative syntax
function greet {
    echo "Hello, $1!"
}
```

The `name() { ...; }` form is widely used and portable across Bash versions. The `function name { ...; }` form is also common in Bash, but it is less portable and offers no major benefit for ordinary scripts. More important than the spelling is the boundary: a function should have a narrow job, validate its inputs, and return a status that the caller can act on. If a function both prints user-facing logs and emits machine-readable data, command substitution becomes harder to use safely.

```bash
# Function arguments
add() {
    local a=$1
    local b=$2
    echo $((a + b))
}

result=$(add 5 3)
echo "5 + 3 = $result"

# Return codes
is_even() {
    if (( $1 % 2 == 0 )); then
        return 0  # Success/true
    else
        return 1  # Failure/false
    fi
}

if is_even 4; then
    echo "4 is even"
fi

# Return string via echo
get_name() {
    echo "John"
}
name=$(get_name)
```

Bash return codes are integers used for control flow, not returned values in the Python sense. A function that computes a string generally prints it, and the caller captures that output. A predicate function returns `0` for true and nonzero for false, which matches how `if command; then` works. This convention may feel inverted if you come from other languages, but it is consistent with the Unix idea that exit code `0` means success.

```bash
# Without local - global scope
broken() {
    x=10  # Modifies global x!
}

# With local - function scope
correct() {
    local x=10  # Only in this function
}

# Always use local for function variables
```

Use `local` for variables that belong inside a function. Without it, Bash variables are global by default, so a helper can accidentally overwrite a value that the main script still needs. Stop and think: what happens if you define a variable without `local` inside a function and then use a variable with the same name in your main script? That bug is hard to see in review because each assignment looks valid in isolation.

A good script often has a `main` function at the bottom that wires together smaller helpers. The helpers check arguments, read configuration, perform work, and return meaningful codes. The top level enables safety settings, installs traps, and calls `main "$@"`. That shape gives you a single entry point while still allowing individual functions to be exercised in small manual tests.

Function boundaries are also a good place to define what output means. A function named `find_config` can print a path to standard output and return nonzero when no usable config exists. A function named `log` can print human messages, ideally to standard error when another command might capture data. Mixing those responsibilities forces callers to parse human text, which is exactly the kind of fragile dependency shell scripts should avoid.

Keep functions small enough that their names remain honest. If `deploy_app` validates arguments, builds artifacts, edits manifests, applies resources, waits for rollout, and sends a notification, it is not one operation anymore; it is an entire workflow hidden behind one label. Splitting the workflow into named helpers makes errors easier to localize and lets future maintainers change one step without rereading the whole script.

## Input, Output, and Failure Signals

Input and output are not just convenience features; they are how scripts communicate with users, pipelines, and other programs. Standard output should carry the data a caller may want to capture, while standard error should carry diagnostics meant for humans or logs. When you separate those streams, a script can be both friendly on a terminal and reliable inside automation.

```bash
# Simple read
echo -n "Enter name: "
read name
echo "Hello, $name"

# With prompt
read -p "Enter name: " name

# Silent (for passwords)
read -sp "Password: " password
echo

# Read with default
read -p "Port [8080]: " port
port=${port:-8080}

# Read with timeout
read -t 5 -p "Quick! " answer || echo "Too slow"
```

Interactive input belongs in scripts meant for humans, not unattended CI jobs. If a script may run without a terminal, prefer flags, environment variables, or configuration files, and validate them before doing work. A default such as `${port:-8080}` is useful when the absence of a value is acceptable, but it can hide a mistake when the value is required. The difference between optional and required input should be explicit in code.

```bash
# stdout
echo "Normal output"
printf "Formatted: %s %d\n" "text" 42

# stderr
echo "Error message" >&2

# Redirect to file
echo "text" > file.txt    # Overwrite
echo "text" >> file.txt   # Append

# Redirect both
command > output.txt 2>&1
command &> output.txt     # Bash shorthand
```

Prefer `printf` when output formatting matters because it is more predictable than `echo` across shells and inputs. Redirection is equally important: `>` overwrites, `>>` appends, `2>&1` combines standard error with standard output, and `&>` is Bash shorthand for redirecting both. Those operators are powerful enough to destroy evidence if misused, so scripts that redirect logs should make file paths obvious and check write permissions before the critical command runs.

```bash
# Here-doc
cat << EOF
This is a multi-line
string with $variables expanded
EOF

# Here-doc without expansion
cat << 'EOF'
This keeps $variables literal
EOF

# Here-doc to command
mysql << EOF
SELECT * FROM users;
EOF
```

Here documents are a readable way to embed templates, sample configuration, or multiline input for another command. Quoting the delimiter, as in `<< 'EOF'`, prevents variable expansion inside the body, which is exactly what you want when generating scripts or configuration that contains literal `$` characters. Leaving the delimiter unquoted expands variables, which is useful for templates but risky when the input contains untrusted text. Before running a here document, decide whether the body is data to preserve or a template to render.

Exit codes are the shell's primary failure signal. Every command returns a status, and an `if` statement asks whether that status represents success. Checking `$?` immediately after a command works, but wrapping the command directly in `if command; then` is usually clearer because it keeps the cause and branch together. The longer the distance between a command and its exit-code check, the easier it is for another command to overwrite `$?`.

```bash
# Exit with code
exit 0   # Success
exit 1   # General error
exit 2   # Misuse of command

# Check last exit code
command
if [ $? -eq 0 ]; then
    echo "Success"
fi

# Or more idiomatically
if command; then
    echo "Success"
else
    echo "Failed"
fi
```

`set -euo pipefail` is a useful safety baseline, but it is not a substitute for understanding control flow. `set -e` exits on many unhandled command failures, `set -u` treats unset variables as errors, and `pipefail` makes a pipeline fail when any command in it fails. These options expose mistakes early, yet they also require intentional handling for commands like `grep` that use nonzero status to mean "not found" rather than "the script is broken."

```bash
#!/bin/bash
set -e          # Exit on error
set -u          # Exit on undefined variable
set -o pipefail # Exit on pipe failure
set -x          # Debug: print commands

# Combined (recommended for scripts)
set -euo pipefail

# Trap errors
trap 'echo "Error on line $LINENO"' ERR

# Trap exit (cleanup)
cleanup() {
    rm -f /tmp/tempfile
}
trap cleanup EXIT
```

Think carefully before putting `set -x` in a script that might handle credentials or sensitive arguments, because tracing prints expanded commands. `trap` gives the script a way to report the failing line or clean temporary files even when a command exits early. Stop and think: if your script uses `set -e` and runs `grep "error" log.txt`, what happens when the word is not found? The answer depends on whether that nonzero status is handled as an expected branch or left as an unhandled failure.

```bash
# Check command exists
command -v kubectl &> /dev/null || {
    echo "kubectl not found" >&2
    exit 1
}

# Check file exists
if [[ ! -f "$config_file" ]]; then
    echo "Config not found: $config_file" >&2
    exit 1
fi

# Default values
name=${1:-"default"}
port=${PORT:-8080}
```

Defensive programming is not pessimism; it is respect for unattended execution. Check that required tools exist, required files are readable, and required variables are present before the script reaches a destructive or expensive operation. When the failure message includes the missing command or path, the next engineer can fix the environment without reading the whole script. That is the difference between automation that scales and automation that creates new handoffs.

The hardest part of `set -euo pipefail` is deciding which failures are expected. A missing match from `grep`, a stopped service in a health check, or an absent optional file may be valid information rather than a reason to abort. Handle those cases close to the command with an `if` statement or a carefully documented fallback. What you should avoid is turning off the safety options globally because one command needed a deliberate exception.

Cleanup deserves the same care as setup. Temporary files should be created with tools designed for that purpose, and cleanup traps should preserve the original exit code so callers are not told that a failed script succeeded. If cleanup itself can fail, report that separately without hiding the original problem. The script's last message should help the next operator understand both the result and the state left behind.

## Debugging as a Practice

Debugging Bash is less about memorizing flags and more about reducing ambiguity. Start by reproducing the failure with the smallest input that still fails, then inspect what the shell is expanding and what each command returns. `set -x` can show expanded commands, ShellCheck can point out common quoting and portability mistakes, and deliberate test cases can prove that paths with spaces, empty arguments, and missing files behave correctly.

A useful debugging session begins with the contract. Which interpreter ran the script? What was the working directory? Which arguments arrived? Which environment variables were required? Which command returned the first unexpected nonzero status? Answering those questions is faster than staring at the final error line, because the final error is often only a symptom of a bad expansion or unchecked assumption earlier in the script.

When a script controls infrastructure, debugging should also protect the target system. Add dry-run modes before destructive commands, print the exact resource or path being changed, and test against temporary files before using real directories. For Kubernetes 1.35 exercises, use `k` interactively for speed after defining the alias, but keep production scripts explicit and testable. The point is to make the script boring under pressure.

ShellCheck is valuable because it encodes years of common shell mistakes, but it should not replace reasoning. If it warns about a variable that should be quoted, understand the word-splitting risk before adding the quotes. If it warns about an intentional pattern, document the exception in the code or refactor the command so the intent is clearer. A linter is most useful when it teaches the team to recognize classes of defects before they land in shared automation.

Small tests are often enough for Bash. You can create temporary files, call a function with known arguments, and assert the output with ordinary shell commands. The point is not to build a huge test framework for every helper script; the point is to capture the cases that have broken before or would be costly to break later. Empty input, spaces in paths, missing commands, and failed pipelines are usually the first cases worth testing.

## Patterns & Anti-Patterns

The strongest Bash scripts are small, explicit, and honest about failure. A proven pattern is to put safety options near the top, define helpers with `local` variables, and call `main "$@"` at the bottom. Use this when the script has more than a handful of commands or when it will run in CI, a runbook, or a shared repository. It scales because the entry point remains stable while helpers can be tested and reviewed independently.

Another strong pattern is validating inputs before doing work. Check argument count with `$#`, check required commands with `command -v`, and check file permissions with `[[ -r "$file" ]]` before opening a file. This works because it moves failure to the edge of the script, where the problem can be explained in user language. It also prevents partial changes, which are usually harder to repair than clean early exits.

Use arrays for command arguments when you need to build a command dynamically. Instead of concatenating a string and asking the shell to split it later, append each argument as an array element and run `"${cmd[@]}"`. This pattern protects spaces and special characters while still letting the script add optional flags. It scales well for wrapper scripts around tools such as `tar`, `rsync`, and cluster clients.

The first anti-pattern is treating Bash as a general-purpose application language. Teams fall into it because Bash is already available and the first version is quick to write. The better alternative is to switch to Python, Go, or another language when the script needs complex parsing, rich data structures, long-lived error handling, or unit-test-heavy business logic. Bash is excellent glue; it is poor concrete for a large application foundation.

The second anti-pattern is parsing human-oriented output when a structured interface exists. `ls`, pretty tables, and default command output are meant for people, so spacing and columns can change or break on unusual names. Prefer globs, null-delimited output, JSON, or explicit machine-readable flags when they are available. In shell scripts, choosing the right output format is often more important than choosing the cleverest pipeline.

The third anti-pattern is relying on ambient shell state. Interactive aliases, current directories, exported variables, and previously created temporary files make scripts pass on one laptop and fail in CI. Define the assumptions the script needs, pass values as arguments or environment variables, and create temporary resources inside the script with cleanup traps. Predictable state is the foundation of repeatable automation.

## Decision Framework

Choose Bash when the task is mostly command orchestration: checking files, calling existing tools, transforming simple text, and returning a clear exit code. Choose a richer language when the task needs nested data, network protocol handling, complex retries, or a large amount of business logic. The decision is not about pride; it is about the failure modes you are willing to own at 03:10 during an incident.

For a one-off terminal action, a command pipeline may be enough if the risk is low and you can see the output immediately. For a repeated team workflow, write a script with a shebang, argument validation, safety settings, and useful errors. For production automation, add logging, dry-run behavior where possible, tests for edge cases, and a clear ownership path. The same Bash feature can be harmless in a terminal and dangerous in an unattended job.

Use this mental flow before writing: first decide whether the input is simple text or structured data, then decide whether failure can be handled with exit codes, then decide whether the script needs to be maintained by other people. If the answer is "structured data, complex recovery, and long-term maintenance," Bash may still launch the tool, but it should not contain the core logic. If the answer is "commands, files, and clear success or failure," Bash is often the fastest reliable choice.

Another useful decision point is observability. A script run by one person at a terminal can rely on immediate visual feedback, but a scheduled job needs logs that explain what happened after the fact. If the script changes important state, add enough output to reconstruct the sequence of targets and decisions without exposing secrets. If the script emits data for another program, keep that data clean and move operational messages to standard error.

Finally, consider ownership. Personal scripts can be optimized for the author's memory, while team scripts need names, usage messages, and failure behavior that survive handoff. The more people depend on a script, the more its interface matters: arguments, environment variables, files touched, exit codes, and output streams become part of a public contract. Bash can support that contract well when the script stays focused and explicit.

## Did You Know?

- **Bash dates to 1989**: Brian Fox released the Bourne Again Shell for the GNU Project as a free software replacement for the Bourne shell, and it remains a default interactive shell on many Linux distributions.
- **POSIX shell is a smaller target**: A script using `#!/bin/sh` should avoid Bash-only features such as arrays, because systems like Alpine Linux commonly link `/bin/sh` to `ash` instead of Bash.
- **Exit code `0` means success**: Unix commands report success with zero and failure with nonzero status, which is why Bash predicate functions return `0` when a condition is true.
- **Quoting prevents word splitting**: Unquoted variables are a leading source of shell bugs because spaces, tabs, and wildcard characters can silently change the number of arguments passed to a command.

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|---------|----------------|---------------|
| `name = "John"` | Bash treats `name` as a command because assignment syntax cannot contain spaces around `=`. | Write `name="John"` and keep assignments visually distinct from comparisons. |
| `if [ $var = "x" ]` | An empty or space-containing value changes the argument list passed to `[`. | Quote expansions as `if [ "$var" = "x" ]` or use `[[ "$var" = "x" ]]` in Bash. |
| `echo $array` | Bash expands only the first indexed element when the array is referenced without an index or `[@]`. | Use `printf '%s\n' "${array[@]}"` or another quoted array expansion. |
| Not checking `$?` | Early scripts are often written as terminal transcripts where failures are visible to the human operator. | Use `if command; then ...` for expected branches and `set -euo pipefail` for unhandled failures. |
| `cd` without check | If the directory change fails, the script continues in the previous directory and may modify the wrong files. | Use `cd dir || exit 1`, or wrap directory changes in a function that reports the failed path. |
| Parsing `ls` output | Human-oriented output breaks on spaces, newlines, hidden files, and locale-specific formatting. | Use globs, `find`, null-delimited formats, or structured command output designed for scripts. |
| Printing diagnostics to standard output | The author tests in a terminal and forgets that another command may capture standard output as data. | Send errors and logs to standard error with `>&2`, and reserve standard output for machine-readable data. |

## Quiz

<details><summary>Question 1: Your script tries `name = "John"` and the log says `name: command not found`. What do you change, and why?</summary>

Bash did not see an assignment because spaces around `=` are not allowed in assignment syntax. It parsed `name` as the command and passed `=` and `"John"` as arguments. The fix is `name="John"`, with no spaces, because that keeps the operation in the shell's assignment grammar. This also shows why shell syntax needs exactness even for simple-looking lines.

```bash
name="John"
```

</details>

<details><summary>Question 2: A backup script receives a config path from `$1`, and the next command will read it. How should the script fail before reading a missing or unreadable file?</summary>

Validate the path before using it, and print the failing path to standard error. A good check is `[[ -f "$file" && -r "$file" ]]` when you specifically need a regular readable file, or `[[ -r "$file" ]]` when readability alone is enough. This maps directly to the outcome of designing input validation because the script refuses to proceed with bad state. The important point is that the failure happens before any backup operation depends on invalid input.

```bash
if [[ -f "$file" && -r "$file" ]]; then
    echo "File exists and is readable"
fi
```

```bash
if [[ -r "$file" ]]; then  # -r implies file exists
    echo "File is readable"
fi
```

</details>

<details><summary>Question 3: Your CI script runs `curl -s https://api.example.com/data | jq '.items' > output.json`, `curl` fails, and the job still continues. Why can this happen with `set -e`, and what should you add?</summary>

Without `pipefail`, a pipeline's status is normally the status of the last command, so a failure earlier in the pipeline can be hidden when the last command exits successfully. `set -e` only reacts to the pipeline status it receives, so it may not stop the script. Add `set -o pipefail`, usually as part of `set -euo pipefail`, and consider validating that the output is nonempty or structurally correct. The fix matters because downstream steps should not consume a file produced from a failed fetch.

```bash
false | true  # Returns 0 (success)
```

```bash
false | true  # Returns 1 (failure)
```

</details>

<details><summary>Question 4: Your deployment helper loops over file paths passed as arguments, and one path is `report 2023.pdf`. Which expansion preserves each original argument?</summary>

Use `for arg in "$@"; do ...; done`. Quoted `"$@"` expands each positional parameter as a separate quoted word, preserving spaces inside individual arguments. Unquoted `$@` or `$*` allows word splitting, which would turn one path into multiple loop iterations. This is the safe pattern for scripts that forward user input or operate on file names.

```bash
# Using $@
for arg in "$@"; do
    echo "$arg"
done

# Important: Quote "$@" to handle spaces
./script.sh "hello world" foo
# With "$@": two iterations - "hello world", "foo"
# With $@: three iterations - "hello", "world", "foo"
```

</details>

<details><summary>Question 5: A helper function sets `status=failed` without `local`, and later the main script sees the wrong status. How do you diagnose and fix the bug?</summary>

The function changed a global variable because Bash variables are global unless declared `local` inside a function. You can diagnose it by tracing the script or by printing the variable before and after the function call in a small reproduction. The fix is to declare function-owned variables with `local status=failed` and return information through exit codes or intentional output. This keeps function internals from corrupting the caller's state.

</details>

<details><summary>Question 6: A script uses `grep "error" log.txt` under `set -e`, and the absence of matching lines stops the script. Is the script wrong, or is the error handling too broad?</summary>

The script is treating an expected non-match as an unhandled failure. `grep` returns nonzero when it finds no matches, and under `set -e` that status can stop the script unless it is handled intentionally. Wrap the command in an `if grep ...; then` branch, or use a controlled fallback such as `grep ... || true` only when the non-match is truly acceptable and documented. The better solution depends on whether "no errors found" is a success case for the workflow.

</details>

<details><summary>Question 7: Your team wants one script to parse nested JSON, retry network calls with backoff, and update several state files. Would you keep the core logic in Bash?</summary>

Bash can launch the tools involved, but it is a poor fit for complex state, structured parsing, and long recovery logic. A richer language gives you safer data structures, clearer tests, and more maintainable error handling. The practical design is often a small Bash wrapper that validates the environment and then calls a Python or Go program for the core work. That decision reduces operational risk rather than making the solution less "shell native."

```bash
# Modern syntax (preferred)
now=$(date)

# Old syntax (still works)
now=`date`
```

</details>

## Hands-On Exercise

This lab turns the concepts into small scripts you can run on any Linux or macOS system with Bash. Work in `/tmp` so the exercise stays isolated, and read each script before executing it. The goal is not to memorize every operator; it is to practice the workflow of writing a small contract, validating inputs, running the script, and observing the exact output.

### Part 1: Variables and Arguments

Create a script that accepts an optional name argument and an optional greeting from the environment. This first task shows how defaults work and how `$0`, `$#`, and positional parameters give a script context about its caller.

```bash
# Create a script
cat > /tmp/greet.sh << 'EOF'
#!/bin/bash

# Get name from argument or default
name=${1:-"World"}

# Get greeting from environment or default
greeting=${GREETING:-"Hello"}

echo "$greeting, $name!"
echo "Script: $0"
echo "Arguments: $#"
EOF

chmod +x /tmp/greet.sh

# Test it
/tmp/greet.sh
/tmp/greet.sh Alice
GREETING="Hi" /tmp/greet.sh Bob
```

<details><summary>Solution notes for Part 1</summary>

The first run uses both defaults, the second run replaces the name, and the third run replaces the greeting through the environment for that single command. Notice that the script does not need interactive input, which makes it easy to repeat in a terminal or CI job. Try adding a quoted name such as `"Alice Example"` and confirm that the script treats it as one argument.

</details>

### Part 2: Conditionals

Now build a file checker that validates the argument before making claims about the path. This script demonstrates empty-input checks, file type checks, command substitution, and portable handling for file size on macOS and Linux.

```bash
cat > /tmp/check_file.sh << 'EOF'
#!/bin/bash
set -euo pipefail

file=${1:-""}

if [[ -z "$file" ]]; then
    echo "Usage: $0 <filename>" >&2
    exit 1
fi

if [[ ! -e "$file" ]]; then
    echo "Does not exist: $file"
elif [[ -d "$file" ]]; then
    echo "Directory: $file"
    echo "Contents: $(ls -1 "$file" | wc -l) items"
elif [[ -f "$file" ]]; then
    echo "File: $file"
    echo "Size: $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file") bytes"
    [[ -r "$file" ]] && echo "Readable: yes" || echo "Readable: no"
    [[ -w "$file" ]] && echo "Writable: yes" || echo "Writable: no"
fi
EOF

chmod +x /tmp/check_file.sh
/tmp/check_file.sh /tmp
/tmp/check_file.sh /etc/passwd
/tmp/check_file.sh /nonexistent
```

<details><summary>Solution notes for Part 2</summary>

You should see different branches for a directory, a regular file, and a missing path. The script sends usage errors to standard error and exits with a nonzero status when no argument is provided. The `stat` command differs between macOS and Linux, so the command substitution tries the macOS form first and falls back to the GNU form.

</details>

### Part 3: Loops

The loop task counts lines in shell scripts under a chosen directory. It uses a glob and then checks each candidate with `[[ -f "$file" ]]`, which protects the script from treating a non-file match as valid input.

```bash
cat > /tmp/count_lines.sh << 'EOF'
#!/bin/bash
set -euo pipefail

dir=${1:-.}

echo "Counting lines in $dir"
echo "========================"

total=0
for file in "$dir"/*.sh 2>/dev/null; do
    if [[ -f "$file" ]]; then
        lines=$(wc -l < "$file")
        echo "$file: $lines lines"
        total=$((total + lines))
    fi
done

if [[ $total -eq 0 ]]; then
    echo "No .sh files found"
else
    echo "========================"
    echo "Total: $total lines"
fi
EOF

chmod +x /tmp/count_lines.sh
/tmp/count_lines.sh /tmp
```

<details><summary>Solution notes for Part 3</summary>

The script should report the `.sh` files you created in earlier steps and print a total. If you run it against a directory without shell scripts, it should explain that no matching files were found. This is the behavior you want from loops in operations: every input path either gets processed intentionally or skipped intentionally.

</details>

### Part 4: Functions

This utility script introduces functions for logging and dependency checks. Notice how the helper returns success or failure while `main` decides what that means for the workflow.

```bash
cat > /tmp/utility.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Logging function
log() {
    local level=$1
    shift
    echo "[$(date +%H:%M:%S)] [$level] $*"
}

# Check if command exists
require() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        log ERROR "Required command not found: $cmd"
        return 1
    fi
    return 0
}

# Main
main() {
    log INFO "Starting utility script"

    if require ls; then
        log INFO "ls is available"
    fi

    if require nonexistent_cmd; then
        log INFO "Command available"
    else
        log WARN "Missing optional command"
    fi

    log INFO "Done"
}

main "$@"
EOF

chmod +x /tmp/utility.sh
/tmp/utility.sh
```

<details><summary>Solution notes for Part 4</summary>

The missing command branch should not crash the script because `main` handles the nonzero return from `require`. The function uses `local` variables so the helper does not leak state into the rest of the script. This is the same structure you can use for required dependencies by changing the caller's branch to exit when a command is missing.

</details>

### Part 5: Error Handling

The final task adds cleanup and error reporting. Read the traps before running the script, then intentionally add a failing command above the final echo to see how the error and cleanup handlers behave.

```bash
cat > /tmp/safe_script.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Cleanup on exit
cleanup() {
    local exit_code=$?
    echo "Cleaning up (exit code: $exit_code)..."
    rm -f /tmp/safe_script_temp_*
    exit $exit_code
}
trap cleanup EXIT

# Error handler
on_error() {
    echo "Error on line $1" >&2
}
trap 'on_error $LINENO' ERR

# Main logic
echo "Creating temp file..."
tempfile=$(mktemp /tmp/safe_script_temp_XXXXXX)
echo "Temp file: $tempfile"

echo "Writing data..."
echo "Hello" > "$tempfile"

echo "Reading data..."
cat "$tempfile"

echo "Done - cleanup will run automatically"
EOF

chmod +x /tmp/safe_script.sh
/tmp/safe_script.sh
```

<details><summary>Solution notes for Part 5</summary>

The cleanup function runs whether the script succeeds or fails because it is attached to `EXIT`. The error handler reports the line that triggered `ERR`, which gives you a starting point for diagnosis. Preserve the original exit code in cleanup so callers still know whether the script succeeded.

</details>

### Success Criteria

- [ ] Created script with variables and arguments
- [ ] Wrote conditionals for file checking
- [ ] Used loops to process files
- [ ] Created and used functions
- [ ] Implemented error handling with traps

## Next Module

[Module 7.2: Text Processing](/linux/operations/shell-scripting/module-7.2-text-processing/) builds on this foundation with `grep`, `sed`, `awk`, and `jq` so your scripts can transform real command output without brittle parsing.

## Further Reading

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/) - Script linter
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [GNU Bash Manual: Shell Parameters](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameters.html)
- [GNU Bash Manual: Conditional Constructs](https://www.gnu.org/software/bash/manual/html_node/Conditional-Constructs.html)
- [GNU Bash Manual: Bourne Shell Builtins](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- [GNU Bash Manual: Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [GNU Bash Manual: Bash Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html)
- [Kubernetes kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
