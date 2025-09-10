# main.py
import pyxel
from core.models import Question
from packs import pack_sample
from datetime import datetime, timedelta  # ← 追加
from typing import List, Tuple

QUESTIONS = pack_sample.QUESTIONS

W, H = 256, 192

STATE_TITLE   = 0
STATE_PLAYING = 1
STATE_CHOICE  = 2
STATE_RESULT  = 3
STATE_BLURB   = 4

def _parse_date(s: str):
    return datetime.fromisoformat(s).date()

def _linear_resample(arr: List[int], new_len: int) -> List[int]:
    """整数の配列を new_len に線形リサンプリング（小数点四捨五入）。"""
    n = len(arr)
    if n == new_len:
        return list(arr)
    if new_len <= 1:
        return [int(round(float(arr[-1])))]
    out = []
    for j in range(new_len):
        # 0..1 の正規化位置
        t = j / (new_len - 1)
        # 旧配列の連続インデックス
        x = t * (n - 1)
        i0 = int(x)
        i1 = min(i0 + 1, n - 1)
        a = arr[i0]
        b = arr[i1]
        w = x - i0
        v = a * (1 - w) + b * w
        out.append(int(round(v)))
    return out

def _slice_by_span_ratio(base_prices: List[int], base_span: Tuple[str, str],
                         target_span: Tuple[str, str]) -> List[int]:
    """
    base_span 全体の中で target_span が占める相対位置に相当する区間を
    base_prices から切り出す（営業日を厳密には見ない近似）。
    """
    b0, b1 = map(_parse_date, base_span)
    t0, t1 = map(_parse_date, target_span)
    total_days = (b1 - b0).days
    if total_days <= 1:
        return list(base_prices)
    start_ratio = max(0.0, min(1.0, (t0 - b0).days / total_days))
    end_ratio   = max(0.0, min(1.0, (t1 - b0).days / total_days))
    if end_ratio < start_ratio:
        start_ratio, end_ratio = end_ratio, start_ratio
    n = len(base_prices)
    s_idx = int(round(start_ratio * (n - 1)))
    e_idx = max(s_idx + 1, int(round(end_ratio * (n - 1))))  # 最低2点
    return base_prices[s_idx:e_idx + 1]

# === 追加: Nikkei 225 の Question を一度だけ特定 ===
INDEX_Q = None
for _q in pack_sample.QUESTIONS:
    if str(getattr(_q, "ticker", "")).startswith("^N225"):
        INDEX_Q = _q
        break

