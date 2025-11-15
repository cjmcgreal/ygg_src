#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 08:46:53 2025

@author: conrad
"""
#%% Basic example
import pandas as pd

# Load the Excel file
df = pd.read_excel("exercises_db.xlsx")

# Preview the data
print(df.head())


#%% Read specific sheet by name
import pandas as pd

# Load the Excel file
df = pd.read_excel("exercises_db.xlsx", sheet_name="exercises")

# Preview the data
print(df.head())

#%% Read all sheets
import pandas as pd

# Load the Excel file
df = pd.read_excel("exercises_db.xlsx", sheet_name=None) # dict of dataframes

# Preview the data
print(df.head())