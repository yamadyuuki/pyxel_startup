import math
import pyxel
from constants import *
from bullet_pattern import *


def rects_intersect(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and bx < ax + aw and
            ay < by + bh and by < ay + ah)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="bullet hell", fps=60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")

        self.scene = START_SCENE
        self.selected_level = None
        self.selected_bullet_pattern = None  # 初期化を追加
        self.game = None
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
        elif self.scene == PLAY_SCENE and self.game:
            self.game.update()

    def draw(self):
        if self.scene == START_SCENE:
            self.draw_start_scene()
        elif self.scene == PLAY_SCENE and self.game:
            self.game.draw()
        elif self.scene == END_SCENE:
            self.draw_end_scene()
            
    def update_start_scene(self):
        # キーボード操作（上下＋決定）
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_idx = (self.menu_idx - 1) % 6
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_idx = (self.menu_idx + 1) % 6
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            if self.menu_idx < 3:  # 難易度選択
                level_name = ("EASY", "NORMAL", "HARD")[self.menu_idx]
                self.selected_level = LEVELS[level_name]
            else:  # 弾パターン選択
                self.selected_bullet_pattern = ("circular", "aimed", "splitting")[self.menu_idx - 3]
            
            # 両方選択されたらゲーム開始
            if self.selected_level is not None and self.selected_bullet_pattern is not None:
                self.start_game(self.selected_level, self.selected_bullet_pattern)
            pyxel.play(0, 0)

        # マウスクリック操作（簡略化）
        if pyxel.btnp(0):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if 100 <= mx <= 160:
                if 50 <= my <= 60:
                    self.selected_level = LEVELS["EASY"]
                elif 70 <= my <= 80:
                    self.selected_level = LEVELS["NORMAL"]
                elif 90 <= my <= 100:
                    self.selected_level = LEVELS["HARD"]
                elif 140 <= my <= 150:
                    self.selected_bullet_pattern = "circular"
                elif 160 <= my <= 170:
                    self.selected_bullet_pattern = "aimed"
                elif 180 <= my <= 190:
                    self.selected_bullet_pattern = "splitting"
                
                # 両方選択されたらゲーム開始
                if self.selected_level is not None and self.selected_bullet_pattern is not None:
                    self.start_game(self.selected_level, self.selected_bullet_pattern)

    def start_game(self, level_config, bullet_pattern):
        self.game = Game(level_config, bullet_pattern)
        self.scene = PLAY_SCENE

    def draw_start_scene(self):
        pyxel.cls(5)
        pyxel.text(96, 30, "SELECT LEVEL", 7)

        # 難易度選択
        level_items = [("EASY", 11), ("NORMAL", 10), ("HARD", 8)]
        level_ys = [50, 70, 90]

        for i, ((label, col), y) in enumerate(zip(level_items, level_ys)):
            if i == self.menu_idx:
                pyxel.rect(92, y - 2, 80, 12, 1)
                pyxel.text(92, y, ">", 7)
            # 選択済みの場合は色を変更
            if self.selected_level == LEVELS[("EASY", "NORMAL", "HARD")[i]]:
                pyxel.text(100, y, label, 14)  # 選択済みは別の色
            else:
                pyxel.text(100, y, label, col)
        
        # 弾パターン選択
        pyxel.text(96, 120, "SELECT BULLET", 7)
        
        bullet_items = [("CIRCULAR", 11), ("AIMED", 10), ("SPLITTING", 14)]
        bullet_ys = [140, 160, 180]
        
        for i, ((label, col), y) in enumerate(zip(bullet_items, bullet_ys)):
            if i + 3 == self.menu_idx:
                pyxel.rect(92, y - 2, 80, 12, 1)
                pyxel.text(92, y, ">", 7)
            # 選択済みの場合は色を変更
            pattern_name = ("circular", "aimed", "splitting")[i]
            if self.selected_bullet_pattern == pattern_name:
                pyxel.text(100, y, label, 14)  # 選択済みは別の色
            else:
                pyxel.text(100, y, label, col)

    def draw_end_scene(self):
        pyxel.cls(5)
        pyxel.text(100, 100, "END", 7)

