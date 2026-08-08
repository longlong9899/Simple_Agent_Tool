# Simple_Agent_Tool

简单的 Agent 工具：DeepSeek 对话、历史消息管理、知识库向量化检索。

## 安装
pip install git+https://github.com/你的用户名/Simple_Agent_Tool.git

## 快速开始
```python
from simple_agent_tool import Model
from pathlib import Path
m = Model(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model_name="deepseek-chat",
    model_prompt="你是一个助手",
    user_id="user1",
    save_path=Path("./chat_history"),
)
print(m.invoke("你好"))