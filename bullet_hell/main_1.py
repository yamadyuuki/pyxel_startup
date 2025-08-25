import math
import pyxel
from constants import *

def rects_intersect(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and bx < ax + aw and
            ay < by + bh and by < ay + ah)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="bullet hell", fps=60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")  # ← これを追加（spriteを使うなら必須）        

        self.scene = START_SCENE
        self.selected_level = None
        self.game = None  # ← 最初はNoneにする
        self.menu_idx = 0

        pyxel.run(self.update, self.draw)


    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R):
            if self.scene == PLAY_SCENE:
                self.scene = START_SCENE
                pyxel.play(0, 0)

        if self.scene == START_SCENE:
            self.update_start_scene()
        elif self.scene == PLAY_SCENE and self.game:      # ← 追加
            self.game.update()                            # ← 追加


    def draw(self):
        if self.scene == START_SCENE:
            self.draw_start_scene()
        elif self.scene == PLAY_SCENE:
            self.game.draw()
        elif self.scene == END_SCENE:
            self.draw_end_scene()
            
    #---update---
    def update_start_scene(self):
        # ---- キーボード操作（上下＋決定）----
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_idx = (self.menu_idx - 1) % 3
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_idx = (self.menu_idx + 1) % 3
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            level_name = ("EASY", "NORMAL", "HARD")[self.menu_idx]
            self.start_game(level_name)
            pyxel.play(0, 0)

        # ---- マウスクリック操作 ----
        if pyxel.btnp(0):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            # クリック位置から選択＆即開始
            if 100 <= mx <= 160 and 80 <= my <= 90:
                self.menu_idx = 0
                self.start_game("EASY")
            elif 100 <= mx <= 160 and 100 <= my <= 110:
                self.menu_idx = 1
                self.start_game("NORMAL")
            elif 100 <= mx <= 160 and 120 <= my <= 130:
                self.menu_idx = 2
                self.start_game("HARD")


    def start_game(self, level_name):
        self.selected_level = LEVELS[level_name]
        self.game = Game(self.selected_level)
        self.scene = PLAY_SCENE


#---draw---
    def draw_start_scene(self):
        pyxel.cls(5)
        pyxel.text(96, 50, "SELECT LEVEL", 7)

        items = [("EASY", 11), ("NORMAL", 10), ("HARD", 8)]
        ys = [80, 100, 120]

        for i, ((label, col), y) in enumerate(zip(items, ys)):
            # 選択中行にカーソル（>）表示＆うっすら背景
            if i == self.menu_idx:
                pyxel.rect(92, y - 2, 80, 12, 1)     # 薄背景
                pyxel.text(92, y, ">", 7)            # カーソル
            pyxel.text(100, y, label, col)

    def draw_end_scene(self):
        pyxel.cls(5)
        pyxel.text(100, 100, "END", 7)

