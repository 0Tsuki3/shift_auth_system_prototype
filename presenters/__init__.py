# presenters package
"""
プレゼンター層（表示用データ整形）

Serviceから取得したデータを、
HTMLで表示しやすい形に整形します。

各Presenterは以下の機能を提供:
- format_for_xxx: 特定の表示形式に整形
- calculate: 計算処理
"""

from .shift_presenter import ShiftPresenter

__all__ = ['ShiftPresenter']

