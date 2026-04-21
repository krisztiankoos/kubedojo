#!/usr/bin/env python3
"""Parse and reassemble curriculum modules by rubric section slots.

Usage:
    python scripts/module_sections.py <path>
    python scripts/module_sections.py <path> --assert-roundtrip
"""

from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass
from pathlib import Path
import re


_FRONTMATTER_FENCE = "---"
_FENCE_RE = re.compile(r"^[ \t]{0,3}([`~]{3,})(.*)$")
_HEADING_RE = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+[ \t]*)?$")
_PUNCT_STRIP = " \t:;,.!?-–—"
_MATCH_PREFIXES = (":", "-", "–", "—")

_CANONICAL_SLOT_ORDER = (
    "learning_outcomes",
    "why_matters",
    "did_you_know",
    "common_mistakes",
    "quiz",
    "hands_on",
    "next_module",
)

_SECTION_RANK = {
    "learning_outcomes": 0,
    "why_matters": 1,
    "core_subsection": 2,
    "did_you_know": 3,
    "common_mistakes": 4,
    "quiz": 5,
    "hands_on": 6,
    "next_module": 7,
}

_LEARNING_OUTCOMES_ALIASES = (
    "learning outcomes",
    "outcomes",
    "what you'll learn",
    "what you will learn",
    "what you'll be able to do",
    "what you will be able to do",
)
_WHY_MATTERS_ALIASES = (
    "why this module matters",
    "why this matters",
)
_DID_YOU_KNOW_ALIASES = (
    "did you know",
    "did you know?",
)
_COMMON_MISTAKES_ALIASES = (
    "common mistakes",
    "mistakes to avoid",
)
_QUIZ_ALIASES = (
    "quiz",
    "quick quiz",
    "quiz yourself",
    "test yourself",
    "module quiz",
)
_HANDS_ON_ALIASES = (
    "hands-on exercise",
    "hands-on",
    "hands-on lab",
    "lab",
    "practice",
)
_NEXT_MODULE_ALIASES = (
    "next module",
    "next",
    "what's next",
    "what is next",
    "continue learning",
    "next steps",
    "where to go next",
    "next section",
    "next modules",
)


@dataclass
class Section:
    slot: str
    heading: str
    body: str
    level: int


@dataclass
class ModuleDocument:
    frontmatter: str
    title_line: str
    sections: list[Section]
    raw: str


@dataclass
class _HeadingToken:
    level: int
    text: str
    start: int
    end: int
    raw_line: str


def _normalize_heading_text(heading: str) -> str:
    return " ".join(heading.strip().lower().split())


def _strip_alias_suffix(text: str) -> str:
    return text.rstrip(_PUNCT_STRIP)


def _matches_alias(heading: str, alias: str) -> bool:
    if heading == alias:
        return True
    if not heading.startswith(alias):
        return False
    suffix = heading[len(alias):].lstrip()
    return suffix.startswith(_MATCH_PREFIXES)


def _slot_from_heading(heading: str) -> str | None:
    normalized = _normalize_heading_text(heading)
    stripped = _strip_alias_suffix(normalized)
    alias_sets = (
        (_LEARNING_OUTCOMES_ALIASES, "learning_outcomes"),
        (_WHY_MATTERS_ALIASES, "why_matters"),
        (_DID_YOU_KNOW_ALIASES, "did_you_know"),
        (_COMMON_MISTAKES_ALIASES, "common_mistakes"),
        (_QUIZ_ALIASES, "quiz"),
        (_HANDS_ON_ALIASES, "hands_on"),
        (_NEXT_MODULE_ALIASES, "next_module"),
    )
    for aliases, slot in alias_sets:
        if any(_matches_alias(stripped, alias) for alias in aliases):
            return slot
    return None


