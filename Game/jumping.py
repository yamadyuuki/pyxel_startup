import pyxel

W = 400
H = 240
PW = 16
PH = 16
SPEED = 1

def clamp(v, lo, hi): return max(lo, min(v, hi))

class App:
    def __init__(self):
        pyxel.init(W, H, title="jumping Game", fps = 60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        self.x, self.y = (W - PW) // 2, (H - PH) //2
        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        pyxel.run(self.update, self.draw, )

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE): pyxel.quit()
        dx = (pyxel.btn(pyxel.KEY_RIGHT) - pyxel.btn(pyxel.KEY_LEFT)) * SPEED
        dy = (pyxel.btn(pyxel.KEY_DOWN) - pyxel.btn(pyxel.KEY_UP)) * SPEED
        self.x = clamp(self.x + dx, 0, W - PW)
        self.y = clamp(self.y + dy, 0, H-PH)

    def draw(self):
        pyxel.cls(3)  # 背景色を設定
        pyxel.blt(self.x, self.y, 1, 0, 0 , PW, PH, colkey=0) # Playerを描画
        pyxel.blt(0, 0, 1, 16, 0, PW, PH, colkey=pyxel.COLOR_BLACK) # 家を描画

App()