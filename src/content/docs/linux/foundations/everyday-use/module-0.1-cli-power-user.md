---
title: "Module 0.1: The CLI Power User (Search & Streams)"
slug: linux/foundations/everyday-use/module-0.1-cli-power-user
sidebar:
  order: 2
lab:
  id: "linux-0.1-cli-power-user"
  url: "https://killercoda.com/kubedojo/scenario/linux-0.1-cli-power-user"
  duration: "30 min"
  difficulty: "intermediate"
  environment: "ubuntu"
---
**Complexity:** [QUICK]
**Time to Complete:** 45 minutes
**Prerequisites:** Zero to Terminal (Module 0.8)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Chain** commands with pipes, redirects, and subshells to build powerful one-liners *(Assessed in Quiz Q6, Exercise Task 6)*
- **Search** files and content efficiently using find, grep, and xargs *(Assessed in Quiz Q1, Q4, Q7, Exercise Task 5)*
- **Process** text streams with cut, sort, uniq, awk, and sed for log analysis *(Assessed in Quiz Q5, Exercise Tasks 3 & 4)*
- **Redirect** stdout, stderr, and combine streams for scripting and debugging *(Assessed in Quiz Q2, Q3, Q8, Exercise Task 2)*

---

## Why This Module Matters

Picture this: it is 2 AM and your pager goes off. The web application is returning 500 errors. Somewhere in 47 log files spread across `/var/log`, there is a clue -- a stack trace, a timeout, a connection refused. You could open each file one by one, scroll through thousands of lines with your tired eyes, and hope you spot the word "error" before sunrise. Or you could type one line:

```bash
grep -ri "error" /var/log/app/ | grep -i "database" | tail -20
```

Three seconds later, you have the 20 most recent database-related errors across every log file. Problem identified. Fix deployed. Back to sleep by 2:15 AM.

That is the difference this module makes. You already know how to navigate the filesystem and run basic commands from Module 0.8. Now you are going to learn how to *combine* those commands into powerful workflows. You will learn to search for files, search *inside* files, control where output goes, and chain commands together like building blocks.

These are not advanced tricks. These are everyday tools that Linux professionals use hundreds of times a day. By the end of this module, you will feel like you have a superpower -- because you will.

---

## 1. Wildcards: Pattern Matching for the Impatient

Typing out full file names is slow and error-prone. Wildcards (also called "globs") let you match multiple files using patterns. The shell expands them *before* the command even runs.

### The Asterisk `*` -- Match Anything

The `*` matches zero or more characters of any kind.

```bash
# List every .txt file in the current directory
ls *.txt
# Matches: notes.txt, readme.txt, a.txt
# Does NOT match: notes.txt.bak (doesn't end with .txt)

# List every file that starts with "report"
ls report*
# Matches: report.pdf, report_2024.csv, report-final.docx, reports/

# Remove all JPEG images
rm *.jpg
# Matches: photo.jpg, screenshot.jpg, a.jpg

# Copy all Python files to a backup directory
cp *.py ~/backup/

# List files with "config" anywhere in the name
ls *config*
# Matches: config.yaml, app-config.json, myconfig, config_backup.tar.gz
```

### The Question Mark `?` -- Match Exactly One Character

The `?` matches exactly one character -- no more, no less.

```bash
# List files like file1.txt, file2.txt, fileA.txt
ls file?.txt
# Matches: file1.txt, fileA.txt, filex.txt
# Does NOT match: file12.txt (two characters where ? expects one)
# Does NOT match: file.txt (zero characters where ? expects one)

# Match two-character extensions
ls *.??
# Matches: archive.gz, image.py, data.js
# Does NOT match: readme.txt (three-character extension)

# Match log files with single-digit rotation number
ls app.log.?
# Matches: app.log.1, app.log.2, app.log.9
# Does NOT match: app.log.10
```

### Square Brackets `[]` -- Match From a Set

Square brackets match exactly one character, but only from the characters you specify.

```bash
# Match specific characters
ls file[abc].txt
# Matches: filea.txt, fileb.txt, filec.txt
# Does NOT match: filed.txt

# Match a range of characters
ls data[0-9].csv
# Matches: data0.csv, data1.csv, ... data9.csv

# Match uppercase letters
ls report[A-Z].pdf
# Matches: reportA.pdf, reportB.pdf, ... reportZ.pdf

# Combine ranges
ls log[0-9a-f].txt
# Matches: log0.txt, loga.txt, logf.txt
# Does NOT match: logg.txt (g is outside the range)

# Negate with ! or ^ -- match anything EXCEPT these
ls file[!0-9].txt
# Matches: filea.txt, fileZ.txt
# Does NOT match: file1.txt, file9.txt
```