def _find_frontmatter(text: str) -> tuple[str, int]:
    if not text.startswith(f"{_FRONTMATTER_FENCE}\n") and not text.startswith(f"{_FRONTMATTER_FENCE}\r\n"):
        return "", 0

    cursor = 0
    for line in text.splitlines(keepends=True):
        cursor += len(line)
        if cursor <= len(line):
            continue
        if line.rstrip("\r\n") == _FRONTMATTER_FENCE:
            return text[:cursor], cursor
    return "", 0


def _scan_headings(text: str, start: int) -> list[_HeadingToken]:
    tokens: list[_HeadingToken] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    cursor = start

    for line in text[start:].splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        fence_match = _FENCE_RE.match(stripped)
        if fence_match:
            marker = fence_match.group(1)
            marker_char = marker[0]
            if not in_fence:
                in_fence = True
                fence_char = marker_char
                fence_len = len(marker)
            elif marker_char == fence_char and len(marker) >= fence_len:
                in_fence = False
                fence_char = ""
                fence_len = 0
            cursor += len(line)
            continue
        if in_fence:
            cursor += len(line)
            continue

        match = _HEADING_RE.match(stripped)
        if match:
            marker = match.group(1)
            heading_text = match.group(2)
            tokens.append(
                _HeadingToken(
                    level=len(marker),
                    text=heading_text,
                    start=cursor,
                    end=cursor + len(line),
                    raw_line=line,
                )
            )
        cursor += len(line)

    return tokens


def _classify_sections(sections: list[Section]) -> None:
    for section in sections:
        mapped = _slot_from_heading(section.heading)
        section.slot = mapped if mapped is not None else "unknown"

    why_index = next((idx for idx, section in enumerate(sections) if section.slot == "why_matters"), None)
    if why_index is None:
        return

    end_index = next(
        (
            idx
            for idx in range(why_index + 1, len(sections))
            if sections[idx].slot in {"common_mistakes", "quiz", "hands_on", "next_module"}
        ),
        None,
    )
    stop = len(sections) if end_index is None else end_index
    for idx in range(why_index + 1, stop):
        if sections[idx].slot == "unknown":
            sections[idx].slot = "core_subsection"


def parse_module(text: str) -> ModuleDocument:
    frontmatter, body_start = _find_frontmatter(text)
    headings = _scan_headings(text, body_start)
    first_h2_index = next((idx for idx, token in enumerate(headings) if token.level == 2), None)

    title_token: _HeadingToken | None = None
    if first_h2_index is None:
        title_token = next((token for token in headings if token.level == 1), None)
    else:
        for token in headings[:first_h2_index]:
            if token.level == 1:
                title_token = token
                break

    first_h2 = None if first_h2_index is None else headings[first_h2_index]
    prefix_after_frontmatter: str
    between_title_and_sections = ""
    title_line = ""

    if title_token is None:
        cutoff = len(text) if first_h2 is None else first_h2.start
        prefix_after_frontmatter = text[body_start:cutoff]
    else:
        prefix_after_frontmatter = text[body_start:title_token.start]
        title_line = title_token.raw_line.rstrip("\r\n")
        if first_h2 is None:
            between_title_and_sections = text[title_token.end:]
        else:
            between_title_and_sections = text[title_token.end:first_h2.start]

    h2_tokens = [token for token in headings if token.level == 2]
    sections: list[Section] = []
    for idx, token in enumerate(h2_tokens):
        next_start = len(text) if idx + 1 >= len(h2_tokens) else h2_tokens[idx + 1].start
        section = Section(
            slot="unknown",
            heading=token.text,
            body=text[token.end:next_start],
            level=2,
        )
        section._heading_line_raw = token.raw_line
        sections.append(section)

    _classify_sections(sections)

    doc = ModuleDocument(
        frontmatter=frontmatter,
        title_line=title_line,
        sections=sections,
        raw=text,
    )
    doc._prefix_after_frontmatter = prefix_after_frontmatter
    doc._title_line_raw = title_token.raw_line if title_token is not None else ""
    doc._between_title_and_sections = between_title_and_sections
    return doc


