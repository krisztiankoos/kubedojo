#!/usr/bin/env python3
"""KubeDojo Site Health Check — validates navigation, links, and content integrity."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"

errors = []
warnings = []


def error(msg: str):
    errors.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def check_nav_files_exist():
    """Check all files in mkdocs.yml nav exist on disk."""
    print("\n1. Checking nav entries point to existing files...")
    nav_files = set()
    with open(MKDOCS_YML) as f:
        for line in f:
            line = line.strip()
            # Match lines like "- path/to/file.md" or "- Title: path/to/file.md"
            m = re.match(r'^-\s+(?:.*:\s+)?(.+\.md)\s*$', line)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                nav_files.add(filepath)
                full_path = DOCS_DIR / filepath
                if not full_path.exists():
                    error(f"Nav references missing file: {filepath}")

    found = len(nav_files) - len([e for e in errors if "Nav references" in e])
    print(f"  {found}/{len(nav_files)} nav entries OK")
    return nav_files


def check_orphaned_modules(nav_files: set):
    """Check for .md files not in navigation."""
    print("\n2. Checking for orphaned modules (not in nav)...")
    orphaned = []
    for md in sorted(DOCS_DIR.rglob("*.md")):
        rel = str(md.relative_to(DOCS_DIR))
        # Skip cumulative quizzes, READMEs already handled, and special files
        if rel in nav_files:
            continue
        # Skip files that are commonly not in nav
        if any(skip in rel for skip in ["cumulative-quiz", "part0-cumulative", "part1-cumulative",
                                         "part2-cumulative", "part3-cumulative", "part4-cumulative",
                                         "part5-cumulative"]):
            continue
        # Skip Ukrainian translation files (handled by i18n plugin, not nav)
        if rel.endswith(".uk.md"):
            continue
        orphaned.append(rel)

    for o in orphaned:
        warn(f"Orphaned (not in nav): {o}")

    if not orphaned:
        print("  All modules are in navigation")
    else:
        print(f"  {len(orphaned)} orphaned files found")


def check_internal_links():
    """Check markdown internal links resolve to existing files."""
    print("\n3. Checking internal markdown links...")
    broken = 0
    checked = 0
    for md in sorted(DOCS_DIR.rglob("*.md")):
        content = md.read_text(errors="replace")
        # Strip fenced code blocks before checking links
        content_no_code = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        # Find markdown links: [text](path.md) or [text](../path.md)
        for match in re.finditer(r'\[([^\]]*)\]\(([^)]+\.md[^)]*)\)', content_no_code):
            link_text, link_path = match.group(1), match.group(2)
            # Skip external URLs
            if link_path.startswith("http"):
                continue
            # Strip anchors
            link_path = link_path.split("#")[0]
            if not link_path:
                continue
            # Resolve relative to the file's directory
            target = (md.parent / link_path).resolve()
            checked += 1
            if not target.exists():
                error(f"Broken link in {md.relative_to(DOCS_DIR)}: [{link_text}]({link_path})")
                broken += 1

    print(f"  {checked - broken}/{checked} internal links OK")


def check_changelog_links():
    """Check that changelog.md has links for mentioned modules."""
    print("\n4. Checking changelog module references have links...")
    changelog = DOCS_DIR / "changelog.md"
    if not changelog.exists():
        error("changelog.md not found")
        return

    content = changelog.read_text()
    # Find module names mentioned in tables without links
    # Pattern: | **Name** | Category | Description |  (no markdown link)
    table_rows = re.findall(r'\|\s*\*\*([^*]+)\*\*\s*\|', content)
    linked_modules = re.findall(r'\[([^\]]+)\]\([^)]+\)', content)

    unlinked = []
    for name in table_rows:
        # Check if this name appears as a link somewhere
        if not any(name.lower() in link.lower() for link in linked_modules):
            # Skip non-module table entries
            if name in ("Metric", "Count", "Module", "Track", "Description", "Category"):
                continue
            unlinked.append(name)

    for u in unlinked:
        warn(f"Changelog mentions '{u}' without a link")

    if not unlinked:
        print("  All changelog references are linked")
    else:
        print(f"  {len(unlinked)} unlinked references found")


def check_duplicate_nav():
    """Check for duplicate entries in mkdocs.yml nav."""
    print("\n5. Checking for duplicate nav entries...")
    seen = {}
    with open(MKDOCS_YML) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            m = re.match(r'^-\s+(?:.*:\s+)?(.+\.md)\s*$', line)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                if filepath in seen:
                    error(f"Duplicate nav entry: {filepath} (lines {seen[filepath]} and {lineno})")
                seen[filepath] = lineno

    dupes = len([e for e in errors if "Duplicate nav" in e])
    print(f"  {len(seen)} entries, {dupes} duplicates")


def check_module_count():
    """Check STATUS.md module count matches reality."""
    print("\n6. Checking module count consistency...")
    status = (REPO_ROOT / "STATUS.md").read_text()
    m = re.search(r'\*\*(\d+)\*\*', status)
    if m:
        claimed = int(m.group(1))
        # Count actual module files (module-*.md), excluding translations
        actual = len([f for f in DOCS_DIR.rglob("module-*.md") if not f.name.endswith(".uk.md")])
        if claimed != actual:
            warn(f"STATUS.md claims {claimed} modules but found {actual} module files")
        else:
            print(f"  Module count matches: {actual}")
    else:
        warn("Could not parse module count from STATUS.md")


def check_readme_completeness():
    """Check toolkit/curriculum READMEs list their child modules."""
    print("\n7. Checking README completeness...")
    missing = 0
    for readme in sorted(DOCS_DIR.rglob("README.md")):
        parent = readme.parent
        modules = sorted(f for f in parent.glob("module-*.md") if not f.name.endswith(".uk.md"))
        if not modules:
            continue
        content = readme.read_text()
        for mod in modules:
            if mod.name not in content:
                warn(f"{readme.relative_to(DOCS_DIR)} doesn't mention {mod.name}")
                missing += 1

    if missing == 0:
        print("  All READMEs reference their modules")
    else:
        print(f"  {missing} missing module references in READMEs")


def main():
    print("=" * 60)
    print("KubeDojo Site Health Check")
    print("=" * 60)

    nav_files = check_nav_files_exist()
    check_orphaned_modules(nav_files)
    check_internal_links()
    check_changelog_links()
    check_duplicate_nav()
    check_module_count()
    check_readme_completeness()

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

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
