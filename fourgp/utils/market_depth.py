import matplotlib
import pandas as pd
from datetime import datetime


class DepthData:
    def __init__(self, depth_data: dict) -> None:
        self.depth_data = depth_data
        self.asks = self.depth_data['asks']
        self.bids = self.depth_data['bids']
        # self.__sort_depth_data__()

    def __sort_depth_data__(self) -> None:
        self.asks.sort(key=lambda x: x[1], reverse=True)
        self.bids.sort(key=lambda x: x[1], reverse=True)

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

    def make_depth(self, depth_data=None):
        if depth_data is not None:
            depth = pd.DataFrame(depth_data)
        else:
            depth = pd.DataFrame(self.depth_data)
        depth.columns = ["symbol", "Bids", "Asks",
                         "timestamp", "datetime", "nounce"]
        depth = depth[["Bids", "Asks"]]
        depth = depth.to_dict()
        timenow = datetime.timestamp(datetime.now())
        return depth, timenow

    def min_ba(self):
        # returns minimum bid and ask values in the depth data with its coresponding values and retun as dictionary
        min_volumes = {"bid": None, "ask": None}
        values = []
        for volume in self.bids:
            if min_volumes['bid'] == None:
                min_volumes['bid'] = volume[1]
                values.append(volume[1])
            elif volume[1] < min_volumes['bid']:
                min_volumes['bid'] = volume[1]
                values[0] = volume[1]
        for volume in self.asks:
            if min_volumes['ask'] == None:
                min_volumes['ask'] = volume[1]
                values.append(volume[1])
            elif volume[1] < min_volumes['ask']:
                min_volumes['ask'] = volume[1]
                values[1] = volume[1]
        new_dict={values[0]:min_volumes['bid'],values[1]:min_volumes['ask']}
        return new_dict

    def max_ba(self):
        # returns maximum bid and ask values in the depth data with its coresponding values and retun as dictionary
        max_volumes = {"bid": None, "ask": None}
        values = []
        for volume in self.bids:
            if max_volumes['bid'] == None:
                max_volumes['bid'] = volume[1]
                values.append(volume[0])
            elif volume[1] > max_volumes['bid']:
                max_volumes['bid'] = volume[1]
                values[0] = volume[0]
        for volume in self.asks:
            if max_volumes['ask'] == None:
                max_volumes['ask'] = volume[1]
                values.append(volume[0])
            elif volume[1] > max_volumes['ask']:
                max_volumes['ask'] = volume[1]
                values[1] = volume[0]
        new_dict={values[0]:max_volumes['bid'],values[1]:max_volumes['ask']}
        return new_dict
