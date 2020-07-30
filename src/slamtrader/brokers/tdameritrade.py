import json

from tda import auth
from tda.orders.common import Duration, OrderType
from tda.orders.equities import equity_sell_market
from tda.utils import Utils


class BrokerException(Exception):
    def __init__(self, response):
        j = response.json()
        if "error" not in j:
            self.message = json.dumps(j, indent=4)
        self.message = response.json()["error"]
        super().__init__(self.message)


class Position:
    def __init__(self, raw):
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
    def symbol(self):
        return self.raw["instrument"]["symbol"]

    @property
    def long(self):
        return self.raw["longQuantity"]

    @property
    def short(self):
        return self.raw["shortQuantity"]

    @property
    def trade_price(self):
        return self.raw["averagePrice"]


class Order:
    def __init__(self, raw):
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

    def __str__(self):
        for leg in self.raw["orderLegCollection"]:
            instruction = leg["instruction"]
            quantity = int(leg["quantity"])
            if instruction == "SELL":
                quantity *= -1
            symbol = leg["instrument"]["symbol"]
            effect = leg["positionEffect"]

            # return f"SELL -1,200 VNM STP 13.86 GTC [TO CLOSE]"
            return (
                f"{instruction} {quantity} {symbol} {self.order_type} "
                f"{self.price} {self.duration} {effect}"
            )

    @property
    def order_type(self):
        return self.raw["orderType"]

    @property
    def duration(self):
        return self.raw["duration"]

    @property
    def price(self):
        if "stopPrice" in self.raw:
            return self.raw["stopPrice"]
        else:
            return 0


class TdAmeritrade:
    def __init__(self, account_id, api_key, token_path, redirect_uri):
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

    def get_positions(self):
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

    def get_position(self, symbol):
        positions = self.get_positions()
        if symbol in positions:
            return positions[symbol]
        return None

    def get_order(self, order_id):
        r = self.c.get_order(order_id, self.account_id)
        if not r.ok:
            raise BrokerException(r)

        return Order(r.json())

    def place_sell_stop(self, symbol, quantity, stop):
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
