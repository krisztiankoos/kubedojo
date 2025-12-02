# Module 0.3: Vim for YAML

> **Complexity**: `[QUICK]` - Learn 10 commands, use them forever
>
> **Time to Complete**: 20-30 minutes
>
> **Prerequisites**: None (Vim is pre-installed on exam systems)

---

## Why This Module Matters

The CKA exam requires editing YAML files. A lot. You'll create manifests, fix broken configs, and modify existing resources—all in a terminal.

The exam environment defaults to **nano** (as of 2025), but you can switch to vim. Whether you use vim or nano, you need to be fast. This module covers vim because it's more powerful once you know the basics.

If you prefer nano, that's fine—it's simpler. But vim skills transfer to production troubleshooting where nano might not be available.

---

## Part 1: Vim Survival Kit

You don't need to be a vim expert. You need 10 commands.

### 1.1 Modes

Vim has modes. This confuses everyone at first.

> **The Gearshift Analogy**
>
> Vim modes are like a car's gearshift. In **Normal mode** (drive), you're navigating—moving around, not typing. In **Insert mode** (park), you're stationary and typing. In **Command mode** (reverse), you're doing special operations like saving. You wouldn't try to park while driving. Vim forces you to "shift gears" deliberately. It feels weird at first, but it's what makes vim so fast once you internalize it.

| Mode | How to Enter | What It Does |
|------|-------------|--------------|
| Normal | `Esc` | Navigate, delete, copy, paste |
| Insert | `i`, `a`, `o` | Type text |
| Command | `:` | Save, quit, search |

**Rule**: When confused, press `Esc` to return to Normal mode.

### 1.2 Essential Commands

```
ENTERING INSERT MODE
i     Insert before cursor
a     Insert after cursor
o     Open new line below and insert
O     Open new line above and insert

NAVIGATION (Normal mode)
h     Left
j     Down
k     Up
l     Right
gg    Go to first line
G     Go to last line
0     Go to beginning of line
$     Go to end of line
w     Jump forward one word
b     Jump backward one word

EDITING (Normal mode)
x     Delete character under cursor
dd    Delete entire line
yy    Copy (yank) entire line
p     Paste below
P     Paste above
u     Undo
Ctrl+r  Redo

SEARCH
/pattern    Search forward
n           Next match
N           Previous match

SAVE AND QUIT
:w          Save (write)
:q          Quit
:wq         Save and quit
:q!         Quit without saving (discard changes)
```

### 1.3 The Minimum You Need

Honestly? For the exam, you can survive with:

```
i       → Start typing
Esc     → Stop typing
:wq     → Save and quit
dd      → Delete line
u       → Undo mistake
```

That's 5 things. Master these, and you won't fail because of vim.

---

## Part 2: Vim Configuration for YAML

### 2.1 Create ~/.vimrc

YAML is whitespace-sensitive. A misconfigured vim will ruin your indentation.

```bash
cat << 'EOF' > ~/.vimrc
" Basic settings
set number              " Show line numbers
set tabstop=2           " Tab = 2 spaces
set shiftwidth=2        " Indent = 2 spaces
set expandtab           " Use spaces, not tabs
set autoindent          " Maintain indentation
set smartindent         " Smart indentation for code
set paste               " Prevent auto-indent on paste (toggle with :set nopaste)

" YAML specific
autocmd FileType yaml setlocal ts=2 sts=2 sw=2 expandtab

" Visual helpers
set cursorline          " Highlight current line
syntax on               " Syntax highlighting
set hlsearch            " Highlight search results
EOF
```

### 2.2 Why These Settings Matter

| Setting | Why |
|---------|-----|
| `tabstop=2` | Kubernetes YAML uses 2-space indentation |
| `expandtab` | Converts tabs to spaces (tabs break YAML) |
| `autoindent` | New lines maintain indentation |
| `number` | Line numbers help with error messages |
| `set paste` | Prevents auto-indent issues when pasting |

