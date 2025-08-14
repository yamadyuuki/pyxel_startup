import pyxel
import math

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

# ===== 敵クラス（デモ用） =====
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16
        self.hp = 3
        self.hurt_timer = 0
        self.active = True
    
    def hit(self):
        """ダメージを受ける"""
        if self.hurt_timer <= 0:
            self.hp -= 1
            self.hurt_timer = 20  # 無敵時間
            if self.hp <= 0:
                self.active = False
    
    def update(self):
        """敵の更新処理"""
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
    
    def draw(self):
        """敵の描画"""
        if not self.active:
            return
            
        # 通常時は赤、ダメージ時は点滅
        color = 8 if self.hurt_timer % 4 < 2 else 14  # 赤と薄い赤で点滅
        pyxel.rect(self.x, self.y, self.w, self.h, color)
        
        # HPバー
        bar_width = (self.w * self.hp) // 3
        pyxel.rect(self.x, self.y - 4, bar_width, 2, 11)

# ===== 剣クラス =====
class Sword:
    def __init__(self):
        # 剣のスプライト情報（修正済み）
        self.u = 16  # スプライトのX座標
        self.v = 24  # スプライトのY座標
        self.w = 16  # スプライトの幅
        self.h = 8   # スプライトの高さ
        
        # 剣の回転アニメーション用
        self.active = False
        self.angle = 0
        self.max_angle = 180  # 180度回転
        self.rotation_speed = 10  # 1フレームの回転角度
        self.center_x = 0
        self.center_y = 0
        self.radius = 20  # 回転半径
        self.facing_right = False
        
        # 当たり判定用
        self.hit_enemies = set()  # 既に当たった敵を記録
    
    def activate(self, center_x, center_y, facing_right):
        """剣の回転アニメーションを開始"""
        self.active = True
        self.angle = 0
        self.center_x = center_x
        self.center_y = center_y
        self.facing_right = facing_right
        self.hit_enemies.clear()  # 当たり判定をリセット
    
    def update(self, enemies):
        """剣の更新と当たり判定"""
        if not self.active:
            return
            
        # 角度の更新
        self.angle += self.rotation_speed
        if self.angle >= self.max_angle:
            self.active = False
            return
        
        # 当たり判定
        self.check_hits(enemies)
    
    def check_hits(self, enemies):
        """敵との当たり判定"""
        if not self.active:
            return
            
        # 剣の現在位置を計算
        angle_rad = math.radians(self.angle)
        if self.facing_right:
            angle_rad = math.pi - angle_rad
        
        # 剣の中心位置
        sword_x = self.center_x + math.cos(angle_rad) * self.radius
        sword_y = self.center_y - math.sin(angle_rad) * self.radius
        
        # 当たり判定サイズ（剣のスプライトサイズに基づく）
        hit_w = self.w
        hit_h = self.h
        
        for enemy in enemies:
            if not enemy.active or enemy in self.hit_enemies:
                continue
                
            # 簡易的な当たり判定（矩形）
            if (sword_x < enemy.x + enemy.w and
                sword_x + hit_w > enemy.x and
                sword_y < enemy.y + enemy.h and
                sword_y + hit_h > enemy.y):
                
                enemy.hit()
                self.hit_enemies.add(enemy)  # 同じ攻撃で複数回ヒットしないように記録
    
    def draw(self):
        """剣の描画"""
        if not self.active:
            return
            
        # 角度に応じた位置計算（向きに応じて調整）
        angle_rad = math.radians(self.angle)
        if self.facing_right:
            angle_rad = math.pi - angle_rad
        
        # 剣の中心位置
        sword_x = self.center_x + math.cos(angle_rad) * self.radius
        sword_y = self.center_y - math.sin(angle_rad) * self.radius
        
        # 角度を描画向きに変換（180度の半円を8方向に分割）
        # 柄を内側にするために剣の向きを調整
        normalized_angle = (self.angle % 360)
        
        # 角度を8方向（45度ごと）に量子化
        angle_bracket = int((normalized_angle + 22.5) / 45) % 8
        
        # 剣を描画（向きに応じて反転）
        # 柄が内側に来るように調整
        flip_x = False
        
        if self.facing_right:  # 左向き（プレイヤーが右を向いている）
            if angle_bracket in [0, 1]:  # 右上方向
                flip_x = True
                offset_x = -self.w
                offset_y = -self.h
            elif angle_bracket in [2, 3]:  # 左上方向
                flip_x = False
                offset_x = 0
                offset_y = -self.h
            elif angle_bracket == 4:  # 左方向
                flip_x = False
                offset_x = 0
                offset_y = -self.h // 2
            else:  # 左下・下方向
                flip_x = False
                offset_x = 0
                offset_y = 0
        else:  # 右向き（プレイヤーが左を向いている）
            if angle_bracket in [0, 1]:  # 左上方向
                flip_x = False
                offset_x = 0
                offset_y = -self.h
            elif angle_bracket in [2, 3]:  # 右上方向
                flip_x = True
                offset_x = -self.w
                offset_y = -self.h
            elif angle_bracket == 4:  # 右方向
                flip_x = True
                offset_x = -self.w
                offset_y = -self.h // 2
            else:  # 右下・下方向
                flip_x = True
                offset_x = -self.w
                offset_y = 0
        
        # 描画（柄が内側に来るように反転）
        w = -self.w if flip_x else self.w
        
        pyxel.blt(
            int(sword_x + offset_x),
            int(sword_y + offset_y),
            0,  # イメージバンク
            self.u,
            self.v,
            w,
            self.h,
            0  # 透明色
        )

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
        
        # 剣攻撃関連
        self.sword = Sword()
        self.attack_cooldown = 0

    def update(self, enemies):
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

        # 攻撃（Aキー）
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if pyxel.btnp(pyxel.KEY_A) and self.attack_cooldown == 0 and not self.sword.active:
            # 剣の回転攻撃を開始
            center_x = self.x + self.w // 2
            center_y = self.y + self.h // 2
            self.sword.activate(center_x, center_y, self.facing_right)
            self.attack_cooldown = 30  # 攻撃のクールダウン
        
        # 剣の更新
        self.sword.update(enemies)

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
        # プレイヤーの描画
        u, v, w, h = 0, 16, 16, 16
        if self.facing_right:
            pyxel.blt(self.x, self.y, 0, u, v, w, h, 0)
        else:
            pyxel.blt(self.x, self.y, 0, u, v, -w, h, 0)
        
        # 剣の描画
        self.sword.draw()
        
        # 攻撃クールダウン表示
        if self.attack_cooldown > 0:
            pyxel.text(self.x, self.y - 8, f"CD:{self.attack_cooldown}", 7)