class Game:
    def __init__(self, level_config):
        self.level = level_config
        self.player = Player()
        self.enemies = []
        self.score = 0
        
        # 初期敵を生成
        self.spawn_initial_enemies()

    def spawn_initial_enemies(self):
        # 画面幅に合わせて均等に配置
        enemy_width = 8  # 敵のスプライト幅
        total_width = enemy_width * 10  # 敵10体の合計幅
        spacing = (SCREEN_WIDTH - total_width) / 11  # 均等な間隔
        
        for i in range(10):
            # レベル設定を渡して敵を生成
            enemy = Enemy(bullet_speed=self.level.get("ENEMY_BULLET_SPEED", 0.2))
            
            # 目標位置を計算: 左端から間隔+敵の幅を考慮
            target_x = spacing + i * (enemy_width + spacing)
            target_y = TARGET_Y  # 上部に配置
            
            # 敵の初期位置を画面下に設定（少しずつ時間差をつける）
            enemy.x = target_x
            enemy.y = SCREEN_HEIGHT + 10 + i * 5  # 少しずつずらす
            
            # 目標位置を設定
            enemy.set_target(target_x, target_y)
            self.enemies.append(enemy)
    
    def update(self):
        self.player.update()

        for enemy in self.enemies[:]:
            if enemy.alive:
                enemy.update()
            else:
                self.enemies.remove(enemy)
                self.score += 100

        if len(self.enemies) == 0:
            self.spawn_initial_enemies()

        # プレイヤーの弾と敵の当たり判定
        self.check_bullet_enemy_collisions()
        
        # 敵の弾とプレイヤーの当たり判定（新規追加）
        self.check_enemy_bullet_player_collisions()

    # 新しい当たり判定メソッド
    def check_enemy_bullet_player_collisions(self):
        # プレイヤーの当たり判定サイズ
        player_size = 7  # 8x8スプライトに対して少し小さめの当たり判定
        
        # 各敵の弾とプレイヤーの当たり判定
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if not bullet.alive:
                    continue
                    
                # 弾の現在位置を保存
                original_x = bullet.x
                original_y = bullet.y

                target_x, target_y = bullet.next_pos()   # ← BulletBaseに用意
                
                
                # 弾のサイズ
                bullet_size = 1
                
                # 衝突フラグ
                collision = False
                
                # steps（分割数）は移動量からざっくり決める
                move_len = abs(bullet.vx) + abs(bullet.vy)
                steps = max(int(move_len), 1)
                
                # 1ステップあたりの移動量
                step_x = (target_x - original_x) / steps
                step_y = (target_y - original_y) / steps
                
                # 各ステップで衝突判定
                for step in range(steps + 1):
                    # 現在のステップでの位置
                    test_x = original_x + step * step_x
                    test_y = original_y + step * step_y
                    
                    # プレイヤーとの衝突チェック
                    if rects_intersect(
                        test_x - bullet_size, test_y - bullet_size, 
                        bullet_size * 2, bullet_size * 2,
                        self.player.x + 0.5, self.player.y + 0.5, 
                        player_size, player_size
                    ):
                        collision = True
                        break
                
                # 衝突処理
                if collision:
                    # プレイヤーにダメージ
                    self.player.take_damage(1)
                    
                    # 弾を削除
                    enemy.bullets.remove(bullet)
                else:
                    # 衝突しなかった場合、弾を目標位置まで移動
                    bullet.x = target_x
                    bullet.y = target_y


        #連続衝突判定バージョン
    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets[:]:
            if not bullet.alive:
                self.player.bullets.remove(bullet)
                continue
                
            # 弾の現在位置を保存
            original_x = bullet.x
            original_y = bullet.y
            
            # 目標位置（次のフレームでの位置）
            # 通常、弾はY軸方向にのみ動くが、将来的に斜めに動く可能性も考慮
            target_x = original_x  # 現在はX方向に動かないため同じ値
            target_y = original_y - bullet.speed  # 上に移動するので減算
            
            # 弾のサイズ
            bullet_size = 1
            
            # 衝突フラグ
            collision = False
            hit_enemy = None
            
            # 移動距離を分割して処理
            steps = max(abs(bullet.speed), 1)  # 最低1ステップ
            
            # 1ステップあたりの移動量
            step_x = (target_x - original_x) / steps
            step_y = (target_y - original_y) / steps
            
            # 各ステップで衝突判定
            for step in range(steps + 1):
                # 現在のステップでの位置
                test_x = original_x + step * step_x
                test_y = original_y + step * step_y
                
                # 各敵との衝突チェック
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                        
                    # 矩形同士の衝突判定
                    if rects_intersect(
                        test_x - bullet_size, test_y - bullet_size, 
                        bullet_size * 2, bullet_size * 2,
                        enemy.x, enemy.y, 8, 8
                    ):
                        # 衝突した敵を記録
                        hit_enemy = enemy
                        collision = True
                        #print(f"Bullet at ({test_x}, {test_y}) hit enemy at ({enemy.x}, {enemy.y})")
                        break
                        
                # 衝突したらループを抜ける
                if collision:
                    break
                    
            # 衝突処理
            if collision and hit_enemy:
                # 敵にダメージ
                hit_enemy.take_damage(1)
                
                # 効果音
                pyxel.play(1, 2)
                
                # 弾を削除
                self.player.bullets.remove(bullet)
            else:
                # 衝突しなかった場合、弾を目標位置まで移動
                bullet.x = target_x
                bullet.y = target_y
                pass

                     
    def draw(self):
        pyxel.cls(0)
        
        # スコアとレベル表示
        pyxel.text(10, 10, f"SCORE: {self.score}", 7)
        pyxel.text(10, 20, f"LEVEL: {self.level['ENEMY_BULLET_SPEED']}", 7)

        # プレイヤーのHP表示を追加
        pyxel.text(10, 30, f"HP: {self.player.hp}", 11)
        
        # HPバーの表示（オプション）
        bar_width = (self.player.hp / PLAYER_HP) * 50  # 最大HPが10の場合
        pyxel.rect(40, 30, int(bar_width), 4, 11)
        pyxel.rectb(40, 30, 50, 4, 7)

        # プレイヤーを描画
        self.player.draw()

        # リセット方法の案内表示
        pyxel.text(SCREEN_WIDTH - 115, 10, "R: BACK TO MENU", 8)        

        # すべての敵を描画
        for enemy in self.enemies:
            enemy.draw()

class SpawnController:
    def __init__(self, x, y, interval):
        self.x = x
        self.y = y
        self.interval = interval
    def update(self):
        pass
    def draw(self):
        pass