### Curly Braces `{}` -- Generate Multiple Strings

Curly braces are not technically wildcards (they are a Bash expansion feature called "brace expansion"), but they are used constantly alongside wildcards.

```bash
# Create multiple files at once
touch report_{jan,feb,mar}.txt
# Creates: report_jan.txt, report_feb.txt, report_mar.txt

# Backup a file with a new extension
cp config.yaml{,.bak}
# Expands to: cp config.yaml config.yaml.bak

# Create a directory structure
mkdir -p project/{src,tests,docs}
# Creates three subdirectories inside project/
```

> **Pause and predict**: If you type `echo file_{1,2,3}.txt`, what exact string will the shell print to the screen before any files are created?

> **Key insight:** The shell expands wildcards *before* the command sees them. When you type `ls *.txt`, the shell turns it into something like `ls notes.txt readme.txt todo.txt` and then runs `ls` with those three arguments. The `ls` command never sees the `*` at all.

---

## 2. Streams: How Data Flows Through Commands

Every single command in Linux works with three invisible channels of data. Understanding these channels is the foundation for everything else in this module.

```mermaid
flowchart LR
    Keyboard["Keyboard<br/>(stdin)<br/>Stream 0"] --> Command["Your Command<br/>(e.g., grep)"]
    Command -- "Stream 1" --> Stdout["Screen<br/>(stdout)"]
    Command -- "Stream 2" --> Stderr["Screen<br/>(stderr)"]
```

> **Pause and predict**: If you run a command that produces both normal output and an error message, and you redirect stream 1 (`>`) to a file, what will you see on your terminal screen?

- **stdin (stream 0):** Where the command reads its input. By default, this is your keyboard. But it can be a file or the output of another command.
- **stdout (stream 1):** Where the command sends its normal results. By default, this is your terminal screen.
- **stderr (stream 2):** Where the command sends error messages. Also goes to your screen by default -- but it is a *separate* stream from stdout.

Why are stdout and stderr separate? Because you often want to handle them differently. You might want to save normal output to a file while still seeing errors on screen. Or you might want to hide errors while keeping the output. The separation gives you that control.

---

## 3. Redirection: Controlling Where Output Goes

Redirection lets you reroute those three streams -- sending output to files instead of the screen, or reading input from files instead of the keyboard.

### `>` Redirect Output (Overwrite)

Sends stdout to a file. **Warning:** this destroys the existing contents of the file.

```bash
# Save a directory listing to a file
ls -la /etc > etc_contents.txt

# Save the current date and time
date > timestamp.txt

# Save your system's hostname
hostname > server_info.txt
```

### `>>` Redirect Output (Append)

Adds stdout to the end of a file. Existing contents are preserved.

```bash
# Build a log file over time
echo "=== Deploy started ===" >> deploy.log
echo "Version: 2.4.1" >> deploy.log
echo "=== Deploy finished ===" >> deploy.log

# Append today's disk usage to a daily report
df -h >> /var/log/daily_disk_report.txt
```

**Real-world use case -- simple logging:**

```bash
# Every time this script runs, it appends a timestamped entry
echo "$(date): Backup completed successfully" >> /var/log/backup.log
```

### `2>` Redirect Errors

Sends only stderr (stream 2) to a file. Normal output still goes to the screen.

```bash
# Try listing a directory you can't access -- send errors to a file
ls /root 2> errors.log
# The "Permission denied" error goes to errors.log, not your screen

# Run find without being spammed by permission errors
find / -name "nginx.conf" 2> /dev/null
# /dev/null is Linux's black hole -- errors vanish, results appear on screen
```

### `&>` Redirect Everything

Sends both stdout and stderr to the same file.

```bash
# Capture all output from a build process
make build &> build_output.log

# Run a script and capture everything for debugging
./deploy.sh &> deploy_full_log.txt
```

### `<` Redirect Input

Sends the contents of a file into a command's stdin (instead of typing from the keyboard).

```bash
# Count lines, words, and characters in a file
wc < report.txt

# Sort the contents of a file
sort < unsorted_names.txt

# Send an email with file contents as the body (if mail is configured)
mail -s "Report" admin@example.com < report.txt
```

### Combining Redirections