class Game:
    def __init__(self, level_config, bullet_pattern="circular"):
        self.level = level_config
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.bullet_pattern_type = bullet_pattern
        
        # 初期敵を生成
        self.spawn_initial_enemies()

    def spawn_initial_enemies(self):
        # 画面幅に合わせて等間隔に配置
        enemy_count = 5  # 敵の数を調整
        enemy_width = 8
        total_width = enemy_width * enemy_count
        spacing = (SCREEN_WIDTH - total_width) / (enemy_count + 1)
        
        for i in range(enemy_count):
            x = spacing * (i + 1) + enemy_width * i
            enemy = Enemy(bullet_speed=self.level.get("ENEMY_BULLET_SPEED", 0.2))
            enemy.set_target(x, TARGET_Y)
            enemy.pattern_type = self.bullet_pattern_type
            enemy.player = self.player  # プレイヤー参照を設定
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
        
        # 敵の弾とプレイヤーの当たり判定
        self.check_enemy_bullet_player_collisions()

    def check_enemy_bullet_player_collisions(self):
        # プレイヤーの当たり判定サイズ
        player_size = 7
        
        for enemy in self.enemies:
            # 通常の弾をチェック
            for bullet in enemy.bullets[:]:
                if not bullet.alive:
                    continue
                    
                if self.check_bullet_player_collision(bullet, player_size):
                    self.player.take_damage(1)
                    enemy.bullets.remove(bullet)
            
            # 分裂弾の子弾もチェック
            for bullet in enemy.bullets[:]:
                if hasattr(bullet, 'children'):
                    for child in bullet.children[:]:
                        if child.alive and self.check_bullet_player_collision(child, player_size):
                            self.player.take_damage(1)
                            bullet.children.remove(child)

    def check_bullet_player_collision(self, bullet, player_size):
        # 弾の現在位置を保存
        original_x = bullet.x
        original_y = bullet.y

        target_x, target_y = bullet.next_pos()
        
        # 弾のサイズ
        bullet_size = 1
        
        # 移動距離を分割して処理
        move_len = abs(bullet.vx) + abs(bullet.vy)
        steps = max(int(move_len), 1)
        
        # 1ステップあたりの移動量
        step_x = (target_x - original_x) / steps
        step_y = (target_y - original_y) / steps
        
        # 各ステップで衝突判定
        for step in range(steps + 1):
            test_x = original_x + step * step_x
            test_y = original_y + step * step_y
            
            if rects_intersect(
                test_x - bullet_size, test_y - bullet_size, 
                bullet_size * 2, bullet_size * 2,
                self.player.x + 0.5, self.player.y + 0.5, 
                player_size, player_size
            ):
                return True
        return False

    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets[:]:
            if not bullet.alive:
                self.player.bullets.remove(bullet)
                continue
                
            # 弾の現在位置を保存
            original_x = bullet.x
            original_y = bullet.y
            
            # 目標位置（次のフレームでの位置）
            target_x = original_x
            target_y = original_y - bullet.speed
            
            # 弾のサイズ
            bullet_size = 1
            
            # 衝突フラグ
            collision = False
            hit_enemy = None
            
            # 移動距離を分割して処理
            steps = max(abs(bullet.speed), 1)
            
            # 1ステップあたりの移動量
            step_x = (target_x - original_x) / steps
            step_y = (target_y - original_y) / steps
            
            # 各ステップで衝突判定
            for step in range(steps + 1):
                test_x = original_x + step * step_x
                test_y = original_y + step * step_y
                
                # 各敵との衝突チェック
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                        
                    if rects_intersect(
                        test_x - bullet_size, test_y - bullet_size, 
                        bullet_size * 2, bullet_size * 2,
                        enemy.x, enemy.y, 8, 8
                    ):
                        hit_enemy = enemy
                        collision = True
                        break
                        
                if collision:
                    break
                    
            # 衝突処理
            if collision and hit_enemy:
                hit_enemy.take_damage(1)
                pyxel.play(1, 2)
                self.player.bullets.remove(bullet)
            else:
                bullet.x = target_x
                bullet.y = target_y
                     
    def draw(self):
        pyxel.cls(0)
        
        # スコアとレベル表示
        pyxel.text(10, 10, f"SCORE: {self.score}", 7)
        pyxel.text(10, 20, f"LEVEL: {self.level['ENEMY_BULLET_SPEED']}", 7)

        # プレイヤーのHP表示を追加
        pyxel.text(10, 30, f"HP: {self.player.hp}", 11)
        
        # HPバーの表示（オプション）
        bar_width = (self.player.hp / PLAYER_HP) * 50
        pyxel.rect(40, 30, int(bar_width), 4, 11)
        pyxel.rectb(40, 30, 50, 4, 7)

        # プレイヤーを描画
        self.player.draw()

        # リセット方法の案内表示
        pyxel.text(SCREEN_WIDTH - 115, 10, "R: BACK TO MENU", 8)

        # すべての敵を描画
        for enemy in self.enemies:
            enemy.draw()

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 16
        self.speed = 1
        self.bullets = []
        self.cooldown = 0
        self.hp = PLAYER_HP
        self.invincible_timer = 0
        self.hit_effect = 0

    def take_damage(self, amount):
        if self.invincible_timer > 0:  # 無敵時間中はダメージを受けない
            return
            
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0

        # ヒット時の効果音
        pyxel.play(1, 1)
        
        # ヒットエフェクト用
        self.hit_effect = 20
        
        # 無敵時間を設定
        self.invincible_timer = 0  # 60フレーム = 1秒

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

        # 弾の更新
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.alive:
                self.bullets.remove(bullet)

        # 無敵時間の更新
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
        # ヒットエフェクトの更新
        if self.hit_effect > 0:
            self.hit_effect -= 1

    def draw(self):
        # 無敵時間中は点滅表示
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            # 点滅中は描画しない
            pass
        else:
            # 通常描画
            pyxel.blt(int(self.x), int(self.y), 0, 8, 0, 8, 8, 0)

        # ヒットエフェクト
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
        self.bullet_speed = bullet_speed
        self.pattern_type = "circular"  # デフォルト値を設定
        self.player = None  # プレイヤー参照（後で設定される）

        # 各種弾パターンを初期化
        self.circular_pattern = CircularBurstPattern(
            count=12,
            speed=bullet_speed,
            start_deg=90,
            spread_deg=360,
            spin_deg=6,
            radius=1,
            color=10
        )

        self.aimed_pattern = AimedShot(
            speed=bullet_speed * 1.5,
            radius=1,
            color=8
        )

        self.splitting_pattern = SplittingBulletPattern(
            speed=bullet_speed * 1.2,
            split_count=3,
            split_time=30,
            max_splits=2,
            spread_deg=60,
            radius=1,
            color=14
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
        # 目標位置に向かって移動
        if self.is_moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            if abs(dx) < self.move_speed and abs(dy) < self.move_speed:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
            else:
                # 方向ベクトルを正規化して移動
                distance = (dx**2 + dy**2)**0.5
                self.x += (dx / distance) * self.move_speed
                self.y += (dy / distance) * self.move_speed
        
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
        # 弾パターンの選択
        if self.pattern_type == "circular":
            new_bullets = self.circular_pattern.fire(self.x + 4, self.y + 8)
            self.bullets.extend(new_bullets)
        elif self.pattern_type == "aimed" and self.player:
            new_bullets = self.aimed_pattern.fire(
                self.x + 4, self.y + 8, 
                self.player.x + 4, self.player.y + 4
            )
            self.bullets.extend(new_bullets)
        elif self.pattern_type == "splitting":
            new_bullets = self.splitting_pattern.fire(
                self.x + 4, self.y + 8,
                self.player.x + 4 if self.player else None,
                self.player.y + 4 if self.player else None
            )
            self.bullets.extend(new_bullets)

    def draw(self):
        if self.alive:
            pyxel.blt(int(self.x), int(self.y), 0, 0, 8, 8, 8, 0)

            # HPバーの表示
            bar_width = (self.hp / ENEMY_HP) * 8
            pyxel.rect(int(self.x), int(self.y) - 2, int(bar_width), 1, 8)

            # 弾を描画
            for bullet in self.bullets:
                bullet.draw()

class Player_Bullet:
    def __init__(self, x, y):
        self.x = x + 4
        self.y = y
        self.speed = PLAYER_BULLET_SPEED
        self.alive = True

    def update(self):
        self.y -= self.speed  # 上に向かって移動
        if self.y < -2:
            self.alive = False

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), 1, 8)

# アプリケーション開始
if __name__ == "__main__":
    App()