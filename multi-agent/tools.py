"""
共享工具层：汇率查询。与 forex 示例保持一致，便于对比。
"""

from typing import Optional

EXCHANGE_RATE_DB = {
    ("USD", "CNY"): 7.2,
    ("CNY", "USD"): 1 / 7.2,
    ("EUR", "JPY"): 160.0,
    ("JPY", "EUR"): 1 / 160.0,
}


def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """
    汇率查询工具。Demo 使用本地字典，实际可替换为真实 API。
    """
    print(f"[Tool:get_exchange_rate] 输入参数 from={from_currency}, to={to_currency}")
    rate = EXCHANGE_RATE_DB.get((from_currency.upper(), to_currency.upper()))
    print(f"[Tool:get_exchange_rate] 返回结果 rate={rate}")
    return rate