You can redirect stdout and stderr to *different* files:

```bash
# Save output to one file and errors to another
find / -name "*.conf" > results.txt 2> errors.txt

# Save output to a file, throw away errors
grep -r "TODO" /project > todos.txt 2> /dev/null
```

**The /dev/null trick:** `/dev/null` is a special file that discards everything written to it. Think of it as a black hole. It is incredibly useful when you want to suppress output you do not care about.

```bash
# Run a command silently -- no output, no errors
command_that_is_noisy > /dev/null 2>&1

# Check if a command succeeds without caring about output
if grep -q "ready" status.txt 2> /dev/null; then
    echo "System is ready"
fi
```

---

## 4. Pipes: The Assembly Line

Pipes (`|`) are the single most powerful concept in this module. A pipe takes the stdout of one command and feeds it directly into the stdin of the next command. No temporary files needed.

Think of it like a factory assembly line: each machine (command) does one small job and passes the result to the next machine.

```mermaid
flowchart LR
    cmd1["cmd1"] -- "stdout becomes stdin" --> cmd2["cmd2"]
    cmd2 -- "stdout becomes stdin" --> cmd3["cmd3"]
    cmd3 -- "stdout becomes stdin" --> cmd4["cmd4"]
    cmd4 -- "stdout" --> final["Final output"]
```

> **Stop and think**: If `cmd2` in the assembly line fails and produces an error message (stderr), does that error flow into `cmd3`? (Hint: look at which stream the pipe connects!)

### Starting Simple

```bash
# List files and scroll through the output page by page
ls -la /etc | less

# Count how many files are in a directory
ls /etc | wc -l

# Show only the first 5 largest files
du -sh /var/log/* | sort -rh | head -5
```

### Building Up: Two-Command Pipes

```bash
# Find all running processes containing "nginx"
ps aux | grep nginx

# Show disk usage sorted by size (largest first)
du -sh /home/* | sort -rh

# List only directories in the current location
ls -la | grep "^d"

# Show unique shells used on the system
cat /etc/passwd | cut -d: -f7 | sort -u
```

### The Real Power: Multi-Command Chains

Here is where pipes really shine. Each step does one simple thing, but together they solve complex problems.

```bash
# Find the 5 IP addresses that hit your web server most often
cat /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
# Step by step:
# 1. cat: read the log file
# 2. awk '{print $1}': extract the first field (IP address) from each line
# 3. sort: sort the IPs alphabetically (required for uniq)
# 4. uniq -c: count consecutive duplicate lines
# 5. sort -rn: sort by count, numerically, in reverse (highest first)
# 6. head -5: show only the top 5

# Find which processes are using the most memory
ps aux | sort -k4 -rn | head -10 | awk '{print $4"% "$11}'
# Shows: memory percentage and command name for top 10 processes

# Count how many times each HTTP status code appears in a log
cat access.log | awk '{print $9}' | sort | uniq -c | sort -rn
# Output might look like:
# 15234 200
#  2341 304
#   187 404
#    23 500
```

### The "Before and After" -- Why Pipes Change Everything

**Without pipes (the hard way):**

```bash
# Step 1: Save all process info to a temp file
ps aux > /tmp/all_processes.txt
# Step 2: Search that file for python
grep python /tmp/all_processes.txt > /tmp/python_processes.txt
# Step 3: Count the lines
wc -l /tmp/python_processes.txt
# Step 4: Clean up temp files
rm /tmp/all_processes.txt /tmp/python_processes.txt
```

**With pipes (the power user way):**

```bash
ps aux | grep python | wc -l
```

One line. No temp files. No cleanup. Same result.

---

## 5. `find`: Locating Files Like a Detective

The `find` command searches the filesystem for files and directories that match criteria you specify. Unlike `ls`, it searches recursively through subdirectories by default.

**Basic syntax:** `find [where to look] [what to match]`

### Find by Name

```bash
# Find a file named exactly "config.yaml" starting from current directory
find . -name "config.yaml"

# Find all YAML files (case-sensitive)
find . -name "*.yaml"

# Find all YAML files (case-insensitive -- also matches .YAML, .Yaml)
find . -iname "*.yaml"

# Find in a specific directory
find /etc -name "*.conf"
```

### Find by Type

```bash
# Find only directories
find . -type d

# Find only regular files (not directories, not symlinks)
find . -type f

# Find only symbolic links
find . -type l

# Find all directories named "test"
find . -type d -name "test"
```

### Find by Size -- Real-World Scenarios

