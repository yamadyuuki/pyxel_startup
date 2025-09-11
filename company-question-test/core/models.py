from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class Question:
    ticker: str
    name: str
    span: Tuple[str, str]
    prices: List[int]
    choices: List[str]
    blurb: str
    # 追加
    index_label: Optional[str] = None
    index_prices: Optional[List[int]] = None
