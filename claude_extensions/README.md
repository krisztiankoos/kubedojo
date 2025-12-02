# Claude Extensions for KubeDojo

This folder contains Claude Code slash commands and skills for the KubeDojo project.

## Structure

```
claude_extensions/
├── commands/           # Slash commands (user-invoked)
│   ├── review-module.md
│   ├── review-part.md
│   └── verify-technical.md
├── skills/             # Skills (auto-invoked by Claude)
│   ├── module-quality-reviewer.md
│   ├── cka-expert.md
│   └── curriculum-writer.md
└── README.md
```

## Commands vs Skills

| Type | Invocation | Best For |
|------|------------|----------|
| **Commands** | User types `/command` | Specific tasks on demand |
| **Skills** | Claude auto-detects when relevant | Background knowledge, standards |

## Available Commands

### `/review-module [path]`
Review a single module against quality standards.

```
/review-module docs/cka/part0-environment/module-0.1-cluster-setup.md
```

### `/review-part [directory]`
Review all modules in a part for consistency.

```
/review-part docs/cka/part0-environment/
```

### `/verify-technical [path]`
Verify technical accuracy of commands and YAML.

```
/verify-technical docs/cka/part1-cluster-architecture/module-1.3-helm.md
```

## Available Skills

### `module-quality-reviewer`
Comprehensive quality assessment using the KubeDojo quality rubric. Scores modules on Theory, Practical, Engagement, and Exam Relevance.

### `cka-expert`
Authoritative CKA 2025 curriculum knowledge. Use when writing or reviewing CKA content to ensure accuracy.

### `curriculum-writer`
Module template and writing guidelines. Use when creating new modules to ensure consistent structure and tone.

## Deployment

To deploy extensions to your local Claude Code:

```bash
# From kubedojo root
cp -r claude_extensions/commands/* .claude/commands/
cp -r claude_extensions/skills/* .claude/skills/

# Or use the deploy script
./scripts/deploy-claude-extensions.sh
```

After deployment, restart Claude Code to load new commands.

## Development Workflow

1. **Edit** extensions in `claude_extensions/` (tracked in git)
2. **Test** by deploying to `.claude/` locally
3. **Commit** changes to `claude_extensions/`
4. **Deploy** to `.claude/` when ready to use

The `.claude/` directory is gitignored—it's the "installed" version.

## Creating New Commands

1. Create `claude_extensions/commands/your-command.md`
2. Add YAML frontmatter with description
3. Write the prompt/instructions
4. Deploy to `.claude/commands/`
5. Restart Claude Code

Example:
```markdown
---
description: Brief description of what this command does
---

# Command Title

Instructions for Claude when this command is invoked...

$ARGUMENTS contains any arguments passed to the command.
```

## Creating New Skills

1. Create `claude_extensions/skills/your-skill.md`
2. Write comprehensive knowledge/instructions
3. Deploy to `.claude/skills/`
4. Claude will auto-invoke when relevant

Skills don't need YAML frontmatter—they're reference documents that Claude uses when the topic is relevant.

## Quality Standards Reference

All modules should score 8+/10 to be considered complete:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Theory Depth | 25% | Explains "why", junior-friendly |
| Practical Value | 25% | Runnable code, clear steps |
| Engagement | 25% | Analogies, war stories, tone |
| Exam Relevance | 25% | CKA 2025 aligned, speed tips |

Target: **10/10** for all modules (Part 0 is the reference standard).