> **Gotcha: Tabs vs Spaces**
>
> YAML requires consistent indentation. A single tab character mixed with spaces will break your manifest. Always use spaces. The `expandtab` setting converts tabs to spaces automatically.

> **War Story: The Invisible Character**
>
> A senior engineer spent 45 minutes debugging why `kubectl apply` kept failing with a cryptic YAML parsing error. The manifest looked perfect. They eventually ran `cat -A` on the file and discovered invisible tab characters mixed with spaces—introduced when they copied code from a Confluence page. The lesson: never trust copy-paste. Always verify indentation, and configure your editor to show invisible characters or convert tabs automatically.

---

## Part 3: YAML Editing Workflows

### 3.1 Creating a New File

```bash
vim pod.yaml
```

Press `i` to enter Insert mode, then type:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
```

Press `Esc`, then `:wq` to save and quit.

### 3.2 Copying Lines (Faster Than Retyping)

You need to add another container. Instead of typing from scratch:

1. Navigate to the container block
2. Position cursor on `- name: nginx`
3. Press `V` (visual line mode)
4. Press `j` twice to select 3 lines
5. Press `y` to yank (copy)
6. Navigate to where you want the new container
7. Press `p` to paste

### 3.3 Indenting Blocks

Selected the wrong indentation? Fix it:

1. `V` to enter visual line mode
2. Select lines with `j`/`k`
3. `>` to indent right
4. `<` to indent left

Or in Normal mode:
- `>>` indent current line right
- `<<` indent current line left

### 3.4 Deleting Multiple Lines

Need to remove a whole section?

1. Navigate to start of section
2. Type `5dd` to delete 5 lines
3. Or `d}` to delete until next blank line

### 3.5 Search and Replace

Wrong image name throughout file?

```
:%s/nginx:1.19/nginx:1.25/g
```

- `%s` = substitute in whole file
- `/old/new/` = pattern
- `g` = all occurrences (not just first)

---

## Part 4: Paste Without Mangling

When you copy YAML from documentation and paste into vim, auto-indent can mangle it.

### Method 1: Set Paste Mode

Before pasting:
```
:set paste
```

Paste your content (usually `Cmd+V` or right-click).

After pasting:
```
:set nopaste
```

### Method 2: Use the Terminal Paste

In the exam environment, you might paste directly into the terminal. The `:set paste` in your `.vimrc` helps, but be aware of it.

### Method 3: Alternative—Use `cat`

If vim paste is problematic:

```bash
cat << 'EOF' > pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
EOF
```

This avoids vim entirely for creating files.

---

## Part 5: Quick Reference Card

Print this or memorize it:

```
╔════════════════════════════════════════════════════╗
║              VIM YAML QUICK REFERENCE              ║
╠════════════════════════════════════════════════════╣
║ MODES                                              ║
║   Esc       → Normal mode (navigation)             ║
║   i         → Insert mode (typing)                 ║
║   :         → Command mode (save/quit)             ║
╠════════════════════════════════════════════════════╣
║ MOVEMENT                                           ║
║   gg        → Top of file                          ║
║   G         → Bottom of file                       ║
║   0         → Start of line                        ║
║   $         → End of line                          ║
║   /pattern  → Search                               ║
╠════════════════════════════════════════════════════╣
║ EDITING                                            ║
║   dd        → Delete line                          ║
║   yy        → Copy line                            ║
║   p         → Paste below                          ║
║   u         → Undo                                 ║
║   >>        → Indent right                         ║
║   <<        → Indent left                          ║
╠════════════════════════════════════════════════════╣
║ SAVE/QUIT                                          ║
║   :w        → Save                                 ║
║   :q        → Quit                                 ║
║   :wq       → Save and quit                        ║
║   :q!       → Quit without saving                  ║
╠════════════════════════════════════════════════════╣
║ YAML SPECIFIC                                      ║
║   :set paste    → Before pasting                   ║
║   :set nopaste  → After pasting                    ║
╚════════════════════════════════════════════════════╝
```

---

## Part 6: Nano Alternative

If vim feels like too much, use nano. It's the exam default now.

```bash
nano pod.yaml
```

Nano shows shortcuts at the bottom:
- `Ctrl+O` = Save (Write Out)
- `Ctrl+X` = Exit
- `Ctrl+K` = Cut line
- `Ctrl+U` = Paste

For YAML, create `~/.nanorc`:

```bash
cat << 'EOF' > ~/.nanorc
set tabsize 2
set tabstospaces
set autoindent
set linenumbers
EOF
```

> **Exam Tip**
>
> The exam environment (as of 2025) defaults to nano, but you can use vim if you prefer. Pick one and stick with it—don't waste exam time debating editors.

---

## Did You Know?

- **Vim is on every Linux server**. Learning vim pays off beyond the exam—you'll use it for production troubleshooting, container debugging, and anywhere a GUI isn't available.

- **The creator of vim (Bram Moolenaar) passed away in 2023**. The project continues as an open-source community effort. Neovim is a popular modern fork.

- **`vimtutor`** is built in. Run `vimtutor` in any terminal for an interactive vim tutorial. Takes about 30 minutes and teaches you more than this module.

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Stuck in insert mode | Can't navigate | Press `Esc` |
| Pasted YAML is mangled | Auto-indent | `:set paste` before pasting |
| Tab characters in YAML | YAML syntax error | Use `expandtab` in .vimrc |
| Lost changes | Quit without saving | Use `:wq` not `:q!` |
| Wrong indentation | YAML parsing fails | `>>` and `<<` to fix |

---

## Quiz

1. **How do you delete 3 lines in vim?**
   <details>
   <summary>Answer</summary>
   Position cursor on first line, type `3dd` in Normal mode.
   </details>

2. **You pasted YAML and the indentation is broken. What happened and how do you prevent it?**
   <details>
   <summary>Answer</summary>
   Vim's auto-indent mangled the paste. Use `:set paste` before pasting, then `:set nopaste` after.
   </details>

3. **What's the command to save and quit vim?**
   <details>
   <summary>Answer</summary>
   `:wq` (write and quit). Or `ZZ` in Normal mode (less common).
   </details>

4. **Why must you use spaces instead of tabs in YAML?**
   <details>
   <summary>Answer</summary>
   YAML requires consistent indentation. Mixing tabs and spaces (or using tabs when the parser expects spaces) causes syntax errors. Kubernetes manifests expect 2-space indentation.
   </details>

---

## Hands-On Exercise

**Task**: Configure vim and practice YAML editing.

**Setup**:
```bash
# Create .vimrc with YAML settings
cat << 'EOF' > ~/.vimrc
set number
set tabstop=2
set shiftwidth=2
set expandtab
set autoindent
syntax on
EOF
```

**Practice Tasks**:

1. Create a pod manifest from scratch:
   ```bash
   vim practice-pod.yaml
   # Type a complete Pod manifest
   # Save and exit
   ```

2. Duplicate a container block:
   - Open the file
   - Copy the container section
   - Paste and modify the name

3. Fix intentionally broken indentation:
   ```bash
   cat << 'EOF' > broken.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: test
   spec:
       containers:
         - name: nginx
         image: nginx
   EOF
   # Open in vim and fix indentation
   ```

**Success Criteria**:
- [ ] Can create a valid Pod manifest in vim
- [ ] Can copy and paste blocks within vim
- [ ] Can fix indentation issues
- [ ] Know how to save and quit

**Verification**:
```bash
# Validate your YAML
kubectl apply -f practice-pod.yaml --dry-run=client
```

---

## Next Module

[Module 0.4: kubernetes.io Navigation](module-0.4-k8s-docs.md) - Finding documentation fast during the exam.
