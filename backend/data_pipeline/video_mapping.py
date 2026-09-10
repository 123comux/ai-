"""章节 → B 站视频 的权威映射（由 docs/video-mapping-draft.md 自动生成，勿手改）。

背景：原先每门课只配一个 BV、且 video_page 恒为 1，导致同一阶段所有章节播放同一集
（用户反馈「每个视频都是一样的」）。这里逐章指定真实合集的**具体分P**。

生成方式：`cd backend && py gen_video_mapping.py`（读取已评审的映射表 md）。
覆盖情况见模块尾部 `_STATS`；未列入 VIDEO_MAP 的章节视为「视频待补充」，
会清空 video_bv，页面显示待补充提示（当前为 0 条）。
"""

from typing import Dict, List, Tuple

# 章节 id -> (B 站 BV 号, 分P 序号)
VIDEO_MAP: Dict[str, Tuple[str, int]] = {
    # ---- s1-api-dev ----
    "s1-api-c1": ("BV1xr3Mz2EXD", 1),  # OpenAI API 快速上手
    "s1-api-c2": ("BV1xr3Mz2EXD", 58),  # 国产大模型 API
    "s1-api-c3": ("BV1Bq421A74G", 58),  # 关键参数：temperature / top_p / max_tokens
    "s1-api-c4": ("BV1ptXPYREpe", 7),  # 流式输出与错误处理
    "s1-api-c5": ("BV1xr3Mz2EXD", 46),  # AI 开发规范：从脚本到工程
    # ---- s1-llm-basics ----
    "s1-llm-c1": ("BV1h1VbzHER2", 109),  # 什么是大语言模型（LLM）
    "s1-llm-c2": ("BV1fGeAz6Eie", 6),  # Transformer 架构入门
    "s1-llm-c3": ("BV1Bq421A74G", 59),  # 主流大模型与选型
    "s1-llm-c4": ("BV1xr3Mz2EXD", 12),  # Token 与上下文窗口
    "s1-llm-c5": ("BV1Bq421A74G", 8),  # 模型能力与局限性
    # ---- s1-ollama ----
    "s1-ollama-c1": ("BV1h1VbzHER2", 112),  # 本地模型 vs 云端 API
    "s1-ollama-c2": ("BV1h1VbzHER2", 115),  # 安装 Ollama 与拉取模型
    "s1-ollama-c3": ("BV1h1VbzHER2", 122),  # Python / HTTP 调用本地模型
    "s1-ollama-c4": ("BV1h1VbzHER2", 125),  # 本地调试的完整工作流
    # ---- s1-prompt ----
    "s1-prompt-c1": ("BV1xr3Mz2EXD", 14),  # Prompt 基础：一句话说清任务
    "s1-prompt-c2": ("BV1xr3Mz2EXD", 56),  # Few-shot Learning：给示例
    "s1-prompt-c3": ("BV1ptXPYREpe", 5),  # Chain of Thought 思维链
    "s1-prompt-c4": ("BV1xr3Mz2EXD", 20),  # 角色扮演与场景化
    "s1-prompt-c5": ("BV1Bq421A74G", 13),  # Prompt 优化与迭代
    # ---- s2-agent-arch ----
    "s2-arch-c1": ("BV1xr3Mz2EXD", 76),  # ReAct：推理与行动交替
    "s2-arch-c2": ("BV1xr3Mz2EXD", 77),  # Plan and Execute：先规划再执行
    "s2-arch-c3": ("BV1HeZNYMEyf", 4),  # Reflection：自我反思
    "s2-arch-c4": ("BV1jR4k6SEUz", 1),  # Multi-Agent 模式概览
    "s2-arch-c5": ("BV1D7Gm6JE39", 1),  # 架构选型实战
    # ---- s2-agent-core ----
    "s2-core-c1": ("BV1xr3Mz2EXD", 82),  # 什么是 AI Agent
    "s2-core-c2": ("BV1xr3Mz2EXD", 83),  # Agent 的核心能力
    "s2-core-c3": ("BV1xr3Mz2EXD", 81),  # Agent 与 LLM 的区别
    "s2-core-c4": ("BV1Bq421A74G", 98),  # Agent 的应用场景
    "s2-core-c5": ("BV1xr3Mz2EXD", 71),  # 动手：搭一个最小 Agent
    # ---- s2-memory ----
    "s2-mem-c1": ("BV1xr3Mz2EXD", 2),  # 为什么要记忆
    "s2-mem-c2": ("BV1xr3Mz2EXD", 73),  # 短期记忆：对话历史
    "s2-mem-c3": ("BV1xr3Mz2EXD", 36),  # 长期记忆：向量数据库
    "s2-mem-c4": ("BV1xr3Mz2EXD", 79),  # 记忆的检索与更新
    "s2-mem-c5": ("BV1xr3Mz2EXD", 80),  # 综合记忆 Agent
    # ---- s2-tool-calling ----
    "s2-tool-c1": ("BV1xr3Mz2EXD", 84),  # Function Calling 原理
    "s2-tool-c2": ("BV1HeZNYMEyf", 3),  # 工具定义与描述
    "s2-tool-c3": ("BV1xr3Mz2EXD", 85),  # 工具参数解析
    "s2-tool-c4": ("BV1xr3Mz2EXD", 86),  # 工具执行与结果返回
    "s2-tool-c5": ("BV1xr3Mz2EXD", 87),  # 实战：天气查询 Agent
    # ---- s3-agentic-rag ----
    "s3-agc1": ("BV1xr3Mz2EXD", 44),  # 传统 RAG 的局限
    "s3-agc2": ("BV1HeZNYMEyf", 4),  # 核心循环：retrieve → grade → rewrite → generate → check
    "s3-agc3": ("BV1HeZNYMEyf", 2),  # 文档评分与查询重写
    "s3-agc4": ("BV1Bq421A74G", 62),  # 自纠错：幻觉检测与回答检查
    "s3-agc5": ("BV1Bq421A74G", 73),  # 循环刹车与成本控制
    "s3-agc6": ("BV1HeZNYMEyf", 5),  # 实践：自纠错 RAG 服务
    # ---- s3-langchain ----
    "s3-lc-c1": ("BV1xr3Mz2EXD", 48),  # LangChain 设计思想
    "s3-lc-c2": ("BV1xr3Mz2EXD", 68),  # LangChain RAG 线：Loaders 与 Splitters
    "s3-lc-c3": ("BV1xr3Mz2EXD", 69),  # LangChain RAG 线：Embeddings 与 VectorStores
    "s3-lc-c4": ("BV1xr3Mz2EXD", 70),  # LangChain RAG 线：Retrieval Chain
    "s3-lc-c5": ("BV1xr3Mz2EXD", 78),  # LangChain Agent 线：Tool 与 AgentExecutor
    "s3-lc-c6": ("BV1Bq421A74G", 84),  # LangChain Agent 线：Memory 与 RAG 工具
    "s3-lc-c7": ("BV1xr3Mz2EXD", 51),  # LangChain 综合：知识问答 Agent
    # ---- s3-langgraph ----
    "s3-lg-c1": ("BV1z3NY66EY1", 9),  # 核心三件套：State / Node / Edge
    "s3-lg-c2": ("BV1z3NY66EY1", 32),  # 条件路由与手搓 ReAct
    "s3-lg-c3": ("BV1z3NY66EY1", 65),  # Checkpointer：多轮状态记忆
    "s3-lg-c4": ("BV1z3NY66EY1", 88),  # Human-in-the-Loop：人工审批
    "s3-lg-c5": ("BV1KSYx6zEZL", 28),  # LangGraph 综合：客服 Agent「小 G」
    # ---- s3-mcp ----
    "s3-mcp-c1": ("BV1ULJPz4EBD", 2),  # 为什么需要 MCP
    "s3-mcp-c2": ("BV1ULJPz4EBD", 3),  # 核心架构：Client ↔ Server ↔ 工具
    "s3-mcp-c3": ("BV1ULJPz4EBD", 9),  # 使用现成的 MCP Server
    "s3-mcp-c4": ("BV1ULJPz4EBD", 4),  # MCP 在 Agent 生态中的位置
    "s3-mcp-c5": ("BV1ULJPz4EBD", 5),  # 动手：接一个文件系统 Server
    # ---- s3-rag ----
    "s3-rag-c1": ("BV1xr3Mz2EXD", 28),  # RAG 解决的问题
    "s3-rag-c2": ("BV1xr3Mz2EXD", 34),  # 文档加载与文本分块
    "s3-rag-c3": ("BV1xr3Mz2EXD", 32),  # Embedding 与向量数据库
    "s3-rag-c4": ("BV1xr3Mz2EXD", 37),  # 检索 + 回答 + 引用溯源
    "s3-rag-c5": ("BV1Bq421A74G", 54),  # 检索质量进阶优化
    "s3-rag-c6": ("BV1xr3Mz2EXD", 43),  # 实践：企业知识库问答系统
    # ---- s3-skills ----
    "s3-skills-c1": ("BV1ugdgBQED4", 1),  # 为什么要有 Skill
    "s3-skills-c2": ("BV1ahFmzqE9z", 10),  # Skill 的描述与边界
    "s3-skills-c3": ("BV1ahFmzqE9z", 15),  # 多 Skill 协作
    "s3-skills-c4": ("BV1ahFmzqE9z", 14),  # Skill 与工具、RAG 的关系
    "s3-skills-c5": ("BV1ahFmzqE9z", 11),  # 实践：沉淀你自己的 Skill
    # ---- s4-metagpt-autogen ----
    "s4-fw-c1": ("BV1DEivY5Ewe", 1),  # MetaGPT：模拟软件公司
    "s4-fw-c2": ("BV1L36uYZEPz", 2),  # AutoGen：对话式多 Agent
    "s4-fw-c3": ("BV1KSYx6zEZL", 1),  # 框架对比与选型
    "s4-fw-c4": ("BV1Y94y1T7gL", 1),  # 源码与设计思路学习
    "s4-fw-c5": ("BV1L36uYZEPz", 7),  # Demo：一个多 Agent 小任务
    # ---- s4-multi-agent ----
    "s4-ma-c1": ("BV1iR4k6SEpn", 1),  # 五种协作模式
    "s4-ma-c2": ("BV1f6AAzYEMU", 4),  # 通信机制与任务分配
    "s4-ma-c3": ("BV1f6AAzYEMU", 1),  # 角色设计与何时需要多 Agent
    "s4-ma-c4": ("BV1aQMX6oEni", 12),  # 多 Agent 的代价 ⚠️
    "s4-ma-c5": ("BV1f6AAzYEMU", 2),  # 实践：Supervisor 最小 Demo
    # ---- s4-orchestration ----
    "s4-or-c1": ("BV1Bq421A74G", 97),  # 工作流设计
    "s4-or-c2": ("BV1z3NY66EY1", 40),  # 条件分支与循环迭代
    "s4-or-c3": ("BV1z3NY66EY1", 48),  # 错误处理与重试
    "s4-or-c4": ("BV1z3NY66EY1", 44),  # 四大工程化陷阱
    "s4-or-c5": ("BV1z3NY66EY1", 131),  # 实践：带护栏的工作流
    # ---- s5-deploy ----
    "s5-dep-c1": ("BV1zV2QBtE39", 3),  # FastAPI + Uvicorn API 服务
    "s5-dep-c2": ("BV1SmG3zAEkF", 1),  # Docker 容器化部署
    "s5-dep-c3": ("BV1h1VbzHER2", 124),  # Web 前端：Streamlit / Gradio
    "s5-dep-c4": ("BV1jg4y13718", 1),  # 消息队列与异步任务
    "s5-dep-c5": ("BV1G66rBBEXT", 1),  # 微信 / 钉钉集成
    # ---- s5-observability ----
    "s5-obs-c1": ("BV1Bq421A74G", 70),  # 为什么 Agent 必须可观测
    "s5-obs-c2": ("BV1BfC1YGEg2", 1),  # LangSmith：官方监控工具
    "s5-obs-c3": ("BV1Bq421A74G", 69),  # 日志、监控与错误追踪
    "s5-obs-c4": ("BV1Bq421A74G", 44),  # 评估：RAG 检索质量
    "s5-obs-c5": ("BV1Bq421A74G", 71),  # 评估：Agent 执行效果与成本
    # ---- s5-performance ----
    "s5-perf-c1": ("BV1xr3Mz2EXD", 16),  # Prompt 优化省 Token
    "s5-perf-c2": ("BV1z3NY66EY1", 53),  # 缓存策略
    "s5-perf-c3": ("BV19H4y1a7me", 1),  # 并行执行与吞吐
    "s5-perf-c4": ("BV1Bq421A74G", 74),  # 流式输出与首字延迟
    "s5-perf-c5": ("BV1Bq421A74G", 72),  # 成本度量与预算控制
    # ---- s5-security ----
    "s5-sec-c1": ("BV1xr3Mz2EXD", 21),  # Prompt 注入防护
    "s5-sec-c2": ("BV1ptXPYREpe", 4),  # 输入过滤与输出审查
    "s5-sec-c3": ("BV1KSYx6zEZL", 30),  # 权限控制与行为约束
    "s5-sec-c4": ("BV1dM411n7Nz", 1),  # 敏感信息保护
    "s5-sec-c5": ("BV1Bq421A74G", 75),  # 安全加固实践
    # ---- s6-cs-agent ----
    "s6-cs-c1": ("BV1xr3Mz2EXD", 5),  # 需求与角色设计
    "s6-cs-c2": ("BV1z3NY66EY1", 101),  # 多工具调用与 RAG 作为工具
    "s6-cs-c3": ("BV1z3NY66EY1", 78),  # 多轮记忆与会话管理
    "s6-cs-c4": ("BV1z3NY66EY1", 86),  # Human-in-the-Loop 审批
    "s6-cs-c5": ("BV1z3NY66EY1", 45),  # 循环刹车与成本控制
    "s6-cs-c6": ("BV1z3NY66EY1", 100),  # 部署、演示与复盘
    # ---- s6-rag-project ----
    "s6-rag-c1": ("BV1xr3Mz2EXD", 30),  # 项目规划与技术选型
    "s6-rag-c2": ("BV1xr3Mz2EXD", 31),  # 文档处理 pipeline
    "s6-rag-c3": ("BV1xr3Mz2EXD", 22),  # 问答：检索 + 引用溯源
    "s6-rag-c4": ("BV1Bq421A74G", 64),  # Agentic RAG 增强
    "s6-rag-c5": ("BV1xr3Mz2EXD", 23),  # SSE 流式与前端演示
    "s6-rag-c6": ("BV146X5Y4E9R", 1),  # Docker 部署与文档
    # ---- s7-career ----
    "s7-car-c1": ("BV1gwGt6fEdH", 1),  # 简历与项目包装
    "s7-car-c2": ("BV1aQMX6oEni", 30),  # 高频面试题：基础概念
    "s7-car-c3": ("BV1aQMX6oEni", 5),  # 高频面试题：架构与技术实现
    "s7-car-c4": ("BV1KSYx6zEZL", 26),  # 项目经验与难点复盘
    "s7-car-c5": ("BV1KSYx6zEZL", 16),  # 技术趋势与行动清单
}

