import sys
import json
import datetime

import config

from tda import auth
from tda.orders.common import Duration, OrderType, one_cancels_other
from tda.orders.equities import equity_sell_market, equity_sell_limit

try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager

    with webdriver.Chrome(ChromeDriverManager().install()) as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path
        )

account_id = "455102033"
symbol = "CGC"
quantity = 300
target_ratio = 0.5
stop = 15.87
target = 21.40

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
r = c.place_order(account_id, order)

if not r.ok:
    print(json.dumps(r.json(), indent=4))
    sys.exit(1)

assert r.ok
