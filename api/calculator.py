# api/calculator.py

import pandas as pd


class Calculator:
    """ Main calculator"""

    def __init__(self) -> None:
        self._dataset = {}

    def verify_data(self, start=None, max=None):
        self._load_dataset(start, max)
        return self._validate_dataset()

    def run(self):
        self._load_dataset()

    def _load_dataset(self, start=None, max=None):
        self._dataset = pd.read_csv(
            'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv')

        # select a subset of the data if start and max are given
        if start and max:
            next_val = start + max
            self._dataset = self._dataset.iloc[start:next_val]

    def _validate_dataset(self):
        return bool(self._dataset['sex'].isnull().sum() == 0)
