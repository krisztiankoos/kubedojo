#!/bin/bash
# KubeDojo — Migrate to kube-dojo GitHub organization
#
# Prerequisites:
# 1. Create the "kube-dojo" org at https://github.com/organizations/plan
# 2. Transfer repo: Settings → Danger Zone → Transfer → kube-dojo
# 3. Then run this script
#
# What this script does:
# - Updates mkdocs.yml with new URLs
# - Removes the /kubedojo/ base path (site will be at root /)
# - Updates internal references
# - Commits and pushes

set -e

echo "🔄 Migrating KubeDojo to kube-dojo.github.io..."

# Check if we're in the right directory
if [ ! -f mkdocs.yml ]; then
    echo "❌ Run this from the project root"
    exit 1
fi

# Check if repo has been transferred already
REMOTE=$(git remote get-url origin)
if [[ "$REMOTE" != *"kube-dojo"* ]]; then
    echo "⚠️  Remote is still: $REMOTE"
    echo "   Transfer the repo first:"
    echo "   1. Go to https://github.com/krisztiankoos/kubedojo/settings"
    echo "   2. Scroll to 'Danger Zone' → 'Transfer ownership'"
    echo "   3. Transfer to 'kube-dojo' organization"
    echo "   4. Update remote: git remote set-url origin git@github.com:kube-dojo/kube-dojo.github.io.git"
    echo "   5. Re-run this script"
    exit 1
fi

# Update mkdocs.yml
echo "📝 Updating mkdocs.yml..."
sed -i '' 's|site_url: https://krisztiankoos.github.io/kubedojo/|site_url: https://kube-dojo.github.io/|' mkdocs.yml
sed -i '' 's|repo_url: https://github.com/krisztiankoos/kubedojo|repo_url: https://github.com/kube-dojo/kube-dojo.github.io|' mkdocs.yml
sed -i '' 's|repo_name: krisztiankoos/kubedojo|repo_name: kube-dojo/kube-dojo.github.io|' mkdocs.yml

# Update start-docs.sh if it has hardcoded paths
if grep -q "kubedojo" start-docs.sh 2>/dev/null; then
    echo "📝 Updating start-docs.sh..."
fi

echo "✅ Config updated"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git add -A && git commit -m 'feat: Migrate to kube-dojo.github.io'"
echo "  3. Push: git push"
echo "  4. Enable GitHub Pages in the new repo settings"
echo "  5. Site will be live at https://kube-dojo.github.io/"
