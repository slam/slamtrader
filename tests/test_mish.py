import click.testing
import pytest

from slamtrader import mish


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_main_succeeds(runner):
    result = runner.invoke(mish.main)
    assert result.exit_code == 0
