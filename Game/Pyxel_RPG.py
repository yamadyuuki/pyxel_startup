import pyxel

# ゲーム画面サイズ
W = 256
H = 256

# プレイヤーサイズ
PW = 16
PH = 16
SPEED = 1

# マップ設定
T = 8  # タイルサイズ
MAP_W, MAP_H = 512, 512
TM = 0  # タイルマップ番号

def clamp(v, lo, hi): 
    return max(lo, min(v, hi))

BG_X = 0    # イメージバンク内のX座標
BG_Y = 16   # イメージバンク内のY座標
BG_W = 32   # 背景の幅
BG_H = 32   # 背景の高さ
BG_BANK = 0  # 背景画像のバンク番号

# マップ上のオブジェクトを表すクラス
class GameObject:
    def __init__(self, x, y, img, u, v, w, h, colkey=0):
        self.x = x  # マップ上のX座標
        self.y = y  # マップ上のY座標
        self.img = img  # 画像バンク番号
        self.u = u  # 画像内のX位置
        self.v = v  # 画像内のY位置
        self.w = w  # 幅
        self.h = h  # 高さ
        self.colkey = colkey  # 透明色
    
    def draw(self):
        pyxel.blt(self.x, self.y, self.img, self.u, self.v, self.w, self.h, self.colkey)

# プレイヤークラス
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 0, 0, PW, PH, 0)
    
    def update(self):
        dx = (pyxel.btn(pyxel.KEY_RIGHT) - pyxel.btn(pyxel.KEY_LEFT)) * SPEED
        dy = (pyxel.btn(pyxel.KEY_DOWN) - pyxel.btn(pyxel.KEY_UP)) * SPEED
        self.x = clamp(self.x + dx, 0, MAP_W - self.w)
        self.y = clamp(self.y + dy, 0, MAP_H - self.h)

# メインゲームクラス
class App:
    def __init__(self):
        pyxel.init(W, H, title="jumping Game", fps=60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        
        # マップの読み込み
        pyxel.tilemap(TM).refimg = 0
        
        # カメラ位置
        self.cam_x = 0
        self.cam_y = 0
        
        # プレイヤーの作成（マップの中央に配置）
        self.player = Player(60, 60)
        
        # 家オブジェクトの作成（マップ上の固定位置に配置）
        self.house = GameObject(32, 48, 1, 16, 0, PW, PH, 0)
        
        # 日本語フォントの読み込み
        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # プレイヤーの更新
        self.player.update()
        
        # カメラの更新（プレイヤーを中心に）
        target_cx = self.player.x + self.player.w // 2 - W // 2
        target_cy = self.player.y + self.player.h // 2 - H // 2
        self.cam_x = clamp(target_cx, 0, MAP_W - W)
        self.cam_y = clamp(target_cy, 0, MAP_H - H)

    def draw(self):
        pyxel.cls(3)
        
        # カメラの設定（スクロール効果）
        pyxel.camera(self.cam_x, self.cam_y)
        
        # マップの描画
        self.draw_tiled_background()
        
        # 家の描画（マップ上の固定位置）
        self.house.draw()
        
        # プレイヤーの描画
        self.player.draw()
        
        # UI要素がある場合はここでカメラをリセットして描画
        pyxel.camera(0, 0)
        # UIの描画コードをここに記述（必要に応じて）
        pyxel.text(10, 10, "8", 7)  

    def draw_tiled_background(self):
        """背景をタイル状に繰り返し描画する"""
        # 画面に表示される範囲のみ描画（最適化）
        start_x = (self.cam_x // BG_W) * BG_W
        start_y = (self.cam_y // BG_H) * BG_H
        end_x = self.cam_x + W + BG_W
        end_y = self.cam_y + H + BG_H
        
        # タイル状に背景を敷き詰める
        for y in range(start_y, end_y, BG_H):
            for x in range(start_x, end_x, BG_W):
                pyxel.blt(x, y, BG_BANK, BG_X, BG_Y, BG_W, BG_H, colkey=None)

App()