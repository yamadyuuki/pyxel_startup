import pyxel
from models import Player, Stock, StockMarket, RandomWalkStrategy, TrendingStrategy

# --- ゲーム設定 ---
INITIAL_MONEY = 100000
TARGET_ASSETS = 200000
GAME_DAYS = 30
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192

# --- ここからシーン定義 ---

class SceneManager:
    """
    シーンを管理し、切り替えを行う司令塔
    """
    def __init__(self):
        self.scenes = {}
        self.current_scene = None

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def change_scene(self, name, **kwargs):
        """シーンを切り替える。kwargsで次のシーンにデータを渡せる"""
        self.current_scene = self.scenes[name]
        # on_enterメソッドがあれば呼び出し、kwargsを渡す
        if hasattr(self.current_scene, 'on_enter'):
            self.current_scene.on_enter(**kwargs)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self):
        if self.current_scene:
            self.current_scene.draw()

class BaseScene:
    """全シーンの親クラス。SceneManagerへの参照を持つ"""
    def __init__(self, manager):
        self.manager = manager

    def update(self):
        pass

    def draw(self):
        pass

class TitleScene(BaseScene):
    """タイトル画面"""
    def update(self):
        # SPACEキーが押されたらプレイ画面に遷移
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.manager.change_scene("play")

    def draw(self):
        pyxel.text(85, 60, "Mini Stock Trader", pyxel.COLOR_WHITE)
        pyxel.text(90, 120, "- PRESS SPACE -", pyxel.COLOR_YELLOW)

class PlayScene(BaseScene):
    """メインのゲームプレイ画面"""
    def on_enter(self, **kwargs):
        """このシーンが表示される度に呼ばれ、ゲームの状態をリセットする"""
        self.day = 1
        self.action_cursor_pos = 0 # 0:買う, 1:売る, 2:次の日へ
        
        # ★★★ 修正点1: 選択中の銘柄を管理する変数を追加 ★★★
        self.selected_stock_index = 0 # 0番目の銘柄を最初に選択

        # --- モデルの初期化 ---
        self.player = Player(initial_money=INITIAL_MONEY)
        
        # 市場と銘柄の準備
        self.market = StockMarket()

        random_strategy = RandomWalkStrategy()
        trending_strategy = TrendingStrategy()

        self.market.add_stock(Stock(name="Pixel Inc.", initial_price=5000, strategy=random_strategy))
        self.market.add_stock(Stock(name="Dot Foods", initial_price=3000, strategy=trending_strategy))
        
        # ★★★ 修正点2: 銘柄名をリストとして保持しておく ★★★
        # これによりインデックスで簡単に銘柄を切り替えられる
        self.stock_names = list(self.market.stocks.keys())


    def update(self):
        # --- 入力処理 ---
        # 上下キーでアクション（買う/売る/次へ）を選択
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.action_cursor_pos = (self.action_cursor_pos + 1) % 3
        if pyxel.btnp(pyxel.KEY_UP):
            self.action_cursor_pos = (self.action_cursor_pos - 1 + 3) % 3
            
        # ★★★ 修正点3: 左右キーで銘柄を選択できるようにする ★★★
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.selected_stock_index = (self.selected_stock_index + 1) % len(self.stock_names)
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.selected_stock_index = (self.selected_stock_index - 1 + len(self.stock_names)) % len(self.stock_names)

        if pyxel.btnp(pyxel.KEY_SPACE):
            # ★★★ 修正点4: 選択中の銘柄を取得して処理を行う ★★★
            selected_stock_name = self.stock_names[self.selected_stock_index]
            stock = self.market.stocks[selected_stock_name]
            
            if self.action_cursor_pos == 0: # 買う
                self.player.buy(stock.name, 1, stock.current_price)
            elif self.action_cursor_pos == 1: # 売る
                self.player.sell(stock.name, 1, stock.current_price)
            elif self.action_cursor_pos == 2: # 次の日へ
                self.market.next_day()
                self.day += 1

        # --- ゲーム終了判定 ---
        total_assets = self.player.total_assets(self.market)
        if total_assets >= TARGET_ASSETS:
            self.manager.change_scene("result", message="YOU WIN!", score=total_assets)
        elif self.day > GAME_DAYS:
            self.manager.change_scene("result", message="GAME OVER...", score=total_assets)

    def draw(self):
        # --- UI描画 ---
        pyxel.text(5, 5, f"DAY: {self.day}/{GAME_DAYS}", 7)
        pyxel.text(5, 15, f"MONEY: {self.player.money:,} YEN", 7)
        
        total_assets = self.player.total_assets(self.market)
        pyxel.text(120, 5, f"TOTAL ASSETS: {total_assets:,} YEN", 7)
        pyxel.text(120, 15, f"TARGET: {TARGET_ASSETS:,} YEN", 7)

        # ★★★ 修正点5: 選択中の銘柄の情報を描画する ★★★
        selected_stock_name = self.stock_names[self.selected_stock_index]
        stock = self.market.stocks[selected_stock_name]
        
        # 銘柄選択のUI
        pyxel.text(5, 30, "STOCK:", 7)
        # 左右の矢印で銘柄を切り替えられることを示す
        pyxel.text(35, 30, f"< {stock.name} >", pyxel.COLOR_WHITE)
        
        pyxel.text(5, 40, f"PRICE: {stock.current_price:,} YEN", 7)
        pyxel.text(5, 50, f"HOLD: {self.player.stocks.get(stock.name, 0)}", 7)
        
        # 選択中銘柄の株価チャート
        multiple = 10
        history = stock.price_history
        for i in range(1, len(history)):
            # 画面外に描画しないようにチェック
            if 5 + i * multiple < SCREEN_WIDTH:
                y1 = 150 - history[i-1] // 100
                y2 = 150 - history[i] // 100
                pyxel.line(5 + (i-1) * multiple, y1, 5 + i * multiple, y2, pyxel.COLOR_GREEN)


        # --- メニュー ---
        pyxel.text(100, 150, "BUY (1 stock)", 7)
        pyxel.text(100, 160, "SELL (1 stock)", 7)
        pyxel.text(100, 170, "NEXT DAY", 7)
        pyxel.text(90, 150 + self.action_cursor_pos * 10, ">", pyxel.COLOR_YELLOW)
        

class ResultScene(BaseScene):
    """結果表示画面"""
    def on_enter(self, **kwargs):
        """PlaySceneからメッセージとスコアを受け取る"""
        self.message = kwargs.get("message", "RESULT")
        self.score = kwargs.get("score", 0)

    def update(self):
        # SPACEキーが押されたらタイトル画面に戻る
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.manager.change_scene("title")

    def draw(self):
        pyxel.text(110, 60, self.message, pyxel.frame_count % 16)
        pyxel.text(90, 80, f"YOUR ASSETS: {self.score:,} YEN", 7)
        # ★★★ おまけ修正: 元のコードがENTERだったのでSPACEに変更 ★★★
        pyxel.text(90, 120, "- PRESS SPACE -", 7)