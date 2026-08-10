# Simple_Agent_Tool

简单的 Agent 工具库：基于 DeepSeek 的对话、带历史的消息管理、知识库向量化检索、以及工具（Function Calling）调用能力。

## 特性

- **对话**：`Model`（带历史）、`Model_no_history`（单轮）
- **工具调用**：`Model_With_Tool` + `BaseTool`，支持 OpenAI Function Calling
- **消息体系**：`HumanMessage` / `SystemMessage` / `AIMMessage` / `AICallMessage` / `ToolMessage`
- **历史持久化**：按 `user_id` 自动保存对话历史到本地 JSON（带文件锁，进程安全）
- **知识库**：`KnowledgeVector` 文本向量化 + 余弦相似度检索
- **文件读取**：`ReadFile` 支持 docx / markdown

## 安装

### 方式一：pip 从 GitHub 安装
```bash
pip install git+https://github.com/longlong9899/Simple_Agent_Tool.git
```

### 方式二：本地复制 + requirements
将源码复制到项目目录后：
```bash
pip install -r requirements.txt
```

> 环境要求：Python >= 3.12

## 快速开始

### 1. 基础对话（带历史）

```python
from pathlib import Path
from simple_agent_tool import Model

m = Model(
    api_key="sk-xxx",                          # DeepSeek API Key
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    model_prompt="你是一个乐于助人的助手",
    user_id="user1",                           # 历史按用户隔离
    save_path=Path("./chat_history"),
)
print(m.invoke("你好"))
print(m.invoke("还记得我刚才说了什么吗？"))    # 自动带上历史
```

### 2. 单轮对话（无历史）

```python
from simple_agent_tool import Model_no_history

m = Model_no_history(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    model_prompt="你是助手",
    user_id="user1",
)
print(m.invoke("你好"))
```

### 3. 工具调用（Function Calling）

定义工具——继承 `BaseTool`，重写 `execute`，通过构造函数声明参数 name, description, properties, required：

```python
from simple_agent_tool import Model_With_Tool, BaseTool, ToolCall
from pathlib import Path

class GetWeatherTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="获取指定城市的天气，用户应先提供城市",
            properties={
                "city": {
                    "type": "string",
                    "description": "城市名，如 北京",
                }
            },
            required=["city"],
        )

    def execute(self, arguments: dict) -> str:
        city = arguments["city"]
        return f"{city} 今天晴，28℃"   # 这里可替换为真实天气 API

# 创建模型并注册工具
m = Model_With_Tool(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    model_prompt="你是一个助手",
    user_id="user1",
    Tools=[GetWeatherTool()],
    save_path=Path("./chat_history"),
)
# 之后添加方法
# m.addTool(GetWeatherTool())

# 调用：返回 (内容, 工具调用列表)
content, tool_calls = m.run("北京天气怎么样？")
print(content, tool_calls)

# 若有工具调用，逐条执行并自动写回 tool 消息到历史
for tc in tool_calls:            # tc 是 ToolCall 对象
    m.call_tool(tc)

# 工具执行结果已写入历史，再次调用即可让模型基于结果回答
content, tool_calls = m.run("天气怎么样？")
print(content)
```

> **注意**：`Model_With_Tool.run()` 只执行**一轮**调用。若模型返回了工具调用，需由调用方循环执行 `call_tool` 后再 `run`，直到模型不再请求工具。

## 概览

### 消息类（`Message.py`）

| 类 | role | 用途 |
|---|---|---|
| `HumanMessage` | `user` | 用户消息 |
| `SystemMessage` | `system` | 系统提示词 |
| `AIMMessage` | `assistant` | 模型回复 |
| `AICallMessage` | `assistant` | 模型发起的工具调用（含 tool_calls） |
| `ToolMessage` | `tool` | 工具执行结果 |
| `HistoryMessage` | - | 历史消息管理（add / unpack，自动持久化兼容） |

### 模型类（`Model.py`）

| 类 | 特性 | 返回 |
|---|---|---|
| `Model` | 带历史、可选 JSON 输出 | `str` 或 `dict`（json_output=True 时,返回dict） |
| `Model_no_history` | 单轮、可选 JSON 输出 | `str` 或 `dict` （json_output=True 时,返回dict）|
| `Model_With_Tool` | 工具调用、带历史 | `(content, tool_calls)` 元组 (不支持返回dict) |

### 工具类（`Tool.py`）

| 类 | 用途 |
|---|---|
| `BaseTool` | 工具基类。构造传 `name/description/properties/required`；子类实现 `execute(arguments: dict) -> str`；`to_dict()` 生成 OpenAI tools 格式 |
| `ToolCall` | 一次工具调用的主要数据载体：`tool_call_id` / `tool_name` / `arguments` |

### 其他

| 类 | 文件 | 用途 |
|---|---|---|
| `Data` | `Data.py` | JSON 持久化 |
| `ReadFile` | `ReadFile.py` | 读取 docx / markdown 文本 |
| `TextVector` / `KnowledgeVector` / `cosine_similarity` | `vector.py` | 文本向量化与知识库检索 |

## 知识库（可选）

```python
from simple_agent_tool.vector import KnowledgeVector
from simple_agent_tool import Model
from pathlib import Path

# 初始化知识库（首次使用会自动下载向量模型 BAAI/bge-small-zh-v1.5，约 100MB）
kb = KnowledgeVector(Path("./kb.json"))
```

`KnowledgeVector` 支持：
- `create_by_docx(file, api_key, base_url, model_name)`：用大模型将 docx 按语义分块（200~300 字/段）后向量化入库
- `search(vector, top_k)`：余弦相似度检索
- `add(TextVector)`：手动添加向量

## 历史存储

文件内容为标准 JSON，可直接查看。

## 缺点

- 不支持返回dict格式的模型回复
- 没有实现异步调用
- 没有实现上下文压缩，历史消息会无限增长
- 不支持自定义模型参数（如 temperature, top_p, max_tokens 等）
- 因为导入了sentence-transformers去实现知识库，所以包的体积会比较大

## License

MIT
