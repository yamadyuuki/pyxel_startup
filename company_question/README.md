# Stock Price Quiz (Beta)

Pyxel で動作する株価クイズゲームです。ローソクではないシンプルな折れ線チャートが徐々に伸びていき、任意のタイミングで止めて銘柄名を4択で当てます。`main.py` と `tools/` のスクリプトで、独自のクイズパック（問題データ）も作成できます。

## 特長 / 画面操作

- タイトル: 矢印キーで問題を選択、`Enter` または `Space` で開始
- プレイ中: チャートが自動再生。`Space` で停止し選択肢表示へ
- 選択肢: `↑/↓` または 数字キー `1..4` で選択、`Enter` で決定
- 結果画面: `Space` で解説、`Enter` でタイトルへ
- 解説表示: `Esc` で閉じる
- いつでも: `R` でタイトルへリセット

画面サイズは `256x192` 固定（レトロ解像度）です。

## 必要環境

- Python 3.10+ 目安
- パッケージ
  - `pyxel`（ゲーム本体）
  - `pandas`, `yfinance`（データ取得・CSV保存。tools で使用）

インストール例:

```bash
pip install pyxel pandas yfinance
# もしくは uv を使う場合
uv pip install pyxel pandas yfinance
```

## 実行方法（ゲーム）

```bash
python main.py
```

既定では `packs/pack_sample.py` の `QUESTIONS` が読み込まれます。自分で作成したパックを使う場合は、後述の手順で生成し、`main.py` のインポート先を差し替えてください。

```python
from packs import pack_sample  # 例: 生成した pack_generated を使うなら pack_generated に変更
```

## 自作クイズパックの作り方（tools 利用）

`tools/` ディレクトリに、データ取得とパック生成のユーティリティがあります。

### 1) 株価CSVの取得（`tools/fetch_stock.py`）

`yfinance` を使って、指定銘柄の株価CSVを `data/raw/` に保存します。ファイル形式は `Date, Open, High, Low, Close, Adj Close, Volume` の一般的な形式です。

- 数値のみの銘柄は東証想定で自動的に `.T` が付与されます（例: `7203` → `7203.T`）。
- 期間未指定の場合は「過去3年程度」が自動設定されます。

使用例:

```bash
# 複数銘柄を直接指定
python tools/fetch_stock.py --tickers 7203 6758.T 5032.T --out data/raw

# 銘柄リストファイルを使う（1行1銘柄、# でコメント可）
python tools/fetch_stock.py --file tickers.txt --start 2023-01-01 --end 2024-12-31 --out data/raw
```

出力例: `data/raw/7203_T_2023-01-01_to_2024-12-31.csv`

### 2) パックの生成（`tools/build_pack.py`）

取得済みCSVから、ゲームが読み込める Python モジュール（`packs/pack_generated.py`）を生成します。価格系列は先頭の終値を基準に `scale`（既定 10000）で正規化され、`QUESTIONS` リストに変換されます。

使用例:

```bash
# ディレクトリ内のCSVをまとめて使う
python tools/build_pack.py --csv-dir data/raw

# 明示リストで指定
python tools/build_pack.py --csv-files data/raw/5032_T_*.csv data/raw/7203_T_*.csv

# ダウンサンプリング間隔（step）、正規化基準（scale）、出力先、社名マップを指定
python tools/build_pack.py \
  --csv-dir data/raw \
  --step 3 \
  --scale 10000 \
  --out packs/pack_generated.py \
  --name-map tools/name_map.csv
```

補足:

- 社名マップはヘッダー付きCSV（`ticker,name`）です。例:

  ```csv
  ticker,name
  5032.T,ANYCOLOR Inc.
  7203.T,Toyota Motor
  6758.T,Sony Group
  ```

- リポジトリにはサンプルが `tools/name_map.py` として含まれていますが、中身は CSV 形式です。拡張子が `.csv` の方が分かりやすいので、`--name-map tools/name_map.py` のまま使うか、ファイル名を `name_map.csv` に変更して指定してください。
- 生成後は `main.py` のインポートを `pack_generated` に変えると新パックで遊べます。

## ディレクトリ構成（抜粋）

```
core/
  models.py           # Question データモデル
data/
  raw/                # fetch_stock.py の出力CSV置き場
packs/
  __init__.py
  pack_sample.py      # サンプル問題（既定で読み込み）
  pack_generated.py   # build_pack.py が生成（任意）
tools/
  fetch_stock.py      # yfinance で株価CSVを取得
  build_pack.py       # CSV から QUESTIONS を生成
  name_map.py         # 社名マップのサンプル（CSV形式の中身）
main.py               # Pyxel ゲーム本体
```

## 開発メモ

- 描画や入力はすべて `main.py` 内（`App` クラス）で処理しています。
- チャートの横軸ラベルは期間（`span=(start, end)`）から内挿して月表記を描画します。
- 正解インデックスは暫定で先頭固定（`correct_idx = 0`）になっています。パック生成側やゲーム側でランダム化するなど拡張可能です。

## トラブルシューティング

- 起動時に Pyxel のウィンドウが出ない/落ちる: `pyxel` のインストールと Python バージョン、GPU ドライバを確認してください。
- `yfinance` の取得が失敗する: 無料API側のレート制限に注意し、`--sleep` を増やしてください。期間や銘柄コードの指定も確認。
- 文字化け（Windows 端末）: 端末の表示コードページやフォントに依存することがあります。VS Code のターミナルや UTF-8 設定を試してください。


