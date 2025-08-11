import pyxel

W = 256
H = 256
PW = 16
PH = 16
SPEED = 1

# ---マップ設定---
T = 8
MAP_W, MAP_H  = 512, 512
TM = 0

def clamp(v, lo, hi): return max(lo, min(v, hi))

class App:
    def __init__(self):
        pyxel.init(W, H, title="jumping Game", fps = 60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        # マップの読み込み
        pyxel.tilemap(TM).refimg = 0
        # カメラ位置
        self.cam_x = 0
        self.cam_y = 0
        # プレイヤーの初期位置
        self.x, self.y = (W - PW) // 2, (H - PH) //2
        # 家の初期位置
        pyxel.blt(4, 4, 1, 16, 0, PW, PH, colkey=0)    # ← これで左上固定

        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        pyxel.run(self.update, self.draw, )

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE): pyxel.quit()
        dx = (pyxel.btn(pyxel.KEY_RIGHT) - pyxel.btn(pyxel.KEY_LEFT)) * SPEED
        dy = (pyxel.btn(pyxel.KEY_DOWN) - pyxel.btn(pyxel.KEY_UP)) * SPEED
        self.x = clamp(self.x + dx, 0, MAP_W - PW)
        self.y = clamp(self.y + dy, 0, MAP_H - PH)

        # ---- カメラ追従（画面中央へ寄せる）----
        target_cx = self.x + PW // 2 - W // 2
        target_cy = self.y + PH // 2 - H // 2
        self.cam_x = clamp(target_cx, 0, MAP_W - W)
        self.cam_y = clamp(target_cy, 0, MAP_H - H)

    def draw(self):
        pyxel.cls(3)

        # --- ワールド描画：カメラの影響を受ける ---
        pyxel.camera(self.cam_x, self.cam_y)          # 追従スクロール
        pyxel.bltm(0, 0, TM, 0, 0, MAP_W//T, MAP_H//T)

        # --- UI描画：画面固定にしたいもの ---
        pyxel.camera(0,0)                                 # カメラ解除（=0,0に戻す）


App()