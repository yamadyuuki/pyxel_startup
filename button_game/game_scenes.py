# -*- coding: utf-8 -*-
import pyxel
import random
from typing import Callable

WIDTH, HEIGHT = 160, 120
FPS = 30

# 難易度ごとの1セット内の回数
ROUNDS_PER_SET = {
    "EASY": 10,
    "NORMAL": 15,
    "HARD": 20,
}

SET_COUNT = 5               # 総セット数
INTERVAL_FRAMES = 2 * FPS   # 矢印が出てから次に切り替わるまで（約2秒）
SET_GAP_FRAMES = 5 * FPS    # セット間の休憩（約5秒）

ARROWS = ("UP", "DOWN", "LEFT", "RIGHT")
KEY_MAP = {
    "UP": pyxel.KEY_UP,
    "DOWN": pyxel.KEY_DOWN,
    "LEFT": pyxel.KEY_LEFT,
    "RIGHT": pyxel.KEY_RIGHT,
}


# ---------- 共通UI ----------
def draw_center_text(y: int, text: str, col: int = 7):
    w = len(text) * 4
    x = (WIDTH - w) // 2
    pyxel.text(x, y, text, col)


def draw_arrow(cx: int, cy: int, size: int, direction: str, col: int = 10):
    s = size
    if direction == "UP":
        # 上向き三角
        pyxel.tri(cx, cy - s, cx - s, cy + s, cx + s, cy + s, col)
    elif direction == "DOWN":
        pyxel.tri(cx, cy + s, cx - s, cy - s, cx + s, cy - s, col)
    elif direction == "LEFT":
        pyxel.tri(cx - s, cy, cx + s, cy - s, cx + s, cy + s, col)
    elif direction == "RIGHT":
        pyxel.tri(cx + s, cy, cx - s, cy - s, cx - s, cy + s, col)


def frame_to_seconds(fr: int) -> float:
    return fr / FPS


# ---------- スタート画面 ----------
class StartScene:
    def __init__(self, on_start: Callable[[str], None]):
        self.on_start = on_start
        self.options = ["EASY", "NORMAL", "HARD"]
        self.index = 0

    def update(self):
        # 難易度選択：左右/上下で移動
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_UP):
            self.index = (self.index - 1) % len(self.options)
            pyxel.play(0,0)
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_DOWN):
            self.index = (self.index + 1) % len(self.options)
            pyxel.play(0,0)

        # SPACEで開始
        if pyxel.btnp(pyxel.KEY_SPACE):
            difficulty = self.options[self.index]
            self.on_start(difficulty)
            pyxel.play(0,1)

    def draw(self):
        draw_center_text(22, "ARROW RHYTHM", 11)
        draw_center_text(38, "SELECT DIFFICULTY", 7)

        # 難易度表示
        for i, name in enumerate(self.options):
            col = 10 if i == self.index else 6
            draw_center_text(56 + i * 10, name, col)

        draw_center_text(90, "SPACE: START", 7)
        draw_center_text(100, "ARROWS: CHOOSE", 6)


