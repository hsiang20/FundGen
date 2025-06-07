import pandas as pd
import numpy as np

"""
DATA PROCESSING
"""
def nanto0(data):
    data[np.isnan(data)] = 0.0
    return data

def cap_floor(data, cap, floor):
    data[data > cap] = cap
    data[data < floor] = floor
    return data

"""
EASY DATA MANIPULATION
"""
def add(data1, data2):
    out = data1 + data2
    return out

def sub(data1, data2):
    out = data1 - data2
    return out

def mul(data1, data2):
    out = data1 * data2
    return out

def div(data1, data2):
    out = data1 / data2
    return out

def addconst(data1, c):
    out = data1 + c
    return out

def subconst(data1, c):
    out = data1 - c
    return out

def mulconst(data1, c):
    out = data1 * c
    return out

def divconst(data1, c):
    out = data1 / c
    return out

def flip(data):
    return -data

def power(data, c):
    return data ** c

# def absolute(data):
#     return abs(data)

"""
ASSET-WISE OPERATIONS
"""
def rank(data):
    ranks = data.rank(axis=1, method="average")
    N = data.shape[1]
    return (ranks - 1) / (N - 1)

def demean(data):
    row_means = data.mean(axis=1)
    return data.sub(row_means, axis=0)

def normalize(data):
    # row_sums = data.sum(axis=1).abs()
    # row_sums[row_sums == 0] = 1
    # normalized_data = data.div(row_sums, axis=0)
    # return normalized_data
    row_mean = data.mean(axis=1)
    row_std = data.std(axis=1)
    # Avoid division by zero
    row_std = row_std.replace(0, 1)
    normalized_data = data.sub(row_mean, axis=0).div(row_std, axis=0)
    return normalized_data

"""
TIME-SERIES OPERATIONS
"""
def tsmean(data, days):
    result = data.rolling(window = days, min_periods = 1).mean()
    return result


def tsrank(data, t):
    arr = data.to_numpy()
    T, N = arr.shape
    result = np.full((T, N), np.nan, dtype=np.float64)

    for i in range(T):
        start = max(0, i - t + 1)
        window = arr[start:i+1]  # shape: (window_len, N)
        # Rank each column in the window, take rank of the last row
        ranks = np.apply_along_axis(
            lambda x: pd.Series(x).rank(method="average").iloc[-1], 
            axis=0, arr=window
        )
        result[i] = ranks
    result = result / t
    return pd.DataFrame(result, index=data.index, columns=data.columns)

def tscorr(data1, data2, t):
    T, N = data1.shape
    result = np.full((T, N), np.nan)

    d1 = data1.to_numpy()
    d2 = data2.to_numpy()

    for i in range(T):
        start = max(0, i - t + 1)
        window1 = d1[start:i+1]
        window2 = d2[start:i+1]

        # Compute correlation per column
        for j in range(N):
            x = window1[:, j]
            y = window2[:, j]
            if np.std(x) > 0 and np.std(y) > 0:
                result[i, j] = np.corrcoef(x, y)[0, 1]
            else:
                result[i, j] = 0

    return pd.DataFrame(result, index=data1.index, columns=data1.columns)

def tsstd(data, t):
    return data.rolling(window=t, min_periods=t).std()