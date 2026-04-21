from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import module_sections  # type: ignore[import-not-found]  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent


ROUNDTRIP_MODULES = [
    # Frontmatter only, `What You'll Learn`, `Quick Quiz`
    "src/content/docs/ai/ai-building/module-1.1-from-chat-to-ai-systems.md",
    # Frontmatter only, `What You'll Learn`, thin /ai v4 target
    "src/content/docs/ai/ai-for-kubernetes-platform-work/module-1.2-ai-for-kubernetes-troubleshooting-and-triage.md",
    # Frontmatter only, KCNA theory module with preamble + separators
    "src/content/docs/k8s/kcna/part0-introduction/module-0.1-kcna-overview.md",
    # Frontmatter only, `What You'll Learn`
    "src/content/docs/ai/ai-building/module-1.2-models-apis-context-structured-output.md",
    # Frontmatter + H1 title
    "src/content/docs/ai-ml-engineering/advanced-genai/module-1.1-fine-tuning-llms.md",
    # Frontmatter + H1 title, CKA-adjacent prerequisites module
    "src/content/docs/prerequisites/kubernetes-basics/module-1.1-first-cluster.md",
    # `Did You Know?` appears before the core body; `## Prerequisites` precedes rubric sections
    "src/content/docs/cloud/aws-essentials/module-1.12-cloudformation.md",
    # H3 preamble before first H2
    "src/content/docs/platform/foundations/systems-thinking/module-1.1-what-is-systems-thinking.md",
    # CKA module with thematic separators and no H1
    "src/content/docs/k8s/cka/part3-services-networking/module-3.1-services.md",
    # KCNA theory module
    "src/content/docs/k8s/kcna/part1-kubernetes-fundamentals/module-1.1-what-is-kubernetes.md",
    # `What's Next?` variant
    "src/content/docs/prerequisites/zero-to-terminal/module-0.1-what-is-a-computer.md",
]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_parse_and_assemble_roundtrip_real_modules() -> None:
    for relative_path in ROUNDTRIP_MODULES:
        original = _read(relative_path)
        parsed = module_sections.parse_module(original)
        assembled = module_sections.assemble_module(parsed)
        assert assembled == original, relative_path


def test_heading_variant_mapping() -> None:
    cases = {
        "Learning Outcomes": "learning_outcomes",
        "Outcomes": "learning_outcomes",
        "What You'll Learn": "learning_outcomes",
        "What You Will Learn": "learning_outcomes",
        "What You'll Be Able to Do": "learning_outcomes",
        "Why This Module Matters": "why_matters",
        "Why This Matters": "why_matters",
        "Did You Know?": "did_you_know",
        "Did You Know": "did_you_know",
        "Common Mistakes": "common_mistakes",
        "Mistakes to Avoid": "common_mistakes",
        "Quiz": "quiz",
        "Quick Quiz": "quiz",
        "Quiz Yourself": "quiz",
        "Test Yourself": "quiz",
        "Quiz: Test Your Understanding": "quiz",
        "Hands-On Exercise": "hands_on",
        "Hands-On Exercise: Event-Driven Processing with KEDA": "hands_on",
        "Hands-On": "hands_on",
        "Lab": "hands_on",
        "Practice": "hands_on",
        "Hands-On Lab": "hands_on",
        "Next Module": "next_module",
        "Next": "next_module",
        "What's Next": "next_module",
        "Continue Learning": "next_module",
        "Next Steps": "next_module",
    }
    for heading, expected in cases.items():
        assert module_sections._slot_from_heading(heading) == expected


def test_random_heading_is_core_subsection_when_between_why_and_trailing_slots() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
                "## Random Section",
                "",
                "core",
                "",
                "## Did You Know?",
                "",
                "fact",
                "",
            ]
        )
    )
    random_section = next(section for section in doc.sections if section.heading == "Random Section")
    assert random_section.slot == "core_subsection"


def test_random_heading_is_unknown_outside_core_band() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Random Section",
                "",
                "outside",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
            ]
        )
    )
    random_section = next(section for section in doc.sections if section.heading == "Random Section")
    assert random_section.slot == "unknown"


def test_find_section_returns_none_when_slot_missing() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
            ]
        )
    )
    assert module_sections.find_section(doc, "quiz") is None


def test_insert_section_places_quiz_before_hands_on_when_missing() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
                "## Deep Dive",
                "",
                "core",
                "",
                "## Hands-On Exercise",
                "",
                "lab",
                "",
                "## Sources",
                "",
                "- source",
                "",
            ]
        )
    )

    updated = module_sections.insert_section(
        doc,
        "quiz",
        "Quick Quiz",
        "\n\n1. Example?\n",
    )
    headings = [section.heading for section in updated.sections]
    assert headings == ["Why This Module Matters", "Deep Dive", "Quick Quiz", "Hands-On Exercise", "Sources"]
    assert module_sections.find_section(updated, "quiz") is not None


def test_insert_section_raises_when_slot_exists() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
                "## Quiz",
                "",
                "q",
                "",
            ]
        )
    )

    try:
        module_sections.insert_section(doc, "quiz", "Quick Quiz", "\n\n1. Duplicate\n")
    except ValueError as exc:
        assert "section already exists" in str(exc)
    else:
        raise AssertionError("expected ValueError for duplicate slot")


def test_insert_section_keeps_unknown_lead_in_before_inserted_learning_outcomes() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Prerequisites",
                "",
                "prep",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
            ]
        )
    )

    updated = module_sections.insert_section(
        doc,
        "learning_outcomes",
        "Learning Outcomes",
        "\n\n- learn\n",
    )
    headings = [section.heading for section in updated.sections]
    assert headings == ["Prerequisites", "Learning Outcomes", "Why This Module Matters"]


def test_insert_section_keeps_core_subsection_ordering_intact() -> None:
    doc = module_sections.parse_module(
        "\n".join(
            [
                "---",
                "title: Test",
                "---",
                "",
                "## Why This Module Matters",
                "",
                "why",
                "",
                "## Core A",
                "",
                "a",
                "",
                "## Core B",
                "",
                "b",
                "",
                "## Hands-On Exercise",
                "",
                "lab",
                "",
            ]
        )
    )

    updated = module_sections.insert_section(
        doc,
        "did_you_know",
        "Did You Know?",
        "\n\nfact\n",
    )
    headings = [section.heading for section in updated.sections]
    assert headings == ["Why This Module Matters", "Core A", "Core B", "Did You Know?", "Hands-On Exercise"]
    assert [section.heading for section in updated.sections if section.slot == "core_subsection"] == ["Core A", "Core B"]
