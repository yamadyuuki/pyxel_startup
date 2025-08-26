import pyxel
import math
from constants import *

class BulletBase:
    def __init__(self, x, y, vx, vy, speed=1.0, radius=1, color=10):
        self.x = x
        self.y = y
        # 速度ベクトル（1フレーム当たりの移動量）
        self.vx = vx * speed
        self.vy = vy * speed
        self.radius = radius
        self.color = color
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # 画面外で消す（少しマージン）
        if (self.x < -4 or self.x > SCREEN_WIDTH + 4 or
            self.y < -4 or self.y > SCREEN_HEIGHT + 4):
            self.alive = False

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), self.radius, self.color)

    # 次フレーム位置（当たり判定の"連続判定"で使いやすい）
    def next_pos(self):
        return (self.x + self.vx, self.y + self.vy)


# 2) 弾パターンの基底：将来、他パターンも追加しやすい形
class BulletPattern:
    def fire(self, x, y):
        """(x,y)から弾リストを生成して返す。"""
        raise NotImplementedError


# 3) 円状一斉発射（BulletML風の基本）
class CircularBurstPattern(BulletPattern):
    def __init__(self, count=16, speed=1.2, start_deg=90, spread_deg=360, spin_deg=0,
                 radius=1, color=10):
        """
        count      : 一度に出す弾の数
        speed      : 弾速（ピクセル/フレーム）
        start_deg  : 発射の開始角度（右=0°, 下=90°, 左=180°, 上=270°想定）
        spread_deg : 何度の扇形に分配するか（360で全周）
        spin_deg   : 呼ぶたびにstart_degへ加算する角度（回転弾幕）
        """
        self.count = count
        self.speed = speed
        self.start_deg = start_deg
        self.spread_deg = spread_deg
        self.spin_deg = spin_deg
        self.radius = radius
        self.color = color

    def fire(self, x, y):
        bullets = []
        if self.count <= 0:
            return bullets
        step = self.spread_deg / self.count  # 1発ごとの角度差
        for i in range(self.count):
            ang_deg = self.start_deg + i * step
            ang = math.radians(ang_deg)
            vx, vy = math.cos(ang), math.sin(ang)
            bullets.append(
                BulletBase(x, y, vx, vy, speed=self.speed,
                           radius=self.radius, color=self.color)
            )
        # 次回の発射時に回転させたい場合
        self.start_deg = (self.start_deg + self.spin_deg) % 360
        return bullets


class AimedShot(BulletPattern):
    def __init__(self, speed=1.2, radius=1, color=10):
        self.speed = speed
        self.radius = radius
        self.color = color

    def fire(self, x, y, target_x=None, target_y=None):
        # targetが無い時は真下に撃つ（保険）
        if target_x is None or target_y is None:
            vx, vy = 0, 1
        else:
            dx, dy = target_x - x, target_y - y
            dist = math.hypot(dx, dy) or 1.0
            vx, vy = dx / dist, dy / dist

        return [BulletBase(x, y, vx, vy, speed=self.speed,
                           radius=self.radius, color=self.color)]
    
class SplittingBulletPattern(BulletPattern):
    def __init__(self, speed=0.8, split_count=2, split_time=30, max_splits=2, 
                 spread_deg=45, radius=1, color=10):
        """
        speed       : 弾の速度（ピクセル/フレーム）
        split_count : 分裂時に生成される弾の数
        split_time  : 弾が分裂するまでの時間（フレーム数）
        max_splits  : 最大分裂回数（防弾幕が無限に増えるのを防ぐ）
        spread_deg  : 分裂時の角度の広がり
        radius      : 弾の半径
        color       : 弾の色
        """
        self.speed = speed
        self.split_count = split_count
        self.split_time = split_time
        self.max_splits = max_splits
        self.spread_deg = spread_deg
        self.radius = radius
        self.color = color

    def fire(self, x, y, target_x=None, target_y=None):
        # 初期弾は真下または狙い撃ちの1発
        if target_x is None or target_y is None:
            vx, vy = 0, 1  # 真下方向
        else:
            dx, dy = target_x - x, target_y - y
            dist = math.hypot(dx, dy) or 1.0
            vx, vy = dx / dist, dy / dist
        
        # SplittingBulletインスタンスを作成して返す
        return [SplittingBullet(x, y, vx, vy, speed=self.speed,
                               split_count=self.split_count,
                               split_time=self.split_time,
                               max_splits=self.max_splits,
                               spread_deg=self.spread_deg,
                               radius=self.radius, color=self.color)]
    
class SplittingBullet(BulletBase):
    def __init__(self, x, y, vx, vy, speed=0.8, split_count=2, split_time=30, 
                 max_splits=2, spread_deg=45, radius=1, color=10, splits_left=None):
        super().__init__(x, y, vx, vy, speed, radius, color)
        
        # 分裂関連のパラメータ
        self.split_count = split_count
        self.split_time = split_time
        self.timer = 0
        self.splits_left = max_splits if splits_left is None else splits_left
        self.spread_deg = spread_deg
        self.max_splits = max_splits
        self.children = []  # 分裂して生成された子弾を管理
        
        # 速度を保存（分裂時に使用するため）
        self.speed = speed

    def update(self):
        # 基本的な移動処理を親クラスから呼び出し
        super().update()
        
        # 分裂タイマーを更新
        self.timer += 1
        
        # 分裂処理
        if self.alive and self.splits_left > 0 and self.timer >= self.split_time:
            self.split()
            self.splits_left -= 1  # 分裂回数を減らす
            self.timer = 0  # タイマーリセット
        
        # 子弾の更新
        for bullet in self.children[:]:
            bullet.update()
            if not bullet.alive:
                self.children.remove(bullet)

    def split(self):
        # 現在の進行方向を角度に変換
        current_angle = math.degrees(math.atan2(self.vy, self.vx))
        
        # 弾の分裂角度を計算
        if self.split_count <= 1:
            return  # 分裂数が1以下の場合は何もしない
            
        step = self.spread_deg / (self.split_count - 1)
        start_angle = current_angle - self.spread_deg / 2
        
        for i in range(self.split_count):
            # 新しい角度を計算
            new_angle = start_angle + i * step
            new_angle_rad = math.radians(new_angle)
            
            # 新しい速度ベクトルを計算
            new_vx = math.cos(new_angle_rad)
            new_vy = math.sin(new_angle_rad)
            
            # 新しい分裂弾を作成（残り分裂回数を減らす）
            new_bullet = SplittingBullet(
                self.x, self.y, new_vx, new_vy, 
                speed=self.speed,
                split_count=self.split_count,
                split_time=self.split_time,
                max_splits=self.max_splits,
                spread_deg=self.spread_deg,
                radius=self.radius, 
                color=self.color,
                splits_left=self.splits_left - 1
            )
            
            self.children.append(new_bullet)
        
        # 元の弾は分裂後に消滅させる（オプション）
        # self.alive = False

    def draw(self):
        # 自分自身を描画
        if self.alive:
            super().draw()
        
        # 子弾も描画
        for bullet in self.children:
            bullet.draw()