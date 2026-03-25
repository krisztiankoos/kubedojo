#!/usr/bin/env python3
"""Migrate KubeDojo from MkDocs Material to Starlight (Astro).

Handles:
- Frontmatter injection (extract # Title from line 1)
- README.md → index.md rename
- .uk.md → uk/ directory relocation
- Internal link fixup
- Sidebar ordering from mkdocs.yml nav

Usage:
    python scripts/migrate-to-starlight.py                    # dry-run (default)
    python scripts/migrate-to-starlight.py --execute          # actually write files
    python scripts/migrate-to-starlight.py --execute --clean  # remove docs/ after migration
"""

import argparse
import json
import re
import shutil
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
OUT_DIR = REPO_ROOT / "src" / "content" / "docs"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"


# ---------------------------------------------------------------------------
# 1. Parse mkdocs.yml nav into ordered file list
# ---------------------------------------------------------------------------

def parse_nav(nav_data: list, prefix: str = "") -> list[tuple[str, str, int]]:
    """Parse mkdocs.yml nav into flat list of (label, filepath, order).

    Returns list of (label, filepath, global_order_index).
    """
    results = []
    counter = [0]  # mutable counter for closure

    def _walk(items, parent_label=""):
        for item in items:
            if isinstance(item, str):
                # Bare file path
                counter[0] += 1
                results.append((parent_label, item, counter[0]))
            elif isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # "Label: path.md"
                        counter[0] += 1
                        results.append((key, value, counter[0]))
                    elif isinstance(value, list):
                        # "Label:" followed by list of children
                        _walk(value, key)

    _walk(nav_data)
    return results


def build_nav_index(mkdocs_path: Path) -> dict[str, tuple[str, int]]:
    """Build {filepath: (label, order)} from mkdocs.yml nav."""
    with open(mkdocs_path) as f:
        config = yaml.safe_load(f)

    nav = config.get("nav", [])
    entries = parse_nav(nav)

    # Build lookup: filepath → (label, order_within_parent)
    # Group by parent directory to get local ordering
    by_dir: dict[str, list[tuple[str, str, int]]] = {}
    for label, filepath, global_order in entries:
        parent = str(Path(filepath).parent)
        if parent not in by_dir:
            by_dir[parent] = []
        by_dir[parent].append((label, filepath, global_order))

    # Assign local order within each directory
    index = {}
    for parent, items in by_dir.items():
        for local_order, (label, filepath, _) in enumerate(items, start=1):
            index[filepath] = (label, local_order)

    return index


# ---------------------------------------------------------------------------
# 2. Convert a single file
# ---------------------------------------------------------------------------

