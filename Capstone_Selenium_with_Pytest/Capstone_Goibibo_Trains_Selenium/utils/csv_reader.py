#  Reads CSV files and returns data as a list of dictionaries (each row becomes a dictionary with column headers as keys).

import csv
import os

class CSVReader:

    @staticmethod
    def read_csv(file_name):
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            file_name
        )

        data = []
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data