import matplotlib


class DepthData:
    def __init__(self, depth_data: dict) -> None:
        self.depth_data = depth_data
        self.asks = self.depth_data['asks']
        self.bids = self.depth_data['bids']
        # self.__sort_depth_data__()

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
        return 'asks' if self.get_total_asks() > self.get_total_bids() else 'bids'

    def create_depth_chart(self) -> None:
       # create market depth chart same as depth chart in Binance
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pandas as pd
        asks = pd.DataFrame(self.asks, columns=['price', 'amount'])
        bids = pd.DataFrame(self.bids, columns=['price', 'amount'])
        asks['type'] = 'asks'
        bids['type'] = 'bids'
        df = pd.concat([asks, bids])
        df.plot(x='price', y='amount', kind='bar', stacked=True, legend=False)
        plt.xlabel('Price')
        plt.ylabel('Amount')
        plt.title('Market Depth')
        plt.savefig('depth.png')
        plt.close()
        return

    def find_min_max(self, price, current_price):
        # Get the nearest min and max volumes in top and bottom of the given price from the depth data
        if price > current_price:
            max(self.asks[1])
        elif price < current_price:
            min(self.bids[1])