```bash
# Find files larger than 100 MB (hunting disk space hogs)
find /var -type f -size +100M

# Find files larger than 1 GB
find / -type f -size +1G 2> /dev/null

# Find small files (less than 1 KB) -- possible empty or junk files
find . -type f -size -1k

# Find files exactly 0 bytes (empty files)
find . -type f -empty
```

### Find by Time -- What Changed Recently?

```bash
# Find files modified in the last 24 hours
find /var/log -type f -mtime -1

# Find files modified in the last 30 minutes
find . -type f -mmin -30

# Find files NOT modified in the last 90 days (stale files)
find /home -type f -mtime +90

# Find files accessed in the last hour
find . -type f -amin -60
```

> **Pause and predict**: If you want to find log files older than 30 days and immediately delete them, how could you combine the `-mtime` and `-delete` actions in a single `find` command?

### Find with Actions

`find` can do things with the files it discovers, not just list them.

```bash
# Delete all .tmp files (BE CAREFUL -- no undo!)
find /tmp -name "*.tmp" -delete

# Run a command on each file found (-exec)
find . -name "*.log" -exec wc -l {} \;
# {} is replaced with each filename found
# \; marks the end of the -exec command

# Change permissions on all shell scripts
find . -name "*.sh" -exec chmod +x {} \;

# Print results with details (like ls -l)
find . -name "*.conf" -ls
```

> **Tip:** Always quote your patterns in `find`. If you write `find . -name *.txt` without quotes and there are .txt files in your current directory, the shell will expand `*.txt` before `find` sees it, and you will get unexpected results. Always use `find . -name "*.txt"`.

---

## 6. `grep`: Searching Inside Files

While `find` locates files by name, size, or date, `grep` looks *inside* files for text that matches a pattern. It prints every line that contains a match.

**Basic syntax:** `grep [options] "pattern" file`

### Basic Searches

```bash
# Find lines containing "error" in a log file
grep "error" /var/log/syslog

# Case-insensitive search (matches Error, ERROR, error, eRRoR)
grep -i "error" /var/log/syslog

# Search multiple files at once
grep "timeout" server1.log server2.log server3.log

# Search all files in a directory recursively
grep -r "password" /etc/
# CAUTION: this can reveal sensitive information -- use responsibly
```

### Context -- Show Surrounding Lines

When you find a match, you often need to see what is happening around it. That is what `-A`, `-B`, and `-C` are for.

```bash
# Show 3 lines AFTER each match (A = After)
grep -A 3 "Exception" app.log
# Great for seeing stack traces that follow an error

# Show 2 lines BEFORE each match (B = Before)
grep -B 2 "failed" deploy.log
# Great for seeing what command caused a failure

# Show 3 lines before AND after each match (C = Context)
grep -C 3 "timeout" app.log
# The full picture around each match

# Combine with case-insensitive
grep -i -C 5 "critical" /var/log/syslog
```

### Counting and Listing

```bash
# Count matching lines (instead of showing them)
grep -c "404" access.log
# Output: 187 (just the number)

# Show only filenames that contain a match (not the lines themselves)
grep -rl "TODO" /project/src/
# Output: list of files, one per line

# Show line numbers alongside matches
grep -n "def main" *.py
# Output: main.py:42:def main():
```

### Inverting and Exact Matching

```bash
# Show lines that do NOT match (invert)
grep -v "DEBUG" app.log
# Shows everything except debug lines -- great for reducing noise

# Match whole words only (not partial matches)
grep -w "error" app.log
# Matches "error" but NOT "errors" or "error_handler"

# Match at the start or end of a line
grep "^#" config.conf     # Lines starting with # (comments)
grep "\.conf$" filelist    # Lines ending with .conf
```

### grep with Pipes -- The Most Common Pattern

You will use `grep` with pipes more than any other combination in Linux.

```bash
# Find running processes by name
ps aux | grep nginx

# Filter command history
history | grep "docker"

# Find listening network ports for a specific service
ss -tlnp | grep 8080

# Check if a package is installed (Debian/Ubuntu)
dpkg -l | grep "nginx"

# Find environment variables related to Java
env | grep -i java
```

> **Stop and think**: If you use `grep -v "INFO" app.log | grep -v "DEBUG"`, what kind of log levels are you attempting to isolate in the output?

---

## 7. The Power Combo: find + grep + Pipes

The real magic happens when you combine these tools. This is how experienced Linux users solve real problems.

