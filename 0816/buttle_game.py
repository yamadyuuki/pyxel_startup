import pyxel
import math
import random
from buttle_constants import (
    SCREEN_W, SCREEN_H, FPS,
    TILE_SIZE, TILE_TO_TILETYPE, BLOCKING_TYPES,TILE_NONE,
    PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y, PLAYER_W, PLAYER_H,
    GRAVITY, MAX_FALL, MOVE_SPEED, JUMP_POWER,
    KEY_LEFT, KEY_RIGHT, KEY_JUMP, KEY_ATTACK, KEY_RESET, KEY_QUIT, KEY_RETRY,
    KEY_LABELS, HUD_POS,
    SWORD_COOLDOWN, SWORD_ACTIVE_FRAMES,
    # HP関連の定数
    PLAYER_MAX_HP, INVINCIBLE_FRAMES, KNOCKBACK_POWER, DAMAGE_FLASH_INTERVAL,
    # ゲーム状態関連の定数
    GAME_STATE_PLAYING, GAME_STATE_GAME_OVER,
    GAMEOVER_TILEMAP, GAMEOVER_IMAGE, GAMEOVER_TILE_X, GAMEOVER_TILE_Y,
    GAMEOVER_TILE_W, GAMEOVER_TILE_H,
    # 敵関連の定数（新規追加）
    ENEMY_W, ENEMY_H, ENEMY_HP, ENEMY_HURT_FRAMES,
    ENEMY_GRAVITY, ENEMY_MAX_FALL, ENEMY_MOVE_SPEED, ENEMY_SPAWN_HEIGHT,
    ENEMY_STATE_FALLING, ENEMY_STATE_GROUND, ENEMY_DIRECTION_LEFT, ENEMY_DIRECTION_RIGHT,
    SCORE_ENEMY_DEFEAT,
)



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