def extract_title(content: str) -> tuple[str, str]:
    """Extract first # Title from content, return (title, remaining_content).

    Handles files with leading whitespace, empty lines, or comments before the H1.
    """
    match = re.search(r'^#\s+(.+)$', content, flags=re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Remove the H1 line from content (Starlight renders title from frontmatter)
        remaining = content[:match.start()] + content[match.end():]
        # Strip leading whitespace left after removal
        remaining = remaining.lstrip("\n")
        return title, remaining

    # No H1 found — use filename as fallback
    return "", content


def generate_frontmatter(title: str, sidebar_order: int | None = None,
                         sidebar_label: str | None = None,
                         slug: str | None = None) -> str:
    """Generate Starlight-compatible YAML frontmatter."""
    # Build YAML manually — use json.dumps for safe string escaping
    lines = ["---"]
    lines.append(f"title: {json.dumps(title)}")

    # Explicit slug to preserve dots (Starlight strips dots from filenames)
    if slug:
        lines.append(f"slug: {slug}")

    sidebar = {}
    if sidebar_order is not None:
        sidebar["order"] = sidebar_order
    if sidebar_label and sidebar_label != title:
        sidebar["label"] = sidebar_label

    if sidebar:
        lines.append("sidebar:")
        if "order" in sidebar:
            lines.append(f"  order: {sidebar['order']}")
        if "label" in sidebar:
            lines.append(f'  label: "{sidebar["label"]}"')

    lines.append("---")
    return "\n".join(lines)


def fix_internal_links(content: str, is_ukrainian: bool = False,
                       src_rel: str = "") -> str:
    """Fix internal markdown links for Starlight structure.

    Order matters: .uk.md→.md first, then README.md→index.md,
    so that README.uk.md → README.md → index.md.
    """
    if is_ukrainian:
        # In Ukrainian files, links to .uk.md siblings become plain .md
        # since they'll be in the same uk/ directory
        content = re.sub(
            r'\[([^\]]*)\]\(([^)]*?)\.uk\.md([^)]*)\)',
            r'[\1](\2.md\3)',
            content
        )

    # README.md → index (not index.md — Starlight uses slug-based routing)
    content = re.sub(
        r'\[([^\]]*)\]\(([^)]*?)README\.md(#[^)]*)?\)',
        lambda m: f'[{m.group(1)}]({m.group(2)}{m.group(3) or ""})',
        content
    )

    # Strip .md extension from all internal links (Starlight resolves by slug)
    # Preserve anchors: file.md#section → file/#section
    def _strip_md(m):
        text, pre, anchor = m.group(1), m.group(2), m.group(3) or ""
        if pre.startswith("http"):
            return m.group(0)
        # file.md → file/  or  file.md#anchor → file/#anchor
        return f"[{text}]({pre}/{anchor})"

    content = re.sub(
        r'\[([^\]]*)\]\(([^)]+?)\.md(#[^)]*)?\)',
        _strip_md,
        content
    )

    if is_ukrainian:
        # Ukrainian files at the uk/ root (e.g. uk/changelog.md, uk/index.md)
        # link to English content that is now one level up. Prepend ../
        # to non-relative links (those not starting with . or / or http or #)
        src_depth = src_rel.count("/")
        if src_depth == 0:
            def _prefix_link(m):
                text, path = m.group(1), m.group(2)
                if path.startswith((".", "/", "http", "#")):
                    return m.group(0)
                return f"[{text}](../{path})"

            content = re.sub(
                r'\[([^\]]*)\]\(([^)]+/[^)]*)\)',
                lambda m: _prefix_link(m),
                content
            )

    return content


def compute_output_path(src_path: Path, is_ukrainian: bool) -> Path:
    """Compute the output path for a source file.

    English: docs/k8s/cka/module.md → src/content/docs/k8s/cka/module.md
    Ukrainian: docs/k8s/cka/module.uk.md → src/content/docs/uk/k8s/cka/module.md
    README.md → index.md
    """
    rel = src_path.relative_to(DOCS_DIR)

    if is_ukrainian:
        # Strip .uk.md suffix → .md
        name = rel.name.replace(".uk.md", ".md")
        rel = rel.parent / name
        # Prepend uk/ locale directory
        out = OUT_DIR / "uk" / rel
    else:
        out = OUT_DIR / rel

    # README.md → index.md
    if out.name == "README.md":
        out = out.parent / "index.md"

    return out


# ---------------------------------------------------------------------------
# 3. Main migration logic
# ---------------------------------------------------------------------------

def collect_files() -> tuple[list[Path], list[Path]]:
    """Collect all English and Ukrainian .md files."""
    english = []
    ukrainian = []

    for md in sorted(DOCS_DIR.rglob("*.md")):
        if md.name.endswith(".uk.md"):
            ukrainian.append(md)
        else:
            english.append(md)

    return english, ukrainian


def migrate_file(src: Path, nav_index: dict, is_ukrainian: bool,
                 dry_run: bool) -> tuple[Path, bool]:
    """Migrate a single file. Returns (output_path, success)."""
    content = src.read_text(errors="replace")
    rel = str(src.relative_to(DOCS_DIR))

    # Extract title
    title, body = extract_title(content)
    if not title:
        # Fallback: use filename
        title = src.stem.replace("-", " ").replace("_", " ").title()

    # Look up sidebar order from nav index
    # For Ukrainian files, look up the English equivalent path
    sidebar_order = None
    sidebar_label = None
    lookup_rel = rel.replace(".uk.md", ".md") if is_ukrainian else rel
    if lookup_rel in nav_index:
        sidebar_label, sidebar_order = nav_index[lookup_rel]

    # Compute explicit slug to preserve dots in filenames
    # Starlight strips dots: module-1.1-foo.md → module-11-foo (wrong)
    # We want: module-1.1-foo.md → module-1.1-foo (correct)
    out_path = compute_output_path(src, is_ukrainian)
    slug = None
    stem = out_path.stem  # e.g. "module-1.1-control-plane" or "index"
    if stem != "index":
        # Build slug from output path relative to docs root
        rel_out = out_path.relative_to(OUT_DIR)
        # e.g. k8s/cka/part1-cluster-architecture/module-1.1-control-plane.md
        # → k8s/cka/part1-cluster-architecture/module-1.1-control-plane
        slug_path = str(rel_out.parent / stem)
        # Only set explicit slug if filename contains a dot (would be stripped)
        if "." in stem:
            slug = slug_path

    # Generate frontmatter
    frontmatter = generate_frontmatter(title, sidebar_order, sidebar_label, slug)

    # Fix links
    body = fix_internal_links(body, is_ukrainian, rel)

    # Combine
    output = f"{frontmatter}\n{body}"

    if dry_run:
        return out_path, True

    # Write
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output)
    return out_path, True


