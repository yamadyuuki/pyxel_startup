import random
import abc

# --- 戦略パターンのためのクラス定義 ---

class PriceUpdateStrategy(abc.ABC):
    """
    株価更新戦略の「型」を定義する親クラス（抽象基底クラス）。
    このクラスを継承するクラスは、必ずupdateメソッドを実装する必要がある。
    """
    @abc.abstractmethod
    def update(self, current_price):
        """現在の株価を受け取り、次の日の株価を返す"""
        pass

class RandomWalkStrategy(PriceUpdateStrategy):
    """
    株価がランダムに上下する戦略。
    """
    def update(self, current_price):
        # -10%から+12%の範囲でランダムに変動させる（少し上昇傾向にする）
        change_rate = random.randint(-10, 12) / 100
        next_price = current_price * (1 + change_rate)
        
        # 価格が0以下にならないように、最低価格を1円とする
        return max(1, int(next_price))

class TrendingStrategy(PriceUpdateStrategy):
    """
    株価が上昇傾向を持つ戦略。
    """
    def update(self, current_price):
        # -5%から+10%の範囲で変動させ、より上昇しやすくする
        change_rate = random.randint(-5, 10) / 100
        next_price = current_price * (1 + change_rate)
        return max(1, int(next_price))

# --- ゲームの主要モデル定義 ---

class Stock:
    """
    個別の銘柄データを管理するクラス。
    """
    def __init__(self, name, initial_price, strategy: PriceUpdateStrategy):
        self.name = name
        self.price_history = [initial_price] # 株価の履歴をリストで保持
        self.strategy = strategy # 外部から注入された株価変動戦略

    @property
    def current_price(self):
        """現在の価格を返すプロパティ。リストの最後の値が現在の価格。"""
        return self.price_history[-1]

class Player:
    """
    プレイヤーの状態（所持金、保有株）を管理するクラス。
    """
    def __init__(self, initial_money):
        self.money = initial_money
        self.stocks = {} # 保有株を辞書で管理。例: {"Pixel Inc.": 10}

    def buy(self, stock_name, quantity, price):
        """株を買う処理"""
        cost = price * quantity
        if self.money >= cost:
            self.money -= cost
            self.stocks[stock_name] = self.stocks.get(stock_name, 0) + quantity
            return True # 購入成功
        return False # 購入失敗

    def sell(self, stock_name, quantity, price):
        """株を売る処理"""
        if self.stocks.get(stock_name, 0) >= quantity:
            self.money += price * quantity
            self.stocks[stock_name] -= quantity
            return True # 売却成功
        return False # 売却失敗

    def total_assets(self, market):
        """総資産（所持金 + 保有株の評価額）を計算して返す"""
        asset_value = self.money
        for stock_name, quantity in self.stocks.items():
            current_price = market.stocks[stock_name].current_price
            asset_value += current_price * quantity
        return asset_value

class StockMarket:
    """
    株式市場全体と、時間の経過を管理するクラス。
    """
    def __init__(self):
        self.stocks = {} # 市場に存在する銘柄を辞書で管理

    def add_stock(self, stock: Stock):
        """市場に新しい銘柄を追加する"""
        self.stocks[stock.name] = stock

    def next_day(self):
        """
        市場の時間を1日進める。
        管理している全銘柄の株価を、保持している戦略に従って更新する。
        """
        for stock in self.stocks.values():
            new_price = stock.strategy.update(stock.current_price)
            stock.price_history.append(new_price)