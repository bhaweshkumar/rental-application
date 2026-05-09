from unittest import mock

import pytest


class SimpleMocker:
    Mock = mock.Mock

    def __init__(self):
        self._patchers = []

    def patch(self, target, *args, **kwargs):
        patcher = mock.patch(target, *args, **kwargs)
        mocked = patcher.start()
        self._patchers.append(patcher)
        return mocked

    def stop(self):
        while self._patchers:
            self._patchers.pop().stop()


@pytest.fixture
def mocker():
    helper = SimpleMocker()
    try:
        yield helper
    finally:
        helper.stop()
