"""Skip optional integration tests when external dependencies are unavailable."""

import pytest

pytest.importorskip("redis", reason="redis is required for external integration tests")
pytest.importorskip("passlib", reason="passlib is required for external integration tests")
