# Stock Price Quiz (Beta)

Pyxel で動作する株価クイズゲームです。ローソクではないシンプルな折れ線チャートが徐々に伸びていき、任意のタイミングで止めて銘柄名を4択で当てます。`main.py` と `tools/` のスクリプトで、独自のクイズパック（問題データ）も作成できます。

## クイック実行

### ゲームの起動
```bash
python main.py
```

### サンプルクイズパックの生成
```bash
# 株価データの取得
uv run python tools/fetch_stock.py --tickers 7832 3659 9766 9697 9602 9684 4816 7974 3635

# 企業名マップの作成
uv run python tools/build_name_map.py --from-csv-dir data/raw --out tools/name_map.csv

# クイズパックの生成
uv run python tools/build_pack.py --csv-dir data/raw --out packs/pack_sample.py

# 一括実行（推奨）
uv run python tools/build_all.py --csv-dir data/raw --pack-out packs/pack_sample.py
```


## ゲームの概要

### 特長
- 株価チャートを見て銘柄名を当てる教育ゲーム
- 11問の日本企業株価データ（M3、Kao、武田薬品、オリエンタルランドなど）
- 日経225指数との比較チャート機能
- 期間とスケールを正規化した株価データ（過去3年程度）

### 画面操作
- **タイトル画面**: 矢印キー（↑↓）または数字キー（1-9）で問題選択、`Enter`/`Space`で開始
- **プレイ中**: チャート自動描画、`Space`で停止して選択画面へ
- **選択画面**: 矢印キー（↑↓）または数字キー（1-4）で選択、`Space`で決定
- **結果画面**: `Space`で解説表示、`Enter`でタイトルに戻る
- **解説画面**: `Space`でタイトルに戻る
- **共通**: `R`キーでいつでもタイトル画面にリセット

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

## ゲームデータの仕組み

### 使用されているデータ
現在のゲームには以下の株式データが含まれています：
- **M3（2413.T）**: 医療情報プラットフォーム
- **Kao Corporation（4452.T）**: 消費財メーカー  
- **Takeda Pharmaceutical（4502.T）**: 製薬会社
- **Oriental Land Co.（4661.T）**: 東京ディズニーランド運営
- **Panasonic Holdings（6752.T）**: 電機メーカー
- **Sony Group Corporation（6758.T）**: エンターテインメント・電子機器
- **Toyota Motor Corporation（7203.T）**: 自動車メーカー
- **Mitsubishi UFJ Financial Group（8306.T）**: 金融グループ
- **NTT（9432.T）**: 通信会社
- **Fast Retailing Co.（9983.T）**: ユニクロ運営
- **日経225指数**: 比較基準として表示

### クイズパックの切り替え
デフォルトでは `packs/pack_sample.py` が読み込まれます。独自パックを使用する場合は、`main.py` の4行目を変更：

```python
from packs import pack_sample  # pack_generated など、他のパックに変更可能
```

## 自作クイズパックの作り方

`tools/` ディレクトリには4つのユーティリティスクリプトが用意されています：

### tools/ ディレクトリの構成
```
tools/
├── fetch_stock.py      # 株価データの取得
├── build_name_map.py   # 企業名マップの作成
├── build_pack.py       # クイズパックの生成
├── build_all.py        # 一括処理スクリプト（推奨）
└── name_map.csv        # 企業名マップファイル
```

### 1) 一括処理（推奨方法）

`tools/build_all.py` を使用すると、データ取得からパック生成まで一度に実行できます：

```bash
# 基本的な使用法
uv run python tools/build_all.py --csv-dir data/raw --pack-out packs/pack_sample.py

# 追加の銘柄も含めて処理
uv run python tools/build_all.py \
  --csv-dir data/raw \
  --tickers 1234 5678 \
  --pack-out packs/my_pack.py \
  --step 2 \
  --scale 10000
```

### 2) 個別実行

