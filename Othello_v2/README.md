# Pyxelオセロ

これは、レトロゲームエンジン[Pyxel](https://github.com/kitao/pyxel)を使用して作成されたオセロ（リバーシ）ゲームです。

## 特徴

- シンプルで直感的なユーザーインターフェース。
- 複数の難易度を持つCPUとの対戦が可能です。
  - **HARD**: 盤面評価関数を使用した基本的なAIです。
  - **VERY HARD**: ミニマックス探索アルゴリズムを使用した、より高度なAIです。
  - **LUNATIC**: (将来のAIのためのプレースホルダーです。現在はHARDと同じロジックです。)

## ファイル構成

- `main.py`: メインアプリケーションファイルです。ゲームループ、ユーザー入力、画面描画を処理します。
- `game_logic.py`: 盤面の状態、石を置くルール、ゲームの進行など、ゲームのコアロジックが含まれています。
- `players.py`: `HumanPlayer`（人間プレイヤー）や、さまざまなAI戦略を持つ`CPUPlayer`など、さまざまなプレイヤータイプを定義します。

## 実行方法

1.  **依存関係のインストール:**

    Pythonがインストールされていることを確認してください。`pyxel`ライブラリをインストールする必要があります。

    ```bash
    pip install pyxel
    ```

2.  **ゲームの実行:**

    `main.py`ファイルを実行してゲームを開始します。

    ```bash
    python main.py
    ```

## 操作方法

- スタート画面で**上下の矢印キー**を使用して難易度を選択します。
- **ENTER**キーまたは**Z**キーを押してゲームを開始します。
- ゲーム中は、**マウス**を使用して石を置きます。
- **R**キーを押すと、いつでもタイトル画面に戻ることができます。
- **Z**キーを押すと、最後の手（プレイヤーとCPUの両方）を元に戻します。

---

# Pyxel Othello

This is an Othello (Reversi) game created using the Pyxel retro game engine.

## Features

- Simple and intuitive user interface.
- Play against a CPU with multiple difficulty levels:
  - **HARD**: A basic AI using a board evaluation function.
  - **VERY HARD**: A more advanced AI using a minimax search algorithm.
  - **LUNATIC**: (Placeholder for a future AI, currently uses the same logic as HARD).

## Files

- `main.py`: The main application file. It handles the game loop, user input, and screen rendering.
- `game_logic.py`: Contains the core game logic, including the board state, rules for placing discs, and game progression.
- `players.py`: Defines the different player types, including the `HumanPlayer` and various `CPUPlayer` implementations with different AI strategies.

## How to Run

1.  **Install dependencies:**

    Make sure you have Python installed. You will need to install the `pyxel` library.

    ```bash
    pip install pyxel
    ```

2.  **Run the game:**

    Execute the `main.py` file to start the game.

    ```bash
    python main.py
    ```

## How to Play

- Use the **UP/DOWN arrow keys** to select a difficulty on the start screen.
- Press **ENTER** or **Z** to start the game.
- During the game, use the **mouse** to place your disc.
- Press **R** to return to the title screen at any time.
- Press **Z** to undo the last move (for both player and CPU).