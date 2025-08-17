# game_constants.py
import pyxel

# 画面・タイル
SCREEN_W = 256
SCREEN_H = 256
FPS      = 60
TILE_SIZE = 8

# ゲーム状態
GAME_STATE_PLAYING = 0
GAME_STATE_GAME_OVER = 1

# ゲームオーバー画面設定
GAMEOVER_TILEMAP = 2     # ゲームオーバー画面のタイルマップ番号
GAMEOVER_IMAGE = 1       # ゲームオーバー画面の画像番号
GAMEOVER_TILE_X = 0      # ゲームオーバー画面の開始X座標（タイル単位）
GAMEOVER_TILE_Y = 0      # ゲームオーバー画面の開始Y座標（タイル単位）
GAMEOVER_TILE_W = 32     # ゲームオーバー画面の幅（タイル単位）
GAMEOVER_TILE_H = 32     # ゲームオーバー画面の高さ（タイル単位）

# 入力（実キー設定をここだけで定義）
KEY_LEFT   = pyxel.KEY_LEFT
KEY_RIGHT  = pyxel.KEY_RIGHT
KEY_JUMP   = pyxel.KEY_UP
KEY_ATTACK = pyxel.KEY_SPACE
KEY_RESET  = pyxel.KEY_R
KEY_QUIT   = pyxel.KEY_Q
KEY_RETRY  = pyxel.KEY_SPACE  # ゲームオーバー画面でのリトライキー

# 入力のラベル（画面左上の操作ヒント用／表示文字列はここを変えるだけ）
KEY_LABELS = {
    "MOVE": "←/→",
    "JUMP": "UP",
    "ATK":  "SPACE",
    "RST":  "R",
    "QUIT": "Q",
    "GUN" : "G",
    "RETRY": "SPACE",
}

# HUDレイアウト（表示位置もここで一元管理）
HUD_POS = {
    "HELP":  (5, 5),        # 入力ヘルプ
    "HP":    (5, 18),       # HPバー/HP値
    "SCORE": (5, 28),       # スコア
    "WAVE":  (SCREEN_W - 70, 5),  # ウェーブ
    "GAMEOVER_TEXT": (SCREEN_W // 2, SCREEN_H // 2 + 60),  # ゲームオーバーテキスト
}

# プレイヤー関連
PLAYER_RESPAWN_X = 30
PLAYER_RESPAWN_Y = 30
PLAYER_W = 16
PLAYER_H = 16
GRAVITY = 0.35
MAX_FALL = 5.0
MOVE_SPEED = 1.2
JUMP_POWER = -6

# HP関連
PLAYER_MAX_HP = 30        # プレイヤーの最大HP
INVINCIBLE_FRAMES = 30    # 無敵時間（フレーム）約0.5秒
KNOCKBACK_POWER = 3.0     # ノックバックの強さ
DAMAGE_FLASH_INTERVAL = 8 # 被ダメージ点滅の間隔（フレーム）

# 攻撃関連
SWORD_COOLDOWN = 30
SWORD_ACTIVE_FRAMES = 20

# 敵関連（新規追加）
ENEMY_W = 8              # 敵の幅
ENEMY_H = 8              # 敵の高さ
ENEMY_HP = 3              # 敵の初期HP
ENEMY_HURT_FRAMES = 20    # 敵の無敵時間

# 敵の物理パラメータ（新規追加）
ENEMY_GRAVITY = 0.35      # 敵の重力（プレイヤーと同じ）
ENEMY_MAX_FALL = 5.0      # 敵の最大落下速度
ENEMY_MOVE_SPEED = 0.6    # 敵の左右移動速度
ENEMY_SPAWN_HEIGHT = -32  # 敵の初期スポーン高さ（画面上）

# 敵の行動パターン（新規追加）
ENEMY_STATE_FALLING = 0   # 落下中
ENEMY_STATE_GROUND = 1    # 地面移動中
ENEMY_DIRECTION_LEFT = -1 # 左向き
ENEMY_DIRECTION_RIGHT = 1 # 右向き

# スコア関連（新規追加）
SCORE_ENEMY_DEFEAT = 100  # 敵撃破時のスコア

# タイルタイプ
TILE_NONE  = 0
TILE_STONE = 1
BLOCKING_TYPES = {TILE_STONE}

# タイルセット(U,V)→ゲーム内タイルタイプ
TILE_TO_TILETYPE = {
    (2, 2): TILE_STONE,
    (3, 2): TILE_STONE,
}

# 敵のAI関連（新規追加）
ENEMY_DETECTION_RANGE = 80    # プレイヤー感知範囲（ピクセル）
ENEMY_ALERT_SPEED_MULTIPLIER = 1.5  # 警戒時の速度倍率

# buttle_constants.py に追加する定数

# スポーン関連の定数
SPAWN_INITIAL_DELAY = 180       # ゲーム開始からの初期待機時間（フレーム）
SPAWN_BASE_INTERVAL = 300       # 基本スポーン間隔（フレーム）
SPAWN_MIN_INTERVAL = 180         # 最小スポーン間隔（フレーム）
# スポーン可能な(x, y)座標リスト（修正版）
SPAWN_POSITIONS = [
    (24, 24),      # 左上
    (242, 24),     # 右上
    (24, 128),     # 左中
    (242, 128),    # 右中
    (24, 192),     # 左下
    (242, 192),    # 右下
    (128, 152),    # 中央下
]

# ウェーブ関連の定数
WAVE_DURATION = 1200            # 1ウェーブの長さ（フレーム）約30秒
WAVE_MAX = 2                   # 最大ウェーブ数
WAVE_CLEAR_BONUS = 500          # ウェーブクリア時のボーナススコア

# 難易度スケーリング関連
SPAWN_INTERVAL_DECREASE = 10    # ウェーブごとのスポーン間隔減少量（フレーム）
ENEMY_SPEED_INCREASE = 0.0      # ウェーブごとの敵の速度増加量
ENEMY_HP_INCREASE = 1           # 3ウェーブごとの敵のHP増加量

# スポーン確率テーブル（将来の敵タイプ拡張用）
# フォーマット: {敵タイプ: {ウェーブ番号: 出現確率}}
ENEMY_SPAWN_CHANCES = {
    "normal": {  # 通常敵
        1: 100,   # ウェーブ1: 100%
        3: 80,    # ウェーブ3: 80%
        5: 60,    # ウェーブ5: 60%
        7: 40,    # ウェーブ7: 40%
        9: 30,    # ウェーブ9: 30%
    },
    # 将来の敵タイプ用（実装後にコメントを外す）
    # "fast": {   # 高速敵
    #     3: 20,    # ウェーブ3から20%の確率で出現
    #     5: 30,
    #     7: 40,
    #     9: 40,
    # },
    # "tank": {   # 高HPの敵
    #     5: 10,    # ウェーブ5から10%の確率で出現
    #     7: 20,
    #     9: 30,
    # },
}

# ウェーブ表示関連
WAVE_NOTIFICATION_DURATION = 60  # ウェーブ開始通知の表示時間（フレーム）
WAVE_NOTIFICATION_COLOR = 10      # ウェーブ通知の色（10=黄色）

# 入力に追加
KEY_GUN = pyxel.KEY_G

# 銃関連
GUN_COOLDOWN = 30      # 銃の発射クールダウン