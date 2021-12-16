import matplotlib
class DepthData:
    def __init__(self, depth_data: dict) -> None:
        self.depth_data = depth_data
        self.asks = self.depth_data['asks']
        self.bids = self.depth_data['bids']
        self.__sort_depth_data__()

    def __sort_depth_data__(self) -> None:
        self.asks.sort(key=lambda x: x[1], reverse=True)
        self.bids.sort(key=lambda x: x[1], reverse=True)

    def get_depth_prices(self) -> list:
        return [x[0] for x in self.asks] + [x[0] for x in self.bids]

    def get_depth_amounts(self) -> list:
        return [x[1] for x in self.asks] + [x[1] for x in self.bids]

    def get_total_asks(self) -> float:
        return sum(x[1] for x in self.asks)

    def get_total_bids(self) -> float:
        return sum(x[1] for x in self.bids)

    def which_has_more_volume(self) -> str:
        if self.get_total_asks() > self.get_total_bids():
            return 'asks'
        else:
            return 'bids'