#### A) 株価データの取得（`fetch_stock.py`）
yfinanceを使用して指定銘柄の株価CSVを取得します：

```bash
# 複数銘柄を直接指定（数値のみは自動的に.Tが付与）
python tools/fetch_stock.py --tickers 7203 6758 --out data/raw

# ファイルから銘柄リストを読み込み
python tools/fetch_stock.py --file tickers.txt --start 2023-01-01 --end 2024-12-31
```

#### B) 企業名マップの作成（`build_name_map.py`）
yfinanceから企業名を取得してCSVマップを作成します：

```bash
# CSVディレクトリから自動的に銘柄を検出
python tools/build_name_map.py --from-csv-dir data/raw --out tools/name_map.csv

# 特定の銘柄を指定
python tools/build_name_map.py --tickers 7203 6758 --out tools/name_map.csv
```

#### C) クイズパックの生成（`build_pack.py`）
取得したCSVデータからゲーム用のPythonモジュールを生成します：

```bash
# 基本的な生成
python tools/build_pack.py --csv-dir data/raw --out packs/pack_generated.py

# カスタマイズした生成
python tools/build_pack.py \
  --csv-dir data/raw \
  --step 3 \
  --scale 10000 \
  --name-map tools/name_map.csv \
  --out packs/pack_generated.py
```

### 3) データ仕様

**企業名マップ（name_map.csv）**:
```csv
ticker,name
2413.T,M3, Inc.
4452.T,Kao Corporation
7203.T,Toyota Motor Corporation
```

**価格データの正規化**:
- 各銘柄の最初の終値を基準値（デフォルト10000）として正規化
- `step`パラメータでダウンサンプリング（例：3なら3日おき）
- 期間は各銘柄のデータ開始・終了日で自動設定

## プロジェクト構成

```
company-question-test/
├── main.py                 # Pyxelゲーム本体（App クラス）
├── core/
│   └── models.py          # Question データクラス定義
├── packs/                 # クイズパック（問題データ）
│   ├── __init__.py
│   ├── pack_sample.py     # デフォルトのサンプル問題（11問）
│   └── pack_generated.py  # tools で生成される問題（任意）
├── tools/                 # データ処理ユーティリティ
│   ├── fetch_stock.py     # yfinance経由で株価CSV取得
│   ├── build_name_map.py  # 企業名マップ作成
│   ├── build_pack.py      # CSVからクイズパック生成
│   ├── build_all.py       # 一括処理スクリプト
│   └── name_map.csv       # 企業名対応表
├── data/
│   └── raw/               # 取得した株価CSVファイル格納場所
└── README.md              # このファイル
```

## 技術仕様

### ゲーム実装（main.py）
- **ゲームエンジン**: Pyxel（レトロスタイルゲームライブラリ）
- **メインクラス**: `App`クラスですべての描画と入力を処理
- **状態管理**: タイトル→プレイ中→選択→結果→解説の5状態で管理
- **チャート機能**: 
  - 線形リサンプリングによる期間正規化
  - 日経225指数との重ね合わせ表示
  - 月単位の横軸ラベル表示

### データ処理の特徴
- **正規化方式**: 各銘柄の初日終値を10000として正規化
- **期間統一**: 異なる期間のデータを比率ベースで統一表示
- **選択肢生成**: 他の企業名からランダムサンプリングして4択を構築
- **リアルデータ**: yfinanceから取得した実際の株価データを使用

## トラブルシューティング

- 起動時に Pyxel のウィンドウが出ない/落ちる: `pyxel` のインストールと Python バージョン、GPU ドライバを確認してください。
- `yfinance` の取得が失敗する: 無料API側のレート制限に注意し、`--sleep` を増やしてください。期間や銘柄コードの指定も確認。
- 文字化け（Windows 端末）: 端末の表示コードページやフォントに依存することがあります。VS Code のターミナルや UTF-8 設定を試してください。


