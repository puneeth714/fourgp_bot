from fourgp.order_management.OrderManagement import Orders
import ccxt

class Mover(Orders):
    def __init__(self, config,levels:dict,connection:ccxt or str) -> bool:
        self.config=config
        self.levels=levels
        self.connection=connection

    def configs_needed(self):
        """just print the configurations names and value types ever needed by the mover function"""
        print("configs needed by the mover function")
        print("Hard_mm : int")
        print("local_mm")

        
    def config_vals(self):
        """Get all the config values required for mover and set them in self."""
        pass

    def check_vals(self):
        """check if all the configs needed are as expected"""
        # TODO : mix up all the prechecks at once and then check if all the checks are true and fail the bot if not and exit
        # make it up at the starting itself so the bot will be working more effectively rather than checking configs after 4
        # doing some computations
        pass

    def price_forever(self,price):
        """Get current price forever and set self.price"""
        pass

    def check_vals():
        """Check if the values are in the range of the levels"""
        # check if the values are in the given bound range i.e based on config or ml values
        pass

    def check_profit(self):
        """check if the current price levels are still profitable with current change in price"""
        pass

    def pre_checks(self):
        """Do all the pre checks before sending the order"""
        pass

    def move_vals(self):
        """change the valuse to the new levels"""
        pass