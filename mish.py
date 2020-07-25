#!/usr/bin/env python3

import config
from brokers.tdameritrade import TdaPortfolio

if __name__ == "__main__":
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
