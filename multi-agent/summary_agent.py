"""
总结 Agent：将「汇率数据 + 建议」整理成统一、易读的格式（如「汇率：…；建议：…」），作为最终回复。
"""

import os
from typing import Any, Optional

from openai import OpenAI

SYSTEM_PROMPT = """你是回复总结助手。根据提供的汇率数据和建议内容，整理成一段简洁、格式清晰的最终回复给用户。
- 若存在汇率数据，先简要写出汇率（如「当前 1 USD ≈ 7.2 CNY」），再写建议。
- 若只有错误或说明，则直接整理成一句友好、清晰的说明。
- 输出不要带「汇率：」「建议：」等标题式前缀，用自然的一段话即可。总长度控制在 2～4 句。"""


class SummaryAgent:
    """将查询结果与建议汇总成最终一段话的 Agent。"""

    def __init__(self, verbose: bool = True, api_key: Optional[str] = None):
        self.verbose = verbose
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("未设置 DEEPSEEK_API_KEY，请在环境变量中设置。")
        self.client = OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")
        self.model = "deepseek-chat"

    def _log(self, message: str):
        if self.verbose:
            print(f"[SummaryAgent-Log] {message}")

    def run(
        self,
        user_input: str,
        query_result: dict[str, Any],
        advice_text: str,
    ) -> str:
        """
        根据 query_result、advice_text 和用户问题，生成格式统一的最终回复。
        """
        self._log("汇总汇率与建议，生成最终回复。")

        if "error" in query_result:
            data_desc = f"查询结果：{query_result['error']}"
        else:
            data_desc = (
                f"汇率：1 {query_result['from_currency']} = {query_result['rate']} {query_result['to_currency']}"
            )

        prompt = (
            f"用户问题：{user_input}\n"
            f"{data_desc}\n"
            f"建议/说明：{advice_text}\n"
            "请整理成一段简洁、自然的最终回复（2～4 句）。"
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
            return f"汇总时出错：{e}"

        self._log("最终回复已生成。")
        return reply or advice_text