def migrate_all(dry_run: bool = True) -> dict:
    """Run the full migration. Returns stats."""
    nav_index = build_nav_index(MKDOCS_YML)

    english_files, ukrainian_files = collect_files()

    stats = {
        "english": 0,
        "ukrainian": 0,
        "errors": [],
        "renamed_readmes": 0,
    }

    print(f"Found {len(english_files)} English, {len(ukrainian_files)} Ukrainian files")
    print(f"Nav index has {len(nav_index)} entries")
    print(f"Output: {OUT_DIR}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()

    # Migrate English files
    for src in english_files:
        try:
            out_path, ok = migrate_file(src, nav_index, False, dry_run)
            if ok:
                stats["english"] += 1
                if src.name == "README.md":
                    stats["renamed_readmes"] += 1
                if not dry_run and stats["english"] % 50 == 0:
                    print(f"  ... {stats['english']} English files processed")
        except Exception as e:
            stats["errors"].append(f"{src}: {e}")

    # Migrate Ukrainian files
    for src in ukrainian_files:
        try:
            out_path, ok = migrate_file(src, nav_index, True, dry_run)
            if ok:
                stats["ukrainian"] += 1
        except Exception as e:
            stats["errors"].append(f"{src}: {e}")

    return stats


# ---------------------------------------------------------------------------
# 4. Verification
# ---------------------------------------------------------------------------

def verify_migration() -> list[str]:
    """Verify the migrated output for common issues."""
    issues = []

    if not OUT_DIR.exists():
        issues.append("Output directory does not exist — run with --execute first")
        return issues

    # Check all files have frontmatter
    for md in OUT_DIR.rglob("*.md"):
        content = md.read_text(errors="replace")
        if not content.startswith("---"):
            issues.append(f"Missing frontmatter: {md.relative_to(OUT_DIR)}")

    # Check no README.md files remain (should all be index.md)
    for readme in OUT_DIR.rglob("README.md"):
        issues.append(f"README.md not renamed: {readme.relative_to(OUT_DIR)}")

    # Check no .uk.md files in English dir (should be in uk/ subdir)
    for ukmd in OUT_DIR.glob("*.uk.md"):
        issues.append(f"Ukrainian file in root: {ukmd.relative_to(OUT_DIR)}")
    for ukmd in OUT_DIR.rglob("*.uk.md"):
        if not str(ukmd.relative_to(OUT_DIR)).startswith("uk/"):
            issues.append(f"Ukrainian file outside uk/: {ukmd.relative_to(OUT_DIR)}")

    # Check internal links point to existing files
    for md in OUT_DIR.rglob("*.md"):
        content = md.read_text(errors="replace")
        # Strip code blocks before checking links
        content_no_code = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        for match in re.finditer(r'\[([^\]]*)\]\(([^)]+\.md[^)]*)\)', content_no_code):
            link_text, link_path = match.group(1), match.group(2)
            if link_path.startswith("http"):
                continue
            link_path = link_path.split("#")[0]
            if not link_path:
                continue
            target = (md.parent / link_path).resolve()
            if not target.exists():
                issues.append(f"Broken link in {md.relative_to(OUT_DIR)}: [{link_text}]({link_path})")

    return issues


# ---------------------------------------------------------------------------
# 5. CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Migrate KubeDojo from MkDocs to Starlight",
    )
    parser.add_argument("--execute", action="store_true",
                        help="Actually write files (default is dry run)")
    parser.add_argument("--clean", action="store_true",
                        help="Remove docs/ after successful migration")
    parser.add_argument("--verify", action="store_true",
                        help="Verify existing migration output")
    args = parser.parse_args()

    if args.verify:
        print("Verifying migration output...")
        issues = verify_migration()
        if issues:
            print(f"\n{len(issues)} issues found:")
            for issue in issues[:50]:
                print(f"  - {issue}")
            if len(issues) > 50:
                print(f"  ... and {len(issues) - 50} more")
            sys.exit(1)
        else:
            print("All checks passed!")
            sys.exit(0)

    dry_run = not args.execute

    if not dry_run and OUT_DIR.exists():
        print(f"Output directory already exists: {OUT_DIR}")
        print("Remove it first or use --verify to check existing output")
        sys.exit(1)

    stats = migrate_all(dry_run)

    print(f"\nResults:")
    print(f"  English files: {stats['english']}")
    print(f"  Ukrainian files: {stats['ukrainian']}")
    print(f"  READMEs → index.md: {stats['renamed_readmes']}")
    print(f"  Errors: {len(stats['errors'])}")

    if stats["errors"]:
        print("\nErrors:")
        for err in stats["errors"]:
            print(f"  - {err}")

    if dry_run:
        print(f"\nDry run complete. Run with --execute to write files.")

    if args.clean and not dry_run and not stats["errors"]:
        print(f"\nRemoving {DOCS_DIR}...")
        shutil.rmtree(DOCS_DIR)
        print("Done.")


if __name__ == "__main__":
    main()
