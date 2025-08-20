
# シーン
START_SCENE = 0
PLAY_SCENE = 1
GAME_OVER_SCENE = 2
SCENE_BATTLE = 3  # 追加
SCENE_RESULT = 4  # 追加


PLAYER_INIT = dict(
    name="戦艦",
    hp=120,
    hp_max=120,
    atk=20,
    defense=8,
)

COMMANDS = [
    {
        "name": "Attack",
        "atk": +10,       # 攻撃補正
        "hp": 0,          # 回復量
        "defense": 0,     # 防御補正
        "damage": True,   # ダメージを与えるか？
    },
    {
        "name": "Power Up",
        "atk": +5,        # 次ターン以降の基礎攻撃力上昇
        "hp": 0,
        "defense": 0,
        "damage": False,  # このターンは攻撃しない
    },
    {
        "name": "Repair",
        "atk": 0,
        "hp": +20,
        "defense": 0,
        "damage": False,
    },
    {
        "name": "Defence",
        "atk": 0,
        "hp": 0,
        "defense": +5,
        "damage": False,
    },
]

WAVES = [
    [
        dict(name="小型艦A", hp=30, hp_max=30, atk=5, defense=1),
        dict(name="小型艦B", hp=30, hp_max=30, atk=5, defense=1),
        dict(name="中型艦A", hp=50, hp_max=50, atk=10, defense=1),
     ],
        [
        dict(name="小型艦A", hp=30, hp_max=30, atk=5, defense=1),
        dict(name="小型艦B", hp=30, hp_max=30, atk=5, defense=1),
        dict(name="中型艦A", hp=50, hp_max=50, atk=10, defense=1),
     ],
]

# 色（Pyxelの16色想定）
COL_BG = 1         # 深い海色
COL_PANEL = 0      # 黒
COL_TEXT = 7       # 白
COL_ACCENT = 10    # 黄緑
COL_HP = 8         # 赤
COL_HP_BACK = 5    # くすんだ紫
COL_CURSOR = 9     # 黄

# 画面
SCREEN_W = 256
SCREEN_H = 256
FPS = 60
TITLE = "DOT BATTLESHIP"

# ログ行数
LOG_LINES = 5

# HPバー描画
HP_BAR_W = 80
HP_BAR_H = 4