#!/bin/bash
# KubeDojo - Claude Code Wrapper
# Ensures extensions are deployed and starts Claude

set -e

# Get script directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🥋 Starting Claude in KubeDojo project..."
echo "📁 Project: $PROJECT_DIR"

# Preflight check: Verify required tools
echo "🔍 Preflight check..."
MISSING_TOOLS=""
for tool in git gh kubectl; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ -n "$MISSING_TOOLS" ]; then
    echo "⚠️  Optional tools not found:$MISSING_TOOLS"
    echo "   (These are recommended but not required to start)"
fi

# Check for claude
if ! command -v claude &> /dev/null; then
    echo "❌ Error: Claude CLI not found"
    echo "   Install with: npm install -g @anthropic-ai/claude-code"
    exit 1
fi
echo "✅ Claude CLI found"

# Change to project directory
cd "$PROJECT_DIR"

# Show current branch
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_BRANCH=$(git branch --show-current)
    echo "🌿 Current branch: $CURRENT_BRANCH"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "📝 Uncommitted changes detected"
    fi
fi

# Deploy Claude extensions (always run to ensure up-to-date)
if [ -f "claude_extensions/deploy.sh" ]; then
    echo "🔧 Checking Claude extensions..."
    bash claude_extensions/deploy.sh --quiet
    echo "✅ Extensions deployed"
fi

# Show KubeDojo-specific reminders
echo ""
echo "📚 KUBEDOJO - CKA Certification Training"
echo "   • Progress: Part 0 complete (5/46 modules)"
echo "   • Issues: https://github.com/krisztiankoos/kubedojo/issues"
echo "   • Commands: /review-module, /review-part, /verify-technical"

# Check if kubectl can connect (optional)
if command -v kubectl &> /dev/null; then
    if kubectl cluster-info &> /dev/null 2>&1; then
        CLUSTER_NAME=$(kubectl config current-context 2>/dev/null || echo "unknown")
        echo "   • K8s cluster: $CLUSTER_NAME (connected)"
    else
        echo "   • K8s cluster: (not connected)"
    fi
fi

echo ""

# Start Claude
echo "🤖 Launching Claude Code..."
claude "$@"
