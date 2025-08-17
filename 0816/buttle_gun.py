# buttle_gun.py
import pyxel
from buttle_constants import TILE_SIZE

class Bullet:
    def __init__(self, x, y, direction):
        # 弾の位置と大きさ
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        
        # 物理パラメータ
        self.speed = 1.5
        self.direction = direction  # 1:右向き, -1:左向き
        self.active = True
        
        # スプライト情報
        self.sprite_u = 8
        self.sprite_v = 40
        
    def update(self):
        """弾の更新処理"""
        if not self.active:
            return
        
        # 弾の移動
        self.x += self.speed * self.direction
        
        # 画面外に出たら非アクティブに
        if self.x < -self.w or self.x > pyxel.width:
            self.active = False
    
    def draw(self):
        """弾の描画"""
        if not self.active:
            return
        
        # 弾のスプライト描画
        pyxel.blt(
            self.x, self.y,     # 描画位置
            0,                  # image0を使用
            self.sprite_u, self.sprite_v, # スプライト座標
            self.w, self.h,     # スプライトサイズ
            0                   # 透明色
        )


class Gun:
    def __init__(self):
        # 銃のスプライト情報
        self.u = 0
        self.v = 32
        self.w = 16
        self.h = 8
        
        # 銃の状態
        self.active = False
        self.cooldown = 0
        self.max_cooldown = 30  # 発射クールダウン
        
        # 銃の位置
        self.x = 0
        self.y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.facing_right = False
        
        # 弾のリスト
        self.bullets = []
    
    def activate(self, player_x, player_y, player_w, player_h, facing_right):
        """銃を構える/発射する"""
        self.active = True
        self.facing_right = facing_right
        
        # プレイヤーの向きに応じて銃のオフセットを設定
        if facing_right:
            self.offset_x = player_w  # 右側
        else:
            self.offset_x = -self.w  # 左側
        
        # Y方向のオフセットを設定（プレイヤーの中央あたりに配置）
        self.offset_y = (player_h - self.h) // 2
        
        # 初期位置を更新
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y
        
        # 発射可能な場合は弾を発射
        if self.cooldown <= 0:
            self._fire_bullet()
            self.cooldown = self.max_cooldown
    
    def _fire_bullet(self):
        """弾を発射する"""
        # 銃の向きに応じて弾の初期位置と方向を設定
        if self.facing_right:
            bullet_x = self.x + self.w   # 銃の先端
            direction = 1       # 右向き
        else:
            bullet_x = self.x - self.h
            direction = -1      # 左向き
        
        # 弾を生成してリストに追加
        new_bullet = Bullet(bullet_x, self.y, direction)
        self.bullets.append(new_bullet)
    
    def update(self, player_x, player_y, enemies=None):
        """銃の更新処理"""
        # クールダウンの更新
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # 銃の位置更新（プレイヤーに追従）
        self.x = player_x + self.offset_x
        self.y = player_y + self.offset_y
        
        # 弾の更新
        for bullet in self.bullets:
            bullet.update()
        
        # 非アクティブな弾を削除
        self.bullets = [bullet for bullet in self.bullets if bullet.active]
        
        # 敵との当たり判定（敵リストが渡された場合）
        defeated_enemies = []
        if enemies:
            defeated_enemies = self._check_bullet_hits(enemies)
        
        return defeated_enemies
    
    def _check_bullet_hits(self, enemies):
        """弾と敵の当たり判定"""
        defeated_enemies = []
        
        for bullet in self.bullets:
            if not bullet.active:
                continue
                
            for enemy in enemies:
                if not enemy.active:
                    continue
                
                # 弾と敵のAABB衝突判定
                if (bullet.x < enemy.x + enemy.w and
                    bullet.x + bullet.w > enemy.x and
                    bullet.y < enemy.y + enemy.h and
                    bullet.y + bullet.h > enemy.y):
                    
                    # 敵にダメージを与える
                    was_defeated = enemy.hit()
                    
                    # 弾を非アクティブに
                    bullet.active = False
                    
                    if was_defeated:
                        defeated_enemies.append(enemy)
                    
                    break  # この弾の判定は終了
        
        return defeated_enemies
    
    def draw(self):
        """銃と弾の描画"""
        # 銃の描画
        if self.active:
            w = self.w
            if not self.facing_right:
                w = -self.w  # 左向きの場合は反転

            pyxel.blt(self.x, self.y, 0, self.u, self.v, w, self.h, 0)

            # デバッグ: 銃の位置を可視化
            pyxel.pset(self.x, self.y, 8)  # 赤色で銃の左上を表示
            if self.facing_right:
                pyxel.pset(self.x + self.w, self.y, 11)  # 緑色で銃の右端を表示
            else:
                pyxel.pset(self.x, self.y, 11)  # 緑色で銃の左端を表示        


        # 弾の描画
        for bullet in self.bullets:
            bullet.draw()