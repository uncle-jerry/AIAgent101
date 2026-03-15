"""
建议 Agent：根据汇率查询结果和用户问题，生成一句简短的自然语言建议（是否适合换汇等）。
"""

import os
from typing import Any, Optional

from openai import OpenAI

SYSTEM_PROMPT = """你是换汇建议助手。根据给定的汇率数据以及用户的问题，用一两句自然语言给出简短建议。
- 若用户问「是否适合换汇」「现在换合适吗」等，可基于汇率给出中性、客观的建议（如「仅供参考，请以银行实时汇率为准」）。
- 不要编造汇率数字，只使用提供的数据。
- 语气简洁、友好。"""


class AdviceAgent:
    """根据汇率与用户问题生成建议的 Agent，不调用工具。"""

    def __init__(self, verbose: bool = True, api_key: Optional[str] = None):
        self.verbose = verbose
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("未设置 DEEPSEEK_API_KEY，请在环境变量中设置。")
        self.client = OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")
        self.model = "deepseek-chat"

    def _log(self, message: str):
        if self.verbose:
            print(f"[AdviceAgent-Log] {message}")

    def run(self, user_input: str, query_result: dict[str, Any]) -> str:
        """
        根据 query_result（含 from_currency, to_currency, rate 或 error）和用户问题，生成建议文本。
        """
        self._log("根据查询结果生成建议。")

        if "error" in query_result:
            self._log(f"查询阶段有误：{query_result['error']}，仅做说明性回复。")
            prompt = f"用户问题：{user_input}\n查询阶段结果：{query_result['error']}\n请用一句话说明无法给出汇率建议的原因，并提示用户如何正确提问。"
        else:
            prompt = (
                f"用户问题：{user_input}\n"
                f"汇率数据：1 {query_result['from_currency']} = {query_result['rate']} {query_result['to_currency']}\n"
                "请用一两句话给出简短、客观的换汇建议。"
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            reply = (response.choices[0].message.content or "").strip()
        except Exception as e:
            self._log(f"API 调用失败：{e}")
            return f"生成建议时出错：{e}"

        self._log("建议已生成。")
        return reply or "（未生成建议）"
