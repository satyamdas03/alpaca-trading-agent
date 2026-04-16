"""conftest.py — install a lightweight apify stub before any test imports src.main."""
import sys
from unittest.mock import AsyncMock, MagicMock

# Build a minimal stub for the `apify` package so unit tests don't need the real SDK.
apify_stub = MagicMock()

# Actor is used as an async context manager and has async methods
actor_instance = MagicMock()
actor_instance.__aenter__ = AsyncMock(return_value=actor_instance)
actor_instance.__aexit__ = AsyncMock(return_value=False)
actor_instance.get_input = AsyncMock(return_value={})
actor_instance.push_data = AsyncMock()
actor_instance.fail = AsyncMock()

apify_stub.Actor = actor_instance

sys.modules.setdefault("apify", apify_stub)
