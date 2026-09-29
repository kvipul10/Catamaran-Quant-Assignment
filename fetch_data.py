# Script to download the data used in strategy_backtest.ipynb
# Needs internet access and the yfinance package.
#
# The csv files in data/ were downloaded through the browser, this script
# gets the same data automatically:
#   nifty50.csv               - Yahoo Finance ^NSEI (daily open/high/low/close)
#   india_vix.csv             - Yahoo Finance ^INDIAVIX (daily)
#   india_short_rate_fred.csv - FRED series IRSTCI01INM156N, India call money rate
#                               (monthly, % per year). If this download fails the
#                               notebook uses a constant 6.5% instead.

import io
import os
import json
import datetime
import urllib.request

import pandas as pd
import yfinance as yf

START = "2009-01-01"
END = datetime.date.today().isoformat()

os.makedirs("data", exist_ok=True)

# keep a small log of what was downloaded
log = {"run_date": END, "sources": {}}


def download_yahoo(ticker, name):
    data = yf.download(ticker, start=START, end=END, auto_adjust=False, progress=False)

    # newer versions of yfinance give multi level columns, keep only the first level
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data[["Open", "High", "Low", "Close"]]
    data = data.dropna(subset=["Close"])
    data.index.name = "Date"
    data.to_csv("data/" + name + ".csv")

    first_date = str(data.index[0].date())
    last_date = str(data.index[-1].date())
    log["sources"][name] = {
        "provider": "Yahoo Finance",
        "ticker": ticker,
        "rows": int(len(data)),
        "first": first_date,
        "last": last_date,
    }
    print(name, len(data), first_date, "->", last_date)
    return data


download_yahoo("^NSEI", "nifty50")
download_yahoo("^INDIAVIX", "india_vix")


# short rate from FRED
try:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01INM156N"
    text = urllib.request.urlopen(url, timeout=30).read().decode()

    rf = pd.read_csv(io.StringIO(text))
    rf.columns = ["Date", "rate_pct"]
    rf["Date"] = pd.to_datetime(rf["Date"])
    rf = rf.set_index("Date")["rate_pct"]
    rf = pd.to_numeric(rf, errors="coerce").dropna()  # FRED uses "." for missing values
    rf = rf[rf.index >= START]
    rf.to_frame().to_csv("data/india_short_rate_fred.csv")

    log["sources"]["india_short_rate_fred"] = {
        "provider": "FRED (OECD MEI)",
        "series": "IRSTCI01INM156N",
        "rows": int(len(rf)),
        "first": str(rf.index[0].date()),
        "last": str(rf.index[-1].date()),
        "units": "% p.a., monthly",
    }
    print("short rate", len(rf), rf.index[0].date(), "->", rf.index[-1].date(), "last =", rf.iloc[-1])

except Exception as e:
    print("FRED download failed:", e)
    print("notebook will use the fallback constant rate of 6.5%")
    log["sources"]["india_short_rate_fred"] = {"provider": "FALLBACK constant", "rate_pct": 6.5}


with open("data/DATA_SOURCES.json", "w") as f:
    json.dump(log, f, indent=2)
