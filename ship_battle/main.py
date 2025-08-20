import pyxel
from constants import *
from collections import deque

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

class PlayerShip:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.hp = data["hp"]
        self.hp_max = data["hp_max"]
        self.atk = data["atk"]
        self.defense = data["defense"]

class EnemyShip:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.atk = data["atk"]
        self.hp = data["hp"]
        self.defense = data["defense"]
        self.hp_max = data["hp_max"]
        #self.damage = data["damage"]

    @property
    def alive(self):
        return self.hp > 0


class Battle:
    def __init__(self, waves:list[list:[dict]], log_deque: deque):
        self.log = log_deque
        self.wave_idx = 0
        self.player = PlayerShip(PLAYER_INIT.copy())
        self.enemies: list[EnemyShip] = []
        self.turn = 1

        # ターン内の状態
        self.phase = "COMMAND"      # COMMAND / TARGET / RESOLVE
        self.command_idx = 0
        self.target_idx = 0

        self._load_wave(waves)

    def _load_wave(self, waves):
        self.waves = waves
        self._spawn_enemies()
        self.log.clear()
        self._log(f"Wave {self.wave_idx+1} 開始！")
        self.phase = "COMMAND"
        self.command_idx = 0
        self.target_idx = 0
        self.turn = 1

    def _spawn_enemies(self):
        self.enemies = [EnemyShip(d.copy()) for d in self.waves[self.wave_idx]]

    def _log(self, msg: str):
        self.log.append(msg)

    def all_enemies_down(self):
        return all(not e.alive for e in self.enemies)

    def _player_attack(self, target_idx : int, cmd: dict):
        if 0 <= target_idx < len(self.enemies):
            tgt = self.enemies[target_idx]
            if tgt.alive:
                effective_atk = self.player.atk + cmd.get("atk", 0)
                dmg = self._damage_formula(effective_atk, tgt.defense)
                tgt.hp = clamp(tgt.hp - dmg, 0, tgt.hp_max)
                self._log(f"{cmd['name']}！ {tgt.name} に {dmg} ダメージ")
                if tgt.hp <= 0:
                    self._log(f"{tgt.name} を撃沈！")

    def _apply_non_damage(self, cmd: dict):
        """非ダメージ系（Power Up / Repair / Defence）を即時適用。"""
        name = cmd["name"]
        if name == "Power Up":
            inc = cmd.get("atk", 0)
            self.player.atk += inc
            self._log(f"ATKが {inc} 上昇！（現在 {self.player.atk}）")
        elif name == "Repair":
            before = self.player.hp
            heal = cmd.get("hp", 0)
            self.player.hp = clamp(self.player.hp + heal, 0, self.player.hp_max)
            self._log(f"修理！ HP {before}→{self.player.hp}")
        elif name == "Defence":
            inc = cmd.get("defense", 0)
            self.player.defense += inc
            self._log(f"DEFが {inc} 上昇！（現在 {self.player.defense}）")
        else:
            self._log(f"{name} は準備中…")


    def update(self):
        # 入力処理（フェーズ別）
        if self.phase == "COMMAND":
            self._update_command()
        elif self.phase == "TARGET":
            self._update_target()
        elif self.phase == "RESOLVE":
            self._resolve_turn()

    def _move_idx(self, cur, delta, n):
        return (cur + delta) % n if n > 0 else 0

    def _update_command(self):
        # 左右でコマンド選択
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.command_idx = self._move_idx(self.command_idx, -1, len(COMMANDS))
            pyxel.play(0,0)         
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.command_idx = self._move_idx(self.command_idx, +1, len(COMMANDS))
            pyxel.play(0,0)

        # 決定
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE):
            cmd = COMMANDS[self.command_idx]
            self.last_cmd = cmd  # ← RESOLVEで使うため保持
            if cmd.get("damage"):
                # 生存ターゲットがいるならTARGETへ
                if any(e.alive for e in self.enemies):
                    alive_indices = [i for i, e in enumerate(self.enemies) if e.alive]
                    self.target_idx = alive_indices[0] if alive_indices else 0
                    self.phase = "TARGET"
                    pyxel.play(0,1)
                else:
                    self._log("攻撃対象がいない！")
            else:
                # 非ダメージ系は即時適用してRESOLVEへ（敵ターンも解決）
                self._apply_non_damage(cmd)
                self.phase = "RESOLVE"
                pyxel.play(0,1)

        # キャンセル
        if pyxel.btnp(pyxel.KEY_X):
            self._log("何もしなかった。")

    def _update_target(self):
        # 上下でターゲット選択
        if pyxel.btnp(pyxel.KEY_UP):
            self.target_idx = self._prev_alive(self.target_idx)
            pyxel.play(0,0)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.target_idx = self._next_alive(self.target_idx)
            pyxel.play(0,0)

        # 決定 → RESOLVE
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE):
            self.phase = "RESOLVE"
            pyxel.play(0,1)            

        # キャンセルでコマンドに戻る
        if pyxel.btnp(pyxel.KEY_X):
            self.phase = "COMMAND"

    def _prev_alive(self, start):
        idx = start
        n = len(self.enemies)
        for _ in range(n):
            idx = (idx - 1) % n
            if self.enemies[idx].alive:
                return idx
        return start

    def _next_alive(self, start):
        idx = start
        n = len(self.enemies)
        for _ in range(n):
            idx = (idx + 1) % n
            if self.enemies[idx].alive:
                return idx
        return start

    def _damage_formula(self, atk, defense):
        # 超シンプル：ATK - DEF を基準に、最低1ダメ、±2の揺らぎ
        base = max(1, atk - defense)
        jitter = pyxel.rndi(-2, 2)
        return max(1, base + jitter)

    def _resolve_turn(self):
        # プレイヤー行動
        if self.last_cmd and self.last_cmd.get("damage"):
            # ターゲット指定済みの攻撃系
            self._player_attack(self.target_idx, self.last_cmd)

        # 敵行動（デモ用：生きている敵がそれぞれ小ダメージ）
        total_dmg = 0
        for e in self.enemies:
            if e.alive:
                dmg = max(1, e.atk // 4)  # ちょい弱い固定ダメージ
                total_dmg += dmg
        if total_dmg > 0:
            self.player.hp = clamp(self.player.hp - total_dmg, 0, self.player.hp_max)
            self._log(f"敵の一斉射！ あなたは {total_dmg} ダメージ")

        # 勝敗 or 続行
        if self.player.hp <= 0:
            App.instance.to_result(win=False)
            return

        if self.all_enemies_down():
            # 次のWAVEがあれば進行、なければ勝利
            if self.wave_idx + 1 < len(self.waves):
                self.wave_idx += 1
                # 軽く補給
                self.player.hp = clamp(self.player.hp + 15, 0, self.player.hp_max)
                self._load_wave(self.waves)
            else:
                App.instance.to_result(win=True)
                return

        # 次ターンへ
        self.turn += 1
        self.phase = "COMMAND"

    # 描画 ---------------------------------------------------
    def draw(self):
        self._draw_panels()
        self._draw_player()
        self._draw_enemies()
        self._draw_commands()
        self._draw_log()
        self._draw_turn()

    def _draw_panels(self):
        pyxel.cls(COL_BG)
        # 上：ログ
        pyxel.rect(4, 4, SCREEN_W - 8, 40, COL_PANEL)
        # 左：プレイヤー
        pyxel.rect(4, 48, SCREEN_W // 2 - 6, 90, COL_PANEL)
        # 右：敵
        pyxel.rect(SCREEN_W // 2 + 2, 48, SCREEN_W // 2 - 6, 150, COL_PANEL)
        # 下：コマンド
        pyxel.rect(4, SCREEN_H - 48, SCREEN_W - 8, 44, COL_PANEL)

    def _draw_text(self, x, y, s, col=COL_TEXT):
        pyxel.text(x, y, s, col)

    def _draw_hp_bar(self, x, y, w, h, hp, hp_max):
        # 背景
        pyxel.rect(x, y, w, h, COL_HP_BACK)
        # 本体
        if hp_max > 0 and hp > 0:
            ww = int(w * hp / hp_max)
            pyxel.rect(x, y, ww, h, COL_HP)

    def _draw_player(self):
        x = 8
        y = 52
        self._draw_text(x, y, f"{self.player.name}", COL_ACCENT)
        self._draw_text(x, y + 10, f"HP {self.player.hp}/{self.player.hp_max}")
        self._draw_hp_bar(x, y + 20, HP_BAR_W, HP_BAR_H, self.player.hp, self.player.hp_max)
        self._draw_text(x, y + 30, f"ATK {self.player.atk}  DEF {self.player.defense}")

    def _draw_enemies(self):
        x = SCREEN_W // 2 + 6
        y = 52
        for i, e in enumerate(self.enemies):
            col = COL_ACCENT if e.alive else 13  # 13: グレー
            self._draw_text(x, y, f"{e.name}", col)
            self._draw_text(x, y + 10, f"HP {e.hp}/{e.hp_max}", col)
            self._draw_hp_bar(x, y + 20, HP_BAR_W, HP_BAR_H, e.hp, e.hp_max)

            # ターゲットカーソル（TARGETフェーズ中のみ）
            if self.phase == "TARGET" and i == self.target_idx and e.alive:
                pyxel.rectb(x - 3, y - 2, HP_BAR_W + 20, 28, COL_CURSOR)

            y += 36

    def _draw_commands(self):
        x = 10
        y = SCREEN_H - 40
        self._draw_text(x, y - 12, f"[LEFT/RIGHT] Select   [Z/SPACE] Confirm   [X] Back", COL_ACCENT)
        cx = x
        for i, c in enumerate(COMMANDS):
            label = c["name"]
            if i == self.command_idx and self.phase == "COMMAND":
                pyxel.rectb(cx - 2, y - 2, len(label) * 4 + 6, 10, COL_CURSOR)
            self._draw_text(cx, y, label)
            cx += len(label) * 4 + 16  # 適当な横間隔

    def _draw_log(self):
        x = 8
        y = 8
        for i, line in enumerate(self.log):
            self._draw_text(x, y + i * 8, line)

    def _draw_turn(self):
        s = f"TURN {self.turn}  PHASE:{self.phase}"
        self._draw_text(SCREEN_W - len(s) * 4 - 6, SCREEN_H - 10, s, COL_ACCENT)

class App:
    def __init__(self):
        pyxel.init(256, 256, title="Battle", fps=30)
        pyxel.load("my_resource.pyxres") # リソースの読み込み
        self.jp_font = pyxel.Font("umplus_j10r.bdf")
        pyxel.mouse(True)
        
        self.scene = START_SCENE

        self.win = False
        self.battle = None
        self.log = deque(maxlen=LOG_LINES)
        pyxel.run(self.update, self.draw)

    # シーン遷移 ---------------------------------------------
    def to_battle(self):
        self.battle = Battle(WAVES, self.log)
        self.scene = SCENE_BATTLE

    def to_result(self, win: bool):
        self.win = win
        self.scene = SCENE_RESULT

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            
        if self.scene == START_SCENE:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                self.to_battle()
        elif self.scene == SCENE_BATTLE:
            if self.battle:
                self.battle.update()
        elif self.scene == SCENE_RESULT:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                self.scene = START_SCENE  # タイトルに戻る

    def draw(self):
        if self.scene == START_SCENE:
            pyxel.cls(COL_BG)
            pyxel.text(SCREEN_W//2 - 40, SCREEN_H//2 - 10, "DOT BATTLESHIP", COL_TEXT)
            pyxel.text(SCREEN_W//2 - 60, SCREEN_H//2 + 10, "PRESS SPACE TO START", COL_TEXT)
        elif self.scene == SCENE_BATTLE:
            if self.battle:
                self.battle.draw()
        elif self.scene == SCENE_RESULT:
            pyxel.cls(COL_BG)
            result = "VICTORY!" if self.win else "DEFEAT..."
            pyxel.text(SCREEN_W//2 - len(result)*2, SCREEN_H//2 - 10, result, COL_TEXT)
            pyxel.text(SCREEN_W//2 - 60, SCREEN_H//2 + 10, "PRESS SPACE TO TITLE", COL_TEXT)

App()