def assemble_module(doc: ModuleDocument) -> str:
    pieces: list[str] = [doc.frontmatter, getattr(doc, "_prefix_after_frontmatter", "")]
    title_line_raw = getattr(doc, "_title_line_raw", "")
    if doc.title_line:
        if title_line_raw and title_line_raw.rstrip("\r\n") == doc.title_line:
            pieces.append(title_line_raw)
        else:
            suffix = "\n" if not doc.title_line.endswith(("\n", "\r\n")) else ""
            pieces.append(f"{doc.title_line}{suffix}")
    pieces.append(getattr(doc, "_between_title_and_sections", ""))

    for section in doc.sections:
        heading_line_raw = getattr(section, "_heading_line_raw", "")
        if heading_line_raw and heading_line_raw.rstrip("\r\n") == f"{'#' * section.level} {section.heading}":
            pieces.append(heading_line_raw)
        else:
            pieces.append(f"{'#' * section.level} {section.heading}\n")
        pieces.append(section.body)
    return "".join(pieces)


def find_section(doc: ModuleDocument, slot: str) -> Section | None:
    return next((section for section in doc.sections if section.slot == slot), None)


def _copy_document(doc: ModuleDocument) -> ModuleDocument:
    sections: list[Section] = []
    for section in doc.sections:
        copied = Section(
            slot=section.slot,
            heading=section.heading,
            body=section.body,
            level=section.level,
        )
        if hasattr(section, "_heading_line_raw"):
            copied._heading_line_raw = section._heading_line_raw
        sections.append(copied)

    cloned = ModuleDocument(
        frontmatter=doc.frontmatter,
        title_line=doc.title_line,
        sections=sections,
        raw=doc.raw,
    )
    cloned._prefix_after_frontmatter = getattr(doc, "_prefix_after_frontmatter", "")
    cloned._title_line_raw = getattr(doc, "_title_line_raw", "")
    cloned._between_title_and_sections = getattr(doc, "_between_title_and_sections", "")
    return cloned


def _find_insert_index(sections: list[Section], slot: str) -> int:
    target_rank = _SECTION_RANK[slot]
    next_anchor = next(
        (
            idx
            for idx, section in enumerate(sections)
            if _SECTION_RANK.get(section.slot) is not None and _SECTION_RANK[section.slot] > target_rank
        ),
        None,
    )
    if next_anchor is not None:
        return next_anchor

    prev_anchor = next(
        (
            idx
            for idx in range(len(sections) - 1, -1, -1)
            if _SECTION_RANK.get(sections[idx].slot) is not None
            and _SECTION_RANK[sections[idx].slot] <= target_rank
        ),
        None,
    )
    if prev_anchor is not None:
        return prev_anchor + 1

    return 0


def insert_section(doc: ModuleDocument, slot: str, heading: str, body: str) -> ModuleDocument:
    if slot not in _CANONICAL_SLOT_ORDER:
        raise ValueError(f"unknown insertable slot: {slot}")
    if find_section(doc, slot) is not None:
        raise ValueError(f"section already exists for slot {slot}")

    updated = _copy_document(doc)
    insert_at = _find_insert_index(updated.sections, slot)
    section = Section(slot=slot, heading=heading, body=body, level=2)
    section._heading_line_raw = f"## {heading}\n"
    updated.sections.insert(insert_at, section)
    updated.raw = assemble_module(updated)
    return updated


def _first_body_line(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _print_roundtrip_diff(expected: str, actual: str, path: Path) -> None:
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile=f"{path} (original)",
        tofile=f"{path} (assembled)",
    )
    sys.stderr.writelines(diff)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--assert-roundtrip", action="store_true")
    args = parser.parse_args(argv)

    text = args.path.read_text(encoding="utf-8")
    doc = parse_module(text)
    assembled = assemble_module(doc)

    if args.assert_roundtrip:
        if assembled != text:
            _print_roundtrip_diff(text, assembled, args.path)
            return 1
        return 0

    for section in doc.sections:
        first_line = _first_body_line(section.body)
        print(f"{section.slot}: {first_line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
