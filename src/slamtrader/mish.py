from decimal import Decimal
import importlib

import click

from . import __version__
from .brokers.tdameritrade import BrokerException, TdAmeritrade


def get_broker(config):
    return TdAmeritrade(
        config.tda_ira,
        config.tda_api_key,
        config.tda_token_path,
        config.tda_redirect_uri,
    )


def upper(ctx, param, value):
    return value.upper()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """ Semi-automate Mish's trading service """

    try:
        config = importlib.import_module("config")
    except ModuleNotFoundError:
        config = importlib.import_module("config_example")

    ctx.obj = config


@main.command("list_orders")
@click.option("-a", "--all", is_flag=True, default=False)
@click.pass_obj
def list_orders(config, all: bool) -> None:
    """ List all active orders """
    broker = get_broker(config)

    try:
        orders = broker.get_orders()
        for order in orders:
            if order.active or all:
                click.echo(order)
    except BrokerException as error:
        raise click.ClickException(str(error))


@main.command("cancel_order")
@click.argument("order_id")
@click.pass_obj
def cancel_order(config, order_id: str):
    """ Cancel an order """
    broker = get_broker(config)

    try:
        order = broker.get_order(order_id)
        # This check is not entirely reliable. A canceled order could stay in
        # QUEUED state for many seconds
        if not order.active:
            raise click.ClickException(f"{order.order_id} is not active")
        broker.cancel_order(order.order_id)
        click.echo(f"{order.order_id} canceled")
    except BrokerException as error:
        raise click.ClickException(str(error))


@main.command("buy_market")
@click.argument("symbol", callback=upper)
@click.argument("quantity", type=int)
@click.pass_obj
def buy_market(config, symbol: str, quantity: int) -> None:
    """ Buy a stock at market """

    broker = get_broker(config)

    try:
        order_id = broker.place_buy_market(symbol, quantity)
        order = broker.get_order(order_id)
        click.echo(order)
    except BrokerException as error:
        raise click.ClickException(str(error))


@main.command("buy_limit")
@click.argument("symbol", callback=upper)
@click.argument("quantity", type=int)
@click.argument("limit", type=float)
@click.pass_obj
def buy_limit(config, symbol: str, quantity: int, limit) -> None:
    """ Buy a stock with a buy stop """

    broker = get_broker(config)

    try:
        order_id = broker.place_buy_limit(symbol, quantity, limit)
        order = broker.get_order(order_id)
        click.echo(order)
    except BrokerException as error:
        raise click.ClickException(str(error))


@main.command("sell_stop")
@click.argument("symbol", callback=upper)
@click.argument("percentage", type=float)
@click.argument("stop", type=Decimal)
@click.pass_obj
def sell_stop(config, symbol: str, percentage: float, stop: Decimal) -> None:
    """ Sell a stock with a sell stop """

    broker = get_broker(config)

    try:
        position = broker.get_position(symbol)
        if not position:
            raise click.ClickException(f"No position in {symbol}")
        quantity = int(round(position.long * (percentage / 100), 0))
        click.echo(
            (
                f"Selling {quantity} shares ({percentage}%) of "
                f"{symbol} with a sell stop at {stop}"
            )
        )
        order_id = broker.place_sell_stop(symbol, quantity, stop)

        order = broker.get_order(order_id)
        click.echo(order)
    except BrokerException as error:
        raise click.ClickException(str(error))
