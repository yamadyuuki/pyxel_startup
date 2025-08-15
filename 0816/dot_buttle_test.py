# dot_runner_decorated.py
from __future__ import annotations
import pyxel
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import List, Set, Tuple

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
    (3, 2): TILE_STONE,   # 追加のタイル定義
}

# ===== タイル参照のメモ化 =====
@lru_cache(maxsize=4096)
def tile_uv(tx: int, ty: int) -> Tuple[int, int]:
    """タイル座標(tx,ty)→タイルセットのUVをキャッシュ付きで取得"""
    if tx < 0 or ty < 0 or tx >= 256 // TILE_SIZE or ty >= 256 // TILE_SIZE:
        return (-1, -1)
    try:
        return pyxel.tilemaps[0].pget(tx, ty)
    except Exception:
        return (-1, -1)

def get_tile_type(x: float, y: float) -> int:
    """ワールド座標(x,y)にあるタイルタイプを返す"""
    tx = int(x) // TILE_SIZE
    ty = int(y) // TILE_SIZE
    u, v = tile_uv(tx, ty)
    return TILE_TO_TILETYPE.get((u, v), TILE_NONE)

def is_block_at(x: float, y: float) -> bool:
    """その座標がブロックタイルか？（画面外でもFalse扱い）"""
    if x < 0 or y < 0 or x >= pyxel.width or y >= pyxel.height:
        return False
    return get_tile_type(x, y) in BLOCKING_TYPES

