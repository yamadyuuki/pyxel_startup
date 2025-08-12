import pyxel
from RPG_constants import *

TILE_SIZE = 8  # 1タイルのサイズ（px）
BLOCKING_TYPES = {TILE_STONE, TILE_HOUSE}  # 進入禁止タイル
COLLECTIBLE_TYPES = {TILE_GEM}  # 収集可能アイテム

def get_tile_type(x, y):
    """ワールド座標(x,y)にあるタイルタイプを返す"""
    tx = x // TILE_SIZE
    ty = y // TILE_SIZE
    tile = pyxel.tilemaps[0].pget(tx, ty)  # (u, v) タプル
    return TILE_TO_TILETYPE.get(tile, TILE_NONE)

def set_tile_empty(x, y):
    """指定座標のタイルを空に設定"""
    tx = x // TILE_SIZE
    ty = y // TILE_SIZE
    pyxel.tilemaps[0].pset(tx, ty, (0, 0))  # 空のタイルに設定

def is_block_at(x, y):
    """その座標にブロックタイルがあるか"""
    tile_type = get_tile_type(x, y)
    
    # 通常のブロック判定
    if tile_type in BLOCKING_TYPES:
        return True
    
    # 家の特別判定: 家は16x16ピクセル（2x2タイル）なので
    # 家タイルの左上から1タイル分の範囲も進入禁止とする
    # タイルマップ上の位置を計算
    tx, ty = x // TILE_SIZE, y // TILE_SIZE
    
    # 家タイルの周辺を調べる（2x2の範囲）
    for dx in range(2):
        for dy in range(2):
            check_x, check_y = (tx - dx) * TILE_SIZE, (ty - dy) * TILE_SIZE
            check_tile = get_tile_type(check_x, check_y)
            if check_tile == TILE_HOUSE:
                # 家タイルの一部なので進入禁止
                return True
                
    return False

def rect_hits_block(x, y, w, h):
    """矩形がブロックタイルに重なっているか（四隅チェック）"""
    return (
        is_block_at(x,         y        ) or
        is_block_at(x + w - 1, y        ) or
        is_block_at(x,         y + h - 1) or
        is_block_at(x + w - 1, y + h - 1)
    )

# ゲーム画面サイズ
W = 256
H = 256

# プレイヤーサイズ
PW = 16
PH = 16
SPEED = 1

# マップ設定
MAP_W, MAP_H = 512, 512
TM = 0  # タイルマップ番号

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

BG_X = 0
BG_Y = 16
BG_W = 32
BG_H = 32
BG_BANK = 0

SCROLL_BORDER_X = 64
SCROLL_BORDER_Y = 64


# 汎用オブジェクト
class GameObject:
    def __init__(self, x, y, img, u, v, w, h, colkey=0):
        self.x = x
        self.y = y
        self.img = img
        self.u = u
        self.v = v
        self.w = w
        self.h = h
        self.colkey = colkey
    
    def draw(self):
        pyxel.blt(self.x, self.y, self.img, self.u, self.v, self.w, self.h, self.colkey)

# プレイヤー
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 0, 0, PW, PH, 0)
        self.facing = False  # false: 左向き, true: 右向き
        self.gems_collected = 0  # 収集した宝石の数

    def update(self):
        dx = (pyxel.btn(pyxel.KEY_RIGHT) - pyxel.btn(pyxel.KEY_LEFT)) * SPEED
        dy = (pyxel.btn(pyxel.KEY_DOWN) - pyxel.btn(pyxel.KEY_UP)) * SPEED
            #右向き
        if dx > 0:
            self.facing = True
            #左向き
        elif dx < 0:
            self.facing = False

        nx = clamp(self.x + dx, 0, MAP_W - self.w)
        if not rect_hits_block(nx, self.y, self.w, self.h):
            self.x = nx
    
        # --- Y軸 ---
        ny = clamp(self.y + dy, 0, MAP_H - self.h)
        if not rect_hits_block(self.x, ny, self.w, self.h):
            self.y = ny
        # 当たるならYはそのまま
        
        # 宝石などのアイテム収集判定
        self.check_item_collection()

    def check_item_collection(self):
        """プレイヤーの周囲のアイテム収集判定"""
        # プレイヤーの周囲8点をチェック
        for i in [0, 7, 15]:  # 上端、中央、下端
            for j in [0, 7, 15]:  # 左端、中央、右端
                check_x = self.x + j
                check_y = self.y + i
                tile_type = get_tile_type(check_x, check_y)
                
                # 宝石の場合
                if tile_type == TILE_GEM:
                    # 宝石を収集（タイルを空に設定）
                    set_tile_empty(check_x, check_y)
                    self.gems_collected += 1
                    pyxel.play(0, 2)  # 効果音再生（チャンネル0、サウンド0）

    def draw_player(self):
        if self.facing:
            # 右向き（水平反転）: u,vはそのまま。wを負に
            pyxel.blt(self.x, self.y, self.img, self.u, self.v, -self.w, self.h, self.colkey)
        else:
            # 左向き（通常）
            pyxel.blt(self.x, self.y, self.img, self.u, self.v, self.w, self.h, self.colkey)


