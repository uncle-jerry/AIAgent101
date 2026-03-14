# Agent101

一个用于展示**大语言模型 Agent 工作原理**的极简示例：通过自然语言查询汇率，由 DeepSeek 完成意图理解与工具调用。

## 功能说明

- **场景**：用户用自然语言询问汇率（如「美元兑人民币的汇率是多少」），Agent 理解后调用汇率工具并返回结果。
- **原理展示**：
  - 大模型负责：理解用户意图、决定是否调用工具、从文本中抽取参数（货币对）、根据工具结果生成自然语言回复。
  - 工具层负责：执行 `get_exchange_rate(from_currency, to_currency)`（当前为本地字典，可替换为真实 API）。
- **可观察性**：运行时可打印 `[Agent-Log]` 与 `[Tool:get_exchange_rate]` 等日志，便于理解 Agent 的思考与调用过程。

## 环境要求

- Python 3.8+
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)（用于调用 DeepSeek 大模型）

## 安装与运行

```bash
# 克隆或进入项目目录
cd Agent101

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（必填）
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"

# 运行
python exchange_agent.py
```

运行后可在命令行输入自然语言进行汇率查询，输入 `q` 退出。

## 使用示例

```
你：帮我查一下美元兑人民币的汇率
[Agent-Log] 收到用户输入：'帮我查一下美元兑人民币的汇率'
[Agent-Log] 调用 DeepSeek：意图识别与是否使用工具。
[Tool:get_exchange_rate] 输入参数 from=USD, to=CNY
[Tool:get_exchange_rate] 返回结果 rate=7.2
Agent：当前 1 USD 约等于 7.2 CNY ...
```

支持的货币对（Demo 数据）：USD/CNY、EUR/JPY 及其反向。

## 项目结构

```
Agent101/
├── README.md           # 本说明
├── requirements.txt    # Python 依赖（openai）
└── exchange_agent.py   # 汇率查询 Agent 主程序
```

## 技术说明

- 使用 **DeepSeek** 作为大模型后端，通过 **OpenAI 兼容 API**（`base_url` 指向 DeepSeek）调用，因此依赖 `openai` 包。
- 工具调用采用 OpenAI 标准的 Function Calling 格式，由模型决定是否调用 `get_exchange_rate` 及传入参数。

## License

MIT
