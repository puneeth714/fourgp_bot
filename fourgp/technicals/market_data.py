class marketTrades:
    def __init__(self,market_pair,api_object,limit:int) -> None:
        self.api_object = api_object
        self.limit = limit
        self.market_pair = market_pair
    def get_trades(self):
        return self.api_object.fetchTrades(self.market_pair,limit=int(self.limit))
    def trades_obj(self):
        return self.api_object.fetchTrades