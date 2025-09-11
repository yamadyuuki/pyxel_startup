# tools/build_all.py
# -*- coding: utf-8 -*-
"""
name_map の生成 → クイズパック生成 を 1コマンドで実行する統合スクリプト。
既存の tools/build_name_map.py と tools/build_pack.py を順番に呼び出します。

例:
  uv run python tools/build_all.py --csv-dir data/raw --pack-out packs/pack_sample.py
  # 既存の name_map を再利用したい場合
  uv run python tools/build_all.py --csv-dir data/raw --skip-name-map --name-map tools/name_map.csv
"""
import argparse
import os
import subprocess
import sys
from typing import List, Optional


def find_script(name: str) -> str:
    """tools/ 配下 or カレントから探す"""
    candidates = [os.path.join("tools", name), name]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise SystemExit(f"{name} が見つかりません。プロジェクトルートで実行していますか？")


def run(cmd: List[str]) -> None:
    print("+", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)


def main():
    p = argparse.ArgumentParser(description="Build name_map and pack in one shot.")
    # 入力元
    p.add_argument("--csv-dir", type=str, help="株価CSVのディレクトリ（例: data/raw）")
    p.add_argument("--csv-files", nargs="*", help="個別CSVパスを列挙する場合")
    p.add_argument("--tickers", nargs="*", help="name_map作成時に追加で問い合わせるティッカー")
    # 出力系
    p.add_argument("--name-map", default="tools/name_map.csv", help="name_map の出力/再利用パス")
    p.add_argument("--pack-out", default="packs/pack_sample.py", help="生成するパックの出力先")
    # ビルドオプション（従来と同じ既定）
    p.add_argument("--step", type=int, default=3, help="間引きステップ（例: 3）")
    p.add_argument("--scale", type=int, default=10000, help="初日=scale で正規化")
    p.add_argument("--sleep", type=float, default=0.5, help="yfinance問い合わせの待機秒")
    # 制御
    p.add_argument("--skip-name-map", action="store_true", help="name_map の生成をスキップして既存CSVを使う")
    p.add_argument("--python", default=sys.executable, help="子プロセスで使うPython（既定: 現在のPython）")

    args = p.parse_args()

    # スクリプトを探す（tools/ またはカレント）
    path_build_name = find_script("build_name_map.py")
    path_build_pack = find_script("build_pack.py")

    # --- 1) name_map 生成（スキップ可） ---
    if not args.skip_name_map:
        nm_cmd = [args.python, path_build_name]
        if args.tickers:
            nm_cmd += ["--tickers"] + args.tickers
        if args.csv_dir:
            nm_cmd += ["--from-csv-dir", args.csv_dir]
        # 入力が csv_files の場合でも、name_map は csv_dir から拾う設計にしています。
        # 必要ならここで csv_files からティッカー抽出する実装を足せます。
        nm_cmd += ["--out", args.name_map, "--sleep", str(args.sleep)]
        run(nm_cmd)
    else:
        if not os.path.exists(args.name_map):
            raise SystemExit(f"--skip-name-map 指定ですが {args.name_map} が存在しません。")

    # --- 2) パック生成 ---
    pack_cmd = [args.python, path_build_pack]
    if args.csv_dir:
        pack_cmd += ["--csv-dir", args.csv_dir]
    if args.csv_files:
        pack_cmd += ["--csv-files"] + args.csv_files
    pack_cmd += ["--step", str(args.step), "--scale", str(args.scale)]
    # name_map のパスは、スキップ時も存在すれば渡す（既存の動作と同じになるように）
    if os.path.exists(args.name_map):
        pack_cmd += ["--name-map", args.name_map]
    pack_cmd += ["--out", args.pack_out]
    run(pack_cmd)

    print(f"[OK] 完了: {args.pack_out}")


if __name__ == "__main__":
    main()
