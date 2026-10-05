"""
Data exploration and basic statistics
"""
import pandas as pd
import numpy as np
from scipy import stats

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Display basic information
print("Dataset shape:", df.shape)
print("\nFirst few rows:")
print(df.head(10))
print("\nData types:")
print(df.dtypes)
print("\nBasic statistics:")
print(df.describe())
print("\nValue counts for x (treatment):")
print(df['x'].value_counts())
print("\nMissing values:")
print(df.isnull().sum())