# メインゲーム
class App:
    def __init__(self):
        pyxel.init(W, H, title="RPG Camera", fps=60)
        pyxel.load("my_resource.pyxres")
        
        self.cam_x = 0
        self.cam_y = 0
        
        self.player = Player(60, 60)
        self.debug_mode = False  # デバッグモードフラグ
        
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # デバッグモード切り替え
        if pyxel.btnp(pyxel.KEY_D):
            self.debug_mode = not self.debug_mode
        
        self.player.update()

        # X方向カメラ追従
        if self.player.x > self.cam_x + W - SCROLL_BORDER_X:
            self.cam_x = min(self.player.x - (W - SCROLL_BORDER_X), MAP_W - W)
        elif self.player.x < self.cam_x + SCROLL_BORDER_X:
            self.cam_x = max(self.player.x - SCROLL_BORDER_X, 0)

        # Y方向カメラ追従
        if self.player.y > self.cam_y + H - SCROLL_BORDER_Y:
            self.cam_y = min(self.player.y - (H - SCROLL_BORDER_Y), MAP_H - H)
        elif self.player.y < self.cam_y + SCROLL_BORDER_Y:
            self.cam_y = max(self.player.y - SCROLL_BORDER_Y, 0)

    def draw(self):
        pyxel.cls(3)
        pyxel.camera(self.cam_x, self.cam_y)
        
        # タイルマップを描画（透明色を指定）
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256, colkey=0)
        self.player.draw_player()
        
        # デバッグ情報表示（デバッグモード時）
        if self.debug_mode:
            # プレイヤーの位置と当たり判定を表示
            player_tile_x = self.player.x // TILE_SIZE
            player_tile_y = self.player.y // TILE_SIZE
            tile_type = get_tile_type(self.player.x, self.player.y)
            
            pyxel.text(self.player.x, self.player.y - 10, 
                      f"({player_tile_x},{player_tile_y}) T:{tile_type}", 7)
            
            # 周囲のタイルの当たり判定を可視化
            for y in range(player_tile_y - 2, player_tile_y + 3):
                for x in range(player_tile_x - 2, player_tile_x + 3):
                    if is_block_at(x * TILE_SIZE, y * TILE_SIZE):
                        pyxel.rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, 8)
                    # 宝石タイルを緑色で表示
                    if get_tile_type(x * TILE_SIZE, y * TILE_SIZE) == TILE_GEM:
                        pyxel.rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, 11)
        
        pyxel.camera()  # UI描画のためリセット
        
        # UIの表示
        pyxel.text(10, 10, f"HP: 8", 7)
        pyxel.text(W - 80, 10, f"Gems: {self.player.gems_collected}", 11)
        
        # デバッグモードの状態表示
        if self.debug_mode:
            pyxel.text(10, H - 10, "DEBUG: ON (D key)", 8)


# RPG_constants.pyを正しく修正してください:
# TILE_TO_TILETYPE = {
#     (4, 0): TILE_STONE,
#     (5, 0): TILE_GEM,
#     (4, 2): TILE_HOUSE,  # <- ここを修正(4,4)から(4,2)へ
# }


App()