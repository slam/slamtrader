import datetime
from decimal import Decimal
import json
from typing import Dict, List, Optional

from tda import auth
from tda.orders.common import Duration, OrderType
from tda.orders.equities import equity_buy_limit, equity_buy_market, equity_sell_market
from tda.utils import Utils


class BrokerException(Exception):
    def __init__(self, response):
        j = response.json()
        if "error" not in j:
            self.message = json.dumps(j, indent=4)
        self.message = response.json()["error"]
        super().__init__(self.message)


class Position:
    def __init__(self, raw) -> None:
        # {
        #     "shortQuantity": 0.0,
        #     "averagePrice": 399.95,
        #     "currentDayProfitLoss": 659.59,
        #     "currentDayProfitLossPercentage": 2.22,
        #     "longQuantity": 71.0,
        #     "settledLongQuantity": 71.0,
        #     "settledShortQuantity": 0.0,
        #     "instrument": {
        #         "assetType": "EQUITY",
        #         "cusip": "252131107",
        #         "symbol": "DXCM"
        #     },
        #     "marketValue": 30322.68,
        #     "maintenanceRequirement": 30322.68
        # }
        self.raw = raw

    @property
    def symbol(self) -> str:
        return self.raw["instrument"]["symbol"]

    @property
    def long(self) -> int:
        return self.raw["longQuantity"]

    @property
    def short(self) -> int:
        return self.raw["shortQuantity"]

    @property
    def trade_price(self) -> Decimal:
        return Decimal(self.raw["averagePrice"])


class Order:
    def __init__(self, raw) -> None:
        # {
        #     "session": "NORMAL",
        #     "duration": "GOOD_TILL_CANCEL",
        #     "orderType": "STOP",
        #     "complexOrderStrategyType": "NONE",
        #     "quantity": 1200.0,
        #     "filledQuantity": 0.0,
        #     "remainingQuantity": 1200.0,
        #     "requestedDestination": "AUTO",
        #     "destinationLinkName": "AutoRoute",
        #     "stopPrice": 13.86,
        #     "orderLegCollection": [
        #         {
        #             "orderLegType": "EQUITY",
        #             "legId": 1,
        #             "instrument": {
        #                 "assetType": "EQUITY",
        #                 "cusip": "92189F817",
        #                 "symbol": "VNM"
        #             },
        #             "instruction": "SELL",
        #             "positionEffect": "CLOSING",
        #             "quantity": 1200.0
        #         }
        #     ],
        #     "orderStrategyType": "SINGLE",
        #     "orderId": 3126389058,
        #     "cancelable": true,
        #     "editable": true,
        #     "status": "QUEUED",
        #     "enteredTime": "2020-07-30T01:08:58+0000",
        #     "accountId": 455102033
        # }
        self.raw = raw

    def __str__(self) -> str:
        if self.is_single:
            # The API only supports single leg anyways, so this for loop always
            # returns a single leg . OCO orders, for example, are not returned,
            # even when Thinkorswim does show them.
            str = []
            for leg in self.raw["orderLegCollection"]:
                instruction = leg["instruction"]
                quantity = int(leg["quantity"])

                sign = "+"
                if instruction == "SELL":
                    sign = "-"
                else:
                    sign = "+"

                symbol = leg["instrument"]["symbol"]
                if self.order_type == "STOP" or self.order_type == "LIMIT":
                    order = f"{self.order_type} {self.price}"
                else:
                    order = f"{self.order_type}"

                effect = leg["positionEffect"]

                # return f"SELL -1,200 VNM STP 13.86 GTC [TO CLOSE]"
                str.append(
                    f"{self.order_id} {instruction} {sign}{quantity} {symbol} {order} "
                    f"{self.duration} {effect} {self.status}"
                )
            return "\n".join(str)
        elif self.is_oco:
            str = [f"{self.order_id} OCO"]
            for child in self.raw["childOrderStrategies"]:
                child_order = Order(child)
                str.append(f"    {child_order}")

            return "\n".join(str)
        else:
            raise BrokerException(f"Unhandled orderStrategyType {self.strategy_type}")

    @property
    def order_id(self) -> str:
        return self.raw["orderId"]

    @property
    def status(self) -> str:
        return self.raw["status"]

    @property
    def active(self) -> bool:
        if self.is_single:
            return (
                self.status != "CANCELED"
                and self.status != "EXPIRED"
                and self.status != "FILLED"
                and self.status != "REJECTED"
                and self.status != "REPLACED"
            )
        elif self.is_oco:
            active = False
            for child in self.raw["childOrderStrategies"]:
                child_order = Order(child)
                active |= child_order.active
            return active
        else:
            raise BrokerException(f"Unhandled orderStrategyType {self.strategy_type}")

    @property
    def strategy_type(self) -> str:
        return self.raw["orderStrategyType"]

    @property
    def is_single(self) -> bool:
        return self.strategy_type == "SINGLE"

    def is_oco(self) -> bool:
        return self.strategy_type == "OCO"

    @property
    def order_type(self) -> str:
        return self.raw["orderType"]

    @property
    def duration(self) -> str:
        return self.raw["duration"]

    @property
    def price(self) -> float:
        if "stopPrice" in self.raw:
            return self.raw["stopPrice"]
        else:
            return self.raw["price"]


