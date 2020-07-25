import json
import config
import tda
from tda.orders.common import OrderType
from tda.orders.common import Duration
from tda.orders.common import Session
import datetime

try:
    c = tda.auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    with webdriver.Chrome(ChromeDriverManager().install()) as driver:
        c = tda.auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)

account_id = '455102033'
symbol = 'CGC'
quantity = 300
target_ratio = 0.5
stop = 15.87
target = 21.40

# sell_stop_order = tda.orders.equities.equity_sell_market('CGC', quantity).set_order_type(tda.orders.common.OrderType.STOP).set_duration(
#     Duration.GOOD_TILL_CANCEL).set_session(Session.NORMAL).set_stop_price(15.87)

order = tda.orders.equities.equity_sell_market(
    'CGC', quantity * target_ratio).set_duration(Duration.DAY).set_session(Session.NORMAL).set_activation_price(target)

# order = tda.orders.common.one_cancels_other(
#     sell_stop_order, sell_limit_order).build()

r = c.place_order(account_id, order)

#assert r.ok, r.raise_for_status()
print(json.dumps(r.json(), indent=4))
