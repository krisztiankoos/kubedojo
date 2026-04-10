#!/usr/bin/env python3
"""Apply the 2026 reorganization plan to the AI/ML Engineering track.

Reads phase remap from PHASE_REMAP, then for every module file:
  - rename file (module-OLD.Y-... → module-NEW.Y-...)
  - update frontmatter slug (path includes new phase number)
  - update frontmatter sidebar.order (NEW*100+seq+1)
  - merges ai-safety phase 9 modules into advanced-genai phase 7 (as 7.6+)
  - regenerates each phase index.md

Then prints the new phase ordering for astro.config.mjs.

Usage:
    python scripts/reorganize_ai_ml.py --dry-run
    python scripts/reorganize_ai_ml.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TRACK_ROOT = REPO_ROOT / "src" / "content" / "docs" / "ai-ml-engineering"

# (old_phase, slug_dir) → (new_phase, target_slug_dir, label, seq_offset)
# seq_offset shifts module sequence numbers when merging into another phase
PHASE_REMAP = {
    0: ("prerequisites", 0, "prerequisites", "Phase 0: Prerequisites", 0),
    1: ("ai-native-development", 1, "ai-native-development", "Phase 1: AI-Native Development", 0),
    2: ("generative-ai", 2, "generative-ai", "Phase 2: Generative AI", 0),
    3: ("vector-rag", 3, "vector-rag", "Phase 3: Vector Search & RAG", 0),
    4: ("frameworks-agents", 4, "frameworks-agents", "Phase 4: Frameworks & Agents", 0),
    10: ("mlops", 5, "mlops", "Phase 5: MLOps & LLMOps", 0),
    11: ("ai-infrastructure", 6, "ai-infrastructure", "Phase 6: AI Infrastructure", 0),
    7: ("advanced-genai", 7, "advanced-genai", "Phase 7: Advanced GenAI & Safety", 0),
    # Merge ai-safety (phase 9) into advanced-genai (phase 7) starting at seq 6
    9: ("ai-safety", 7, "advanced-genai", "Phase 7: Advanced GenAI & Safety", 5),
    5: ("multimodal-ai", 8, "multimodal-ai", "Phase 8: Multimodal AI", 0),
    6: ("deep-learning", 9, "deep-learning", "Phase 9: Deep Learning Foundations", 0),
    8: ("classical-ml", 10, "classical-ml", "Phase 10: Classical ML", 0),
    12: ("history", 11, "history", "Appendix A: History of AI/ML", 0),
}

MODULE_RE = re.compile(r"^module-(\d+)\.(\d+)-(.+)\.md$")


def find_modules() -> list[dict]:
    """Discover every module file with its old phase/seq."""
    modules = []
    for old_phase, (old_dir, new_phase, new_dir, _label, seq_offset) in PHASE_REMAP.items():
        src_dir = TRACK_ROOT / old_dir
        if not src_dir.exists():
            continue
        for f in sorted(src_dir.glob("module-*.md")):
            m = MODULE_RE.match(f.name)
            if not m:
                continue
            file_phase = int(m.group(1))
            file_seq = int(m.group(2))
            slug = m.group(3)
            if file_phase != old_phase:
                # filename phase prefix doesn't match expected — skip safely
                print(f"  WARN: {f.name} expected phase {old_phase}, got {file_phase}", file=sys.stderr)
                continue
            new_seq = file_seq + seq_offset
            modules.append({
                "old_path": f,
                "old_phase": old_phase,
                "old_dir": old_dir,
                "new_phase": new_phase,
                "new_dir": new_dir,
                "old_seq": file_seq,
                "new_seq": new_seq,
                "slug": slug,
            })
    return modules


def rewrite_file(item: dict, dry_run: bool) -> None:
    """Rename file and update its frontmatter."""
    old_path: Path = item["old_path"]
    new_filename = f"module-{item['new_phase']}.{item['new_seq']}-{item['slug']}.md"
    new_path = TRACK_ROOT / item["new_dir"] / new_filename
    new_slug = f"ai-ml-engineering/{item['new_dir']}/module-{item['new_phase']}.{item['new_seq']}-{item['slug']}"
    new_order = (item["new_phase"] + 1) * 100 + item["new_seq"] + 1

    content = old_path.read_text()
    # Update slug line
    content = re.sub(
        r"^slug:\s*ai-ml-engineering/[\w/.-]+$",
        f"slug: {new_slug}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    # Update sidebar.order line
    content = re.sub(
        r"^(\s+order:\s*)\d+$",
        rf"\g<1>{new_order}",
        content,
        count=1,
        flags=re.MULTILINE,
    )

    print(f"  {old_path.relative_to(TRACK_ROOT)} → {new_path.relative_to(TRACK_ROOT)}")
    if dry_run:
        return

    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(content)
    if new_path != old_path:
        old_path.unlink()


def regenerate_indexes(modules: list[dict], dry_run: bool) -> None:
    """Rewrite index.md for every target phase directory."""
    by_dir: dict[str, list[dict]] = {}
    for m in modules:
        by_dir.setdefault(m["new_dir"], []).append(m)

    for new_dir, items in by_dir.items():
        items.sort(key=lambda i: (i["new_phase"], i["new_seq"]))
        new_phase = items[0]["new_phase"]
        # Pull label from any matching remap entry
        label = next(v[3] for v in PHASE_REMAP.values() if v[2] == new_dir)

        lines = [
            "---",
            f'title: "{label}"',
            "sidebar:",
            "  order: 0",
            f'  label: "{label}"',
            "---",
            "",
            f"> **AI/ML Engineering Track** | Phase {new_phase}",
            "",
            "## Modules",
            "",
            "| # | Module |",
            "|---|--------|",
        ]
        for m in items:
            mod_path = TRACK_ROOT / m["new_dir"] / f"module-{m['new_phase']}.{m['new_seq']}-{m['slug']}.md"
            # Read original title from old (or new) file
            src = m["old_path"] if m["old_path"].exists() and not dry_run else mod_path
            try:
                fm = src.read_text()
                title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
                title = title_match.group(1) if title_match else m["slug"]
            except FileNotFoundError:
                title = m["slug"]
            mod_slug = f"module-{m['new_phase']}.{m['new_seq']}-{m['slug']}"
            lines.append(f"| {m['new_phase']}.{m['new_seq']} | [{title}]({mod_slug}/) |")

        index_path = TRACK_ROOT / new_dir / "index.md"
        print(f"  index: {index_path.relative_to(TRACK_ROOT)}")
        if not dry_run:
            index_path.write_text("\n".join(lines) + "\n")


def cleanup_empty_phases(dry_run: bool) -> None:
    """Remove ai-safety dir (now merged into advanced-genai)."""
    safety_dir = TRACK_ROOT / "ai-safety"
    if not safety_dir.exists():
        return
    remaining = [f for f in safety_dir.iterdir() if f.name != "index.md"]
    if remaining:
        print(f"  WARN: ai-safety still has files: {[f.name for f in remaining]}")
        return
    print(f"  rmdir: {safety_dir.relative_to(REPO_ROOT)}")
    if not dry_run:
        for f in safety_dir.iterdir():
            f.unlink()
        safety_dir.rmdir()


def print_sidebar_order() -> None:
    """Print the new sidebar config snippet for astro.config.mjs."""
    print("\n=== New astro.config.mjs sidebar order ===")
    ordered = sorted(set((v[1], v[2], v[3]) for v in PHASE_REMAP.values()))
    for new_phase, new_dir, label in ordered:
        print(f"  {{ label: '{label}', autogenerate: {{ directory: 'ai-ml-engineering/{new_dir}' }}, collapsed: true }},")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Reorganizing AI/ML Engineering track ({'dry-run' if args.dry_run else 'live'})\n")
    modules = find_modules()
    print(f"Found {len(modules)} modules\n")

    print("Renaming + frontmatter rewrites:")
    for m in modules:
        rewrite_file(m, args.dry_run)

    print("\nRegenerating phase indexes:")
    regenerate_indexes(modules, args.dry_run)

    print("\nCleaning up merged phase directories:")
    cleanup_empty_phases(args.dry_run)

    print_sidebar_order()
    return 0


if __name__ == "__main__":
    sys.exit(main())
