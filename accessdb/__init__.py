# -*- coding: utf-8 -*-
"""
Created on Wed May 17 17:09:10 2017

@author: Dhana Babu
"""
import pandas as pd

from .utils import to_accessdb, create_accessdb

try:
    pd.DataFrame.to_accessdb = to_accessdb
except Exception:
    pass
