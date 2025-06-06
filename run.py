import numpy as np
import sys
from parse import parse
from utils import ScopedDict
from AST import *
from helpers import load_from_cache

fund_size = 1000000

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "BRK-B", "META", "TSLA", "UNH", "JNJ",
    "V", "XOM", "JPM", "PG", "MA", "HD", "LLY", "CVX", "MRK", "PEP",
    "ABBV", "KO", "AVGO", "COST", "WMT", "DIS", "BAC", "ADBE", "MCD", "CRM",
    "ACN", "PFE", "ABT", "TMO", "CSCO", "INTC", "VZ", "TXN", "DHR", "NFLX",
    "LIN", "NKE", "ORCL", "MDT", "AMGN", "NEE", "QCOM", "PM", "IBM", "UPS"
]

def main():
    if len(sys.argv) < 2:
        print("Usage: run.py [file]")
        exit(1)

    ast = parse(sys.argv[1])
    # print("AST:")
    # print(ast)
    # print()
    
    bindings = ScopedDict()
    declarations = ScopedDict()
    interpret_block(ast, bindings, declarations)

    if len(sys.argv) > 2:
        if sys.argv[2] == "sim":
            block = None
            with open("portfolio/portfolio.txt", "r") as f:
                block = f.read().split("\n")[:-1]
            for i in range(len(block)):
                try:
                    block[i] = eval(block[i])                
                except:
                    pass
            print("==========Portfolio Today==========")
            print(block)
            cached_data, cached_dates = load_from_cache("cache/portfolio.npz")
            portfolio = pd.DataFrame(cached_data, index=cached_dates).iloc[-1]
            portfolio.index = tickers
            portfolio = portfolio / sum(abs(portfolio)) * fund_size
            print(round(portfolio, 2))
            


if __name__ == "__main__":
    main()
