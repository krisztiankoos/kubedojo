#!/bin/bash
# Deploy Claude extensions from source to .claude/
# Usage: ./claude_extensions/deploy.sh [--quiet]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$SCRIPT_DIR"
TARGET_DIR="$PROJECT_ROOT/.claude"

QUIET=false
if [[ "$1" == "--quiet" ]]; then
    QUIET=true
fi

log() {
    if [[ "$QUIET" == "false" ]]; then
        echo "$1"
    fi
}

log "🔧 Deploying Claude extensions..."
log "   Source: $SOURCE_DIR"
log "   Target: $TARGET_DIR"

# Create target directories
mkdir -p "$TARGET_DIR/commands"
mkdir -p "$TARGET_DIR/skills"

# Track changes
COMMANDS_CHANGED=0
SKILLS_CHANGED=0

# Deploy commands
if [ -d "$SOURCE_DIR/commands" ]; then
    for file in "$SOURCE_DIR/commands"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            target_file="$TARGET_DIR/commands/$filename"

            # Check if file changed
            if [ ! -f "$target_file" ] || ! cmp -s "$file" "$target_file"; then
                cp "$file" "$target_file"
                log "   📄 commands/$filename"
                COMMANDS_CHANGED=$((COMMANDS_CHANGED + 1))
            fi
        fi
    done
fi

# Deploy skills (directory structure: skills/skill-name/SKILL.md)
if [ -d "$SOURCE_DIR/skills" ]; then
    for skill_dir in "$SOURCE_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            source_file="$skill_dir/SKILL.md"
            target_skill_dir="$TARGET_DIR/skills/$skill_name"
            target_file="$target_skill_dir/SKILL.md"

            if [ -f "$source_file" ]; then
                mkdir -p "$target_skill_dir"
                # Check if file changed
                if [ ! -f "$target_file" ] || ! cmp -s "$source_file" "$target_file"; then
                    cp "$source_file" "$target_file"
                    log "   📄 skills/$skill_name/SKILL.md"
                    SKILLS_CHANGED=$((SKILLS_CHANGED + 1))
                fi
            fi
        fi
    done
fi

# Summary
TOTAL_CHANGED=$((COMMANDS_CHANGED + SKILLS_CHANGED))
if [ $TOTAL_CHANGED -gt 0 ]; then
    log "✅ Deployed $TOTAL_CHANGED extension(s)"
else
    log "✅ Extensions up to date"
fi
