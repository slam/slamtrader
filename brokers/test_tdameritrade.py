import pytest
import oauthlib
from .tdameritrade import TdaPortfolio


def test_bad_login():
    with pytest.raises(oauthlib.oauth2.rfc6749.errors.InvalidClientError):
        TdaPortfolio("123", "abc", "def", "https://localhost")
