import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import factorial
from itertools import permutations
import copy
from config import *

price_index = yf.download("AAPL", auto_adjust=True, start=start_date, end=end_date, progress=False).index
price_data = ["High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
financials_data = yf.Ticker("AAPL").financials.index

def args_check(args, needed_args):
    for needed_arg in needed_args:
        if needed_arg not in args:
            raise ValueError(f"{needed_arg} is not specified")

def find_data_in(args, bindings, name="in"):
    if (args[name] == "_"):
        data_in = bindings["_tmp"]
    else:
        data_in = bindings[args[name]]
    return data_in

"""
Historical price/volume data
High, Low, Close, Volume, Dividends, Stock Splits
"""
def load(data_name):
    cache_name = f"{cache_path}/{data_name}.npz"
    cached_data, cached_dates = load_from_cache(cache_name)
    if is_cache_valid(cached_dates, price_index):
        # print(data_name, "cache valid!")
        return_data = pd.DataFrame(cached_data, index=cached_dates)
        # print(return_data)
        return return_data
    if data_name in price_data:
        data = yf.download(tickers, start=start_date, end=end_date, actions=True, progress=False)
        return_data = data[data_name]
    elif data_name in financials_data:
        return_data = pd.DataFrame(index=price_index)
        for ticker in tickers:
            try:
                data = yf.Ticker(ticker).financials.loc[data_name]
                daily_series = pd.Series(index=price_index, dtype=float)
                for fin_date, value in data.items():
                    mask = daily_series.index <= fin_date
                    if mask.any():
                        daily_series.loc[mask] = value
                daily_series = daily_series.ffill()
            except:
                daily_series = np.nan
            return_data[ticker] = daily_series
    else:
        raise ValueError(f"Unknown data field: {data_name}")
    save_to_cache(return_data, price_index, cache_name)
    return return_data

def save_to_cache(data, dates, filename):
    np.savez(filename, data = data, dates = np.array(dates, dtype="str"))

def load_from_cache(filename):
    try:
        data = np.load(filename, allow_pickle=True)
        dates = pd.to_datetime(data["dates"])
        return data["data"], dates
    except (FileNotFoundError, KeyError):
        return None, None

def is_cache_valid(old_dates, new_dates):
    # print("old_dates:", old_dates)
    # print("new_dates:", new_dates)
    return (old_dates is not None) and (len(old_dates) == len(new_dates)) and (all(old_dates == new_dates))

def get_returns(new_dates):
    cached_returns, cached_dates = load_from_cache(f"{cache_path}/returns.npz")
    if is_cache_valid(cached_dates, new_dates):
        # print("returns cache valid!")
        # print(cached_returns["data"])
        return cached_returns
    else:
        # print("cache invalid, reload returns data")
        close_data = load("Close")
        returns = close_data.pct_change()
        save_to_cache(returns, new_dates, f"{cache_path}/returns.npz")
        return returns
    
def get_daily_profit(portfolio):
    returns = get_returns(portfolio.index)
    # daily_profit[t]=portfolio[t−1]⋅returns[t]
    portfolio_shift = portfolio.shift(1).fillna(0)
    # print("shifted portfolio: ")
    # print(portfolio_shift)
    daily_profit = np.sum(portfolio_shift.to_numpy() * returns, axis = 1)
    daily_profit[np.isnan(daily_profit)] = 0.0
    return daily_profit

def get_cumulative_profit(portfolio):
    portfolio_shift = portfolio.shift(1)
    daily_profit = get_daily_profit(portfolio)
    cumulative_profit = np.cumsum(daily_profit)
    time_index = portfolio_shift.index
    return cumulative_profit, time_index

def draw_profit(data):
    cumulative_profit, dates = get_cumulative_profit(data)
    cumulative_profit = cumulative_profit * fund_size
    plt.figure(figsize=(12, 5))
    plt.plot(dates, cumulative_profit)
    plt.xlabel("Date")
    plt.ylabel("Profit ($)")
    plt.title("Portfolio Cumulative Profit Over Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return cumulative_profit

def save_profit(data):
    cumulative_profit, dates = get_cumulative_profit(data)
    cumulative_profit = cumulative_profit * fund_size
    plt.figure(figsize=(12, 5))
    plt.plot(dates, cumulative_profit)
    plt.xlabel("Date")
    plt.ylabel("Profit ($)")
    plt.title("Portfolio Cumulative Profit Over Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{image_path}/profit.png")
    return cumulative_profit

def show_stat(portfolio):
    daily_return = get_daily_profit(portfolio)
    # print("daily return")
    # print(daily_return)
    sharpe_ratio = get_Sharpe(daily_return)
    print("Sharpe Ratio:", round(sharpe_ratio, 3))
    annual_return_rate = get_annual_returns(daily_return)
    print("Annual Return Rate:", round(annual_return_rate, 3), "%")
    turnover_rate = get_turnover(portfolio)
    print("Turnover Rate:", round(turnover_rate, 3), "%")
    return sharpe_ratio, annual_return_rate, turnover_rate

def get_annual_returns(daily_return):
    cumulative_profit = np.cumsum(daily_return)
    cumulative_profit = cumulative_profit * fund_size
    total_return = cumulative_profit[-1] / fund_size
    # annual_return = np.sum(daily_return) * (252 / len(daily_return))
    total_return = np.nan_to_num(total_return, nan=1)
    annual_return = abs(total_return)/total_return * abs(total_return) ** (252/len(daily_return)) * 100
    return annual_return

def get_Sharpe(daily_return):
    mean_daily_return = np.mean(daily_return)
    std_daily_return = np.std(daily_return)

    sharpe_ratio = (mean_daily_return) / std_daily_return * np.sqrt(252)
    return sharpe_ratio

def get_turnover(portfolio):
    # print(portfolio)
    turnover = (portfolio.diff().abs()).sum(axis=1)
    # print(turnover)
    turnover_rate = (turnover / portfolio.replace(0, np.nan).abs().sum(axis=1)).mean() * 100
    return turnover_rate

def get_comb_num(total, select):
    # from n objects choose m objects, with any order
    return int(factorial(total) / factorial(total - select))

def get_comb(total, select):
    # from n objects choose m objects, return all orders
    numbers = list(range(total))
    orders = [list(perm) for perm in permutations(numbers, select)]
    return orders

def repeat_block_n(all_block, num_of_iteration, stmt):
    comb_num = get_comb_num(len(stmt.exprs), stmt.num)
    comb = get_comb(len(stmt.exprs), stmt.num)
    original_num_of_iteration = num_of_iteration
    original_all_block = all_block
    num_of_iteration *= comb_num
    for i in range(comb_num - 1):
        all_block = all_block + copy.deepcopy(original_all_block)
    for i in range(comb_num):
        for j in range(original_num_of_iteration):
            for order in comb[i]:
                all_block[i*original_num_of_iteration + j].append(stmt.exprs[order])
    return all_block, num_of_iteration

def repeat_block_all(all_block, num_of_iteration, stmt):
    comb_num = 0
    comb = []
    for i in range(1, len(stmt.exprs)+1):
        comb_num += get_comb_num(len(stmt.exprs), i)
        comb += copy.deepcopy(get_comb(len(stmt.exprs), i))
    original_num_of_iteration = num_of_iteration
    original_all_block = all_block
    num_of_iteration *= comb_num
    for i in range(comb_num - 1):
        all_block = all_block + copy.deepcopy(original_all_block)
    for i in range(comb_num):
        for j in range(original_num_of_iteration):
            for order in comb[i]:
                all_block[i*original_num_of_iteration + j].append(stmt.exprs[order])
    return all_block, num_of_iteration

def print_stat(stat):
    for key in stat:
        if "Rate" in key:
            print(f"{key}: {round(stat[key], 3)}%")
        else:
            print(f"{key}: {round(stat[key], 3)}")

def print_config(config):
    for s in config:
        if str(s)[0] == "[":
            continue
        print(str(s))

if __name__ == "__main__":
    print(get_comb_num(3, 1))
    print(get_comb(3, 2))
    print(round(load("Low"), 3))