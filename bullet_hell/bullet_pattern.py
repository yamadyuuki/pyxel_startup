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
        pyxel.circ(self.x, self.y, self.radius, self.color)

    # 次フレーム位置（当たり判定の“連続判定”で使いやすい）
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