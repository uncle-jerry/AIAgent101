# 多 Agent 协作示例（方向四：三 Agent 流水线）

在 [forex](../forex/) 单 Agent + 工具的基础上，本示例展示**三个 Agent 顺序协作**：  
**查询 Agent → 建议 Agent → 总结 Agent**，完成「查汇率 → 给建议 → 整理成统一格式」的流水线。

## 功能说明

- **查询 Agent（Query Agent）**：从用户问题中识别货币对，调用 `get_exchange_rate` 工具，返回结构化结果（货币对 + 汇率）。
- **建议 Agent（Advice Agent）**：根据汇率和用户问题，生成一两句自然语言建议（如是否适合换汇、仅供参考等）。
- **总结 Agent（Summary Agent）**：将「汇率数据 + 建议」整理成一段简洁、格式统一的最终回复（如先写汇率再写建议）。

用户只需输入一句（如「美元兑人民币汇率多少，现在换汇合适吗？」），经三阶段后得到一条格式统一、易读的回复。

## 与 forex 的对比

| 维度     | forex              | multi-agent（本示例）                    |
|----------|--------------------|-----------------------------------------|
| Agent 数 | 1                  | 3（查询 / 建议 / 总结）                 |
| 流程     | 用户 → 工具 → 回复 | 用户 → 查汇率 → 给建议 → 汇总成回复     |
| 工具     | get_exchange_rate  | 同左，仅查询 Agent 调用                 |

## 环境要求

- Python 3.8+
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)

## 安装与运行

```bash
cd multi-agent
pip install -r requirements.txt
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
python main.py
```

运行后在命令行输入自然语言进行汇率与换汇建议查询，输入 `q` 退出。

## 使用示例

```
你：美元兑人民币汇率多少，现在换汇合适吗？

[QueryAgent-Log] 收到用户输入：'美元兑人民币汇率多少，现在换汇合适吗？'
[Tool:get_exchange_rate] 输入参数 from=USD, to=CNY
[Tool:get_exchange_rate] 返回结果 rate=7.2
[QueryAgent-Log] 查询结果：{'from_currency': 'USD', 'to_currency': 'CNY', 'rate': 7.2}
[AdviceAgent-Log] 根据查询结果生成建议。
[AdviceAgent-Log] 建议已生成。
[SummaryAgent-Log] 汇总汇率与建议，生成最终回复。
[SummaryAgent-Log] 最终回复已生成。

Agent：当前 1 USD 约等于 7.2 CNY，仅供参考，请以银行实时汇率为准后再做换汇决策。
```

## 目录结构

```
multi-agent/
├── README.md         # 本说明
├── requirements.txt  # 依赖（openai）
├── tools.py          # 共享汇率工具 get_exchange_rate
├── query_agent.py    # 查询 Agent
├── advice_agent.py   # 建议 Agent
├── summary_agent.py  # 总结 Agent
└── main.py           # 主入口：串联三 Agent
```

## License

MIT
