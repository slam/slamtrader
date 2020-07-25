import json

from tda import auth
from tda.orders.common import Duration, OrderType, one_cancels_other
from tda.orders.equities import equity_sell_market, equity_sell_limit


class TdaPortfolio:
    def __init__(self, account_id, api_key, token_path, redirect_uri):
        self.account_id = account_id
        try:
            self.c = auth.client_from_token_file(token_path, api_key)
        except FileNotFoundError:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            options.add_argument("--disable-dev-shm-usage")
            with webdriver.Chrome(
                ChromeDriverManager().install(), options=options
            ) as driver:
                self.c = auth.client_from_login_flow(
                    driver, api_key, redirect_uri, token_path
                )

    def set_mish_stop(self, symbol, quantity, target_ratio, target, stop):
        sell_stop_order = (
            equity_sell_market(symbol, quantity)
            .set_order_type(OrderType.STOP)
            .set_duration(Duration.GOOD_TILL_CANCEL)
            .set_stop_price(stop)
        )

        sell_limit_order = equity_sell_limit(
            symbol, quantity * target_ratio, target
        ).set_duration(Duration.GOOD_TILL_CANCEL)

        order = one_cancels_other(sell_stop_order, sell_limit_order).build()

        # Currently getting this error:
        #
        # Conditional Orders are not permitted for accounts in this segment.
        #
        # Ticket opened with TDAmeritrade
        r = self.c.place_order(self.account_id, order)

        if not r.ok:
            print(json.dumps(r.json(), indent=4))
            r.raise_for_status