# ---------- プレイ画面 ----------
class PlayScene:
    """
    ゲーム仕様
    - 難易度に応じて 1セットあたりの矢印数(EASY:10 / NORMAL:15 / HARD:20)
    - 矢印は約2秒ごとに出る（時間内に正しいキーを押すと即次へ）
    - 5セット実施。セット間は約5秒の休憩
    """

    def __init__(self, difficulty: str, on_finish: Callable[[], None]):
        self.on_finish = on_finish
        self.difficulty = difficulty
        self.rounds_per_set = ROUNDS_PER_SET[difficulty]

        # 進行管理
        self.set_index = 0  # 0..4
        self.round_index = 0  # 0..rounds_per_set-1
        self.in_break = True   # セット間休憩中か
        self.break_start_frame = pyxel.frame_count # 休憩開始フレーム

        # 現在の矢印
        self.current_arrow = None           # type: str | None
        self.spawn_frame = 0                # この矢印が出たフレーム
        self.waiting_input = False          # 入力待ち中か

        # 成績
        self.score = 0
        self.miss = 0

        # 終了フラグ
        self.finished = False

    # 次の矢印を出す
    def _spawn_arrow(self):
        self.current_arrow = random.choice(ARROWS)
        self.spawn_frame = pyxel.frame_count
        self.waiting_input = True

    # 次のラウンドへ進む（正否に関係なく移行）
    def _advance_round(self):
        self.round_index += 1
        self.waiting_input = False 
        self.current_arrow = None

        if self.round_index >= self.rounds_per_set:
            # セット終了
            self.set_index += 1
            self.round_index = 0
            if self.set_index >= 5:
                self.finished = True
            else:
                # 休憩に入る
                self.in_break = True
                self.break_start_frame = pyxel.frame_count

    def _update_break(self):
        # 休憩経過
        if pyxel.frame_count - self.break_start_frame >= SET_GAP_FRAMES:
            self.in_break = False
            self._spawn_arrow()

    def _update_playing(self):
        # 現在のターゲットがなければ生成
        if not self.waiting_input and self.current_arrow is None:
            self._spawn_arrow()

        if self.waiting_input and self.current_arrow:
            # 時間切れチェック
            elapsed = pyxel.frame_count - self.spawn_frame
            if elapsed >= INTERVAL_FRAMES:
                self.miss += 1
                self._advance_round()
                return

            # 入力チェック
            pressed = None
            for name, key in KEY_MAP.items():
                if pyxel.btnp(key):
                    pressed = name
                    pyxel.play(0,0)
                    break

            if pressed is not None:
                if pressed == self.current_arrow:
                    self.score += 1
                else:
                    self.miss += 1
                self._advance_round()

    def update(self):
        if self.finished:
            # 結果画面中：SPACEでタイトルへ
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
                self.on_finish()
            return
        # プレイ中：Rで途中終了
        if pyxel.btnp(pyxel.KEY_R):
            self.on_finish()
            return

        if self.in_break:
            self._update_break()
        else:
            self._update_playing()

    # 進捗バー
    def _draw_progress(self):
        # セット番号と進行
        txt = f"SET {self.set_index+1}/5  ROUND {self.round_index}/{self.rounds_per_set}"
        pyxel.text(4, 4, txt, 7)

        # ラウンドの進行バー
        bar_w = WIDTH - 8
        done_w = int(bar_w * (self.round_index / max(1, self.rounds_per_set)))
        pyxel.rect(4, 12, bar_w, 4, 5)
        pyxel.rect(4, 12, done_w, 4, 11)

        # スコア
        pyxel.text(4, 20, f"SCORE:{self.score}  MISS:{self.miss}", 10)

    # 残り時間ゲージ
    def _draw_timer(self):
        if not self.waiting_input:
            return
        elapsed = pyxel.frame_count - self.spawn_frame
        remain = max(0, INTERVAL_FRAMES - elapsed)
        ratio = remain / INTERVAL_FRAMES
        w = int((WIDTH - 40) * ratio)
        pyxel.rect(20, 90, WIDTH - 40, 5, 1)  # 背景
        pyxel.rect(20, 90, w, 5, 12)          # 残り

        sec = frame_to_seconds(remain)
        draw_center_text(98, f"{sec:.1f}s", 7)

    def draw(self):
        self._draw_progress()

        if self.finished:
            draw_center_text(40, "RESULT", 11)
            draw_center_text(58, f"SCORE: {self.score}", 10)
            draw_center_text(68, f"MISS : {self.miss}", 8)
            draw_center_text(90, "SPACE/ENTER: TITLE", 7)
            return

        if self.in_break:
            # セット間休憩表示
            draw_center_text(52, f"SET {self.set_index+1} READY...", 7)
            remain = SET_GAP_FRAMES - (pyxel.frame_count - self.break_start_frame)
            sec = max(0.0, frame_to_seconds(remain))
            draw_center_text(66, f"NEXT IN {sec:.1f}s", 6)
            return

        # 矢印表示
        if self.current_arrow:
            draw_center_text(30, f"{self.difficulty}", 6)
            draw_arrow(WIDTH // 2, HEIGHT // 2, 20, self.current_arrow, col=10)

        self._draw_timer()
