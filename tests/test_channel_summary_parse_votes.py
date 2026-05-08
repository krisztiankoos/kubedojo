from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_channels_route():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "local_api"
        / "routes"
        / "channels.py"
    )
    spec = importlib.util.spec_from_file_location("channels_route_vote_parse", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


channels_route = _load_channels_route()


def test_vote_regex_extracts_last_structured_vote() -> None:
    cases = [
        ("I considered [OPTION B], but final is [AGREE]", "AGREE"),
        ("Ship [OPTION A]", "OPTION A"),
        ("Use the alternate [OPTION A′]", "OPTION A′"),
        ("Use the alternate [OPTION A‘]", "OPTION A‘"),
        ("Pause this [DEFER]", "DEFER"),
        ("Not ready [NEEDS-CHANGES]", "NEEDS-CHANGES"),
        ("Not ready [NEEDS CHANGES]", "NEEDS CHANGES"),
        ("No bracketed vote here", None),
        ("Earlier fallback [DEFER]\nFinal line [DISAGREE]", None),
        ("Earlier fallback [DEFER]\nFinal line without protocol", None),
        ("Earlier fallback [DEFER]\n\nFinal line [AGREE]", "AGREE"),
    ]

    for body, expected in cases:
        assert channels_route.extract_thread_vote(body) == expected
