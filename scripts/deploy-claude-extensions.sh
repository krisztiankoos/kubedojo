#!/bin/bash
# Deploy Claude extensions from git source to local .claude directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SOURCE_DIR="$PROJECT_ROOT/claude_extensions"
TARGET_DIR="$PROJECT_ROOT/.claude"

echo "Deploying Claude extensions..."
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"

# Create target directories
mkdir -p "$TARGET_DIR/commands"
mkdir -p "$TARGET_DIR/skills"

# Copy commands
if [ -d "$SOURCE_DIR/commands" ]; then
    cp -v "$SOURCE_DIR/commands/"*.md "$TARGET_DIR/commands/" 2>/dev/null || echo "No commands to copy"
fi

# Copy skills
if [ -d "$SOURCE_DIR/skills" ]; then
    cp -v "$SOURCE_DIR/skills/"*.md "$TARGET_DIR/skills/" 2>/dev/null || echo "No skills to copy"
fi

echo ""
echo "Deployment complete!"
echo ""
echo "Commands deployed:"
ls -1 "$TARGET_DIR/commands/" 2>/dev/null || echo "  (none)"
echo ""
echo "Skills deployed:"
ls -1 "$TARGET_DIR/skills/" 2>/dev/null || echo "  (none)"
echo ""
echo "Restart Claude Code to load new extensions."
