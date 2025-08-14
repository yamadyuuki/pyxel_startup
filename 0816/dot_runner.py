import pyxel

# ===== タイル定義と当たり判定の変換辞書 =====
TILE_NONE = 0
TILE_STONE = 1
BLOCKING_TYPES = {TILE_STONE}  # ←侵入を禁止するタイル
TILE_SIZE = 8

# ===== 設定（外部で一元管理） =====
PLAYER_RESPAWN_X = 30
PLAYER_RESPAWN_Y = 30
PLAYER_WIDTH     = 16
PLAYER_HEIGHT    = 16

# タイルセット上のUV(= pgetで返る(u,v)) → ゲーム内のタイルタイプ への対応表
TILE_TO_TILETYPE = {
    (2, 2): TILE_STONE,   # 例：タイルUV(2,2)は「壁（石）」扱い
}

def get_tile_type(x, y):
    """ワールド座標(x,y)にあるタイルタイプを返す"""
    tx = int(x) // TILE_SIZE
    ty = int(y) // TILE_SIZE
    u, v = pyxel.tilemaps[0].pget(tx, ty)  # タイルセット内のUV
    return TILE_TO_TILETYPE.get((u, v), TILE_NONE)

def is_block_at(x, y):
    """その座標がブロックタイルか？（画面外でもFalse扱いにしておく）"""
    if x < 0 or y < 0 or x >= pyxel.width or y >= pyxel.height:
        return False
    return get_tile_type(x, y) in BLOCKING_TYPES

def rect_hits_block(x, y, w, h):
    """矩形の四隅と辺の中間点にブロックがあるか（改良版AABB×タイル判定）"""
    # 四隅に加えて、各辺の中間点もチェック
    return (
        is_block_at(x,       y) or       # 左上
        is_block_at(x + w-1, y) or       # 右上
        is_block_at(x,       y + h-1) or # 左下
        is_block_at(x + w-1, y + h-1) or # 右下
        is_block_at(x + w//2, y) or      # 上辺中央
        is_block_at(x, y + h//2) or      # 左辺中央
        is_block_at(x + w-1, y + h//2) or # 右辺中央
        is_block_at(x + w//2, y + h-1)    # 下辺中央
    )


def move_y_with_pushback(x, y, dy, w, h):
    """Y軸方向の連続衝突（1pxずつ進め、ぶつかったら直前で止める）"""
    hit_top = hit_bottom = False
    step = 1 if dy > 0 else -1
    for _ in range(abs(int(dy))):
        if rect_hits_block(x, y + step, w, h):
            if step > 0:
                hit_bottom = True
            else:
                hit_top = True
            return y, hit_top, hit_bottom, 0  # 残りdyは0（進めない）
        y += step
    # 端数（小数）も処理：タイル衝突は1px粒度なので最後にまとめて足す
    frac = dy - int(dy)
    if frac != 0:
        if rect_hits_block(x, y + frac, w, h):
            if frac > 0:
                hit_bottom = True
            else:
                hit_top = True
            return y, hit_top, hit_bottom, 0
        y += frac
    return y, hit_top, hit_bottom, dy

def move_x_with_pushback(x, y, dx, w, h):
    """X軸方向の連続衝突（1pxずつ進め、ぶつかったら直前で止める）"""
    hit_left = hit_right = False
    step = 1 if dx > 0 else -1
    for _ in range(abs(int(dx))):
        if rect_hits_block(x + step, y, w, h):
            if step > 0:
                hit_right = True
            else:
                hit_left = True
            return x, hit_left, hit_right, 0
        x += step
    # 端数（小数）
    frac = dx - int(dx)
    if frac != 0:
        if rect_hits_block(x + frac, y, w, h):
            if frac > 0:
                hit_right = True
            else:
                hit_left = True
            return x, hit_left, hit_right, 0
        x += frac
    return x, hit_left, hit_right, dx

# ===== プレイヤー =====
class Player:
    def __init__(self, x, y):
        # 位置と当たり判定サイズ（画像サイズに合わせて調整）
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16

        # 物理パラメータ
        self.vx = 0
        self.vy = 0
        self.move_speed = 1.2
        self.gravity = 0.35
        self.max_fall = 5.0
        self.jump_power = -5.5

        self.on_ground = False
        self.facing_right = False

    def update(self):
        # 入力
        self.vx = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            self.vx -= self.move_speed
            self.facing_right = True
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.vx += self.move_speed
            self.facing_right = False

        # ジャンプ
        if self.on_ground and pyxel.btnp(pyxel.KEY_SPACE):
            self.vy = self.jump_power

        # 重力
        self.vy = min(self.vy + self.gravity, self.max_fall)

        # --- 連続衝突移動：Y→X の順で処理（段差で滑りやすい）---
        new_y, hit_top, hit_bottom, _ = move_y_with_pushback(self.x, self.y, self.vy, self.w, self.h)
        self.y = new_y
        self.on_ground = hit_bottom
        if hit_top and self.vy < 0:
            self.vy = 0
        if hit_bottom and self.vy > 0:
            self.vy = 0

        new_x, hit_left, hit_right, _ = move_x_with_pushback(self.x, self.y, self.vx, self.w, self.h)
        self.x = new_x
        # 横にぶつかったら横速度を0に
        if (hit_left and self.vx < 0) or (hit_right and self.vx > 0):
            self.vx = 0

        # 画面外落下などの簡易リセット（任意）
        if self.y > pyxel.height + 32:
            self.respawn()

    def respawn(self):
        self.x, self.y = PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y
        self.vx = self.vy = 0
        self.on_ground = False

    def draw(self):
        # 画像0番の(0,16) を 8x8で使う例。必要に応じて変更
        u, v, w, h = 0, 16, 16, 16
        if self.facing_right:
            pyxel.blt(self.x, self.y, 0, u, v, w, h, 0)
        else:
            pyxel.blt(self.x, self.y, 0, u , v, -w, h, 0)

# ===== アプリ本体 =====
class App:
    def __init__(self):
        pyxel.init(256, 256, title="dot runner", fps=60)
        # あなたのリソースファイル名に合わせて変更
        pyxel.load("my_resource.pyxres")

        self.x = 30
        self.y = 30

        self.player = Player(PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y)

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.player.update()

        # Rキーでリセット機能を追加
        if pyxel.btnp(pyxel.KEY_R):
            self.player.respawn()

    def draw(self):
        pyxel.cls(0)
        # タイルマップ0を原寸描画
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)
        self.player.draw()

App()