class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 16
        self.speed = 1  # 少し上げてもOK
        self.bullets = []
        self.cooldown = 0  # Cooldownの初期値
        self.hp = PLAYER_HP
        self.invincible_timer = 0
        self.hit_effect = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = 0

        # ヒット時の効果音
        pyxel.play(1, 1)
        
        # ヒットエフェクト用（オプション）
        self.hit_effect = 20
        
        # 無敵時間を設定（オプション）
        self.invincible_timer = 0  # いったん0秒（0fps）

    def update(self):
        dx = (1 if pyxel.btn(pyxel.KEY_RIGHT) else 0) - (1 if pyxel.btn(pyxel.KEY_LEFT) else 0)
        dy = (1 if pyxel.btn(pyxel.KEY_DOWN)  else 0) - (1 if pyxel.btn(pyxel.KEY_UP)   else 0)

        # 正規化（斜めでも等速）
        if dx or dy:
            mag = (dx*dx + dy*dy) ** 0.5
            self.x += (dx / mag) * self.speed
            self.y += (dy / mag) * self.speed

        # 画面内に収める（8x8）
        self.x = max(0, min(self.x, SCREEN_WIDTH - 8))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - 8))

        if self.cooldown > 0:
            self.cooldown -= 1

        if pyxel.btn(pyxel.KEY_SPACE) and self.cooldown == 0:
            self.bullets.append(Player_Bullet(self.x, self.y))
            self.cooldown = COOL_DOWN

        # 弾の更新（画面外に出た弾のみ削除）
        # 敵との衝突チェックはGameクラスで行うため、ここでは画面外チェックのみ
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.alive:
                self.bullets.remove(bullet)

        # 無敵時間の更新（オプション）
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
        # ヒットエフェクトの更新（オプション）
        if self.hit_effect > 0:
            self.hit_effect -= 1

    def draw(self):
       # 無敵時間中は点滅表示（オプション）
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            # 点滅中は描画しない
            pass
        else:
            # 通常描画
            pyxel.blt(int(self.x), int(self.y), 0, 8, 0, 8, 8, 0)

        # # プレイヤーのHP表示を追加
        # pyxel.text(10, 30, f"HP: {self.player.hp}", 11)
        
        # # HPバーの表示（オプション）
        # bar_width = (self.player.hp / PLAYER_HP) * 50  # 最大HPが10の場合
        # pyxel.rect(40, 30, int(bar_width), 4, 11)
        # pyxel.rectb(40, 30, 50, 4, 7)

        # ヒットエフェクト（オプション）
        if self.hit_effect > 0:
            pyxel.circb(int(self.x) + 4, int(self.y) + 4, self.hit_effect // 2, 8)
        
        # 弾を描画
        for bullet in self.bullets:
            bullet.draw()

class Enemy:
    def __init__(self, bullet_speed=0.2):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT + 10
        self.target_x = SCREEN_WIDTH // 2
        self.target_y = 20
        self.move_speed = 1
        self.is_moving = True
        self.hp = ENEMY_HP
        self.alive = True
        self.bullets = []
        self.shoot_timer = 0
        self.bullet_speed = bullet_speed  # 弾の速度を設定        

        self.pattern = CircularBurstPattern(
            count=24,               # 一度に24方向
            speed=bullet_speed,   # 速さ（好みで）
            start_deg=90,           # 画面座標系で“下”が+Yなので90°が下向き
            spread_deg=360,         # 全周
            spin_deg=6,             # 発射のたびに6°回転 → 渦巻き弾幕になる
            radius=1,
            color=10
        )

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y
        self.is_moving = True

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
    
    def update(self):
        #目標位置に向かって移動
        if self.is_moving:
            dx = self.target_x -self.x
            dy = self.target_y -self.y

            if abs(dx) < self.move_speed and abs(dy) < self.move_speed:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
            else:
                #方向ベクトルを正規化して移動
                distance = (dx**2 + dy**2)**0.5
                self.x += (dx / distance)  * self.move_speed
                self.y += (dy / distance)  * self.move_speed
        
        self.shoot_timer += 1

        if self.shoot_timer >= SHOOT_INTERVAL:
            self.shoot()
            self.shoot_timer = 0

        # 弾の更新
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.alive:
                self.bullets.remove(bullet)
    
    def shoot(self):
        # これまで1発だけ落とす → 円状に複数発
        self.bullets += self.pattern.fire(self.x + 4, self.y + 8)

    def draw(self):
        if self.alive:
            pyxel.blt(int(self.x), int(self.y), 0, 0, 8, 8, 8, 0)

            #HPバーの表示
            bar_width = (self.hp / ENEMY_HP) * 8
            pyxel.rect(int(self.x), int(self.y) - 2, int(bar_width), 1, 8)

            for bullet in self.bullets:
                bullet.draw()

class Player_Bullet:
    def __init__(self, x, y):
        self.x = x + 4
        self.y = y
        self.speed = 3
        self.alive = True

    def update(self):
        if self.y < -2:
            self.alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, 1, 8) # Draw a small red circle for the bullet

class Enemy_Bullet:
    def __init__(self, x, y, speed=0.2):
        self.x = x + 4
        self.y = y
        self.speed = speed
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT + 2:
            self.alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, 1, 10)

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


App()

