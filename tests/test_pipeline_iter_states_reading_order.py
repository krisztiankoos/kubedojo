from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.quality import pipeline, state  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_state_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "STATE_DIR", tmp_path / "state")
    state.STATE_DIR.mkdir(parents=True, exist_ok=True)


def _write_states(slugs: list[str]) -> None:
    for slug in slugs:
        state.save_state(
            {
                "slug": slug,
                "stage": "COMMITTED",
                "history": [{"at": state.now_iso(), "stage": "COMMITTED"}],
            }
        )


def _iter_state_slugs() -> list[str]:
    return [st["slug"] for st in pipeline.iter_states()]


def test_iter_states_orders_by_track_then_section_then_module_number() -> None:
    _write_states(
        [
            "platform-toolkits-security-quality-security-tools-module-1.1-kyverno",
            "cloud-aws-essentials-module-1.1-iam",
            "platform-foundations-security-principles-module-1.1-security-mindset",
            "prerequisites-zero-to-terminal-module-0.1-what-is-a-computer",
        ]
    )

    assert _iter_state_slugs() == [
        "prerequisites-zero-to-terminal-module-0.1-what-is-a-computer",
        "cloud-aws-essentials-module-1.1-iam",
        "platform-foundations-security-principles-module-1.1-security-mindset",
        "platform-toolkits-security-quality-security-tools-module-1.1-kyverno",
    ]


def test_module_numbers_sort_numerically_not_lexicographically() -> None:
    _write_states(
        [
            "cloud-aws-essentials-module-1.10-cloudwatch",
            "cloud-aws-essentials-module-1.3-ec2",
            "cloud-aws-essentials-module-1.2-vpc",
        ]
    )

    assert _iter_state_slugs() == [
        "cloud-aws-essentials-module-1.2-vpc",
        "cloud-aws-essentials-module-1.3-ec2",
        "cloud-aws-essentials-module-1.10-cloudwatch",
    ]


def test_index_modules_sort_before_numbered_modules_in_section() -> None:
    _write_states(
        [
            "platform-foundations-security-principles-module-1.1-security-mindset",
            "platform-foundations-security-principles",
        ]
    )

    assert _iter_state_slugs() == [
        "platform-foundations-security-principles",
        "platform-foundations-security-principles-module-1.1-security-mindset",
    ]


def test_unknown_track_sorts_to_end() -> None:
    _write_states(
        [
            "unknown-track-module-1.1-surprise",
            "on-premises-planning-module-1.1-case-for-on-prem",
            "prerequisites-zero-to-terminal-module-0.1-what-is-a-computer",
        ]
    )

    assert _iter_state_slugs() == [
        "prerequisites-zero-to-terminal-module-0.1-what-is-a-computer",
        "on-premises-planning-module-1.1-case-for-on-prem",
        "unknown-track-module-1.1-surprise",
    ]