### Scenario 1: Find All Config Files Containing a Specific Database Host

```bash
find /etc -name "*.conf" -exec grep -l "db.example.com" {} \;
```

This finds every `.conf` file under `/etc`, then checks each one for the text "db.example.com", and prints only the filenames that contain it.

### Scenario 2: Search for a Function Definition Across a Project

```bash
find . -name "*.py" | xargs grep -n "def process_order"
```

Here, `find` lists all Python files, and `xargs` passes that list to `grep`, which searches each file for the function definition and shows the line number.

### Trade-Off: `find -exec` vs `xargs`

You might notice two ways to run commands on found files: `find . -name "*.log" -exec grep "ERROR" {} \;` and `find . -name "*.log" | xargs grep "ERROR"`. Which is better? It depends entirely on scale.

The `-exec ... \;` method runs the command *once for every single file*. If you find 10,000 files, Linux starts the `grep` process 10,000 times. This is completely safe regarding weird filenames, but it is extremely slow due to process overhead.

The `xargs` method batches the files. It runs `grep "ERROR" file1 file2 file3 ...` up to the system's character limit, drastically reducing the number of processes started. It is blazing fast for massive directories. However, `xargs` can stumble if filenames contain spaces (unless you use the safer `find -print0 | xargs -0` variant). **Rule of thumb**: Use `-exec` for a few files or complex command strings, but switch to `xargs` when performance matters and you are parsing thousands of files.

> **Pause and predict**: If you have 10,000 files to search and you use `find -exec grep ... \;`, how many separate `grep` processes will the Linux kernel have to start and stop?

### Scenario 3: Find Large Log Files Modified Today

```bash
find /var/log -name "*.log" -size +10M -mtime -1 -exec ls -lh {} \;
```

Finds log files bigger than 10 MB that were modified in the last 24 hours, and shows their details.

### Scenario 4: Count TODO Comments Across a Codebase

```bash
find . -name "*.js" -o -name "*.ts" | xargs grep -c "TODO" | grep -v ":0$"
```

Finds all JavaScript and TypeScript files, counts TODO occurrences in each, and filters out files with zero TODOs.

### Scenario 5: Find and Kill a Runaway Process

```bash
ps aux | grep "[r]unaway_script" | awk '{print $2}' | xargs kill
```

The `[r]` trick prevents grep from matching its own process. `awk` extracts the PID (second column), and `xargs` passes it to `kill`.

---

## War Story: The 3 AM Log Hunt

A few years ago, a junior engineer got paged because the company's payment processing was failing. They SSH'd into the server, opened `/var/log/app.log` in `nano`, and started scrolling. The file was 2 GB. Nano froze. They tried `vi`. It loaded, slowly, and they started searching manually. Forty-five minutes later, they still had not found the issue.

A senior engineer joined the call and typed:

```bash
grep -i "payment" /var/log/app.log | grep -i "error" | tail -20
```

Eight seconds later they had the answer: a third-party payment gateway had changed their API endpoint. The fix was a one-line config change.

The junior engineer could have found it in under a minute with the tools you just learned. The lesson is not that scrolling through files is bad -- it is that *knowing your tools transforms you from someone who reacts slowly to someone who solves problems fast*. That is what makes you valuable in an on-call rotation, in a job interview, and in your daily work.

---

## Did You Know?

1. **The name `grep` is an acronym.** It stands for "**G**lobal **R**egular **E**xpression **P**rint." It comes from a command in the ancient `ed` text editor: `g/re/p`. The tool was written by Ken Thompson in 1973 and has barely changed since -- because it did not need to.

2. **Pipes were invented over a lunch break.** Doug McIlrath proposed the idea of connecting programs together at Bell Labs in 1964. Ken Thompson liked it so much that he added pipe support to Unix overnight. The `|` symbol was chosen because it was rarely used and looked like a physical pipe.

3. **`/dev/null` has been called "the most useful file in Unix."** Everything written to it vanishes instantly. It has been a part of Unix since 1971. In internet culture, "sending something to /dev/null" means ignoring it completely.

4. **The `find` command can replace dozens of GUI clicks.** A task like "find all PDF files modified in the last week that are larger than 5 MB" would take minutes of clicking through folder after folder in a graphical file manager. With `find`, it is one line: `find . -name "*.pdf" -mtime -7 -size +5M`.

---

## Common Mistakes

