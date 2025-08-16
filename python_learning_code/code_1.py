from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
import re
import heapq

# ---------- 例外定義 ----------
class ParseError(Exception):
    """ログ1行の構文が不正なときに送出する例外"""

# ---------- データ構造 ----------
@dataclass(frozen=True)
class LogEvent:
    user: str
    level: str
    ts: datetime

# ---------- パーサ ----------
LINE_RE = re.compile(r"^\[(?P<ts>[\d\-: ]+)\]\s+(?P<user>\w+)\s+(?P<level>INFO|WARN|ERROR)\b")

def parse_line(line: str) -> LogEvent:
    # セイウチ演算子で1行の正規表現マッチ結果を“その場で”代入しつつ判定
    if not (m := LINE_RE.match(line.strip())):
        raise ParseError(f"invalid line: {line!r}")
    # tsの解析に失敗したら例外を送出（呼び出し側で握る）
    ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
    return LogEvent(user=m.group("user"), level=m.group("level"), ts=ts)

# ---------- コア処理：直近5分のエラー多発ユーザー検出 ----------
def detect_bursts(lines: list[str], window: timedelta = timedelta(minutes=5), err_threshold: int = 3):
    """
    ストリーム的にログを走査し、ユーザーごとに直近window内のERROR数を数える。
    閾値を超えたユーザーを都度yieldする（重複通知抑止のため直近で通知済ならスキップ）。
    """
    errors_by_user: dict[str, deque[datetime]] = defaultdict(deque)  # ユーザー→ERROR時刻のキュー
    last_alerted_at: dict[str, datetime] = {}  # ユーザー→最後に通知した時刻
    totals = Counter()  # ついでに全体統計も取る（INFO/WARN/ERRORの出現回数）

    for line in lines:
        try:
            event = parse_line(line)
        except ParseError:
            # 不正行はスキップしつつ続行（堅牢性）
            continue

        totals[event.level] += 1

        # ERRORだけ時間窓で管理
        if event.level == "ERROR":
            dq = errors_by_user[event.user]
            dq.append(event.ts)
            # 5分窓からはみ出た古いエラーを左から削除
            while dq and (event.ts - dq[0]) > window:
                dq.popleft()

            # 閾値到達かつ、直近通知から1分以上あける（スパム抑止）
            if len(dq) >= err_threshold:
                if (last := last_alerted_at.get(event.user)) is None or (event.ts - last) >= timedelta(minutes=1):
                    last_alerted_at[event.user] = event.ts
                    yield {"user": event.user, "count": len(dq), "at": event.ts}

    # まとめ統計も返せるように最後に付帯情報をyield
    yield {"summary": True, "totals": dict(totals)}

# ---------- ユーティリティ：トップNユーザー（累計ERROR） ----------
def top_error_users(lines: list[str], top_n: int = 3):
    err_counts = Counter()
    for line in lines:
        try:
            ev = parse_line(line)
        except ParseError:
            continue
        if ev.level == "ERROR":
            err_counts[ev.user] += 1
    # heapq.nlargestで上位N件（(ユーザー, 件数)）
    return heapq.nlargest(top_n, err_counts.items(), key=lambda kv: kv[1])

# ---------- 動作例 ----------
if __name__ == "__main__":
    raw = [
        "[2025-08-15 12:00:00] alice INFO",
        "[2025-08-15 12:01:00] bob ERROR",
        "[2025-08-15 12:01:30] bob ERROR",
        "[2025-08-15 12:03:00] bob ERROR",      # ← ここで5分窓内3件到達＝検出
        "[2025-08-15 12:03:10] alice WARN",
        "[2025-08-15 12:04:00] charlie ERROR",
        "[2025-08-15 12:04:10] bob ERROR",      # ← 再度4件目だが1分クールダウン未満なら抑止
        "BROKEN LINE",                           # ← 不正行は握りつぶす
        "[2025-08-15 12:05:10] bob ERROR",      # ← 直近通知から1分以上 → 再通知
        "[2025-08-15 12:06:00] alice ERROR",
        "[2025-08-15 12:06:30] alice ERROR",
        "[2025-08-15 12:06:50] alice ERROR",    # ← aliceも検出
    ]

    # バースト検出（ストリーム結果を逐次消費）
    for notice in detect_bursts(raw):
        if "summary" in notice:
            print("SUMMARY:", notice["totals"])
        else:
            print(f"[ALERT] user={notice['user']} count={notice['count']} at={notice['at'].time()}")

    # 累計エラーの上位ユーザー
    print("TOP:", top_error_users(raw, top_n=2))
