# Enemy クラスを直接インポート（循環インポートなし）
from buttle_enemy import Enemy

import random
from buttle_constants import (
    # スポーン関連の定数
    SPAWN_INITIAL_DELAY, SPAWN_BASE_INTERVAL, SPAWN_MIN_INTERVAL, SPAWN_POSITIONS,
    
    # ウェーブ関連の定数
    WAVE_DURATION, WAVE_MAX, WAVE_CLEAR_BONUS, WAVE_NOTIFICATION_DURATION,
    WAVE_NOTIFICATION_COLOR,
    
    # 難易度スケーリング関連
    SPAWN_INTERVAL_DECREASE, ENEMY_SPEED_INCREASE, ENEMY_HP_INCREASE,
    
    # 敵関連の定数
    ENEMY_HP, ENEMY_SPAWN_HEIGHT, ENEMY_SPAWN_CHANCES,
)


class SpawnController:
    """敵のスポーンと進行を管理するクラス"""
    def __init__(self):
        # スポーン関連
        self.spawn_timer = SPAWN_INITIAL_DELAY  # 初期待機時間を設定
        self.current_spawn_interval = SPAWN_BASE_INTERVAL
        
        # ウェーブ関連
        self.wave = 1
        self.wave_timer = WAVE_DURATION
        self.wave_notification_timer = WAVE_NOTIFICATION_DURATION
        
        # 難易度パラメータ
        self.enemy_speed_multiplier = 1.0
        self.enemy_hp_multiplier = 1
        
        # スポーン確率テーブル（現在のウェーブに合わせて更新）
        self.spawn_chances = self._get_spawn_chances(self.wave)
    
    def update(self):
        """スポーンコントローラーの更新"""
        # スポーンタイマーの更新
        self.spawn_timer -= 1
        
        # ウェーブタイマーの更新
        self.wave_timer -= 1
        
        # 通知タイマーの更新
        if self.wave_notification_timer > 0:
            self.wave_notification_timer -= 1
        
        spawn_enemy = False
        enemy_type = "normal"  # デフォルトタイプ
        
        # スポーンタイマーが0になったら敵をスポーン
        if self.spawn_timer <= 0:
            spawn_enemy = True
            
            # スポーンする敵のタイプを確率で決定
            enemy_type = self._get_random_enemy_type()
            
            # タイマーをリセット
            self.spawn_timer = self.current_spawn_interval
        
        # ウェーブタイマーが0になったら次のウェーブへ
        if self.wave_timer <= 0:
            wave_advanced, bonus_score = self._advance_wave()
            return spawn_enemy, enemy_type, wave_advanced, bonus_score
        
        return spawn_enemy, enemy_type, False, 0
    
    def _advance_wave(self):
        """次のウェーブに進む"""
        if self.wave < WAVE_MAX:
            self.wave += 1
            self.wave_timer = WAVE_DURATION
            self.wave_notification_timer = WAVE_NOTIFICATION_DURATION
            
            # スポーン間隔を短くする（難易度上昇）
            self.current_spawn_interval = max(
                SPAWN_MIN_INTERVAL, 
                SPAWN_BASE_INTERVAL - (self.wave - 1) * SPAWN_INTERVAL_DECREASE
            )
            
            # 敵の速度を増加（難易度上昇）
            self.enemy_speed_multiplier = 1.0 + (self.wave - 1) * ENEMY_SPEED_INCREASE
            
            # 敵のHPを増加（3ウェーブごと）
            self.enemy_hp_multiplier = 1 + ((self.wave - 1) // 3) * ENEMY_HP_INCREASE
            
            # スポーン確率テーブルを更新
            self.spawn_chances = self._get_spawn_chances(self.wave)
            
            return True, WAVE_CLEAR_BONUS  # ウェーブ更新とボーナススコアを返す
        
        return False, 0  # 最大ウェーブに達している場合
    
    def _get_spawn_chances(self, wave):
        """現在のウェーブに基づいたスポーン確率を取得"""
        chances = {}
        
        # 各敵タイプについて、現在のウェーブでの出現確率を計算
        for enemy_type, wave_chances in ENEMY_SPAWN_CHANCES.items():
            # 該当するウェーブの確率を探す（そのウェーブがなければ次に低いウェーブの確率を使用）
            applicable_waves = [w for w in wave_chances.keys() if w <= wave]
            if applicable_waves:
                max_applicable_wave = max(applicable_waves)
                chances[enemy_type] = wave_chances[max_applicable_wave]
            else:
                chances[enemy_type] = 0
        
        return chances
    
    def _get_random_enemy_type(self):
        """確率に基づいて敵のタイプをランダムに選択"""
        # 確率の合計を計算
        total_chance = sum(self.spawn_chances.values())
        
        if total_chance <= 0:
            return "normal"  # デフォルトタイプ
        
        # ランダム値を生成
        r = random.randint(1, total_chance)
        
        # 累積確率で敵タイプを選択
        cumulative = 0
        for enemy_type, chance in self.spawn_chances.items():
            cumulative += chance
            if r <= cumulative:
                return enemy_type
        
        return "normal"  # デフォルトに戻る
    
    def get_spawn_position(self):
        """スポーン位置をランダムに選択"""
        return random.choice(SPAWN_POSITIONS)
    
    def create_enemy(self, enemy_type="normal"):
        """敵を生成（タイプに応じた敵クラスのインスタンスを返す）"""
        spawn_x, spawn_y = self.get_spawn_position()
        
        # 通常の敵を生成
        enemy = Enemy(spawn_x, spawn_y)
        
        # 現在のウェーブに応じて敵のパラメータを調整
        enemy.base_speed *= self.enemy_speed_multiplier
        enemy.move_speed = enemy.base_speed
        
        # HPの調整（最低でも1）
        enemy.max_hp = max(1, int(ENEMY_HP * self.enemy_hp_multiplier))
        enemy.hp = enemy.max_hp
        
        return enemy
    
    def should_show_notification(self):
        """ウェーブ通知を表示すべきかどうか"""
        return self.wave_notification_timer > 0
    
    def get_wave_info(self):
        """現在のウェーブ情報を取得"""
        return {
            "wave": self.wave,
            "max_wave": WAVE_MAX,
            "enemies_stronger": self.enemy_speed_multiplier > 1.0 or self.enemy_hp_multiplier > 1,
            "spawn_interval": self.current_spawn_interval,
        }