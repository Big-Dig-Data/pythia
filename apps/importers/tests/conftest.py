from pathlib import Path

import pytest


@pytest.fixture()
def test_data_path():
    this_dir = Path(__file__).resolve().parent

    def fn(fname: str):
        return this_dir / 'data' / fname

    return fn