class App:
    def __init__(self):
        pyxel.init(W, H, title="Stock Price Quiz (Beta)")
        self.state = STATE_TITLE
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.q = QUESTIONS # 今は1問固定
        self.t = 0          # チャートの進行インデックス
        self.stopped = False
        self.sel = 0        # 選択肢カーソル
        self.correct_idx = 0  # 今は常に先頭が正解（試作）
        self.title_sel = 0
        self.title_top = 0

    # --- update() 内 ---

    def update(self):
        if self.state == STATE_TITLE:
            n = len(QUESTIONS)
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.title_sel = (self.title_sel + 1) % n
            if pyxel.btnp(pyxel.KEY_UP):
                self.title_sel = (self.title_sel - 1 + n) % n

            # 数字キーのオフバイワンを修正（0始まり）
            if pyxel.btnp(pyxel.KEY_1): self.title_sel = 0
            if pyxel.btnp(pyxel.KEY_2) and n >= 2: self.title_sel = 1
            if pyxel.btnp(pyxel.KEY_3) and n >= 3: self.title_sel = 2
            if pyxel.btnp(pyxel.KEY_4) and n >= 4: self.title_sel = 3
            if pyxel.btnp(pyxel.KEY_5) and n >= 5: self.title_sel = 4
            if pyxel.btnp(pyxel.KEY_6) and n >= 6: self.title_sel = 5
            if pyxel.btnp(pyxel.KEY_7) and n >= 7: self.title_sel = 6
            if pyxel.btnp(pyxel.KEY_8) and n >= 8: self.title_sel = 7
            if pyxel.btnp(pyxel.KEY_9) and n >= 9: self.title_sel = 8

            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.start_question(self.title_sel)

        elif self.state == STATE_PLAYING:
            # SPACEで停止→選択肢へ
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.stopped = True
                self.state = STATE_CHOICE

            # 停止していなければ時間進行（グラフが伸びる）
            if not self.stopped:
                self.t = min(self.t + 1, len(self.q.prices) - 1)

        elif self.state == STATE_CHOICE:
            # ↑↓と数字キーでカーソル移動（choicesは4つ想定）
            n = len(self.q.choices)
            if pyxel.btnp(pyxel.KEY_DOWN): self.sel = (self.sel + 1) % n
            if pyxel.btnp(pyxel.KEY_UP):   self.sel = (self.sel - 1 + n) % n
            if pyxel.btnp(pyxel.KEY_1): self.sel = 0
            if pyxel.btnp(pyxel.KEY_2) and n >= 2: self.sel = 1
            if pyxel.btnp(pyxel.KEY_3) and n >= 3: self.sel = 2
            if pyxel.btnp(pyxel.KEY_4) and n >= 4: self.sel = 3

            # 決定
            if pyxel.btnp(pyxel.KEY_SPACE):
                # 選んだ選択肢の文字列と name が一致するかで判定
                self.is_correct = (self.q.choices[self.sel].strip() == self.q.name.strip())
                if self.is_correct:
                    self.score += 1
                self.state = STATE_RESULT
        elif self.state == STATE_RESULT:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = STATE_BLURB
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
                self.state = STATE_TITLE

        elif self.state == STATE_BLURB:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
                self.state = STATE_TITLE

        if pyxel.btnp(pyxel.KEY_R):
            self.reset_game()
            self.state = STATE_TITLE

    def start_question(self, idx: int):
        self.q = QUESTIONS[idx]
        self.t = 0
        self.stopped = False
        self.sel = 0
        self.correct_idx = 0

        # === 追加: Nikkei 225 オーバーレイ用配列を用意 ===
        self.idx_prices = None
        if INDEX_Q is not None and getattr(self.q, "span", None):
            # 期間で切り出し → データ長にリサンプリング
            idx_slice = _slice_by_span_ratio(INDEX_Q.prices, INDEX_Q.span, self.q.span)
            self.idx_prices = _linear_resample(idx_slice, len(self.q.prices))
            self.index_label = "Nikkei 225"
        else:
            self.index_label = None

        self.state = STATE_PLAYING

    # ---------------- draw ----------------
    def draw(self):
        pyxel.cls(1)
        if self.state == STATE_TITLE:
            pyxel.text(62, 10, "Stock Price Quiz (Beta)", 7)
            pyxel.text(20, 24, "Select Question  (UP/DOWN, Enter/Space)", 10)

            # リスト枠
            bx, by, bw, bh = 12, 36, W-24, H-60
            pyxel.rectb(bx, by, bw, bh, 7)

            # スクロール制御（同時表示行数）
            visible = 8
            n = len(QUESTIONS)
            # カーソルが画面外に出ないように先頭行を調整
            if self.title_sel < self.title_top:
                self.title_top = self.title_sel
            if self.title_sel >= self.title_top + visible:
                self.title_top = self.title_sel - visible + 1

            # 各行の表示
            for row in range(visible):
                idx = self.title_top + row
                if idx >= n:
                    break
                q = QUESTIONS[idx]
                line_y = by + 6 + row*10
                # カレント行ハイライト
                if idx == self.title_sel:
                    pyxel.rect(bx+1, line_y-2, bw-2, 9, 1)  # 反転背景
                # 表示テキスト（No, 銘柄、期間など）
                # name や ticker / span はパックから取得
                label = f"Question {idx+1}"
                pyxel.text(bx+6, line_y, label[:46], 10 if idx==self.title_sel else 7)

        elif self.state in (STATE_PLAYING, STATE_CHOICE):
            self.draw_chart()
            if self.state == STATE_CHOICE:
                self.draw_choices()
        elif self.state == STATE_RESULT:
            s = "Correct!" if self.is_correct else "Wrong!"
            pyxel.text(100, 80, s, 10 if self.is_correct else 8)
            pyxel.text(70, 100, f"Score: {self.score}", 7)
            pyxel.text(40, 120, "SPACE:Details / Enter:Next", 6)
        elif self.state == STATE_BLURB:
            self.draw_chart(dim=True)
            self.draw_modal(self.q.blurb)

    # --- helpers ---
    def draw_chart(self, dim=False):
        # 枠
        if dim: pyxel.rect(0,0,W,H,1)
        x0,y0,x1,y1 = 20, 20, W-10, H-50
        pyxel.rectb(x0, y0, x1-x0, y1-y0, 7)

        # --- データ準備 ---
        data_main = self.q.prices[: self.t + 1]
        if not data_main:
            return
        data_idx = []
        if getattr(self, "idx_prices", None):
            data_idx = self.idx_prices[: self.t + 1]

        # --- 共通スケール（銘柄＋指数の全体で min/max を取る） ---
        data_all = data_main + (data_idx or [])
        mi, ma = min(data_all), max(data_all)
        if mi == ma:
            mi -= 1  # 0除算回避

        def map_y(v: int) -> int:
            r = (v - mi) / (ma - mi)
            return int(y1 - r * (y1 - y0))

        # --- 銘柄線（色: 11）---
        last = None
        for i, v in enumerate(data_main):
            x = x0 + int(i * (x1 - x0) / max(1, len(self.q.prices) - 1))
            y = map_y(v)
            if last is not None:
                pyxel.line(last[0], last[1], x, y, 11)
            last = (x, y)

        # --- 指数線（色: 5）---
        if data_idx:
            last = None
            for i, v in enumerate(data_idx):
                x = x0 + int(i * (x1 - x0) / max(1, len(self.idx_prices) - 1))
                y = map_y(v)
                if last is not None:
                    pyxel.line(last[0], last[1], x, y, 10)
                last = (x, y)
            # 凡例（右上）
            pyxel.text(x1 - 100, y0 + 2, (self.q.name or "")[:12], 11)
            pyxel.text(x1 - 100, y0 + 10, (self.index_label or "Index")[:12], 10)

        # 停止ライン
        if self.state == STATE_CHOICE and data_main:
            pyxel.line(last[0], y0, last[0], y1, 8)

        # === 縦軸メモリ ===
        steps = 4
        for i in range(steps+1):
            val = mi + (ma - mi) * i / steps
            y = map_y(val)
            pyxel.line(x0-3, y, x0, y, 7)
            pyxel.text(2, y-2, str(int(val)), 7)

        # === 横軸メモリ（日付ラベル） ===
        x_steps = 5
        n = len(self.q.prices)
        for i in range(x_steps + 1):
            frac = i / x_steps
            idx = int((n - 1) * frac)
            x = x0 + int((idx / max(1, n - 1)) * (x1 - x0))
            pyxel.line(x, y1, x, y1 + 3, 7)
            label = self._interp_date_label(self.q.span, frac, monthly=True)
            pyxel.text(x - (len(label) * 5) // 2, y1 + 6, label, 7)

    def _interp_date_label(self, span, frac: float, monthly: bool = True) -> str:
        # fracは0.0=開始、1.0=終了
        s = datetime.fromisoformat(span[0]).date()
        e = datetime.fromisoformat(span[1]).date()
        total = (e - s).days
        d = s + timedelta(days=int(total * frac))
        return d.strftime("%Y-%m") if monthly else d.strftime("%Y-%m-%d")

    def draw_choices(self):
        bx, by, bw, bh = 40, H-44, W-80, 34
        # pyxel.rectb(bx, by, bw, bh, 7)
        for i, c in enumerate(self.q.choices):
            col = 10 if i == self.sel else 7
            pyxel.text(bx+8, by+6+i*8, f"{i+1}. {c}", col)

    def draw_modal(self, text):
        mx, my, mw, mh = 20, 20, W-40, H-40
        pyxel.rect(mx, my, mw, mh, 0)
        pyxel.rectb(mx, my, mw, mh, 7)
        # ざっくり折り返し（表示専用）
        lines = []
        line = ""
        for ch in text:
            if len(line) > 26 or ch == "\n":
                lines.append(line); line = ""
                if ch == "\n": continue
            line += ch
        if line: lines.append(line)
        for i, ln in enumerate(lines[: (mh//8)-3 ]):
            pyxel.text(mx+6, my+6+i*8, ln, 7)
        pyxel.text(mx+6, my+mh-12, "Press SPACE to close", 6)

App()