| Mistake | Why It Happens | How to Fix It |
|:---|:---|:---|
| Using `>` when you meant `>>` | You wanted to append to a log file but accidentally overwrote it, destroying all previous entries. | Pause and think: "Do I want to *replace* or *add to*?" When in doubt, use `>>`. You can always clean up a file later, but you cannot un-overwrite one. |
| Forgetting quotes around wildcards in `find` | Writing `find . -name *.txt` without quotes. If `.txt` files exist in the current directory, the shell expands `*.txt` before `find` runs, causing confusing errors. | Always quote: `find . -name "*.txt"`. This ensures `find` sees the literal pattern. |
| Piping into commands that ignore stdin | Commands like `ls`, `cd`, and `rm` do not read from stdin. Writing `echo "/etc" \| ls` does nothing useful. | Use `xargs` to convert stdin into arguments: `echo "/etc" \| xargs ls`. Or use command substitution: `ls $(echo "/etc")`. |
| Searching from `/` without suppressing errors | Running `find / -name "myfile"` floods your screen with "Permission denied" errors from directories you cannot access. | Add `2> /dev/null` to hide the errors: `find / -name "myfile" 2> /dev/null`. |
| Using `grep` without `-r` and wondering why nothing matches | You wrote `grep "error" /var/log/` expecting it to search all files in the directory, but `grep` only searches files you explicitly name. | Add `-r` for recursive search: `grep -r "error" /var/log/`. |
| Confusing `find -name` with `find -path` | You expected `find . -name "src/config.yaml"` to match a path, but `-name` only matches the filename portion. | Use `-path` for matching against the full path: `find . -path "*/src/config.yaml"`. |
| Forgetting that `grep "pattern"` with no file waits for keyboard input | You typed `grep "hello"` and the terminal seems frozen. It is actually waiting for you to type stdin input. | Press `Ctrl+C` to cancel. Then either specify a file (`grep "hello" file.txt`) or pipe input into it (`echo "hello world" \| grep "hello"`). |

---

## Quiz

**Test your understanding. Try to answer before revealing the solution.**

<details>
<summary>1. <strong>Scenario:</strong> You are cleaning up a directory filled with backup files. You have <code>backup_1.tar</code>, <code>backup_12.tar</code>, and <code>backup_final.tar</code>. You run <code>rm backup_?.tar</code>. Which files are deleted and why?</summary>

Only `backup_1.tar` is deleted in this scenario. This happens because the `?` wildcard strictly matches exactly one character, no more and no less. Since `1` is a single character, it perfectly matches the pattern. However, `12` is two characters and `final` is five characters, meaning `backup_12.tar` and `backup_final.tar` are safely ignored. If you had used the `*` wildcard instead, which matches zero or more characters of any kind, all three files would have been deleted. *(Maps to Outcome: Search files)*
</details>

<details>
<summary>2. <strong>Scenario:</strong> You have a script that checks system health every hour. You want to record the output of <code>uptime</code> into <code>/var/log/health.log</code> so you can review the history at the end of the week. Which redirection operator should you use and why?</summary>

You should use the append operator `>>` for this task. When you use `>>`, the shell opens the target file and adds the new output to the very end of it, preserving all the existing historical data. If you were to use the standard `>` operator instead, the shell would truncate (empty) the file before writing the new output, meaning you would only ever have the most recent hour's data. For logging purposes where data must be retained over time, appending is always the correct and safe choice. *(Maps to Outcome: Redirect streams)*
</details>

<details>
<summary>3. <strong>Scenario:</strong> You are running <code>find / -name "secret.key"</code> as a regular user. Your screen is instantly flooded with hundreds of "Permission denied" lines, making it impossible to see if the file was actually found. How do you fix this command and why does the fix work?</summary>

