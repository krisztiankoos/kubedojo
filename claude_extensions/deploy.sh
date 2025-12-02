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

# Deploy skills
if [ -d "$SOURCE_DIR/skills" ]; then
    for file in "$SOURCE_DIR/skills"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            target_file="$TARGET_DIR/skills/$filename"

            # Check if file changed
            if [ ! -f "$target_file" ] || ! cmp -s "$file" "$target_file"; then
                cp "$file" "$target_file"
                log "   📄 skills/$filename"
                SKILLS_CHANGED=$((SKILLS_CHANGED + 1))
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
