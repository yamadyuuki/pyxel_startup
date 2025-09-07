# UTF-8
import argparse
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

import pandas as pd
import yfinance as yf


JST = timezone(timedelta(hours=9))


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def normalize_ticker(t: str) -> str:
    """
    入力が数値のみなら東証想定で .T を付与。
    すでにサフィックスがあればそのまま。
    """
    ts = t.strip()
    if ts.isdigit():
        return f"{ts}.T"
    return ts


def load_tickers(args) -> List[str]:
    tickers: List[str] = []
    if args.tickers:
        tickers.extend(args.tickers)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                tickers.append(s)
    if not tickers:
        raise SystemExit("銘柄が指定されていません。--tickers または --file を使ってください。")
    # 正規化＋重複除去
    norm = [normalize_ticker(t) for t in tickers]
    return sorted(set(norm))


def daterange_3y_if_missing(start: Optional[str], end: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """
    start/end のどちらかが未指定なら「過去3年分」をデフォルトにする。
    yfinance は period='3y' でも良いが、ここではCSV出力名に期間を入れたいので
    明示期間に変換しておく。
    """
    if start and end:
        return start, end

    now_jst = datetime.now(JST).date()
    if not end:
        end = now_jst.isoformat()
    if not start:
        start_date = now_jst - timedelta(days=365 * 3 + 10)  # 少しバッファ
        start = start_date.isoformat()
    return start, end


def safe_history(
    ticker: str,
    start: Optional[str],
    end: Optional[str],
    interval: str = "1d",
    retries: int = 3,
    sleep_sec: float = 1.0,
) -> pd.DataFrame:
    """
    yfinance 取得の簡易リトライラッパー。
    """
    last_err: Optional[Exception] = None
    for i in range(retries):
        try:
            if start and end:
                df = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
            else:
                # 期間が空なら period 指定（ただし本スクリプトでは通常使わない）
                df = yf.download(ticker, period="3y", interval=interval, progress=False, auto_adjust=False)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
            # 空なら例外化してリトライ
            raise RuntimeError(f"empty dataframe for {ticker}")
        except Exception as e:
            last_err = e
            time.sleep(sleep_sec * (i + 1))
    assert last_err is not None
    raise last_err


def save_csv(df: pd.DataFrame, out_dir: str, ticker: str, start: Optional[str], end: Optional[str]) -> str:
    """
    CSV 保存。列は Date, Open, High, Low, Close, Adj Close, Volume
    """
    ensure_dir(out_dir)
    # Index(Date)を列に
    df = df.reset_index()
    # 列名の正規化（yfinanceは 'Date' 列を返すが念のため）
    if "Date" not in df.columns:
        # 古いバージョンなどで DatetimeIndex の可能性に対応
        if df.index.name:
            df.rename_axis("Date", axis="index", inplace=True)
            df = df.reset_index()
        else:
            df.insert(0, "Date", pd.Timestamp.utcnow().tz_localize("UTC").tz_convert("Asia/Tokyo"))

    # 出力ファイル名
    span = ""
    if start and end:
        span = f"_{start}_to_{end}"
    out_path = os.path.join(out_dir, f"{ticker.replace('.', '_')}{span}.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Fetch stock prices via yfinance and save as CSV.")
    parser.add_argument("--tickers", nargs="*", help="銘柄コード（例: 7203 6758.T 9984.T）スペース区切り複数可")
    parser.add_argument("--file", type=str, help="銘柄リストファイル（1行1銘柄。数値のみなら .T を自動付与）")
    parser.add_argument("--start", type=str, help="開始日 YYYY-MM-DD（未指定なら過去3年）")
    parser.add_argument("--end", type=str, help="終了日 YYYY-MM-DD（未指定なら今日）")
    parser.add_argument("--out", type=str, default="data/raw", help="出力ディレクトリ（既定: data/raw）")
    parser.add_argument("--interval", type=str, default="1d", choices=["1d", "1wk", "1mo"], help="取得間隔")
    parser.add_argument("--sleep", type=float, default=1.0, help="連続取得の待機秒（無料利用の礼儀）")
    args = parser.parse_args()

    tickers = load_tickers(args)
    start, end = daterange_3y_if_missing(args.start, args.end)

    print(f"[INFO] tickers={tickers}")
    print(f"[INFO] period={start} -> {end}, interval={args.interval}")
    print(f"[INFO] out_dir={args.out}")

    for i, t in enumerate(tickers, 1):
        try:
            print(f"[{i}/{len(tickers)}] fetching {t} ...")
            df = safe_history(t, start, end, interval=args.interval)
            path = save_csv(df, args.out, t, start, end)
            print(f"  -> saved: {path}  rows={len(df)}")
        except Exception as e:
            print(f"[WARN] failed: {t} reason={e}")
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