# ===== 敵クラス（基本挙動実装） =====
class Enemy:
    def __init__(self, x, y):
        # 位置とサイズ
        self.x = x
        self.y = y
        self.w = ENEMY_H
        self.h = ENEMY_W
        
        # HP関連
        self.hp = ENEMY_HP
        self.max_hp = ENEMY_HP
        self.hurt_timer = 0
        self.active = True
        
        # 物理パラメータ
        self.vx = 0
        self.vy = 0
        self.gravity = ENEMY_GRAVITY
        self.max_fall = ENEMY_MAX_FALL
        self.move_speed = ENEMY_MOVE_SPEED
        
        # 行動状態
        self.state = ENEMY_STATE_FALLING  # 初期状態は落下
        self.direction = random.choice([ENEMY_DIRECTION_LEFT, ENEMY_DIRECTION_RIGHT])  # ランダムな方向
        self.on_ground = False
        
        # 移動パターン用
        self.direction_timer = random.randint(60, 180)  # 方向転換タイマー（1-3秒）
    
    @classmethod
    def spawn_from_sky(cls, x):
        """画面上から落下する敵を生成"""
        return cls(x, ENEMY_SPAWN_HEIGHT)
    
    def hit(self):
        """ダメージを受ける"""
        if self.hurt_timer <= 0:
            self.hp -= 1
            self.hurt_timer = ENEMY_HURT_FRAMES
            if self.hp <= 0:
                self.active = False
                return True  # 撃破された
        return False  # 生存中
        
    def update(self):
        """敵の更新処理"""
        if not self.active:
            return
            
        # 無敵時間の更新
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        
        # 現在地面にいるかチェック
        _, _, on_ground, _ = move_y_with_pushback(self.x, self.y, 1, self.w, self.h)
        self.on_ground = on_ground
        
        # 状態更新（地面検出に基づく）
        if on_ground and self.state == ENEMY_STATE_FALLING:
            self.state = ENEMY_STATE_GROUND  # 着地したら地面移動状態に
            self.vy = 0
        
        # 地面にいない場合のみ重力適用
        if not on_ground:
            self.vy = min(self.vy + self.gravity, self.max_fall)
        else:
            self.vy = 0  # 地面にいる場合は落下速度0
        
        # 地面にいる場合は方向に基づいて移動
        if self.state == ENEMY_STATE_GROUND:
            self.vx = self.direction * self.move_speed
            
            # 方向転換タイマーの更新
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                # 方向を反転
                self.direction = ENEMY_DIRECTION_LEFT if self.direction == ENEMY_DIRECTION_RIGHT else ENEMY_DIRECTION_RIGHT
                # タイマーをリセット
                self.direction_timer = random.randint(60, 180)
        else:
            self.vx = 0  # 落下中は横移動しない
        
        # Y軸移動（落下）
        new_y, hit_top, hit_bottom, remaining_dy = move_y_with_pushback(self.x, self.y, self.vy, self.w, self.h)
        self.y = new_y
        
        # X軸移動（地面にいる場合）
        if self.state == ENEMY_STATE_GROUND:
            new_x, hit_left, hit_right, _ = move_x_with_pushback(self.x, self.y, self.vx, self.w, self.h)
            self.x = new_x
            
            # 壁に当たったら方向転換
            if hit_left or hit_right:
                self.direction = -self.direction
        
        # 画面外に落ちたら非アクティブ化
        if self.y > SCREEN_H + 32:
            self.active = False
    
    def get_center(self):
        """敵の中心座標を取得"""
        return (self.x + self.w // 2, self.y + self.h // 2)
    
    def draw(self):
        """敵の描画"""
        if not self.active:
            return
        
        # 敵のスプライト描画（image0の4,2から1×1タイル分）
        sprite_u = 4 * TILE_SIZE  # 4タイル目 = 32px
        sprite_v = 2 * TILE_SIZE  # 2タイル目 = 16px
        sprite_w = TILE_SIZE      # 1タイル分 = 8px
        sprite_h = TILE_SIZE      # 1タイル分 = 8px
        
        # ダメージ時は点滅（色調変更で対応）
        color_key = 0 if self.hurt_timer % 4 < 2 else None
        
        pyxel.blt(
            self.x, self.y,     # 描画位置
            0,                  # image0を使用
            sprite_u, sprite_v, # スプライト座標
            sprite_w, sprite_h, # スプライトサイズ
            color_key           # 透明色（点滅用）
        )
        
        # HPバー（HP満タンでない場合のみ表示）
        if self.hp < self.max_hp:
            bar_width = (self.w * self.hp) // self.max_hp
            pyxel.rect(self.x, self.y - 6, self.w, 2, 5)  # 背景（灰色）
            pyxel.rect(self.x, self.y - 6, bar_width, 2, 11)  # HP（緑色）

# ===== 剣クラス =====
class Sword:
    def __init__(self):
        # 剣のスプライト情報
        self.u = 16  # スプライトのX座標
        self.v = 24  # スプライトのY座標
        self.w = 16  # スプライトの幅
        self.h = 8   # スプライトの高さ
        
        # 剣の状態
        self.active = False
        self.duration = 0
        self.max_duration = SWORD_ACTIVE_FRAMES  # 攻撃の時間を設定

        # 剣の位置
        self.x = 0
        self.y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.facing_right = True

        # 当たり判定
        self.hit_enemies = set()
        self.check_points = []

    def activate(self, player_x, player_y, player_w, player_h, facing_right):
        """剣を前方に出す"""
        self.active = True
        self.duration = self.max_duration
        self.facing_right = facing_right
        self.hit_enemies.clear()

        # プレイヤーの向きに応じて剣のオフセットを設定
        if facing_right:
            self.offset_x = -self.w  # 左側
        else:
            self.offset_x = player_w  # 右側

        # Y方向のオフセットを設定
        self.offset_y = (player_h - self.h) // 2

        # 初期位置を更新
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y

        # 当たり判定用のチェックポイントを生成
        self._generate_check_points()

    def _generate_check_points(self):
        """攻撃の当たり判定用チェックポイントを生成"""
        self.check_points = []
        
        # 剣のサイズに基づいて複数のチェックポイントを生成
        num_points = 5  # チェックポイントの数
        
        for i in range(num_points):
            # X方向に均等に配置
            x_ratio = i / (num_points - 1)
            point_x = self.x + int(self.w * x_ratio)
            
            # Y方向は上下複数点
            for y_offset in [0, self.h // 2, self.h - 1]:
                point_y = self.y + y_offset
                self.check_points.append((point_x, point_y))

    def update(self, player_x, player_y, enemies):
        """剣の更新"""
        if not self.active:
            return

        self.duration -= 1
        if self.duration <= 0:
            self.active = False
            return

        # プレイヤーの位置に追従して剣の位置を更新
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y

        # チェックポイントも更新
        self._generate_check_points()
        
        # 連続衝突検出方式の当たり判定
        return self._check_continuous_hits(enemies)

    def _check_continuous_hits(self, enemies):
        """連続衝突検出方式の当たり判定"""
        defeated_enemies = []
        
        for enemy in enemies:
            if not enemy.active or enemy in self.hit_enemies:
                continue
            
            # 連続的なチェックポイントで当たり判定
            for point_x, point_y in self.check_points:
                if (point_x >= enemy.x and point_x < enemy.x + enemy.w and
                    point_y >= enemy.y and point_y < enemy.y + enemy.h):
                    
                    # 衝突検出
                    was_defeated = enemy.hit()
                    self.hit_enemies.add(enemy)
                    
                    if was_defeated:
                        defeated_enemies.append(enemy)
                    
                    break  # この敵との判定は終了
        
        return defeated_enemies  # 撃破した敵のリストを返す

    def draw(self):
        if not self.active:
            return
        
        w = -self.w if self.facing_right else self.w

        # 剣の描画
        pyxel.blt(self.x, self.y, 0, self.u, self.v, w, self.h, 0)
        
        # デバッグ: チェックポイントを表示（必要に応じてコメントアウト）
        # for px, py in self.check_points:
        #     pyxel.pset(px, py, 8)  # 赤色で表示

# ===== プレイヤー =====
class Player:
    def __init__(self, x, y):
        # 位置とサイズ
        self.x, self.y = x, y
        self.w, self.h = PLAYER_W, PLAYER_H
        
        # 物理パラメータ
        self.vx = 0
        self.vy = 0
        self.move_speed = MOVE_SPEED
        self.gravity = GRAVITY
        self.max_fall = MAX_FALL
        self.jump_power = JUMP_POWER
        self.on_ground = False
        self.facing_right = False
        
        # HP関連
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.invincible_timer = 0
        self.knockback_vx = 0  # ノックバック用の速度
        self.knockback_vy = 0
        
        # 攻撃関連
        self.sword = Sword()
        self.attack_cooldown = 0

    def take_damage(self, amount, source_x=None, source_y=None):
        """ダメージを受ける統一インターフェース"""
        # 無敵時間中はダメージを受けない
        if self.invincible_timer > 0:
            return False
        
        # HPを減らす
        self.hp = max(0, self.hp - amount)
        
        # 無敵時間を設定
        self.invincible_timer = INVINCIBLE_FRAMES
        
        # ノックバック計算（ダメージ源の座標が指定されている場合）
        if source_x is not None and source_y is not None:
            # プレイヤーの中心座標
            player_center_x = self.x + self.w // 2
            player_center_y = self.y + self.h // 2
            
            # ダメージ源からプレイヤーへの方向を計算
            dx = player_center_x - source_x
            dy = player_center_y - source_y
            
            # 距離を計算（0除算を防ぐ）
            distance = max(1, (dx*dx + dy*dy)**0.5)
            
            # 正規化してノックバック力を適用
            self.knockback_vx = (dx / distance) * KNOCKBACK_POWER
            self.knockback_vy = (dy / distance) * KNOCKBACK_POWER * 0.5  # Y方向は少し弱める
        
        return True  # ダメージを受けた

    def is_dead(self):
        """プレイヤーが死亡しているか？"""
        return self.hp <= 0

    def update(self, enemies):
        """プレイヤーの更新（スコアを返す）"""
        score_gained = 0
        
        # 無敵時間の更新
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # 入力（無敵時間中でも移動可能）
        self.vx = 0
        if pyxel.btn(KEY_LEFT):
            self.vx -= self.move_speed
            self.facing_right = True
        if pyxel.btn(KEY_RIGHT):
            self.vx += self.move_speed
            self.facing_right = False

        # ノックバック効果を速度に加算
        self.vx += self.knockback_vx
        self.vy += self.knockback_vy
        
        # ノックバック減衰
        self.knockback_vx *= 0.8
        self.knockback_vy *= 0.8

        # ジャンプ
        if self.on_ground and pyxel.btnp(KEY_JUMP):
            self.vy = self.jump_power

        # 攻撃
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if pyxel.btnp(KEY_ATTACK) and self.attack_cooldown == 0 and not self.sword.active:
            self.sword.activate(self.x, self.y, self.w, self.h, self.facing_right)
            self.attack_cooldown = SWORD_COOLDOWN

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

        # 画面境界チェック（画面外に出ないように）
        # 左端の制限
        if self.x < 0:
            self.x = 0
        # 右端の制限
        if self.x > SCREEN_W - self.w:
            self.x = SCREEN_W - self.w
        # 上端の制限
        if self.y < 0:
            self.y = 0
            self.vy = 0  # 上に移動する速度をリセット
        
        # 下の落下判定は残す（画面外に落ちた場合はダメージを与える方式に変更）
        if self.y > SCREEN_H:
            # 落下ダメージを与える（HPを減らす）
            self.hp -= 5  # 5ダメージ（調整可能）
            self.respawn()
            if self.hp <= 0:
                self.hp = 0  # HPが0未満にならないように
        
        # 剣の更新（撃破した敵のリストを取得）
        defeated_enemies = self.sword.update(self.x, self.y, enemies)
        if defeated_enemies:
            score_gained += len(defeated_enemies) * SCORE_ENEMY_DEFEAT
        
        # 敵との接触判定（無敵時間でなければダメージ）
        self.check_enemy_collision(enemies)
        
        return score_gained

    def check_enemy_collision(self, enemies):
        """敵との接触判定"""
        for enemy in enemies:
            if not enemy.active:
                continue
            
            # AABB衝突判定
            if (self.x < enemy.x + enemy.w and
                self.x + self.w > enemy.x and
                self.y < enemy.y + enemy.h and
                self.y + self.h > enemy.y):
                
                # 敵の中心座標を計算
                enemy_center_x, enemy_center_y = enemy.get_center()
                
                # ダメージを受ける（敵の中心座標を渡す）
                self.take_damage(1, enemy_center_x, enemy_center_y)

    def respawn(self):
        """リスポーン処理"""
        self.x, self.y = PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y
        self.vx = self.vy = 0
        self.knockback_vx = self.knockback_vy = 0
        self.on_ground = False
        self.hp = self.max_hp  # HP回復
        self.invincible_timer = 0

    def draw(self):
        # 無敵時間中は点滅表示
        should_draw = True
        if self.invincible_timer > 0:
            should_draw = (self.invincible_timer // DAMAGE_FLASH_INTERVAL) % 2 == 0
        
        if should_draw:
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
        pyxel.init(SCREEN_W, SCREEN_H, title="dot buttle", fps=FPS)
        # あなたのリソースファイル名に合わせて変更
        pyxel.load("my_resource.pyxres")

        # ゲーム状態管理
        self.game_state = GAME_STATE_PLAYING
        
        # スコア関連（新規追加）
        self.score = 0
        
        # ゲームの初期化
        self.init_game()

        pyxel.run(self.update, self.draw)
    
    def init_game(self):
        """ゲームの初期化（新規ゲーム・リトライ両方で使用）"""
        self.player = Player(PLAYER_RESPAWN_X, PLAYER_RESPAWN_Y)
        
        # 敵の初期配置（デモ用 - 後でスポーンシステムに置き換え予定）
        self.initial_enemies = [
            (150, ENEMY_SPAWN_HEIGHT),  # 画面上から落下
            (100, ENEMY_SPAWN_HEIGHT),
            (200, ENEMY_SPAWN_HEIGHT)
        ]
        
        # 敵を生成
        self.enemies = self.create_enemies()
        
        # スコアリセット
        self.score = 0
        
        # ゲーム状態をプレイ中に設定
        self.game_state = GAME_STATE_PLAYING
    
    def create_enemies(self):
        """敵を初期配置に基づいて生成"""
        return [Enemy.spawn_from_sky(x) for x, y in self.initial_enemies]

    def update(self):
        # 共通の終了処理
        if pyxel.btnp(KEY_QUIT):
            pyxel.quit()
        
        if self.game_state == GAME_STATE_PLAYING:
            self.update_playing()
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.update_game_over()

    def update_playing(self):
        """プレイ中の更新処理"""
        # 敵の更新
        for enemy in self.enemies:
            enemy.update()
        
        # 非アクティブな敵を削除
        self.enemies = [enemy for enemy in self.enemies if enemy.active]
        
        # プレイヤーの更新（獲得スコアを取得）
        score_gained = self.player.update(self.enemies)
        self.score += score_gained
        
        # プレイヤーが死亡したかチェック
        if self.player.is_dead():
            self.game_state = GAME_STATE_GAME_OVER

        # Rキーでリセット機能
        if pyxel.btnp(KEY_RESET):
            self.init_game()  # ゲーム全体をリセット

    def update_game_over(self):
        """ゲームオーバー画面の更新処理"""
        # SPACEキーでリトライ
        if pyxel.btnp(KEY_RETRY):
            self.init_game()  # ゲームを初期化してリトライ

    def draw(self):
        pyxel.cls(0)
        
        if self.game_state == GAME_STATE_PLAYING:
            self.draw_playing()
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.draw_game_over()

    def draw_playing(self):
        """プレイ中の描画処理"""
        # タイルマップ0を原寸描画
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)
        
        # 敵の描画
        for enemy in self.enemies:
            enemy.draw()
            
        # プレイヤーの描画
        self.player.draw()
        
        # HUD描画
        self.draw_help()
        self.draw_hp_bar()
        self.draw_score()

    def draw_game_over(self):
        """ゲームオーバー画面の描画処理"""
        # ゲームオーバー画面のタイルマップを表示
        # tilemap2, image1の(0,0)から32x32タイル分を画面全体に描画
        tile_w_px = GAMEOVER_TILE_W * TILE_SIZE  # タイル幅をピクセル単位に変換
        tile_h_px = GAMEOVER_TILE_H * TILE_SIZE  # タイル高さをピクセル単位に変換
        
        pyxel.bltm(
            0, 0,  # 描画先座標 (画面左上)
            GAMEOVER_TILEMAP,  # タイルマップ番号 (2)
            GAMEOVER_TILE_X * TILE_SIZE,  # ソースX座標（ピクセル単位）
            GAMEOVER_TILE_Y * TILE_SIZE,  # ソースY座標（ピクセル単位）
            tile_w_px,  # 描画幅（ピクセル単位）
            tile_h_px,  # 描画高さ（ピクセル単位）
            GAMEOVER_IMAGE  # 使用する画像番号 (1)
        )
        
        # ゲームオーバーテキストとリトライ指示
        text_x, text_y = HUD_POS["GAMEOVER_TEXT"]
        
        # テキストを中央揃えで表示
        game_over_text = "GAME OVER"
        score_text = f"Score: {self.score}"
        retry_text = f"Press {KEY_LABELS['RETRY']} to Retry"
        quit_text = f"Press {KEY_LABELS['QUIT']} to Quit"
        
        # テキスト幅を計算して中央揃え
        game_over_w = len(game_over_text) * 4  # pyxelの文字幅は約4px
        score_w = len(score_text) * 4
        retry_w = len(retry_text) * 4
        quit_w = len(quit_text) * 4
        
        pyxel.text(text_x - game_over_w // 2, text_y - 30, game_over_text, 8)  # 赤色
        pyxel.text(text_x - score_w // 2, text_y - 10, score_text, 7)  # 白色
        pyxel.text(text_x - retry_w // 2, text_y + 10, retry_text, 7)  # 白色
        pyxel.text(text_x - quit_w // 2, text_y + 20, quit_text, 7)  # 白色

    def draw_help(self):
        """操作ヘルプの描画"""
        x, y = HUD_POS["HELP"]
        t = f"{KEY_LABELS['ATK']}:Attack  {KEY_LABELS['JUMP']}:Jump  {KEY_LABELS['RST']}:Reset  {KEY_LABELS['QUIT']}:Quit"
        pyxel.text(x, y, t, 7)

    def draw_hp_bar(self):
        """HPバーの描画"""
        x, y = HUD_POS["HP"]
        
        # HPテキスト
        pyxel.text(x, y, f"HP: {self.player.hp}/{self.player.max_hp}", 7)
        
        # HPバー背景（灰色）
        bar_x = x + 40
        bar_width = 60
        bar_height = 6
        pyxel.rect(bar_x, y, bar_width, bar_height, 5)  # 灰色
        
        # HPバー（現在HP分だけ緑色）
        if self.player.hp > 0:
            current_bar_width = int((self.player.hp / self.player.max_hp) * bar_width)
            color = 11 if self.player.hp > 2 else 8  # HP少ないと赤色
            pyxel.rect(bar_x, y, current_bar_width, bar_height, color)
        
        # 無敵時間表示（デバッグ用）
        if self.player.invincible_timer > 0:
            pyxel.text(x + 110, y, f"Inv:{self.player.invincible_timer}", 10)

    def draw_score(self):
        """スコア表示"""
        x, y = HUD_POS["SCORE"]
        pyxel.text(x, y, f"Score: {self.score}", 7)

App()