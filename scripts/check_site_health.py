#!/usr/bin/env python3
"""KubeDojo Site Health Check — validates content integrity for Starlight (Astro)."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "src" / "content" / "docs"

errors = []
warnings = []


def error(msg: str):
    errors.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def check_frontmatter():
    """Check all .md files have valid Starlight frontmatter."""
    print("\n1. Checking frontmatter...")
    missing = 0
    no_title = 0
    for md in sorted(DOCS_DIR.rglob("*.md")):
        content = md.read_text(errors="replace")
        rel = str(md.relative_to(DOCS_DIR))
        if not content.startswith("---"):
            error(f"Missing frontmatter: {rel}")
            missing += 1
            continue
        # Check for title
        if "title:" not in content.split("---")[1]:
            warn(f"Missing title in frontmatter: {rel}")
            no_title += 1

    total = len(list(DOCS_DIR.rglob("*.md")))
    ok = total - missing
    print(f"  {ok}/{total} files have frontmatter")
    if no_title:
        print(f"  {no_title} files missing title")


def check_internal_links():
    """Check internal links don't use .md extensions (Starlight uses slug routing)."""
    print("\n2. Checking for broken .md links...")
    broken = 0
    for md in sorted(DOCS_DIR.rglob("*.md")):
        # Skip Ukrainian translations for link checking (many link to untranslated content)
        rel = str(md.relative_to(DOCS_DIR))
        if rel.startswith("uk/"):
            continue
        content = md.read_text(errors="replace")
        # Strip fenced code blocks
        content_no_code = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        for match in re.finditer(r'\[([^\]]*)\]\(([^)]+\.md(?:#[^)]*)?)\)', content_no_code):
            link_text, link_path = match.group(1), match.group(2)
            if link_path.startswith("http"):
                continue
            warn(f"Internal .md link in {rel}: [{link_text[:40]}]({link_path})")
            broken += 1

    if broken == 0:
        print("  All internal links use slug format (no .md extensions)")
    else:
        print(f"  {broken} links still use .md extension")


def check_no_readme():
    """Check no README.md files remain (should all be index.md)."""
    print("\n3. Checking README.md → index.md conversion...")
    readmes = list(DOCS_DIR.rglob("README.md"))
    for r in readmes:
        error(f"README.md not renamed: {r.relative_to(DOCS_DIR)}")
    if not readmes:
        print("  All READMEs converted to index.md")
    else:
        print(f"  {len(readmes)} README.md files remain")


def check_no_uk_suffix():
    """Check no .uk.md files in English dir (should be in uk/ subdir)."""
    print("\n4. Checking Ukrainian file placement...")
    misplaced = []
    for ukmd in DOCS_DIR.rglob("*.uk.md"):
        misplaced.append(str(ukmd.relative_to(DOCS_DIR)))
    for m in misplaced:
        error(f"Ukrainian file with .uk.md suffix: {m}")
    if not misplaced:
        print("  All Ukrainian files in uk/ directory")
    else:
        print(f"  {len(misplaced)} misplaced .uk.md files")


def check_module_count():
    """Check STATUS.md module count matches reality."""
    print("\n5. Checking module count consistency...")
    status_file = REPO_ROOT / "STATUS.md"
    if not status_file.exists():
        warn("STATUS.md not found")
        return
    status = status_file.read_text()
    m = re.search(r'\*\*(\d+)\*\*', status)
    if m:
        claimed = int(m.group(1))
        # Count actual module files, excluding uk/ translations
        actual = len([f for f in DOCS_DIR.rglob("module-*.md")
                      if not str(f.relative_to(DOCS_DIR)).startswith("uk/")])
        if claimed != actual:
            warn(f"STATUS.md claims {claimed} modules but found {actual} module files")
        else:
            print(f"  Module count matches: {actual}")
    else:
        warn("Could not parse module count from STATUS.md")


def check_index_completeness():
    """Check index.md files reference their child modules."""
    print("\n6. Checking index.md completeness...")
    missing = 0
    for index in sorted(DOCS_DIR.rglob("index.md")):
        # Skip uk/ translations
        if str(index.relative_to(DOCS_DIR)).startswith("uk/"):
            continue
        parent = index.parent
        modules = sorted(f for f in parent.glob("module-*.md"))
        if not modules:
            continue
        content = index.read_text()
        for mod in modules:
            if mod.stem not in content and mod.name not in content:
                warn(f"{index.relative_to(DOCS_DIR)} doesn't mention {mod.name}")
                missing += 1

    if missing == 0:
        print("  All index files reference their modules")
    else:
        print(f"  {missing} missing module references")


def main():
    print("=" * 60)
    print("KubeDojo Site Health Check (Starlight)")
    print("=" * 60)

    if not DOCS_DIR.exists():
        print(f"\nERROR: Content directory not found: {DOCS_DIR}")
        print("Run: python scripts/migrate-to-starlight.py --execute")
        sys.exit(1)

    check_frontmatter()
    check_internal_links()
    check_no_readme()
    check_no_uk_suffix()
    check_module_count()
    check_index_completeness()

    print("\n" + "=" * 60)
    print(f"RESULTS: {len(errors)} errors, {len(warnings)} warnings")
    print("=" * 60)

    if errors:
        print("\nERRORS (must fix):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\nWARNINGS (should fix):")
        for w in warnings[:20]:
            print(f"  - {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")

    # Only fail on errors, not warnings
    if errors:
        print("\nSite health check FAILED. Fix errors before pushing.")
        print(f"Run: python scripts/check_site_health.py")
    else:
        print("Site health check passed.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
