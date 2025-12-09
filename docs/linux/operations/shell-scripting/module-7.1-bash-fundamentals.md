# Module 7.1: Bash Fundamentals

> **Shell Scripting** | Complexity: `[MEDIUM]` | Time: 30-35 min

## Prerequisites

Before starting this module:
- **Required**: [Module 1.1: Kernel Architecture](../../foundations/system-essentials/module-1.1-kernel-architecture.md) for understanding commands
- **Required**: Basic command line experience
- **Helpful**: Any programming experience

---

## Why This Module Matters

Shell scripting is the glue of DevOps. Every operational task—deployments, backups, health checks, log analysis—can be automated with Bash. It's available on every Linux system, no installation required.

Understanding Bash helps you:

- **Automate repetitive tasks** — Stop doing things manually
- **Chain commands together** — Build powerful pipelines
- **Write portable scripts** — Run anywhere Linux runs
- **Work faster in exams** — CKA/CKAD allow shell scripting

Bash is the minimum viable automation skill.

---

## Did You Know?

- **Bash is 35+ years old** — Released in 1989 as a free replacement for the Bourne shell. It's still the default on most Linux distros.

- **POSIX compliance matters** — Scripts using `#!/bin/sh` are more portable but can't use Bash-specific features like arrays. Alpine Linux uses ash, not bash.

- **Exit codes are everything** — Every command returns 0 for success, non-zero for failure. Scripts should check and propagate these codes.

- **Quoting is the #1 source of bugs** — Unquoted variables with spaces break scripts. Always quote: `"$var"` not `$var`.

---

## Script Basics

### First Script

```bash
#!/bin/bash
# This is a comment
echo "Hello, World!"
```

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

### Shebang Line

```bash
#!/bin/bash          # Use Bash
#!/bin/sh            # Use system shell (more portable)
#!/usr/bin/env bash  # Find bash in PATH (most portable)

# The shebang must be the first line, no spaces before #!
```

### Running Scripts

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

---

## Variables

### Basic Variables

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

### Special Variables

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

### Arrays

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

### Command Substitution

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

---

## Conditionals

### If Statements

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

### Test Operators

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

### [[ ]] vs [ ]

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

### Logical Operators

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

---

## Loops

### For Loops

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

### While Loops

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

### Loop Control

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

---

## Functions

### Basic Functions

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

### Arguments and Return

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

### Local Variables

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

---

## Input/Output

### Reading Input

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

### Output

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

### Here Documents

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

---

## Exit Codes and Error Handling

### Exit Codes

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

### Error Handling Options

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

### Defensive Programming

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

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| `name = "John"` | Spaces around `=` | `name="John"` |
| `if [ $var = "x" ]` | Unquoted variable | `if [ "$var" = "x" ]` |
| `echo $array` | Only first element | `echo "${array[@]}"` |
| Not checking `$?` | Silent failures | Use `set -e` or check explicitly |
| `cd` without check | Script continues in wrong dir | `cd dir || exit 1` |
| Parsing `ls` output | Breaks on special filenames | Use globs: `for f in *` |

---

## Quiz

### Question 1
What's wrong with this variable assignment: `name = "John"`?

<details>
<summary>Show Answer</summary>

**Spaces around the `=`** — Bash interprets this as running a command called `name` with arguments `=` and `"John"`.

Correct:
```bash
name="John"
```

No spaces around `=` for variable assignment. This is a common mistake for programmers coming from other languages.

</details>

### Question 2
How do you check if a file exists and is readable?

<details>
<summary>Show Answer</summary>

```bash
if [[ -f "$file" && -r "$file" ]]; then
    echo "File exists and is readable"
fi
```

Or using two tests:
```bash
if [[ -r "$file" ]]; then  # -r implies file exists
    echo "File is readable"
fi
```

Key file tests:
- `-e` exists
- `-f` is regular file
- `-d` is directory
- `-r` is readable
- `-w` is writable
- `-x` is executable

</details>

### Question 3
What does `set -euo pipefail` do?

<details>
<summary>Show Answer</summary>

Three separate options:

- **`-e`** (errexit): Exit immediately if a command fails
- **`-u`** (nounset): Exit if undefined variable is used
- **`-o pipefail`**: Exit if any command in a pipeline fails

Without `pipefail`:
```bash
false | true  # Returns 0 (success)
```

With `pipefail`:
```bash
false | true  # Returns 1 (failure)
```

This is the recommended start for robust scripts.

</details>

### Question 4
How do you iterate over all arguments passed to a script?

<details>
<summary>Show Answer</summary>

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

`$@` expands to all positional parameters as separate strings when quoted.

`$#` gives the count of arguments.

</details>

### Question 5
What's the difference between `$(command)` and `` `command` ``?

<details>
<summary>Show Answer</summary>

Both are **command substitution** — they run the command and substitute its output.

```bash
# Modern syntax (preferred)
now=$(date)

# Old syntax (still works)
now=`date`
```

`$()` advantages:
- Easier to read
- Easier to nest: `$(echo $(date))`
- Clearer what's inside
- Fewer escaping issues

Backticks are legacy syntax — use `$()` in new scripts.

</details>

---

## Hands-On Exercise

### Bash Scripting Practice

**Objective**: Write basic Bash scripts using variables, conditionals, loops, and functions.

**Environment**: Any Linux/Mac system with Bash

#### Part 1: Variables and Arguments

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

#### Part 2: Conditionals

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

#### Part 3: Loops

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

#### Part 4: Functions

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

#### Part 5: Error Handling

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

### Success Criteria

- [ ] Created script with variables and arguments
- [ ] Wrote conditionals for file checking
- [ ] Used loops to process files
- [ ] Created and used functions
- [ ] Implemented error handling with traps

---

## Key Takeaways

1. **Quote your variables** — `"$var"` prevents word splitting bugs

2. **Use `set -euo pipefail`** — Catch errors early

3. **Functions are essential** — For readable, reusable code

4. **`[[ ]]` over `[ ]`** — Safer and more features in Bash

5. **Test with edge cases** — Empty strings, spaces, special characters

---

## What's Next?

In **Module 7.2: Text Processing**, you'll learn grep, sed, awk, and jq—the essential tools for processing text and data in shell scripts.

---

## Further Reading

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/) — Script linter
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
