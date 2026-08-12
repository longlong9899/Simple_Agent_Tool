# Simple_Agent_Tool

简单的 Agent 工具库：基于 DeepSeek 的对话、带历史的消息管理、知识库向量化检索、以及工具（Function Calling）调用能力。

## 特性

- **对话**：`Model`（带历史）、`Model_no_history`（单轮）、`AsyncModel`（异步）
- **工具调用**：`Model_With_Tool` + `BaseTool`，支持 OpenAI Function Calling；`AsyncModel_With_Tool`（异步）
- **异步支持**：`AsyncModel` / `AsyncModel_With_Tool`，底层 `AsyncOpenAI`
- **消息体系**：`HumanMessage` / `SystemMessage` / `AIMMessage` / `AICallMessage` / `ToolMessage`
- **历史持久化**：按 `user_id` 自动保存对话历史到本地 JSON（带文件锁，进程安全）
- **上下文压缩**：`ContextManager` 摘要压缩 / 滚动窗口，防止历史无限增长
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

### 3.5 异步对话

```python
import asyncio
from simple_agent_tool import AsyncModel
from pathlib import Path

async def main():
    m = AsyncModel(
        api_key="sk-xxx",
        base_url="https://api.deepseek.com",
        model_name="deepseek-chat",
        model_prompt="你是一个助手",
        user_id="user1",
        save_path=Path("./chat_history"),
    )
    print(await m.invoke("你好"))    # 异步调用，需 await

asyncio.run(main())
```

> 异步类通过继承实现：`AsyncModel(Model)`、`AsyncModel_With_Tool(Model_With_Tool)`，底层使用 `AsyncOpenAI` 客户端，`save/load` 保持同步。适合 FastAPI 等服务端场景。

### 4. 上下文压缩（v2 新增）

```python
from simple_agent_tool import Model, ContextManager
from pathlib import Path

m = Model(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    model_prompt="你是一个助手",
    user_id="user1",
    save_path=Path("./chat_history"),
)

# 创建压缩器（默认配置）
cm = ContextManager(m)
# 可自定义配置
# cm.config(max_context_token=64000, summary_prompt="自定义摘要提示词...")

# 调用方自行判断是否需要压缩
if cm.is_context_over():
    cm.compress()          # 摘要压缩：旧对话 → 摘要，写入 history_summary_prompt
    # cm.compress_by_delete()   # 或滚动窗口：直接删除旧对话
```

**压缩原理**：
- 摘要压缩：将早期对话交给摘要模型提炼为摘要，存入 `history_summary_prompt`，之后每次 `invoke` 会自动拼进系统提示词（`模型提示词 + 摘要`）
- 滚动窗口：按 `reverse_ratio` 比例直接丢弃早期消息
- 摘要永远只保留一条，覆盖更新，不会膨胀
- `compress()` 可重写——继承 `ContextManager` 自定义压缩策略

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
| `AsyncModel` | 异步版 `Model`（继承），`await invoke()` | `str` 或 `dict` |
| `AsyncModel_With_Tool` | 异步版 `Model_With_Tool`（继承），`await run()` | `(content, tool_calls)` 元组 |

### 上下文压缩类（`ContextManager.py`，v2 新增）

| 方法 | 说明 |
|---|---|
| `compress()` | 默认摘要压缩（可重写） |
| `compress_by_summary()` | 早期对话 → 摘要，存入 `history_summary_prompt` |
| `compress_by_delete()` | 滚动窗口，按 `reverse_ratio` 删除早期消息 |
| `is_context_over()` | 判断上下文是否超阈值 |
| `config()` | 自定义阈值 / 摘要提示词 / 摘要模型 |
| `clear()` | 清空历史 |

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

用于 RAG（检索增强生成）：把文档切块 → 向量化 → 存库，查询时按语义相似度检索最相关的片段。

### 原理

```
docx 文档 → 大模型语义分块（每段 200~300 字）→ 向量模型编码 → 存入 JSON
用户提问 → 向量编码 → 余弦相似度检索 → 返回最相似的 top_k 片段
```

向量模型使用 `BAAI/bge-small-zh-v1.5`（中文优化），**首次使用自动从 HuggingFace 下载，约 100MB**，之后走本地缓存。

### 核心类与函数

| 类/函数 | 说明 |
|---|---|
| `TextVector` | 单条文本向量。`TextVector(text)` 编码成向量，`to_dict()` 转字典存储 |
| `KnowledgeVector` | 知识库容器。加载/保存向量列表，提供构建与检索方法 |
| `cosine_similarity(a, b)` | 余弦相似度计算，返回 0~1 的相似度分数 |

### 初始化知识库

```python
from simple_agent_tool.vector import KnowledgeVector, TextVector
from pathlib import Path

# 知识库数据保存在 kb.json（文件锁保护，进程安全）
kb = KnowledgeVector(Path("./kb.json"))
```

### 方式一：从 docx 构建（自动分块 + 向量化）

```python
# 传入大模型凭据，内部用大模型把文档按语义切成 200~300 字/段再向量化
kb.create_by_docx(
    read_file_path="知识文档.docx",
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
)
```

### 方式二：手动添加

```python
tv = TextVector("这是一段知识文本")
kb.add(tv)               # 编码并入库（自动保存）
```

### 检索

```python
# 把查询语句编码成向量，检索最相似的 top_k 条
query_vec = TextVector("用户的问题是什么？").vector
results = kb.search(query_vec, top_k=3)

for r in results:
    print(r['text'])     # 命中的文本片段
    print(r['similarity'])  # 相似度分数
```

### 存储格式

`kb.json` 内容为向量列表：

```json
[
  {
    "vector": [0.0123, -0.0456, ...],   # 768 维浮点数组
    "text": "第一段知识文本"
  },
  {
    "vector": [0.0234, -0.0789, ...],
    "text": "第二段知识文本"
  }
]
```

### 注意事项

- `create_by_text` / `create_by_markdown` 目前为预留接口，尚未实现
- 首次调用 `TextVector` 会下载向量模型（约 100MB）
- 检索的 `vector` 参数需是 numpy 数组（用 `TextVector(...).vector` 获得）

## 历史存储

对话历史按 `save_path / user_id.json` 保存（v2 格式）：

```json
{
  "history_message": [{ "role": "user", "content": "你好" }, ...],
  "history_summary_prompt": "早期对话摘要（v2 新增）",
  "version": 2
}
```

- `history_summary_prompt` 保存上下文压缩产生的摘要，重启后自动恢复
- 兼容 v1 旧格式（纯消息列表），加载时自动识别

## 缺点

- Model_With_Tool 类不支持返回dict格式的模型回复
- 异步类通过复制实现，与同步类存在代码重复（将来可抽公共基类）
- 上下文压缩需调用方手动触发，不会自动执行
- 不支持自定义模型参数（如 temperature, top_p, max_tokens 等）
- 因为导入了sentence-transformers去实现知识库，所以包的体积会比较大

## License

MIT
