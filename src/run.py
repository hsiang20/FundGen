import numpy as np
import sys
from parse import parse
from AST import *
from helpers import load_from_cache
from config import *

def main():
    if len(sys.argv) < 2:
        print("Usage: run.py [file]")
        exit(1)

    ast = parse(sys.argv[1])
    # print("AST:")
    # print(ast)
    # print()
    
    bindings = {}
    declarations = {}
    interpret_block(ast, bindings, declarations)

    block = None
    with open(f"{strategy_path}/strategy.txt", "r") as f:
        block = f.read().split("\n")[:-1]
    for i in range(len(block)):
        try:
            block[i] = eval(block[i])                
        except:
            pass
    # print("==========Portfolio Today==========")
    # print(block)
    cached_data, cached_dates = load_from_cache(f"{cache_path}/portfolio.npz")
    portfolio = pd.DataFrame(cached_data, index=cached_dates).iloc[-1]
    portfolio = portfolio.replace(np.nan, 0)
    portfolio.index = tickers
    portfolio = portfolio / sum(abs(portfolio)) * fund_size
    # print(round(portfolio, 2))
    portfolio = round(portfolio, 2)
    portfolio.to_csv(f"{portfolio_path}/portfolio.csv")
            


if __name__ == "__main__":
    main()
