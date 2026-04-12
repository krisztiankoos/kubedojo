"""Agent adapters — one file per agent CLI.

Each adapter implements the ``AgentAdapter`` protocol from ``base.py`` and wraps
exactly one agent's subprocess CLI. Adding a new agent = one new file here +
one new entry in ``registry.py``.

See ``_template.py`` for a living-documentation reference adapter that new
authors should copy as a starting point.

Issue: #1184
"""
from __future__ import annotations
