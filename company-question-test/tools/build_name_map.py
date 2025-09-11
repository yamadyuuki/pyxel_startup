# tools/build_name_map.py
# -*- coding: utf-8 -*-
"""
yfinance から ticker→company name の対応表を作る。
使い方の例:
  uv run python tools/build_name_map.py --tickers 7832 3659 9766 ...
  uv run python tools/build_name_map.py --from-csv-dir data/raw --out tools/name_map.csv
"""
import argparse
import glob
import os
import re
import time
from typing import Dict, List

import yfinance as yf


def normalize_ticker(t: str) -> str:
    t = t.strip()
    return f"{t}.T" if t.isdigit() else t

def tickers_from_csv_dir(csv_dir: str) -> List[str]:
    out = []
    for p in glob.glob(os.path.join(csv_dir, "*.csv")):
        # 例: 5032_T_2022-... → 5032.T を復元
        base = os.path.basename(p)
        m = re.match(r"^(\d+)_T_", base)
        if m:
            out.append(f"{m.group(1)}.T")
    return sorted(set(out))

def fetch_name(ticker: str) -> str:
    # できるだけ丁寧に（無料APIなので少し待機）
    t = yf.Ticker(ticker)
    try:
        info = t.get_info()       # 新しい yfinance では get_info 推奨
    except Exception:
        time.sleep(0.5)
        info = {}
    name = info.get("longName") or info.get("shortName") or ticker
    return name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*", help="銘柄（例: 7832 3659.T ...）")
    ap.add_argument("--from-csv-dir", type=str, help="data/raw など、CSVからティッカーを推定")
    ap.add_argument("--out", type=str, default="tools/name_map.csv")
    ap.add_argument("--sleep", type=float, default=0.5, help="API呼び出しの間隔秒")
    args = ap.parse_args()

    tickers: List[str] = []
    if args.tickers:
        tickers.extend(args.tickers)
    if args.from_csv_dir:
        tickers.extend(tickers_from_csv_dir(args.from_csv_dir))
    if not tickers:
        raise SystemExit("ティッカーがありません。--tickers か --from-csv-dir を指定してください。")

    tickers = sorted({normalize_ticker(t) for t in tickers})

    rows: Dict[str, str] = {}
    for i, t in enumerate(tickers, 1):
        name = fetch_name(t)
        rows[t] = name
        print(f"[{i}/{len(tickers)}] {t} -> {name}")
        time.sleep(args.sleep)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        f.write("ticker,name\n")
        for t in sorted(rows):
            f.write(f"{t},{rows[t]}\n")
    print(f"[OK] wrote: {args.out}")

if __name__ == "__main__":
    main()
