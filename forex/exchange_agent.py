"""
汇率查询 Agent：使用 DeepSeek 大模型进行意图理解与工具调用。
运行前请设置环境变量 DEEPSEEK_API_KEY（在 https://platform.deepseek.com/api_keys 申请）。
"""

import json
import os
from typing import Optional

from openai import OpenAI

# ===== 工具层：模拟“外部系统 / API” =====

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


# ===== 供 DeepSeek 调用的工具定义（OpenAI 兼容格式） =====

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

SYSTEM_PROMPT = """你是汇率查询助手。你的能力只有：根据用户问题调用 get_exchange_rate 查询汇率。
- 仅当用户明确在问「汇率 / 兑换 / 换算」且能推断出两种货币时，才调用 get_exchange_rate。
- 货币请使用标准三字母代码：USD（美元）、CNY（人民币）、EUR（欧元）、JPY（日元）等。
- 若用户问的不是汇率，或无法确定货币对，请用简短自然语言回复，说明你只支持查汇率，并举例说明如何提问。"""


# ===== Agent 层：DeepSeek 驱动 =====


class ExchangeAgent:
    def __init__(self, verbose: bool = True, api_key: Optional[str] = None):
        self.verbose = verbose
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError(
                "未设置 DEEPSEEK_API_KEY。请在环境变量中设置，或在 https://platform.deepseek.com/api_keys 申请后填入。"
            )
        self.client = OpenAI(
            api_key=key,
            base_url="https://api.deepseek.com/v1",
        )
        self.model = "deepseek-chat"

    def _log(self, message: str):
        if self.verbose:
            print(f"[Agent-Log] {message}")

    def handle(self, user_input: str) -> str:
        """
        Agent 主入口：将用户输入交给 DeepSeek，按需执行工具并返回最终回复。
        """
        self._log("=" * 50)
        self._log(f"收到用户输入：{user_input!r}")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        # 第一轮：让模型决定是否调用工具
        self._log("调用 DeepSeek：意图识别与是否使用工具。")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            self._log(f"DeepSeek API 调用失败：{e}")
            return f"调用大模型时出错：{e}"

        msg = response.choices[0].message
        self._log(f"模型本轮是否请求调用工具：{bool(getattr(msg, 'tool_calls', None))}")

        # 无工具调用：直接返回模型回复
        if not getattr(msg, "tool_calls", None) or len(msg.tool_calls) == 0:
            self._log("模型未请求工具，直接采用文本回复。")
            return (msg.content or "").strip() or "（模型未返回内容）"

        # 将带 tool_calls 的 assistant 消息加入对话（API 要求为 dict）
        assistant_msg = {
            "role": "assistant",
            "content": msg.content or None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        }
        messages.append(assistant_msg)

        # 执行工具调用并追加 tool 结果消息
        for tc in msg.tool_calls:
            name = tc.function.name
            self._log(f"执行工具调用：{name}({tc.function.arguments})")
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                self._log("工具参数 JSON 解析失败，跳过该调用。")
                continue
            if name == "get_exchange_rate":
                rate = get_exchange_rate(
                    args.get("from_currency", ""),
                    args.get("to_currency", ""),
                )
                result = json.dumps({"rate": rate, "from": args.get("from_currency"), "to": args.get("to_currency")})
            else:
                result = json.dumps({"error": f"未知工具: {name}"})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

        # 第二轮：把工具结果交给模型，生成最终自然语言回复
        self._log("调用 DeepSeek：根据工具结果生成最终回复。")
        try:
            response2 = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except Exception as e:
            self._log(f"DeepSeek 第二轮调用失败：{e}")
            return f"生成回复时出错：{e}"

        reply = (response2.choices[0].message.content or "").strip()
        self._log("已得到最终回复。")
        return reply or "（模型未返回内容）"


def main():
    try:
        agent = ExchangeAgent(verbose=True)
    except ValueError as e:
        print(e)
        return
    print("汇率查询 Agent（DeepSeek）示例（输入 q 退出）\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("Agent：再见！")
            break

        reply = agent.handle(user_input)
        print("Agent：", reply)
        print()


if __name__ == "__main__":
    main()
