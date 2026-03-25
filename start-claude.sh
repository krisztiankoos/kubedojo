#!/bin/bash
# KubeDojo - Claude Code Wrapper
# Ensures extensions are deployed and starts Claude

set -e

# Ensure ~/.local/bin is in PATH (where claude installs by default)
export PATH="$HOME/.local/bin:$PATH"
hash -r 2>/dev/null || true  # Clear command cache

# Get script directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Claude in KubeDojo project..."
echo "Project: $PROJECT_DIR"

# Preflight check: Verify required tools
echo "Preflight check..."
MISSING_TOOLS=""
for tool in git gh kubectl; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ -n "$MISSING_TOOLS" ]; then
    echo "Warning: Optional tools not found:$MISSING_TOOLS"
    echo "   (These are recommended but not required to start)"
fi

# Check for claude
if ! command -v claude &> /dev/null; then
    echo "Error: Claude CLI not found"
    echo "   Install with: npm install -g @anthropic-ai/claude-code"
    exit 1
fi
echo "Claude CLI found"

# Change to project directory
cd "$PROJECT_DIR"

# Show current branch
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Current branch: $CURRENT_BRANCH"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "Uncommitted changes detected"
    fi
fi

# Deploy Claude extensions (always run to ensure up-to-date)
if [ -f "claude_extensions/deploy.sh" ]; then
    echo "Checking Claude extensions..."
    bash claude_extensions/deploy.sh --quiet
    echo "Extensions deployed"
fi

# Show KubeDojo status (dynamically from STATUS.md)
echo ""
echo "KUBEDOJO - Cloud Native Curriculum"

if [ -f "STATUS.md" ]; then
    # Extract current state line
    CURRENT_STATE=$(grep -A1 "## Current State" STATUS.md | tail -1 | sed 's/^\*\*//' | sed 's/\*\*.*//')
    if [ -n "$CURRENT_STATE" ]; then
        echo "   Status: $CURRENT_STATE"
    fi

    # Extract curriculum summary table
    echo "   Tracks:"
    grep -E "^\| (Prerequisites|Linux|Cloud|Certifications|Platform) \|" STATUS.md 2>/dev/null | while read line; do
        NAME=$(echo "$line" | cut -d'|' -f2 | xargs)
        MODULES=$(echo "$line" | cut -d'|' -f3 | xargs)
        STATUS=$(echo "$line" | cut -d'|' -f4 | xargs)
        echo "       $NAME: $MODULES modules ($STATUS)"
    done

    # Extract first TODO item
    NEXT=$(grep -m1 "^\- \[ \]" STATUS.md | sed 's/^- \[ \] //')
    if [ -n "$NEXT" ]; then
        echo "   Next: $NEXT"
    fi
else
    echo "   (STATUS.md not found - run from project root)"
fi

echo "   Issues: https://github.com/kube-dojo/kube-dojo.github.io/issues"
echo "   Commands: /review-module, /review-part, /verify-technical"

# Check if kubectl can connect (optional)
if command -v kubectl &> /dev/null; then
    if kubectl cluster-info &> /dev/null 2>&1; then
        CLUSTER_NAME=$(kubectl config current-context 2>/dev/null || echo "unknown")
        echo "   K8s cluster: $CLUSTER_NAME (connected)"
    else
        echo "   K8s cluster: (not connected)"
    fi
fi

echo ""

# Try to update Claude
echo "Checking for Claude updates..."
claude install 2>/dev/null || true

# Refresh command cache after potential update
hash -r 2>/dev/null || true

# Start Claude (use command -v to get actual path, avoiding stale cache)
echo "Launching Claude Code in bypassPermissions mode..."
CLAUDE_BIN="$(command -v claude)"
if [ -z "$CLAUDE_BIN" ]; then
    # Fallback to common install locations
    if [ -x "$HOME/.local/bin/claude" ]; then
        CLAUDE_BIN="$HOME/.local/bin/claude"
    elif [ -x "/opt/homebrew/bin/claude" ]; then
        CLAUDE_BIN="/opt/homebrew/bin/claude"
    else
        echo "Error: Cannot find claude binary after update"
        exit 1
    fi
fi
"$CLAUDE_BIN" --chrome --permission-mode bypassPermissions "$@"
