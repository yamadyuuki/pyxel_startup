#+ Mini Kabu Trader（株トレード・ミニゲーム）

シンプルな株式売買を題材にした Pyxel 製のミニゲームです。30 日間のあいだに資産を目標額まで増やすことを目指します。シーン管理と戦略パターン（Strategy）を用いて、ゲームの流れと株価変動ロジックを分離しています。

https://yamadyuuki.github.io/pyxel_startup/Stock_trading

## 特長
- タイトル/プレイ/結果の3シーン構成（`SceneManager` による遷移）
- 株価更新は戦略パターンで実装（`RandomWalkStrategy` / `TrendingStrategy`）
- 初期資金・目標資産・プレイ日数などは定数で調整可能
- 簡易な折れ線チャートで価格推移を表示

## デモの流れ（ゲームルール）
- 初期資金: 100,000 円
- 目標資産: 200,000 円
- プレイ期間: 30 日
- 毎日「買う（1 株）/ 売る（1 株）/ 次の日へ」を選択
- 総資産が目標に到達すれば勝利、30 日経過で未達ならゲームオーバー

現在のプレイ実装では、メニュー操作対象は `Pixel Inc.` の 1 銘柄です（市場には `Dot Foods` も生成されますが、UI操作は `Pixel Inc.` を対象としています）。

## 操作方法（キー）
- タイトル画面: `SPACE` で開始
- プレイ画面: `UP/DOWN` でメニュー選択、`SPACE` で決定
  - BUY（1株購入）
  - SELL（1株売却）
  - NEXT DAY（翌日に進む）
- 結果画面: `SPACE` でタイトルへ戻る

注: 結果画面の文言に「- PRESS ENTER -」の表示がありますが、実際の入力は `SPACE` キーです。

## 必要環境
- Python 3.8+（推奨）
- [Pyxel](https://github.com/kitao/pyxel)

## セットアップと実行
1. 依存ライブラリをインストール
   ```bash
   pip install pyxel
   ```
2. ゲームを起動
   ```bash
   python main.py
   ```

## ビルド（pyxapp/HTML 出力）
Pyxel の CLI を使って、配布用の `.pyxapp` とブラウザ実行用の `.html` を作成できます。

- 事前準備
  - Python 3.8+
  - `pip install pyxel`

- Windows（PowerShell）
  ```powershell
  ./scripts/package_pyxel.ps1
  ```

- macOS / Linux（bash）
  ```bash
  bash scripts/package_pyxel.sh
  ```

生成物は `dist/` 配下に出力されます。
- `dist/mini-kabu-trader.pyxapp`
- `dist/mini-kabu-trader.html`

補足: `pyxel` コマンドが見つからない場合は、`python -m pip install pyxel` を実行するか、PATH の通った Python 環境で再度お試しください。

## プロジェクト構成
- `main.py`: ウィンドウ初期化、シーン管理の起動、ゲームループ
- `scenes.py`: シーン管理（`SceneManager`）、`TitleScene`/`PlayScene`/`ResultScene`
- `models.py`: ドメインロジック（`Player`/`Stock`/`StockMarket`）と株価更新戦略
- `__pycache__/`: Python のビルドキャッシュ

## 主要コンセプト
- シーン管理（SceneManager）
  - `add_scene(name, scene)` で登録
  - `change_scene(name, **kwargs)` で遷移（`on_enter` にパラメータ受け渡し）
- 戦略パターン（Strategy）
  - `PriceUpdateStrategy` を抽象化し、`RandomWalkStrategy`/`TrendingStrategy` が実装
  - `StockMarket.next_day()` 実行時に各 `Stock` の `strategy.update()` で価格を更新

## カスタマイズ例
- パラメータ調整（`scenes.py` 冒頭）
  - `INITIAL_MONEY`, `TARGET_ASSETS`, `GAME_DAYS`, `SCREEN_WIDTH`, `SCREEN_HEIGHT`
- 銘柄の追加（`PlayScene.on_enter`）
  ```python
  self.market.add_stock(Stock(name="New Corp", initial_price=4000, strategy=RandomWalkStrategy()))
  ```
  UI を複数銘柄に対応させる場合は、選択対象をインデックス化し、`BUY/SELL` 時に対象銘柄名を切り替える処理を追加してください。
- 株価戦略の追加（`models.py`）
  ```python
  class MeanRevertStrategy(PriceUpdateStrategy):
      def __init__(self, mean=5000, strength=0.1):
          self.mean = mean
          self.strength = strength
      def update(self, current_price):
          diff = self.mean - current_price
          next_price = current_price + diff * self.strength
          return max(1, int(next_price))
  ```
  追加後は銘柄作成時に `strategy=MeanRevertStrategy(...)` を渡します。

## 既知の注意点
- コメントの一部に文字化けが見られます（日本語コメントのエンコード由来）。
- 結果画面の表示文言と実際の入力キーが不一致です（表示は ENTER、入力は SPACE）。
- プレイ中、UI操作対象は `Pixel Inc.` のみです。複数銘柄操作に拡張する場合は、UI と入力処理の拡張が必要です。

## ライセンス
未指定。必要に応じて追記してください。
