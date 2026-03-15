"""
多 Agent 协作示例：查询 Agent → 建议 Agent → 总结 Agent。
用户输入经三阶段处理，得到格式统一的最终回复。
运行前请设置环境变量 DEEPSEEK_API_KEY。
"""

from advice_agent import AdviceAgent
from query_agent import QueryAgent
from summary_agent import SummaryAgent


def main():
    try:
        query_agent = QueryAgent(verbose=True)
        advice_agent = AdviceAgent(verbose=True)
        summary_agent = SummaryAgent(verbose=True)
    except ValueError as e:
        print(e)
        return

    print("多 Agent 汇率与建议示例（查询 → 建议 → 总结）")
    print("输入 q 退出\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("再见！")
            break

        print()
        # 阶段 1：查询汇率
        query_result = query_agent.run(user_input)
        # 阶段 2：根据汇率给建议
        advice_text = advice_agent.run(user_input, query_result)
        # 阶段 3：汇总成最终回复
        final_reply = summary_agent.run(user_input, query_result, advice_text)

        print()
        print("Agent：", final_reply)
        print()


if __name__ == "__main__":
    main()
