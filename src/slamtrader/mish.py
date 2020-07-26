import click
import config

from . import __version__
from .brokers.tdameritrade import TdaPortfolio


@click.command()
@click.version_option(version=__version__)
def main():
    """ Semi-automate Mish's trading service """

    account = TdaPortfolio(
        config.tda_ira,
        config.tda_api_key,
        config.tda_token_path,
        config.tda_redirect_uri,
    )

    symbol = "CGC"
    quantity = 300
    target_ratio = 0.5
    stop = 15.87
    target = 21.40

    account.set_mish_stop(symbol, quantity, target_ratio, target, stop)