def rect_hits_block(x: float, y: float, w: int, h: int) -> bool:
    """矩形の四隅＋辺中央をチェックする簡易AABB×タイル判定"""
    return (
        is_block_at(x,       y) or
        is_block_at(x + w-1, y) or
        is_block_at(x,       y + h-1) or
        is_block_at(x + w-1, y + h-1) or
        is_block_at(x + w//2, y) or
        is_block_at(x, y + h//2) or
        is_block_at(x + w-1, y + h//2) or
        is_block_at(x + w//2, y + h-1)
    )

def move_y_with_pushback(x: float, y: float, dy: float, w: int, h: int):
    """Y軸方向の連続衝突（1pxずつ進め、ぶつかったら直前で止める）"""
    hit_top = hit_bottom = False
    step = 1 if dy > 0 else -1
    for _ in range(abs(int(dy))):
        if rect_hits_block(x, y + step, w, h):
            if step > 0:
                hit_bottom = True
            else:
                hit_top = True
            return y, hit_top, hit_bottom, 0
        y += step
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

def move_x_with_pushback(x: float, y: float, dx: float, w: int, h: int):
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

# ===== 便利な矩形型 =====
@dataclass(slots=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h

# ===== 敵クラス =====
@dataclass(slots=True)
class Enemy:
    x: int
    y: int
    w: int = 16
    h: int = 16
    hp: int = 3
    hurt_timer: int = 0
    active: bool = True

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.w, self.h)

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
        color = 8 if self.hurt_timer % 4 < 2 else 14  # 赤と薄い赤で点滅
        pyxel.rect(self.x, self.y, self.w, self.h, color)
        # HPバー
        bar_width = (self.w * self.hp) // 3
        pyxel.rect(self.x, self.y - 4, bar_width, 2, 11)

    @classmethod
    def from_tile(cls, tx: int, ty: int) -> "Enemy":
        return cls(tx * TILE_SIZE, ty * TILE_SIZE)

# ===== 剣クラス =====
@dataclass(slots=True)
class Sword:
    # スプライト情報
    u: int = 16
    v: int = 24
    w: int = 16
    h: int = 8

    # 状態
    active: bool = False
    duration: int = 0
    max_duration: int = 20

    # 位置
    x: int = 0
    y: int = 0
    offset_x: int = 0
    offset_y: int = 0
    facing_right: bool = True

    # 当たり判定
    hit_enemies: Set[Enemy] = field(default_factory=set)
    check_points: List[Tuple[int, int]] = field(default_factory=list)

    def activate(self, player_x: int, player_y: int, player_w: int, player_h: int, facing_right: bool):
        """剣を前方に出す"""
        self.active = True
        self.duration = self.max_duration
        self.facing_right = facing_right
        self.hit_enemies.clear()

        # ※このゲームでは facing_right=True が「左向き」扱い（既存仕様に合わせる）
        if facing_right:
            self.offset_x = -self.w  # 左側
        else:
            self.offset_x = player_w  # 右側

        self.offset_y = (player_h - self.h) // 2
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y
        self._generate_check_points()

    def _generate_check_points(self):
        """攻撃の当たり判定用チェックポイントを生成"""
        self.check_points.clear()
        num_points = 5
        for i in range(num_points):
            x_ratio = i / (num_points - 1)
            point_x = self.x + int(self.w * x_ratio)
            for y_offset in (0, self.h // 2, self.h - 1):
                self.check_points.append((point_x, self.y + y_offset))

    def update(self, player_x: int, player_y: int, enemies: List[Enemy]):
        """剣の更新"""
        if not self.active:
            return
        self.duration -= 1
        if self.duration <= 0:
            self.active = False
            return
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y
        self._generate_check_points()
        self._check_continuous_hits(enemies)

    def _check_continuous_hits(self, enemies: List[Enemy]):
        """連続衝突検出方式の当たり判定"""
        for enemy in enemies:
            if not enemy.active or enemy in self.hit_enemies:
                continue
            for point_x, point_y in self.check_points:
                if enemy.rect.contains(point_x, point_y):
                    enemy.hit()
                    self.hit_enemies.add(enemy)
                    break

    def draw(self):
        if not self.active:
            return
        w = -self.w if self.facing_right else self.w
        pyxel.blt(self.x, self.y, 0, self.u, self.v, w, self.h, 0)
        # デバッグ表示したい場合は下記を有効化
        # for px, py in self.check_points:
        #     pyxel.pset(px, py, 8)

# ===== プレイヤー =====
@dataclass(slots=True)
class Player:
    x: float
    y: float
    w: int = PLAYER_WIDTH
    h: int = PLAYER_HEIGHT

    # 物理
    vx: float = 0.0
    vy: float = 0.0
    move_speed: float = 1.2
    gravity: float = 0.35
    max_fall: float = 5.0
    jump_power: float = -6.0

    on_ground: bool = False
    facing_right: bool = False  # 既存仕様：True=左、False=右

    sword: Sword = field(default_factory=Sword)
    attack_cooldown: int = 0

    @property
    def rect(self) -> Rect:
        return Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def blt_w(self) -> int:
        # 向きに応じた blt 幅（正なら通常、負なら左右反転描画）
        return self.w if self.facing_right else -self.w

    def update(self, enemies: List[Enemy]):
        # 入力
        self.vx = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            self.vx -= self.move_speed
            self.facing_right = True     # 既存仕様に合わせる
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.vx += self.move_speed
            self.facing_right = False

        # ジャンプ（UP）
        if self.on_ground and pyxel.btnp(pyxel.KEY_UP):
            self.vy = self.jump_power

        # 攻撃（SPACE）
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if pyxel.btnp(pyxel.KEY_SPACE) and self.attack_cooldown == 0 and not self.sword.active:
            self.sword.activate(int(self.x), int(self.y), self.w, self.h, self.facing_right)
            self.attack_cooldown = 30

        # 重力
        self.vy = min(self.vy + self.gravity, self.max_fall)

        # 衝突移動 Y→X
        new_y, hit_top, hit_bottom, _ = move_y_with_pushback(self.x, self.y, self.vy, self.w, self.h)
        self.y = new_y
        self.on_ground = hit_bottom
        if (hit_top and self.vy < 0) or (hit_bottom and self.vy > 0):
            self.vy = 0

        new_x, hit_left, hit_right, _ = move_x_with_pushback(self.x, self.y, self.vx, self.w, self.h)
        self.x = new_x
        if (hit_left and self.vx < 0) or (hit_right and self.vx > 0):
            self.vx = 0

        # 剣の更新
        self.sword.update(int(self.x), int(self.y), enemies)

        # 画面外落下などの簡易リセット
        if self.y > pyxel.height + 32:
            self.respawn()

    def respawn(self):
        self.x, self.y = PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y
        self.vx = self.vy = 0
        self.on_ground = False

    def draw(self):
        # プレイヤーの描画
        u, v, w, h = 0, 16, 16, 16
        pyxel.blt(int(self.x), int(self.y), 0, u, v, self.blt_w, h, 0)
        # 剣
        self.sword.draw()
        # クールダウン
        if self.attack_cooldown > 0:
            pyxel.text(int(self.x), int(self.y) - 8, f"CD:{self.attack_cooldown}", 7)

# ===== アプリ本体 =====
class App:
    def __init__(self):
        pyxel.init(256, 256, title="dot runner", fps=60)
        # あなたのリソースファイル名に合わせて変更
        pyxel.load("my_resource.pyxres")

        self.player = Player(PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y)

        # 敵の初期配置
        self.initial_enemies_tiles = [(19, 18), (19, 25), (25, 25)]
        self.enemies: List[Enemy] = self.create_enemies()

        pyxel.run(self.update, self.draw)

    def create_enemies(self) -> List[Enemy]:
        """敵を初期配置に基づいて生成"""
        return [Enemy.from_tile(tx, ty) for tx, ty in self.initial_enemies_tiles]

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # 敵更新
        for e in self.enemies:
            e.update()

        # プレイヤー更新
        self.player.update(self.enemies)

        # Rキーでリセット
        if pyxel.btnp(pyxel.KEY_R):
            self.player.respawn()
            self.enemies = self.create_enemies()
            tile_uv.cache_clear()  # もしマップを書き換えていた場合の保険

    def draw(self):
        pyxel.cls(0)
        # タイルマップ0を原寸描画
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)

        # 敵の描画
        for e in self.enemies:
            e.draw()

        # プレイヤーの描画
        self.player.draw()

        # 操作説明
        pyxel.text(5, 5, "SPACE: Attack  UP: Jump  R: Reset  Q: Quit", 7)

if __name__ == "__main__":
    App()
