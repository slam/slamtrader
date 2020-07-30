import importlib

import click

from . import __version__
from .brokers.tdameritrade import BrokerException, TdAmeritrade


def upper(ctx, param, value):
    return value.upper()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    """ Semi-automate Mish's trading service """

    try:
        config = importlib.import_module("config")
    except ModuleNotFoundError:
        config = importlib.import_module("config_example")

    ctx.obj = config


@main.command("buy_stop")
@click.argument("symbol", callback=upper)
@click.argument("quantity", type=int)
@click.argument("stop", type=float)
@click.pass_obj
def buy_stop(config, symbol, quantity, stop):
    """ Buy a stock with a buy stop """

    click.echo(f"Buying {quantity} share of {symbol} with buy stop at ${stop}")


@main.command("sell_stop")
@click.argument("symbol", callback=upper)
@click.argument("percentage", type=float)
@click.argument("stop", type=float)
@click.pass_obj
def sell_stop(config, symbol, percentage, stop):
    """ Sell a stock with a sell stop """

    broker = TdAmeritrade(
        config.tda_ira,
        config.tda_api_key,
        config.tda_token_path,
        config.tda_redirect_uri,
    )

    try:
        position = broker.get_position(symbol)
        if not position:
            raise click.ClickException(f"Not position in symbol {symbol}")
        quantity = int(round(position.long * (percentage / 100), 0))
        click.echo(
            (
                f"Selling {quantity} shares ({percentage}%) of "
                f"{symbol} with a sell stop at {stop}"
            )
        )
        order_id = broker.place_sell_stop(symbol, quantity, stop)
        click.echo(f"Submitted order ID {order_id}")

        order = broker.get_order(order_id)
        click.echo(order)
    except BrokerException as error:
        raise click.ClickException(error)
