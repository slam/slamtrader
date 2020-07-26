import click.testing
import pytest

from slamtrader import mish


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.fixture
def mock_tda_auth(mocker):
    mock = mocker.patch("tda.auth.client_from_token_file")
    return mock


def test_main_succeeds(runner, mock_tda_auth):
    result = runner.invoke(mish.main)
    assert result.exit_code == 0
