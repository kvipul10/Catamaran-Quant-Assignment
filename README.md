# Catamaran-Quant-Assignment

Backtest of an overnight strategy on the Nifty 50: buy at the close, sell at the next open, only on nights that are one calendar day long (weekends and holidays are skipped).

## Files
- `strategy_backtest.ipynb` - the main notebook. Runs the backtest and saves all tables and charts into `results/`
- `fetch_data.py` - downloads the data again from Yahoo Finance and FRED (needs internet + yfinance)
- `data/` - Nifty 50 and India VIX daily prices, India call money rate (monthly)
- `results/` - output csv files and figures from the notebook

## How to run
```
pip install pandas numpy matplotlib jupyter
jupyter notebook strategy_backtest.ipynb
```
Then run all cells. The notebook only uses the csv files in `data/`, so no internet is needed.
