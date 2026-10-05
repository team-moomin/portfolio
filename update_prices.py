import json, urllib.request
from datetime import datetime, timezone, timedelta
import yfinance as yf

H = json.load(open("holdings.json", encoding="utf-8"))
try:
    old = json.load(open("prices.json", encoding="utf-8"))
except Exception:
    old = {}
prices = dict(old.get("prices", {}))
fx = old.get("usdkrw")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def last_close(sym):
    h = yf.Ticker(sym).history(period="5d")
    return float(h["Close"].dropna().iloc[-1])

up = [h["symbol"] for h in H if h["src"] == "upbit"]
if up:
    try:
        for t in get("https://api.upbit.com/v1/ticker?markets=" + ",".join(up)):
            prices[t["market"]] = t["trade_price"]
    except Exception as e:
        print("upbit 실패:", e)

for h in H:
    if h["src"] == "yahoo":
        try:
            prices[h["symbol"]] = last_close(h["symbol"])
        except Exception as e:
            print("실패:", h["symbol"], e)

try:
    fx = last_close("KRW=X")
except Exception as e:
    print("환율 실패:", e)

kst = timezone(timedelta(hours=9))
json.dump({"updated": datetime.now(kst).strftime("%Y-%m-%d %H:%M KST"), "usdkrw": fx, "prices": prices},
          open("prices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", prices, fx)
