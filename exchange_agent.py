from typing import Optional, Tuple

# ===== 工具层：模拟“外部系统 / API” =====

EXCHANGE_RATE_DB = {
    ("USD", "CNY"): 7.2,
    ("CNY", "USD"): 1 / 7.2,
    ("EUR", "JPY"): 160.0,
    ("JPY", "EUR"): 1 / 160.0,
}


def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """
    模拟一个汇率查询工具。
    在真实 Agent 里，这里可能会请求外部 API。
    """
    print(f"[Tool:get_exchange_rate] 输入参数 from={from_currency}, to={to_currency}")
    rate = EXCHANGE_RATE_DB.get((from_currency.upper(), to_currency.upper()))
    print(f"[Tool:get_exchange_rate] 返回结果 rate={rate}")
    return rate


# ===== Agent 层：负责“理解 + 决策 + 调用工具 + 组织回答” =====

CURRENCY_NAME_MAP = {
    # 英文缩写
    "USD": "USD",
    "CNY": "CNY",
    "RMB": "CNY",
    "EUR": "EUR",
    "JPY": "JPY",
    # 中文别名
    "美元": "USD",
    "美金": "USD",
    "人民币": "CNY",
    "欧元": "EUR",
    "日元": "JPY",
}


class ExchangeAgent:
    def __init__(self, verbose: bool = True):
        """
        verbose=True 时，会打印详细的“思考过程日志”。
        """
        self.verbose = verbose

    def _log(self, message: str):
        if self.verbose:
            print(f"[Agent-Log] {message}")

    def _extract_currencies(self, text: str) -> Optional[Tuple[str, str]]:
        """
        模拟“大模型从自然语言中抽取结构化参数”的过程。
        这里只做简单规则：在文本中按出现顺序找两种货币。
        """
        self._log(f"开始从文本中抽取货币信息，原始文本：{text!r}")
        found_codes = []
        for name, code in CURRENCY_NAME_MAP.items():
            if name.lower() in text.lower():
                self._log(f"在文本中匹配到货币名称 {name!r} → 标准代码 {code!r}")
                if code not in found_codes:
                    found_codes.append(code)

        self._log(f"抽取到的货币代码列表：{found_codes}")
        if len(found_codes) >= 2:
            from_currency, to_currency = found_codes[0], found_codes[1]
            self._log(f"决定使用前两个不同货币代码：from={from_currency}, to={to_currency}")
            return from_currency, to_currency
        else:
            self._log("抽取失败：找到的货币种类不足 2 种")
            return None

    def handle(self, user_input: str) -> str:
        """
        Agent 对外的主入口：
        1. 理解用户想干什么（这里简单假设只支持“查汇率”）
        2. 从文本中抽取 from / to 货币
        3. 决定是否要调用工具
        4. 调用工具拿到结果，组织回复
        """
        self._log("=" * 50)
        self._log(f"收到用户输入：{user_input!r}")

        # （1）判断是否是查汇率相关问题（极简示例）
        intent_keywords = ["汇率", "rate", "兑换", "换算"]
        is_exchange_query = any(kw in user_input for kw in intent_keywords)
        self._log(f"意图识别：是否为汇率查询？→ {is_exchange_query}")

        if not is_exchange_query:
            self._log("判断结果：不是汇率查询，走‘知识问答/拒绝’分支。")
            return "这个小 Agent 目前只会查汇率，你可以试着问：‘帮我查一下美元兑人民币的汇率’。"

        # （2）抽取货币信息（模拟 LLM 做参数抽取）
        self._log("进入参数抽取阶段：准备分析涉及到哪些货币。")
        currencies = self._extract_currencies(user_input)
        if not currencies:
            self._log("参数抽取失败：无法确定 from / to 货币。")
            return "我没看懂你要查询哪些货币之间的汇率，请试着说：‘美元兑人民币的汇率’。"

        from_currency, to_currency = currencies
        self._log(f"参数抽取成功：from={from_currency}, to={to_currency}")

        # （3）决定要调用哪个工具（这里只有一个工具）
        self._log("规划阶段：决定调用工具 get_exchange_rate(from, to)。")
        rate = get_exchange_rate(from_currency, to_currency)

        # （4）检查工具返回结果，并组织自然语言回复
        if rate is None:
            self._log("工具返回 None，说明当前 Demo 数据库不支持这一对货币。")
            return f"暂时不支持 {from_currency} 到 {to_currency} 这一对汇率查询（Demo 里只支持 USD/CNY、EUR/JPY）。"

        self._log(f"工具调用成功，得到汇率：1 {from_currency} = {rate:.4f} {to_currency}")
        self._log("进入回答生成阶段：组织最终自然语言输出。")
        return f"当前我查到 1 {from_currency} ≈ {rate:.4f} {to_currency}（示例数据，仅用于演示 Agent 调用工具和思考过程）。"


def main():
    agent = ExchangeAgent(verbose=True)
    print("汇率查询 Agent 示例（输入 q 退出）\n")

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

