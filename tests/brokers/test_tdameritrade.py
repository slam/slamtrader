import json

import pytest

from slamtrader.brokers.tdameritrade import TdAmeritrade

TEST_ACCOUNT_DETAILS = """
{
    "securitiesAccount": {
        "type": "MARGIN",
        "accountId": "12345678",
        "roundTrips": 0,
        "isDayTrader": false,
        "isClosingOnlyRestricted": false,
        "positions": [
            {
                "shortQuantity": 0.0,
                "averagePrice": 380.783,
                "currentDayProfitLoss": -3.799999999999,
                "currentDayProfitLossPercentage": -0.04,
                "longQuantity": 20.0,
                "settledLongQuantity": 20.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "EQUITY",
                    "cusip": "67066G104",
                    "symbol": "NVDA"
                },
                "marketValue": 8488.0,
                "maintenanceRequirement": 8488.0
            },
            {
                "shortQuantity": 0.0,
                "averagePrice": 0.128,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 4.0,
                "settledLongQuantity": 4.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0VIX..UG00015000",
                    "symbol": "VIX_091620P15",
                    "description": "$VIX.X Sep 16 2020 15.0 Put",
                    "putCall": "PUT",
                    "underlyingSymbol": "$VIX.X"
                },
                "marketValue": 10.0,
                "maintenanceRequirement": 0.0
            },
            {
                "shortQuantity": 4.0,
                "averagePrice": 0.882,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 0.0,
                "settledLongQuantity": 0.0,
                "settledShortQuantity": -4.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0VIX..UG00020000",
                    "symbol": "VIX_091620P20",
                    "description": "$VIX.X Sep 16 2020 20.0 Put",
                    "putCall": "PUT",
                    "underlyingSymbol": "$VIX.X"
                },
                "marketValue": -90.0,
                "maintenanceRequirement": 2000.0
            },
            {
                "shortQuantity": 0.0,
                "averagePrice": 1.23,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 4.0,
                "settledLongQuantity": 4.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0VIX..IG00055000",
                    "symbol": "VIX_091620C55",
                    "description": "$VIX.X Sep 16 2020 55.0 Call",
                    "putCall": "CALL",
                    "underlyingSymbol": "$VIX.X"
                },
                "marketValue": 420.0,
                "maintenanceRequirement": 0.0
            },
            {
                "shortQuantity": 4.0,
                "averagePrice": 0.442,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 0.0,
                "settledLongQuantity": 0.0,
                "settledShortQuantity": -4.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0VIX..IG00080000",
                    "symbol": "VIX_091620C80",
                    "description": "$VIX.X Sep 16 2020 80.0 Call",
                    "putCall": "CALL",
                    "underlyingSymbol": "$VIX.X"
                },
                "marketValue": -160.0,
                "maintenanceRequirement": 0.0
            },
            {
                "shortQuantity": 0.0,
                "averagePrice": 6.065,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 1700.0,
                "settledLongQuantity": 0.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "EQUITY",
                    "cusip": "88166A409",
                    "symbol": "CANE"
                },
                "marketValue": 10302.0,
                "maintenanceRequirement": 10302.0
            },
            {
                "shortQuantity": 0.0,
                "averagePrice": 399.95,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 71.0,
                "settledLongQuantity": 71.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "EQUITY",
                    "cusip": "252131107",
                    "symbol": "DXCM"
                },
                "marketValue": 30923.34,
                "maintenanceRequirement": 30923.34
            }
        ],
        "initialBalances": {
            "accruedInterest": 1.07,
            "availableFundsNonMarginableTrade": 129363.01,
            "bondValue": 0.0,
            "buyingPower": 0.0,
            "cashBalance": 0.0,
            "cashAvailableForTrading": 0.0,
            "cashReceipts": 0.0,
            "dayTradingBuyingPower": 0.0,
            "dayTradingBuyingPowerCall": 0.0,
            "dayTradingEquityCall": 0.0,
            "equity": 260105.73,
            "equityPercentage": 98.0,
            "liquidationValue": 260971.24,
            "longMarginValue": 128742.72,
            "longOptionMarketValue": 430.0,
            "longStockValue": 139690.23,
            "maintenanceCall": 0.0,
            "maintenanceRequirement": 130742.72,
            "margin": -2888.0,
            "marginEquity": 125854.72,
            "moneyMarketFund": 134251.01,
            "mutualFundValue": 0.0,
            "regTCall": 0.0,
            "shortMarginValue": 0.0,
            "shortOptionMarketValue": -250.0,
            "shortStockValue": 0.0,
            "totalCash": 131363.01,
            "isInCall": false,
            "pendingDeposits": 0.0,
            "marginBalance": -2888.0,
            "shortBalance": 0.0,
            "accountValue": 260972.31
        },
        "currentBalances": {
            "accruedInterest": 1.07,
            "cashBalance": 0.0,
            "cashReceipts": 0.0,
            "longOptionMarketValue": 430.0,
            "liquidationValue": 260880.84,
            "longMarketValue": 139648.19,
            "moneyMarketFund": 129363.05,
            "savings": 0.0,
            "shortMarketValue": 0.0,
            "pendingDeposits": 0.0,
            "availableFunds": 119052.65,
            "availableFundsNonMarginableTrade": 119052.65,
            "buyingPower": 119052.65,
            "buyingPowerNonMarginableTrade": 119052.65,
            "dayTradingBuyingPower": 0.0,
            "equity": 260700.84,
            "equityPercentage": 100.0,
            "longMarginValue": 139648.19,
            "maintenanceCall": 0.0,
            "maintenanceRequirement": 141648.19,
            "marginBalance": -8310.4,
            "regTCall": 0.0,
            "shortBalance": 0.0,
            "shortMarginValue": 0.0,
            "shortOptionMarketValue": -250.0,
            "sma": 323072.74,
            "mutualFundValue": 0.0,
            "bondValue": 0.0
        },
        "projectedBalances": {
            "availableFunds": 119052.65,
            "availableFundsNonMarginableTrade": 119052.65,
            "buyingPower": 119052.65,
            "dayTradingBuyingPower": 0.0,
            "dayTradingBuyingPowerCall": 0.0,
            "maintenanceCall": 0.0,
            "regTCall": 0.0,
            "isInCall": false,
            "stockBuyingPower": 119052.65
        }
    }
} """


@pytest.fixture
def broker(mock_tda_client) -> TdAmeritrade:
    return TdAmeritrade("", "", "", "")


@pytest.fixture
def mock_tda_client(mocker):
    mock = mocker.patch("tda.auth.client_from_token_file")
    return mock


def test_get_positions(broker: TdAmeritrade, mock_tda_client):
    (
        mock_tda_client.return_value.get_account.return_value.json.return_value
    ) = json.loads(TEST_ACCOUNT_DETAILS)

    positions = broker.get_positions()
    nvda = positions["NVDA"]
    assert nvda.symbol == "NVDA"
    assert nvda.long == 20.0
    assert nvda.short == 0.0
    assert nvda.trade_price == 380.783

    with pytest.raises(KeyError):
        positions["NONE"]
