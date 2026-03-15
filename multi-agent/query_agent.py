"""
查询 Agent：从用户问题中识别货币对，调用 get_exchange_rate，返回结构化汇率结果。
"""

import json
import os
from typing import Any, Optional

from openai import OpenAI

from tools import get_exchange_rate

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "查询两种货币之间的汇率。支持的货币对：USD 与 CNY、EUR 与 JPY（含反向）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "源货币的三字母代码，如 USD、CNY、EUR、JPY",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "目标货币的三字母代码",
                    },
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    }
]

SYSTEM_PROMPT = """你是汇率查询助手。你的唯一能力是：根据用户问题调用 get_exchange_rate 查询汇率。
- 仅当用户明确在问「汇率/兑换/换算」且能推断出两种货币时，才调用 get_exchange_rate。
- 货币请使用标准三字母代码：USD、CNY、EUR、JPY。
- 若无法确定货币对，不要调用工具。"""


class QueryAgent:
    """负责查汇率的 Agent，只输出结构化结果（货币对 + 汇率），不生成自然语言建议。"""

    def __init__(self, verbose: bool = True, api_key: Optional[str] = None):
        self.verbose = verbose
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("未设置 DEEPSEEK_API_KEY，请在环境变量中设置。")
        self.client = OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")
        self.model = "deepseek-chat"

    def _log(self, message: str):
        if self.verbose:
            print(f"[QueryAgent-Log] {message}")

    def run(self, user_input: str) -> dict[str, Any]:
        """
        解析用户输入，调用汇率工具，返回 {"from_currency", "to_currency", "rate"} 或 {"error": str}。
        """
        self._log(f"收到用户输入：{user_input!r}")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            self._log(f"API 调用失败：{e}")
            return {"error": str(e)}

        msg = response.choices[0].message

        if not getattr(msg, "tool_calls", None) or len(msg.tool_calls) == 0:
            self._log("未识别到可查询的货币对，返回空结果。")
            return {"error": "无法从问题中识别货币对，请明确说出两种货币（如美元兑人民币）。"}

        for tc in msg.tool_calls:
            if tc.function.name != "get_exchange_rate":
                continue
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                continue
            from_c = args.get("from_currency", "")
            to_c = args.get("to_currency", "")
            rate = get_exchange_rate(from_c, to_c)
            if rate is not None:
                result = {"from_currency": from_c, "to_currency": to_c, "rate": rate}
                self._log(f"查询结果：{result}")
                return result
            return {"error": f"暂不支持该货币对 {from_c}/{to_c} 的查询。"}

        return {"error": "未能完成汇率查询。"}
