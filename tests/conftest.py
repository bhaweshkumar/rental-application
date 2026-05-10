"""Shared test fixtures."""
import pytest
from rental_platform.models import DealProfile


@pytest.fixture
def default_profile() -> DealProfile:
    return DealProfile()
