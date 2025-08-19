

# フルーツ＆爆弾データ
FRUITS = [
    {   # さくらんぼ
        "name": "cherry",
        "u": 16, "v": 0,       # bltでのスプライト座標
        "w": 8, "h": 8,       # サイズ
        "point": 1,
        "speed": 0.5,
        "random": False,
        "spawn_interval": 60  # 出現間隔（フレーム単位）
    },
    {   # リンゴ
        "name": "apple",
        "u": 8, "v": 0,
        "w": 8, "h": 8,
        "point": 2,
        "speed": 0.5,
        "random": False,
        "spawn_interval": 90
    },
    {   # バナナ
        "name": "banana",
        "u": 0, "v": 8,
        "w": 8, "h": 8,
        "point": 3,
        "speed": 2,
        "random": True,
        "spawn_interval": 120
    },
    {   # みかん
        "name": "orange",
        "u": 8, "v": 8,
        "w": 8, "h": 8,
        "point": 4,
        "speed": 2,
        "random": True,
        "spawn_interval": 140
    },
    {   # 爆弾
        "name": "bomb",
        "u": 16, "v": 8,
        "w": 8, "h": 8,
        "point": -3,
        "speed": 1,
        "random": True,
        "spawn_interval": 40
    },
]

SCREEN_W = 256
SCREEN_H = 256

NUM_GRANDS = 10
GRAND_HEIGHT = 8

TITLE_SCENE = 0
PLAY_SCENE = 1