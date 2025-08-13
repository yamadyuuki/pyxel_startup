# 定数モジュール

SCROLL_BORDER_X = 80  # スクロール境界X座標
# プレイヤーがこの座標を超えたらスクロールさせる

# タイル種別
TILE_NONE = 0  # 何もない
TILE_GEM = 1  # 宝石
TILE_EXIT = 2  # 出口
TILE_MUSHROOM = 3  # キノコ
TILE_SPIKE = 4  # トゲ
TILE_LAVA = 5  # 溶岩
TILE_WALL = 6  # 壁
TILE_SLIME1_POINT = 7  # グリーンスライム出現位置
TILE_SLIME2_POINT = 8  # レッドスライム出現位置
TILE_MUMMY_POINT = 9  # マミー出現位置
TILE_FLOWER_POINT = 10  # フラワー出現位置

# タイル→タイル種別変換テーブル
TILE_TO_TILETYPE = {
    (1, 0): TILE_GEM,
    (2, 0): TILE_EXIT,
    (3, 0): TILE_MUSHROOM,
    (4, 0): TILE_SPIKE,
    (5, 0): TILE_LAVA,
    (1, 2): TILE_WALL,
    (2, 2): TILE_WALL,
    (3, 2): TILE_WALL,
    (4, 2): TILE_WALL,
    (5, 2): TILE_WALL,
    (6, 2): TILE_WALL,
    (7, 2): TILE_WALL,
    (1, 3): TILE_WALL,
    (2, 3): TILE_WALL,
    (1, 4): TILE_WALL,
    (1, 5): TILE_WALL,
    (0, 9): TILE_SLIME1_POINT,
    (0, 10): TILE_SLIME2_POINT,
    (0, 11): TILE_MUMMY_POINT,
    (0, 12): TILE_FLOWER_POINT,
}
# このテーブルにないタイルはTILE_NONEとして判定する