# ===== アプリ本体 =====
class App:
    def __init__(self):
        pyxel.init(256, 256, title="dot runner", fps=60)
        # あなたのリソースファイル名に合わせて変更
        pyxel.load("my_resource.pyxres")

        self.player = Player(PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y)
        
        # 敵の初期配置を保存
        self.initial_enemies = [
            (150, 150),
            (150, 200),
            (200, 200)
        ]
        
        # 敵を生成
        self.enemies = self.create_enemies()

        pyxel.run(self.update, self.draw)
    
    def create_enemies(self):
        """敵を初期配置に基づいて生成"""
        return [Enemy(x, y) for x, y in self.initial_enemies]

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        # 敵の更新
        for enemy in self.enemies:
            enemy.update()
        
        # プレイヤーの更新（敵リストを渡す）
        self.player.update(self.enemies)

        # Rキーでリセット機能を追加
        if pyxel.btnp(pyxel.KEY_R):
            self.player.respawn()
            # 敵も初期配置に戻す
            self.enemies = self.create_enemies()

    def draw(self):
        pyxel.cls(0)
        # タイルマップ0を原寸描画
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)
        
        # 敵の描画
        for enemy in self.enemies:
            enemy.draw()
            
        # プレイヤーの描画
        self.player.draw()
        
        # 操作説明
        pyxel.text(5, 5, "A: Attack  R: Reset  SPACE: Jump", 7)

App()