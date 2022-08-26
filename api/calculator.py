# api/calculator.py
from urllib.error import URLError
import os

import pandas as pd

from app import app


class Calculator:
    """ Main calculator"""

    default_source ='https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'

    def __init__(self, job_id:int =None, source: str=default_source) -> None:
        self._run_id = job_id
        self._source = source
        self._dataset = {}

    def verify_data(self, start: int=None, max:int=None) -> bool:
        """Verifies data by loading a chunk of data and returning validation result.

        Parameters
        ----------
        start : int, optional
            by default None
        max : int, optional
            by default None

        Returns
        -------
        bool
        """

        self._load_dataset(start, max)
        return self._validate_dataset()

    def _load_dataset(self, start:int=None, max:int=None) -> None:
        """Load a datatset with and convert to df based on source

        Parameters
        ----------
        start : int, optional
            by default None
        max : int, optional
            by default None
        """
        
        try:
            self._dataset = pd.read_csv(self._source)
        except URLError as err:
            app.logger.warning(f'Could not access url, fetching local copy {err}')
            self._dataset = pd.read_csv(os.path.abspath('data/titanic.csv'))
    
        # select a subset of the data if start and max are given
        if start and max:
            next_val = start + max
            self._dataset = self._dataset.iloc[start:next_val]

    def _validate_dataset(self) -> bool:
        """Validate dataset by checking if the gender column contains a value

        Returns
        -------
        bool
        """
        return bool(self._dataset['sex'].isnull().sum() == 0)
