from alpaca.trading.client import TradingClient


class AlpacaClient:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.client = TradingClient(api_key, secret_key, paper=paper)

    def get_account(self):
        return self.client.get_account()

    def submit_order(self, order):
        return self.client.submit_order(order)
