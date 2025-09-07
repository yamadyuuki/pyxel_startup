# core/models.py
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Question:
    ticker: str
    name: str
    span: Tuple[str, str]
    prices: List[int]        # 正規化int（例：基準=10000）
    choices: List[str]       # 4択（ticker/表示名のどちらでも良いが統一）
    blurb: str               # 解説（ゲーム内は要約版）
