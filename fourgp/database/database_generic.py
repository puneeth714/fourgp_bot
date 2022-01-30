import pandas as pd
import json
# create a class to handle json based database


class Database_generic:
    def __init__(self, file_path,file_type="parquet"):
        self.database_name = file_path
        self.file_type = file_type

    def read_data(self):
        if self.file_type == "parquet":
            data = pd.read_parquet(self.database_name)
        elif self.file_type == "csv":
            data = pd.read_csv(self.database_name)
        return data

    def write_data(self, data):
        if self.file_type == "parquet":
            data.to_parquet(self.database_name)
        elif self.file_type == "csv":
            data.to_csv(self.database_name)

    def write_file_json(self,data=None):
        if data is None:
            # check if self.data is not None
            data = self.data
        # append the file
        with open(self.database_name, "a") as f:
            f.write(json.dumps(data))
            f.write("\n")
            