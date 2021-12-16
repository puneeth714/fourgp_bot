import json
import os
import sys
# import json file  config.json or path given as commandline argument and load it to a python dictionary

#Config class will get the config file and return the values in python dictionary format. 
# The config file is a json file path given as commandline argument or default config.json file in the same directory as the script.
class Config:    
    def __init__(self, config_file=None)->None:
        """constructor of the class Config
        Args:
            config_file ([file], optional): [file path as parameter or commandline arg or default config.json file]. Defaults to None.
        """
        #if config_file is given as parameter
        if config_file is not None:
            self.config_file = config_file
        #if config_file is not given as parameter and commandline argument is given
        elif sys.argv[1] is not None:
            self.config_file = sys.argv[1]
        #if config_file is not given as parameter and commandline argument is not given use default config.json file
        elif os.path.isfile('config.json'):
            try:
                self.config_file = 'config.json'
            #if config.json file is not found rise an error
            except Exception as e:
                print(e)
                sys.exit(1)

        self.config = self.load_config()

    def load_config(self) -> dict:
        """load config.json file to a python dictionary

        Returns:
            dict: [config file as python dictionary]
        """   
        #try to open config.json file
        with open(self.config_file,'r') as f:
            #if config.json file is found load it to a python dictionary
            try:
                return json.load(f)
            except Exception as e:
                print(e)
                sys.exit(1)