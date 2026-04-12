"""Exception types for the agent runtime.

All exceptions raised by runner.invoke() are subclasses of AgentRuntimeError.
Callers can catch the base to handle any runtime failure, or specific types
for targeted handling (e.g. backoff on RateLimitedError, alert on AgentStalledError).

Issue: #1184
"""
from __future__ import annotations


class AgentRuntimeError(Exception):
    """Base class for all errors raised by the agent runtime."""


class AgentUnavailableError(AgentRuntimeError):
    """The requested agent is not in the registry or its CLI is not installed.

    Also raised when registry entry has ``cli_available: False`` (e.g. Grok stub).
    """


class RateLimitedError(AgentRuntimeError):
    """The provider rate-limited this request.

    Raised pre-call when has_headroom() reports a recent rate-limit within
    the last 5h window, OR post-call when the adapter's parse_response()
    classifies the failure as rate-limited (matched stderr patterns).

    Callers that want retry behavior should catch this and back off.
    Callers that want fail-fast should let it propagate.
    """

    def __init__(self, agent: str, model: str, reason: str = ""):
        self.agent = agent
        self.model = model
        self.reason = reason
        super().__init__(
            f"{agent}/{model} rate limited" + (f": {reason}" if reason else "")
        )


class AgentTimeoutError(AgentRuntimeError):
    """Hard wall-clock timeout exceeded.

    Distinct from AgentStalledError. Raised when total runtime (from spawn
    to now) exceeds ``hard_timeout``, regardless of whether the agent was
    still making progress. This is the "absolute max" guardrail — agents
    that legitimately need more than 30 minutes should request it per-call.
    """

    def __init__(self, agent: str, hard_timeout: int):
        self.agent = agent
        self.hard_timeout = hard_timeout
        super().__init__(
            f"{agent} exceeded hard_timeout={hard_timeout}s"
        )


class AgentStalledError(AgentRuntimeError):
    """Agent produced no activity for longer than ``stall_timeout``.

    Distinct from AgentTimeoutError. Raised when the last observed activity
    (stdout line OR liveness file mtime bump) is older than ``stall_timeout``.
    The agent might have been alive earlier but is now genuinely stuck —
    waiting for input, deadlocked, or the provider dropped the connection.

    This is the failure mode #1179 etc. are trying to AVOID: in the old code,
    naive `subprocess.run(timeout=N)` killed healthy slow calls; with stall
    detection, we only kill if truly silent.
    """

    def __init__(self, agent: str, stall_timeout: int, last_activity_age: float):
        self.agent = agent
        self.stall_timeout = stall_timeout
        self.last_activity_age = last_activity_age
        super().__init__(
            f"{agent} stalled: {last_activity_age:.0f}s since last activity "
            f"(stall_timeout={stall_timeout}s)"
        )