You fix it by appending `2> /dev/null` to the end of your command. This works because it separates the standard error stream (stream 2) from the standard output stream (stream 1). By redirecting stream 2 into `/dev/null` (the system's black hole), all the "Permission denied" errors are immediately discarded by the operating system. Meanwhile, stream 1 is completely untouched, meaning if `find` does successfully locate "secret.key", that valid result will still print cleanly to your terminal screen. *(Maps to Outcome: Redirect streams)*
</details>

<details>
<summary>4. <strong>Scenario:</strong> Your web server's primary disk is at 99% capacity. You suspect some rotated log files in <code>/var/log</code> have grown out of control, specifically files over 50 Megabytes. How do you locate just these massive files?</summary>

You would use the command `find /var/log -type f -name "*.log" -size +50M`. This approach works because `find` allows you to combine multiple search criteria that must all be evaluated as true. The `-type f` flag ensures you are only looking at actual files rather than directories. The `-name "*.log"` flag filters for the correct extension, and crucially, `-size +50M` restricts the results to files strictly larger than 50 megabytes. This surgical filtering prevents you from wasting time manually checking the size of hundreds of smaller files. *(Maps to Outcome: Search files)*
</details>

<details>
<summary>5. <strong>Scenario:</strong> A customer reported a timeout at exactly 14:32. You search <code>app.log</code> for "timeout" and find the error, but it doesn't tell you which user triggered it. You need to see the log lines immediately before the error to find the user ID. What command do you use?</summary>

You would use the command `grep -B 3 -i "timeout" app.log` (or `-C 3` for context on both sides). This works because `grep` does not just match isolated lines; it can retain a buffer of surrounding text. By specifying `-B 3` (Before), `grep` prints the matching line plus the three lines that immediately preceded it in the file. This context is absolutely critical for debugging, as the events leading up to an error (like a user logging in or initiating a transaction) are almost always printed on the lines just above the actual failure message. *(Maps to Outcome: Process text streams)*
</details>

<details>
<summary>6. <strong>Scenario:</strong> You inherit a server and see this command in the history: <code>cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10</code>. The previous admin used it during a DDoS attack. What exactly was this command helping them discover?</summary>

This command was helping them discover the top 10 IP addresses making the most requests, which is crucial for identifying the primary sources of a DDoS attack. It works by chaining small, focused utilities together through pipes. First, `awk` extracts just the IP address column, then the first `sort` groups identical IPs together so that `uniq -c` can accurately count consecutive duplicates. The second `sort -rn` orders those newly calculated counts numerically from highest to lowest. Finally, `head -10` truncates the massive list to just the top 10 offenders, giving the admin exactly the target list they need to block the malicious traffic. *(Maps to Outcome: Chain commands)*
</details>

<details>
<summary>7. <strong>Scenario:</strong> You are in a directory containing <code>script.py</code>, <code>utils.py</code>, and <code>data.csv</code>. You want to find all Python files in the subdirectories. You run <code>find . -name *.py</code>. It returns <code>script.py</code> and <code>utils.py</code> from the current directory, but completely misses <code>src/main.py</code>. Why did this fail?</summary>

It failed because you forgot to put quotes around the `*.py` wildcard pattern. Because there were already `.py` files in your current working directory, your shell expanded the wildcard *before* passing it to the `find` command. The shell actually executed `find . -name script.py utils.py`, which causes unexpected behavior because `find` was told to look specifically for those two exact filenames, not a broader pattern. By adding quotes (`"*.py"`), you protect the asterisk from the shell, forcing `find` itself to do the expansion dynamically across all subdirectories. *(Maps to Outcome: Search files)*
</details>

<details>
<summary>8. <strong>Scenario:</strong> You are running a massive database migration script (<code>./migrate.sh</code>) that takes hours. You want to save all successful progress messages to <code>progress.txt</code>, but you want any critical failures to be saved separately in <code>alerts.txt</code> so you can review them quickly. How do you run the script?</summary>

You would run it using the command `./migrate.sh > progress.txt 2> alerts.txt`. This solution works because Linux strictly separates standard output (stream 1) from standard error (stream 2) at the kernel level. The `>` operator is shorthand for `1>`, meaning it grabs the normal output and funnels it exclusively into `progress.txt`. The `2>` operator explicitly grabs only the error stream and routes it into `alerts.txt`. This strict separation ensures that your critical error alerts are not buried in the middle of a massive file full of routine success messages. *(Maps to Outcome: Redirect streams)*
</details>

---

## Hands-On Exercise: The Server Investigation

**Scenario:** You are a junior SRE investigating a reported outage. You have been given a server with multiple log files, and your job is to find the relevant errors, extract them, and create a summary report. You will use everything from this module: wildcards, redirection, pipes, `find`, and `grep`.

### Setup

First, create the practice environment:

```bash
# Create the investigation directory
mkdir -p ~/investigation/logs

# Create simulated log files with realistic content
cat > ~/investigation/logs/web.log << 'EOF'
2024-03-15 08:01:12 INFO Request received: GET /api/users
2024-03-15 08:01:13 INFO Response sent: 200 OK
2024-03-15 08:02:44 ERROR Connection to database timed out
2024-03-15 08:02:45 ERROR Failed to process request: GET /api/orders
2024-03-15 08:03:01 WARN Retry attempt 1 for database connection
2024-03-15 08:03:02 INFO Database connection restored
2024-03-15 08:05:30 INFO Request received: GET /api/products
2024-03-15 08:07:15 ERROR OutOfMemoryError: heap space exhausted
2024-03-15 08:07:16 ERROR Service crashed - restarting
EOF

cat > ~/investigation/logs/db.log << 'EOF'
2024-03-15 08:00:00 INFO Database server started
2024-03-15 08:02:40 WARN Connection pool exhausted (max: 100)
2024-03-15 08:02:42 ERROR Too many connections - rejecting new requests
2024-03-15 08:02:43 ERROR Query timeout: SELECT * FROM orders WHERE status='pending'
2024-03-15 08:03:00 INFO Connection pool recovered
2024-03-15 08:06:00 INFO Routine backup started
2024-03-15 08:07:10 ERROR Disk space critical: /var/lib/mysql at 98%
EOF

cat > ~/investigation/logs/app.log << 'EOF'
2024-03-15 08:00:05 INFO Application started on port 8080
2024-03-15 08:01:10 INFO Health check passed
2024-03-15 08:02:44 ERROR Upstream service unavailable: payment-gateway
2024-03-15 08:02:50 WARN Circuit breaker opened for payment-gateway
2024-03-15 08:04:00 INFO Circuit breaker closed for payment-gateway
2024-03-15 08:07:14 ERROR Memory usage exceeded threshold: 95%
2024-03-15 08:07:15 ERROR Initiating graceful shutdown
2024-03-15 08:07:16 INFO Shutdown complete
EOF

# Create a text file to make find exercises interesting
echo "This is a config file" > ~/investigation/config.txt
echo "Important notes here" > ~/investigation/notes.txt
```

### Tasks

Complete each task using the tools you learned. Try each one yourself before checking the answer.

**Task 1:** Use a wildcard to list only the `.log` files in `~/investigation/logs/`.

<details>
<summary>Solution</summary>

```bash
ls ~/investigation/logs/*.log
```
</details>

**Task 2:** Use `grep` to find all lines containing "ERROR" across all log files. Save the results to `~/investigation/all_errors.txt`.

<details>
<summary>Solution</summary>

```bash
grep "ERROR" ~/investigation/logs/*.log > ~/investigation/all_errors.txt
```
</details>

**Task 3:** Count how many ERROR lines exist in each log file (without showing the lines themselves).

<details>
<summary>Solution</summary>

```bash
grep -c "ERROR" ~/investigation/logs/*.log
```

Expected output:
```
/home/user/investigation/logs/app.log:3
/home/user/investigation/logs/db.log:3
/home/user/investigation/logs/web.log:4
```
</details>

**Task 4:** Find all errors related to "database" or "memory" (case-insensitive), showing 1 line of context before each match.

<details>
<summary>Solution</summary>

```bash
grep -i -B 1 "database\|memory" ~/investigation/logs/*.log
```

Or using two greps with a pipe:

```bash
cat ~/investigation/logs/*.log | grep -i -B 1 -E "database|memory"
```
</details>

**Task 5:** Use `find` to locate all `.txt` files in the `~/investigation` directory.

<details>
<summary>Solution</summary>

```bash
find ~/investigation -name "*.txt"
```
</details>

**Task 6 (The Boss Level):** Write a single pipeline that:
1. Reads all log files
2. Filters only ERROR lines
3. Sorts them by timestamp
4. Takes the last 5 (most recent errors)
5. Saves them to `~/investigation/recent_critical.txt`

<details>
<summary>Solution</summary>

```bash
cat ~/investigation/logs/*.log | grep "ERROR" | sort | tail -5 > ~/investigation/recent_critical.txt
```

Verify with:

```bash
cat ~/investigation/recent_critical.txt
```

You should see the 5 most recent ERROR entries sorted by timestamp.
</details>

### Success Criteria

You have completed this exercise when:

- [x] `~/investigation/all_errors.txt` exists and contains only ERROR lines from all three log files
- [x] You can tell how many errors each log file has (Task 3)
- [x] `~/investigation/recent_critical.txt` contains exactly 5 sorted error lines
- [x] You completed each task using commands from this module (no GUI tools)

---

**Next Up:** [Module 0.2: Environment & Permissions](../module-0.2-environment-permissions/) -- Learn how Linux knows who you are, how to customize your shell, and how the permission system keeps everything secure.