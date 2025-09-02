# Pyxel Othello（オセロ）

シンプルなオセロ（リバーシ）ゲーム。`Pyxel` を使った2D描画で、マウス操作の人間プレイヤー対CPUの対戦ができます。難易度（思考エンジン）は3段階を用意しています。
https://kitao.github.io/pyxel/wasm/launcher/?run=yamadyuuki.pyxel_startup.Othello_v4.main

## 特長
- **Pyxel製UI**: 盤面表示・石描画・着手候補ハイライトを実装。
- **3段階のCPU**:
  - HARD: 盤面評価に基づく貪欲法。
  - VERY HARD: アルファベータ探索（深さ固定）。
  - LUNATIC: MCTS（モンテカルロ木探索、時間ベース）。
- **操作ガイド**: マウスで着手、ヒント表示、取り消し、タイトルに戻るをサポート。

## 必要環境
- **Python**: 3.8以降を推奨
- **依存ライブラリ**: `pyxel`

インストール例:
```bash
pip install pyxel
```

## 実行方法
```bash
python main.py
```
起動するとタイトル画面が表示されます。上下キーで難易度を選び、`SPACE` または `Z` で開始します。

## 操作方法
- **難易度選択**: タイトルで `↑/↓` で選択、`SPACE/Z` で開始
- **着手（人間）**: 盤上をマウス左クリック（合法手は円でハイライト）
- **取り消し**: 対局中に `Z`（CPU思考中は無効）。自分・相手の直前手をまとめて1手ずつ戻します。
- **タイトルへ**: `R` でタイトルに戻る

画面下部にスコア（BLACK/WHITE）と、手番やCPU思考中のステータスを表示します。

## 難易度とAI
- **HARD（`CPUPlayer`）**
  - 評価関数による貪欲選択。`players.py` の `EVALUATION_BOARD` を使用。
- **VERY HARD（`SearchCPUPlayer`）**
  - アルファベータ探索。`SEARCH_DEPTH` で深さを制御（既定: 4）。
- **LUNATIC（`MCTSCPUPlayer`）**
  - モンテカルロ木探索（UCT）。`THINK_TIME_MS`（既定: 300ms）で思考時間を制御。

いずれのCPUも合法手が1手のみのときは即座にその手を選びます。

## プロジェクト構成
- `main.py`: Pyxelアプリ本体（画面遷移、入力、描画、ゲーム進行）。
- `game_logic.py`: ルールと盤面・手番管理、合法手・着手・取り消し、スコア計算。
- `players.py`: プレイヤー実装（人間、評価関数CPU、アルファベータCPU、MCTS CPU）。

## カスタマイズ
- **探索深さ**: `players.py` の `SearchCPUPlayer.SEARCH_DEPTH`
- **MCTS思考時間**: `players.py` の `MCTSCPUPlayer.THINK_TIME_MS`（ミリ秒）
- **評価関数**: `players.py` の `EVALUATION_BOARD`（位置重み）
- **盤面サイズ/描画**: `main.py` の `CELL`, `BOARD_LEFT/BOARD_TOP`、`game_logic.py` の `N`

## 既知の注意点
- CPU思考中は取り消し（`Z`）は無効です（思考完了後に可能）。
- フォントや描画はPyxel標準に依存します。環境によって見え方が異なる場合があります。

## ライセンス
このリポジトリにライセンス表記がない場合、私的利用や学習目的の範囲でお使いください。再配布や商用利用が必要な場合は、プロジェクトオーナーに確認してください。

