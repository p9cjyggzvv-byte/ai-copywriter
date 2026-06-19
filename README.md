# 🤖 AI 文案工具集

[![在线体验](https://img.shields.io/badge/%F0%9F%9A%80-%E5%9C%A8%E7%BA%BF%E4%BD%93%E9%AA%8C-2563eb?style=for-the-badge)](https://ai-copywriter-production-0cfd.up.railway.app)

一套基于 DeepSeek API 的 AI 内容生成工具集，支持文案生成、批量处理、一文多发、知识库问答、AI Agent。

## 功能

| 命令 | 功能 |
|------|------|
| `python main.py copy "产品名"` | 生成朋友圈/小红书/抖音等文案 |
| `python main.py batch [文件.csv]` | 批量处理（每个项目可定制风格/人群/卖点） |
| `python main.py matrix "原文" [平台]` | 一文多发（一段内容改6个平台版本） |
| `python main.py ask 文件 "问题"` | 基于文档回答问题 |
| `python main.py agent "任务"` | AI Agent 自动拆解执行多步任务 |
| `python main.py calc "计算式"` | AI 计算器（Function Calling 示例） |
| `python main.py web` | 启动 Streamlit 网页界面 |

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/p9cjyggzvv-byte/ai-copywriter.git
cd ai-copywriter

# 2. 安装依赖
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt

# 3. 设置 API Key
echo 'DEEPSEEK_API_KEY=你的key' > .env

# 4. 运行
python main.py copy "你的产品名"
```

## 项目结构

```
ai-copywriter/
├── src/                # 源代码
│   ├── generators.py   # 文案生成、批量、矩阵、问答
│   ├── agents.py       # Agent + Function Calling
│   ├── rag.py          # RAG 知识库问答系统
│   ├── react_agent.py  # ReAct 模式 Agent
│   ├── robust_generator.py  # 工程示范（错误处理+日志+重试）
│   └── utils.py        # 公共工具函数
├── data/               # 数据文件
├── main.py             # 统一入口
├── app.py              # Streamlit 网页版
└── deploy/             # 部署配置
```

## 技术栈

- Python 3.13
- DeepSeek API（兼容 OpenAI 格式）
- Streamlit（网页界面）
- BM25 关键词检索（RAG 系统）

## 学习路线

对应的教学课程在 `lessons/` 目录中，从 API 调用到完整 RAG 系统，共 15 节课。