# 现有素材中确实没有对应内容、需要客户补充链接的章节（当前为空 = 已 100% 覆盖）
PENDING: List[str] = [
]

# 由生成器写入，便于快速核对：{总章节数, 已映射数, 待补数}
_STATS = {"chapters": 125, "mapped": 125, "pending": 0}


def player_url(bv: str, page: int = 1) -> str:
    """可嵌入播放器的地址（含分P），视频页/章节页统一用它。"""
    return f"https://player.bilibili.com/player.html?bvid={bv}&page={page}"


def apply_video_mapping(courses: list) -> Tuple[int, int]:
    """把 VIDEO_MAP 写到课程章节上。

    - 命中映射：写入 video_bv + video_page；
    - 命中 PENDING：清空 video_bv（页面显示「视频待补充」，不再拿别的视频冒充）；
    - 两者都未命中：保持原样（交给调用方决定兜底策略）。
    返回 (已映射数, 待补充数)。
    """
    mapped = pending = 0
    for co in courses or []:
        for ch in co.get("chapters", []) or []:
            cid = ch.get("id")
            if cid in VIDEO_MAP:
                bv, page = VIDEO_MAP[cid]
                ch["video_bv"] = bv
                ch["video_page"] = page
                mapped += 1
            elif cid in PENDING:
                ch["video_bv"] = ""
                ch["video_page"] = 1
                pending += 1
    return mapped, pending
