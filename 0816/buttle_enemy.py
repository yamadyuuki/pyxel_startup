import pyxel
import random
from buttle_constants import (
    # 画面関連の定数
    SCREEN_W, SCREEN_H, TILE_SIZE,
    
    # 敵関連の定数
    ENEMY_W, ENEMY_H, ENEMY_HP, ENEMY_HURT_FRAMES,
    ENEMY_GRAVITY, ENEMY_MAX_FALL, ENEMY_MOVE_SPEED, ENEMY_SPAWN_HEIGHT,
    ENEMY_STATE_FALLING, ENEMY_STATE_GROUND, ENEMY_DIRECTION_LEFT, ENEMY_DIRECTION_RIGHT,
    ENEMY_DETECTION_RANGE, ENEMY_ALERT_SPEED_MULTIPLIER,
)

class Enemy:
    def __init__(self, x, y):
        # 位置とサイズ
        self.x = x
        self.y = y
        self.w = ENEMY_W
        self.h = ENEMY_H
        
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

        self.alert_state = False      # 警戒状態か？
        self.pause_timer = 0         # 停止タイマー
        self.base_speed = ENEMY_MOVE_SPEED  # 基本速度を保存
        
        # 衝突関数を保持するための属性（後でセットされる）
        self.collision_functions = None

    def detect_player(self, player_x, player_y):
        """プレイヤーを感知する"""
        distance = abs(self.x - player_x)
        return distance <= ENEMY_DETECTION_RANGE            

    @classmethod
    def spawn_at_position(cls, x, y):
        """画面上から落下する敵を生成"""
        return cls(x, y)
    
    def hit(self):
        """ダメージを受ける"""
        if self.hurt_timer <= 0:
            self.hp -= 1
            self.hurt_timer = ENEMY_HURT_FRAMES
            if self.hp <= 0:
                self.active = False
                return True  # 撃破された
        return False  # 生存中
        
    def update(self, player_x=None, player_y=None):
        """敵の更新処理"""
        if not self.active:
            return
            
        # 無敵時間の更新
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        
        # 衝突関数が設定されていない場合は何もしない
        if self.collision_functions is None:
            return
            
        move_y_with_pushback, move_x_with_pushback, is_block_at = self.collision_functions
        
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
        
        # 地面移動処理を関数化
        if self.state == ENEMY_STATE_GROUND:
            self.update_ground_movement(player_x, player_y, is_block_at)
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
    
    def check_cliff(self, is_block_at):
        """崖っぷちをチェック（地面がない場合はTrue）"""
        # 進行方向の足元をチェック
        if self.direction == ENEMY_DIRECTION_RIGHT:
            check_x = self.x + self.w + 4  # 少し先をチェック
        else:
            check_x = self.x - 4
        
        check_y = self.y + self.h + 4  # 足元より少し下
        
        # 地面がない場合はTrue（崖っぷち）
        return not is_block_at(check_x, check_y)

    def update_ground_movement(self, player_x=None, player_y=None, is_block_at=None):
        """地面移動中の挙動（プレイヤー感知対応）"""
        # 地面にいる場合のみ移動処理を実行
        if not self.on_ground:
            self.vx = 0
            return
        
        # プレイヤー感知（新規追加）
        if player_x is not None and player_y is not None:
            self.alert_state = self.detect_player(player_x, player_y)
        
        # 停止タイマーの処理（新規追加）
        if self.pause_timer > 0:
            self.pause_timer -= 1
            self.vx = 0  # 停止中
            return
        
        # is_block_at が None の場合はエラー回避
        if is_block_at is None:
            self.vx = 0
            return
        
        # 崖っぷち検出
        if self.check_cliff(is_block_at):
            self.direction *= -1
            self.direction_timer = random.randint(60, 180)
            return
        
        # 方向転換タイマーの更新
        self.direction_timer -= 1
        if self.direction_timer <= 0:
            self.direction *= -1
            self.direction_timer = random.randint(60, 180)
            
            # たまに停止する（新規追加）
            if not self.alert_state and random.random() < 0.3:  # 30%の確率
                self.pause_timer = random.randint(30, 90)
        
        # 移動速度を設定（警戒状態で速度変化）
        current_speed = self.base_speed
        if self.alert_state:
            current_speed *= ENEMY_ALERT_SPEED_MULTIPLIER
        
        self.vx = self.direction * current_speed

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