class TdAmeritrade:
    def __init__(
        self, account_id: str, api_key: str, token_path: str, redirect_uri: str
    ) -> None:
        self.account_id = account_id
        try:
            self.c = auth.client_from_token_file(token_path, api_key)
        except FileNotFoundError:
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager

            with webdriver.Chrome(ChromeDriverManager().install()) as driver:
                self.c = auth.client_from_login_flow(
                    driver, api_key, redirect_uri, token_path
                )

    def get_positions(self) -> Dict[str, Position]:
        r = self.c.get_account(self.account_id, fields=self.c.Account.Fields.POSITIONS)
        if not r.ok:
            raise BrokerException(r)

        data = r.json()
        account = data["securitiesAccount"]
        positions = {}
        for v in account["positions"]:
            position = Position(v)
            positions[position.symbol] = position
        return positions

    def get_position(self, symbol: str) -> Optional[Position]:
        positions = self.get_positions()
        if symbol in positions:
            return positions[symbol]
        return None

    def get_orders(self) -> List[Order]:
        # tda.debug.enable_bug_report_logging()

        from_date = datetime.datetime.today() + datetime.timedelta(-60)
        r = self.c.get_orders_by_path(
            self.account_id,
            # must specify from_date or the result would be empty
            from_entered_datetime=from_date,
            # The api only accept a single status as filter, not an array
            # Get everything and filter ourselves.
            #
            # Also, with a status filter the API doesn't return any OCO
            # orders, even if the status of the OCO matches the filter.
            # statuses=[Client.Order.Status.QUEUED],
        )
        if not r.ok:
            raise BrokerException(r)

        orders = []
        for order in r.json():
            # print(json.dumps(order, indent=4))
            orders.append(Order(order))
        return orders

    def get_order(self, order_id: str) -> Order:
        r = self.c.get_order(order_id, self.account_id)
        if not r.ok:
            raise BrokerException(r)

        return Order(r.json())

    def cancel_order(self, order_id: str) -> None:
        r = self.c.cancel_order(order_id, self.account_id)
        if not r.ok:
            raise BrokerException(r)

    def place_buy_market(self, symbol: str, quantity: int) -> str:
        order = (
            # market order can only be a day order
            equity_buy_market(symbol, quantity)
        ).build()

        r = self.c.place_order(self.account_id, order)
        if not r.ok:
            raise BrokerException(r)

        order_id = Utils(self.c, self.account_id).extract_order_id(r)
        return order_id

    def place_buy_limit(self, symbol: str, quantity: int, limit: Decimal) -> str:
        order = (
            equity_buy_limit(symbol, quantity, limit).set_duration(
                Duration.GOOD_TILL_CANCEL
            )
        ).build()

        r = self.c.place_order(self.account_id, order)
        if not r.ok:
            raise BrokerException(r)

        order_id = Utils(self.c, self.account_id).extract_order_id(r)
        return order_id

    def place_sell_stop(self, symbol: str, quantity: int, stop: Decimal):
        order = (
            equity_sell_market(symbol, quantity)
            .set_order_type(OrderType.STOP)
            .set_duration(Duration.GOOD_TILL_CANCEL)
            .set_stop_price(stop)
        ).build()

        r = self.c.place_order(self.account_id, order)
        if not r.ok:
            raise BrokerException(r)

        order_id = Utils(self.c, self.account_id).extract_order_id(r)
        return order_id
