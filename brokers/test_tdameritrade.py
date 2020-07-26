import pytest
from .tdameritrade import TdaPortfolio


def test_bad_login():
    with pytest.raises(Exception):
        TdaPortfolio("123", "abc", "def", "https://localhost")
