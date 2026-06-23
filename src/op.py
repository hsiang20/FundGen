import pandas as pd
import numpy as np
import time

"""
DATA PROCESSING
"""
def nanto0(data):
    data = data.copy()
    data[np.isnan(data)] = 0.0
    return data

def cap_floor(data, cap, floor):
    data = data.copy()
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
    # With a single asset there is no cross-sectional ranking; return neutral 0.0.
    if N <= 1:
        return ranks * 0.0
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
    # T, N = data.shape
    # result = np.full((T, N), np.nan)
    # arr = data.to_numpy()
    # for i in range(T):  # loop over time
    #     start = max(0, i - days + 1)
    #     window = arr[start:i+1, :]  # slice window for all assets at once
    #     result[i, :] = np.nanmean(window, axis=0)  # mean across time, skip NaNs
    # result = pd.DataFrame(result, index=data.index, columns=data.columns)
    # return result


def tsrank(data, t):
    ranks = data.rolling(window=t, min_periods=1).apply(
        lambda x: pd.Series(x).rank(method="average").iloc[-1], raw=False
    )
    # Normalize by the actual window length so warm-up rows (window shorter
    # than t) are scaled consistently into (0, 1]: window_len = min(i + 1, t).
    T = data.shape[0]
    window_lens = pd.Series(
        np.minimum(np.arange(1, T + 1), t), index=data.index, dtype=np.float64
    )
    return ranks.div(window_lens, axis=0)

def tscorr(data1, data2, t):
    # min_periods=1 reproduces the original loop's warm-up behavior (values for
    # partial windows). Windows with zero variance (or a NaN) yield NaN, which
    # the original substituted with 0.
    result = data1.rolling(window=t, min_periods=1).corr(data2)
    result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return result.reindex(index=data1.index, columns=data1.columns)

def tsstd(data, t):
    return data.rolling(window=t, min_periods=t).std()