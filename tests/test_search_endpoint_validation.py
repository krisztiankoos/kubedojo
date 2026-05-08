from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from local_api.routes import search as search_route


def test_search_endpoint_rejects_empty_query(tmp_path: Path) -> None:
    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": [""], "kind": ["all"]},
        bridge_db_path=tmp_path / "messages.db",
    )
    assert status == 400
    assert payload["error"] == "query required"


def test_search_endpoint_rejects_long_query(tmp_path: Path) -> None:
    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["x" * 257], "kind": ["all"]},
        bridge_db_path=tmp_path / "messages.db",
    )
    assert status == 400
    assert payload["error"] == "query too long"


def test_search_endpoint_rejects_limit_over_100(tmp_path: Path) -> None:
    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["test"], "kind": ["all"], "limit": ["101"]},
        bridge_db_path=tmp_path / "messages.db",
    )
    assert status == 400
    assert payload["error"] == "invalid limit"


def test_search_endpoint_rejects_bad_kind(tmp_path: Path) -> None:
    status, payload, _ = search_route.route_search_request(
        tmp_path,
        "/api/search",
        {"q": ["test"], "kind": ["garbage"]},
        bridge_db_path=tmp_path / "messages.db",
    )
    assert status == 400
    assert payload["error"] == "invalid kind"
