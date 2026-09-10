# 视频映射表（已确认并落库）

> ✅ **已于 2026-09-11 首次落库、2026-09-12 补齐全部 42 个待补章节**：`cms.db` 的章节字段、`videos` 表、`data/processed/videos.json`
> 与种子生成器（`curriculum_2026.py`）都已按本表更新。
> - 权威映射：`backend/data_pipeline/video_mapping.py`（由本文件生成，勿手改）
> - 落库/重复执行：`cd backend && python apply_video_mapping.py`（幂等）
> - 重新灌种子也不会退回占位：`_apply_video_bv()` / `build_videos()` 已接同一份映射

生成时间：2026-09-11（首批）／2026-09-12（补齐 42 条，覆盖率 100%）｜ 覆盖课程 24 门 / 章节 125 个


## 一、现状与问题

- 线上数据库里 125 个章节的 `video_bv` 只有 **3 个值**、`video_page` **全是 1**，所以每章都播同一个视频的同一集，看起来「每个视频都一样」。
- 其中阶段二的 `BV18hWtzuErE` 已**失效**（接口 62012），阶段一/三的两个链接本身是真实大合集。
- 下表把章节逐条对应到**已核实的真实视频分P**，优先用当前库里那两个有效合集 + 仓库迁移脚本里的真实链接。


## 二、素材来源（均已用 B 站接口核实）

| BV | 类型 | 分P | 备注 |
| --- | --- | --- | --- |
| `BV1h1VbzHER2` | 黑马程序员 Python+AI大模型（当前库中阶段一占位链接，真实有效） | 131 | |
| `BV1xr3Mz2EXD` | LangChain Agent 实战（当前库中阶段三占位链接，真实有效） | 92 | |
| `BV1Bq421A74G` | 吴恩达大模型合集（来自 migrate_curriculum.py，真实有效） | 99 | |
| `BV1ptXPYREpe` | 吴恩达《使用ChatGPT API构建系统》（同合集） | 11 | |
| `BV1ULJPz4EBD` | 吴恩达《用MCP构建AI Apps》（同合集） | 11 | |
| `BV1HeZNYMEyf` | 吴恩达《自主式RAG》（同合集） | 6 | |
| `BV1fGeAz6Eie` | Transformer 动画讲解（来自 migrate_curriculum.py） | 32 | |
| `BV18hWtzuErE` | ❌ 阶段二占位链接，接口返回 62012（稿件不可见）——必须替换 | — | |

### 本轮补齐新增素材（42 个待补章节，均已用 B 站接口核实分P）

| BV | 素材 | 用途 |
| --- | --- | --- |
| `BV1z3NY66EY1` | 尚硅谷《LangGraph 教程》（132P） | 采用 14 章 |
| `BV1KSYx6zEZL` | 楼兰教你学AI《AI Agent 面经合集》（34P） | 采用 5 章 |
| `BV1ahFmzqE9z` | 博学谷《2026版 Agent Skills 保姆级教程》（15P） | 采用 4 章 |
| `BV1ugdgBQED4` | iwenwiki《手把手掌握 Agent Skills》（6P） | 采用 1 章 |
| `BV1L36uYZEPz` | 木羽Cheney《AutoGen 零基础入门》（8P） | 采用 2 章 |
| `BV1DEivY5Ewe` | 南哥AGI研习社《MetaGPT 设计理念拆解》（1P） | 采用 1 章 |
| `BV1Y94y1T7gL` | MetaGPT 官方《智能体开发入门》导学课（1P） | 采用 1 章 |
| `BV1f6AAzYEMU` | 编程不良人《OpenClaw 多 Agent 架构详解》（8P） | 采用 3 章 |
| `BV1aQMX6oEni` | Agent开发实战《AI Agent 高频面试八股》（30P） | 采用 3 章 |
| `BV1iR4k6SEpn` | 赵阳老师《Multi-Agent 三大编排模式》（1P） | 采用 1 章 |
| `BV1jR4k6SEUz` | 赵阳老师《Multi-Agent 核心概念速通》（1P） | 采用 1 章 |
| `BV1D7Gm6JE39` | 张宇技术栈《生产级 AI agent 架构详解》（1P） | 采用 1 章 |
| `BV1zV2QBtE39` | 黑马程序员《FastAPI 从入门到实战》（68P） | 采用 1 章 |
| `BV1SmG3zAEkF` | 《通过 Docker 部署 FastAPI 应用程序》（1P） | 采用 1 章 |
| `BV146X5Y4E9R` | 《Docker Desktop 部署 Ollama 与 OpenWebUI》（1P） | 采用 1 章 |
| `BV1jg4y13718` | 武沛齐《快速搞定——异步框架 celery》（7P） | 采用 1 章 |
| `BV1G66rBBEXT` | 《把智能体配置到钉钉里，让 AI 员工入职群聊》（1P） | 采用 1 章 |
| `BV1sG4y1571G` | 《零基础开发微信公众号》项目课（16P） | 备用（微信侧） |
| `BV1BfC1YGEg2` | 《LangSmith 初体验：调试测试监控》（1P） | 采用 1 章 |
| `BV1rshBzBEhx` | 《langsmith 配置与使用》（1P） | 备用 |
| `BV19H4y1a7me` | 《AI 模型并发请求详解》（1P） | 采用 1 章 |
| `BV1ZQ5u6bEJ7` | 《最大化 Claude Code 缓存命中省 token》（1P） | 备用 |
| `BV1dM411n7Nz` | IT老齐《Spring Boot 如何实现数据脱敏》（1P） | 采用 1 章 |
| `BV1gwGt6fEdH` | 《AI 大模型简历中的项目如何包装》（1P） | 采用 1 章 |
| `BV1RM4y167qu` | 《日志文件如何优雅实现数据脱敏》（1P） | 备用 |
| `BV11jbg6VENh` | 《429 限流/超时/熔断降级》（1P） | 备用 |

## 三、章节 → 视频 映射（已确认并落库）


### s1-api-dev ｜ 大模型 API 调用与 AI 开发规范（大模型基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s1-api-c1` | OpenAI API 快速上手 | `BV1xr3Mz2EXD` | P1 | 1.快速构建对话系统，实现与大模型的高效交互 | 16m10s | 通过 API 与大模型交互的完整入门 |
| `s1-api-c2` | 国产大模型 API | `BV1xr3Mz2EXD` | P58 | 58.大模型之LangChain-Model-语言模型-智普大模型接入 | 4m17s | 智谱（国产）大模型接入 |
| `s1-api-c3` | 关键参数：temperature / top_p / max_tokens | `BV1Bq421A74G` | P58 | 4-3 大语言模型（LLM）采样策略 | 8m13s | 采样策略＝temperature/top_p 等关键参数 |
| `s1-api-c4` | 流式输出与错误处理 | `BV1ptXPYREpe` | P7 | 6-Check Outputs检查输出 | 6m23s | 输出校验/异常处理 |
| `s1-api-c5` | AI 开发规范：从脚本到工程 | `BV1xr3Mz2EXD` | P46 | 46.大模型之LangChain-虚拟环境(上) | 10m06s | 虚拟环境：从脚本到工程化 |

### s1-llm-basics ｜ 大模型基础概念：认识 LLM（大模型基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s1-llm-c1` | 什么是大语言模型（LLM） | `BV1h1VbzHER2` | P109 | AI大模型开发-01-大模型概念入门 | 7m57s | 大模型概念入门 |
| `s1-llm-c2` | Transformer 架构入门 | `BV1fGeAz6Eie` | P6 | 06 简单而强大的Transformer | 10m07s | Transformer 原理（动画讲解） |
| `s1-llm-c3` | 主流大模型与选型 | `BV1Bq421A74G` | P59 | 4-4 选择合适的大语言模型（LLM） | 8m14s | 如何选择合适的大模型 |
| `s1-llm-c4` | Token 与上下文窗口 | `BV1xr3Mz2EXD` | P12 | 12.大模型的认知和核心原理-Token的介绍 | 8m51s | Token 专题 |
| `s1-llm-c5` | 模型能力与局限性 | `BV1Bq421A74G` | P8 | 8 - 生成式 AI 应用 - 大语言模型的能力与局限 | 11m02s | 大模型能力与局限 |

### s1-ollama ｜ Ollama 本地模型部署（大模型基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s1-ollama-c1` | 本地模型 vs 云端 API | `BV1h1VbzHER2` | P112 | AI大模型开发-04-私有化部署实战需求介绍 | 6m30s | 私有化部署需求与架构 |
| `s1-ollama-c2` | 安装 Ollama 与拉取模型 | `BV1h1VbzHER2` | P115 | AI大模型开发-07-Windows系统Ollama私有化模型部署 | 11m04s | Windows 部署 Ollama 全流程 |
| `s1-ollama-c3` | Python / HTTP 调用本地模型 | `BV1h1VbzHER2` | P122 | AI大模型开发-14-Ollama基础Python代码 | 10m46s | Ollama 的 Python 调用代码 |
| `s1-ollama-c4` | 本地调试的完整工作流 | `BV1h1VbzHER2` | P125 | AI大模型开发-17-Ollama&Streamlit开发聊天机器人界面 | 11m12s | Ollama + Streamlit 完整对话应用 |

### s1-prompt ｜ Prompt Engineering 提示词工程（大模型基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s1-prompt-c1` | Prompt 基础：一句话说清任务 | `BV1xr3Mz2EXD` | P14 | 14.大模型之提示词工程-提示词工程介绍 | 5m23s | 提示词工程介绍 |
| `s1-prompt-c2` | Few-shot Learning：给示例 | `BV1xr3Mz2EXD` | P56 | 56.大模型之LangChain-Model-提示词模版-少样本案例模版 | 8m58s | 少样本（Few-shot）模板 |
| `s1-prompt-c3` | Chain of Thought 思维链 | `BV1ptXPYREpe` | P5 | 4-思维链推理 | 10m12s | 思维链推理专题 |
| `s1-prompt-c4` | 角色扮演与场景化 | `BV1xr3Mz2EXD` | P20 | 20.大模型之提示词工程-提示词的应用 | 6m46s | 提示词的应用（角色/场景） |
| `s1-prompt-c5` | Prompt 优化与迭代 | `BV1Bq421A74G` | P13 | 第3集 迭代 | 13m19s | 《提示词工程师》第3集 迭代 |

### s2-agent-arch ｜ Agent 架构模式（Agent基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s2-arch-c1` | ReAct：推理与行动交替 | `BV1xr3Mz2EXD` | P76 | 76.大模型之LangChain-Agent-ReActAgent | 11m03s | ReActAgent 专题 |
| `s2-arch-c2` | Plan and Execute：先规划再执行 | `BV1xr3Mz2EXD` | P77 | 77.大模型之LangChain-Agent-SelfAskAgent | 4m23s | Self-Ask（先规划再执行范式） |
| `s2-arch-c3` | Reflection：自我反思 | `BV1HeZNYMEyf` | P4 | 4-构建代理推理循环 | 11m39s | 代理推理循环（含自反思） |
| `s2-arch-c4` | Multi-Agent 模式概览 | `BV1jR4k6SEUz` | P1 | Multi-Agent：Multi-Agent核心概念速通 | 9m18s | Multi-Agent 核心概念速通（与下一章互补） |
| `s2-arch-c5` | 架构选型实战 | `BV1D7Gm6JE39` | P1 | 生产级AI agent架构详解 | 13m29s | 生产级 AI Agent 架构详解：架构选型视角 |

### s2-agent-core ｜ AI Agent 核心概念（Agent基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s2-core-c1` | 什么是 AI Agent | `BV1xr3Mz2EXD` | P82 | 82.大模型之Agent-什么是Agent | 9m13s | 什么是 Agent |
| `s2-core-c2` | Agent 的核心能力 | `BV1xr3Mz2EXD` | P83 | 83.大模型之Agent-Agent决策流程 | 7m11s | Agent 决策流程 |
| `s2-core-c3` | Agent 与 LLM 的区别 | `BV1xr3Mz2EXD` | P81 | 81.大模型之Agent-Agent和LLM的关系 | 8m15s | Agent 与 LLM 的关系 |
| `s2-core-c4` | Agent 的应用场景 | `BV1Bq421A74G` | P98 | 2-什么是智能体AI？ | 5m12s | 什么是智能体 AI / 应用 |
| `s2-core-c5` | 动手：搭一个最小 Agent | `BV1xr3Mz2EXD` | P71 | 71.大模型之LangChain-Agent-基础应用(上) | 12m35s | LangChain Agent 基础应用（上） |

### s2-memory ｜ Agent 记忆系统（Agent基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s2-mem-c1` | 为什么要记忆 | `BV1xr3Mz2EXD` | P2 | 2.利用内存模块实现多轮对话和上下文跟踪 | 16m15s | 内存模块实现多轮对话与上下文跟踪 |
| `s2-mem-c2` | 短期记忆：对话历史 | `BV1xr3Mz2EXD` | P73 | 73.大模型之LangChain-Agent-添加记忆 | 6m08s | LangChain Agent 添加记忆 |
| `s2-mem-c3` | 长期记忆：向量数据库 | `BV1xr3Mz2EXD` | P36 | 36.大模型之RAG-向量数据库介绍 | 4m51s | 向量数据库介绍 |
| `s2-mem-c4` | 记忆的检索与更新 | `BV1xr3Mz2EXD` | P79 | 79.大模型之LangChain-Memory(上) | 9m20s | LangChain Memory（上） |
| `s2-mem-c5` | 综合记忆 Agent | `BV1xr3Mz2EXD` | P80 | 80.大模型之LangChain-Memory(下) | 10m04s | LangChain Memory（下） |

### s2-tool-calling ｜ 工具调用 Tool Calling（Agent基础）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s2-tool-c1` | Function Calling 原理 | `BV1xr3Mz2EXD` | P84 | 84.大模型之Agent-Function_Calling-流程图 | 8m14s | Function Calling 流程图 |
| `s2-tool-c2` | 工具定义与描述 | `BV1HeZNYMEyf` | P3 | 3-工具调用 | 10m12s | 工具调用 |
| `s2-tool-c3` | 工具参数解析 | `BV1xr3Mz2EXD` | P85 | 85.大模型之Agent-Function_Calling-本地函数调用 | 11m02s | 本地函数调用与参数 |
| `s2-tool-c4` | 工具执行与结果返回 | `BV1xr3Mz2EXD` | P86 | 86.大模型之Agent-Function_Calling-完整流程梳理 | 2m49s | Function Calling 完整流程梳理 |
| `s2-tool-c5` | 实战：天气查询 Agent | `BV1xr3Mz2EXD` | P87 | 87.大模型之Agent-Function_Calling-多Function案例 | 10m37s | 多 Function 案例 |

### s3-agentic-rag ｜ Agentic RAG 进阶（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-agc1` | 传统 RAG 的局限 | `BV1xr3Mz2EXD` | P44 | 44.大模型之RAG-RAG的缺陷介绍 | 12m37s | RAG 的缺陷介绍 |
| `s3-agc2` | 核心循环：retrieve → grade → rewrite → generate → check | `BV1HeZNYMEyf` | P4 | 4-构建代理推理循环 | 11m39s | 构建代理推理循环 |
| `s3-agc3` | 文档评分与查询重写 | `BV1HeZNYMEyf` | P2 | 2-路由器查询引擎 | 9m10s | 路由器查询引擎（查询重写/路由） |
| `s3-agc4` | 自纠错：幻觉检测与回答检查 | `BV1Bq421A74G` | P62 | 4-7 幻觉抑制与处理 | 7m37s | 幻觉抑制与处理 |
| `s3-agc5` | 循环刹车与成本控制 | `BV1Bq421A74G` | P73 | 5-7 成本 vs 响应质量 | 5m38s | 成本 vs 响应质量（刹车与成本） |
| `s3-agc6` | 实践：自纠错 RAG 服务 | `BV1HeZNYMEyf` | P5 | 5-构建多文档代理 | 10m23s | 构建多文档代理 |

### s3-langchain ｜ LangChain 框架（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-lc-c1` | LangChain 设计思想 | `BV1xr3Mz2EXD` | P48 | 48.大模型之LangChain-LangChain的基本介绍 | 9m21s | LangChain 基本介绍 |
| `s3-lc-c2` | LangChain RAG 线：Loaders 与 Splitters | `BV1xr3Mz2EXD` | P68 | 68.大模型之LangChain-RAG-文档加载和文档切割 | 9m42s | 文档加载和文档切割 |
| `s3-lc-c3` | LangChain RAG 线：Embeddings 与 VectorStores | `BV1xr3Mz2EXD` | P69 | 69.大模型之LangChain-RAG-文本向量化和向量存储 | 6m42s | 文本向量化和向量存储 |
| `s3-lc-c4` | LangChain RAG 线：Retrieval Chain | `BV1xr3Mz2EXD` | P70 | 70.大模型之LangChain-RAG-检索器和完整RAG案例 | 10m16s | 检索器和完整 RAG 案例 |
| `s3-lc-c5` | LangChain Agent 线：Tool 与 AgentExecutor | `BV1xr3Mz2EXD` | P78 | 78.大模型之LangChain-Tools | 10m07s | LangChain Tools |
| `s3-lc-c6` | LangChain Agent 线：Memory 与 RAG 工具 | `BV1Bq421A74G` | P84 | 7——完整功能的聊天机器人 | 9m57s | LangChain 完整功能聊天机器人 |
| `s3-lc-c7` | LangChain 综合：知识问答 Agent | `BV1xr3Mz2EXD` | P51 | 51.大模型之LangChain-RAG+LangChain实现 | 10m51s | RAG + LangChain 实现 |

### s3-langgraph ｜ LangGraph 框架（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-lg-c1` | 核心三件套：State / Node / Edge | `BV1z3NY66EY1` | P9 | 09_入门基础_langgraph三要素组成 | 6m50s | 「langgraph 三要素组成」＝State / Node / Edge |
| `s3-lg-c2` | 条件路由与手搓 ReAct | `BV1z3NY66EY1` | P32 | 32_控制流_条件分支 | 9m32s | 「控制流_条件分支」＝条件路由，ReAct 用循环图实现 |
| `s3-lg-c3` | Checkpointer：多轮状态记忆 | `BV1z3NY66EY1` | P65 | 65_持久化_使用数据库作为检查点 | 11m24s | 「使用数据库作为检查点」＝Checkpointer 落库 |
| `s3-lg-c4` | Human-in-the-Loop：人工审批 | `BV1z3NY66EY1` | P88 | 88_中断_审批模型 | 17m03s | 「中断_审批模型」＝人工审批 |
| `s3-lg-c5` | LangGraph 综合：客服 Agent「小 G」 | `BV1KSYx6zEZL` | P28 | 企业级智能客服Agent系统如何设计 | 6m34s | 企业级智能客服 Agent 系统设计（本课程无配套实操项目，用面经视角替代） |

### s3-mcp ｜ MCP 模型上下文协议（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-mcp-c1` | 为什么需要 MCP | `BV1ULJPz4EBD` | P2 | 2-为什么选择MCP | 7m52s | 为什么选择 MCP |
| `s3-mcp-c2` | 核心架构：Client ↔ Server ↔ 工具 | `BV1ULJPz4EBD` | P3 | 3-MCP架构 | 14m53s | MCP 架构 |
| `s3-mcp-c3` | 使用现成的 MCP Server | `BV1ULJPz4EBD` | P9 | 9-为Claude Desktop配置服务器 | 6m21s | 为 Claude Desktop 配置现成 Server |
| `s3-mcp-c4` | MCP 在 Agent 生态中的位置 | `BV1ULJPz4EBD` | P4 | 4-问答机器人示例 | 7m13s | 问答机器人示例（MCP 在生态中的位置） |
| `s3-mcp-c5` | 动手：接一个文件系统 Server | `BV1ULJPz4EBD` | P5 | 5-创建MCP服务器 | 8m57s | 创建 MCP 服务器（动手） |

### s3-rag ｜ RAG 检索增强生成（手写 pipeline）（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-rag-c1` | RAG 解决的问题 | `BV1xr3Mz2EXD` | P28 | 28.大模型之RAG-RAG介绍 | 10m49s | RAG 介绍与要解决的问题 |
| `s3-rag-c2` | 文档加载与文本分块 | `BV1xr3Mz2EXD` | P34 | 34.大模型之RAG-文档的加载和分割 | 10m51s | 文档的加载和分割 |
| `s3-rag-c3` | Embedding 与向量数据库 | `BV1xr3Mz2EXD` | P32 | 32.大模型之RAG-Embeddings处理 | 10m18s | Embeddings 处理 |
| `s3-rag-c4` | 检索 + 回答 + 引用溯源 | `BV1xr3Mz2EXD` | P37 | 37.大模型之RAG-基于向量检索的RAG实现 | 9m46s | 基于向量检索的 RAG 实现 |
| `s3-rag-c5` | 检索质量进阶优化 | `BV1Bq421A74G` | P54 | 3-8 重新排名 | 4m26s | 重新排名（Rerank）提升检索质量 |
| `s3-rag-c6` | 实践：企业知识库问答系统 | `BV1xr3Mz2EXD` | P43 | 43.大模型之RAG-本地向量库-LLM整合 | 8m28s | 本地向量库 + LLM 整合 |

### s3-skills ｜ Agent Skills 能力技能化（开发实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s3-skills-c1` | 为什么要有 Skill | `BV1ugdgBQED4` | P1 | 01_Agent Skills 到底是个啥 | 7m25s | 「Agent Skills 到底是个啥」＝为什么要有 Skill |
| `s3-skills-c2` | Skill 的描述与边界 | `BV1ahFmzqE9z` | P10 | 10-skill开发规则 | 11m07s | 「skill 开发规则」＝描述怎么写、边界在哪 |
| `s3-skills-c3` | 多 Skill 协作 | `BV1ahFmzqE9z` | P15 | 15-claudecode等其他智能体使用skills | 4m43s | 多个智能体共用同一批 skills（协作视角） |
| `s3-skills-c4` | Skill 与工具、RAG 的关系 | `BV1ahFmzqE9z` | P14 | 14-AgentSkills核心机制剖析 | 6m47s | 「AgentSkills 核心机制剖析」＝与工具/RAG 的分工 |
| `s3-skills-c5` | 实践：沉淀你自己的 Skill | `BV1ahFmzqE9z` | P11 | 11-开发自动周报skill | 12m13s | 「开发自动周报 skill」＝从零沉淀自己的 Skill |

### s4-metagpt-autogen ｜ MetaGPT 与 AutoGen 框架（多Agent）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s4-fw-c1` | MetaGPT：模拟软件公司 | `BV1DEivY5Ewe` | P1 | 国产之光？MetaGPT多智能体开源框架，重塑自然语言编程，亲测真的很不错，设计理念拆解很清晰，带你代码中感受它的核心设计思想，核心概念介绍，测试用例 | 45m26s | MetaGPT 设计理念拆解＋核心概念＋测试用例 |
| `s4-fw-c2` | AutoGen：对话式多 Agent | `BV1L36uYZEPz` | P2 | Part 2. MicroSoft AutoGen 项目说明与框架概览 | 16m35s | AutoGen 项目说明与框架概览（对话式多 Agent） |
| `s4-fw-c3` | 框架对比与选型 | `BV1KSYx6zEZL` | P1 | 7种AI Agent架构到底选什么架构 | 4m20s | 7 种 Agent 架构对比与选型 |
| `s4-fw-c4` | 源码与设计思路学习 | `BV1Y94y1T7gL` | P1 | 《MetaGPT智能体开发入门》导学课回放 | 72m19s | MetaGPT 官方《智能体开发入门》导学：设计思路与源码入口 |
| `s4-fw-c5` | Demo：一个多 Agent 小任务 | `BV1L36uYZEPz` | P7 | Part 7. 案例：Two-Agent Chat 对话模式开发实战 | 22m51s | 案例：Two-Agent Chat 对话模式开发实战 |

### s4-multi-agent ｜ 多 Agent 架构与协作（多Agent）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s4-ma-c1` | 五种协作模式 | `BV1iR4k6SEpn` | P1 | Multi-Agent：三大编排模式深度解析 | 7m59s | 三大编排模式深度解析（协作模式总览） |
| `s4-ma-c2` | 通信机制与任务分配 | `BV1f6AAzYEMU` | P4 | 4.OpenClaw 多个Agent 绑定多个Telegram路由配置 | 16m40s | 多个 Agent 绑定多通道路由＝任务分发与通信 |
| `s4-ma-c3` | 角色设计与何时需要多 Agent | `BV1f6AAzYEMU` | P1 | 1.OpenClaw 之为什么要用多Agent | 9m50s | 「为什么要用多 Agent」＝何时才需要多 Agent |
| `s4-ma-c4` | 多 Agent 的代价 ⚠️ | `BV1aQMX6oEni` | P12 | 12.什么场景适合用多Agent系统？ | 4m40s | 「什么场景适合用多 Agent 系统」＝代价与适用边界 |
| `s4-ma-c5` | 实践：Supervisor 最小 Demo | `BV1f6AAzYEMU` | P2 | 2.OpenClaw 多Agent 的简介和创建 | 21m17s | 多 Agent 团队创建＝Supervisor 结构的最小实操 |

### s4-orchestration ｜ Agent 编排与工程化陷阱（多Agent）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s4-or-c1` | 工作流设计 | `BV1Bq421A74G` | P97 | 《Agentic AI》【模块1：智能体工作流简介】1-Welcome！ | 1m59s | 智能体工作流简介（近似） |
| `s4-or-c2` | 条件分支与循环迭代 | `BV1z3NY66EY1` | P40 | 40_控制流_agent构建中的循环结构 | 6m24s | 「agent 构建中的循环结构」＝分支＋循环迭代 |
| `s4-or-c3` | 错误处理与重试 | `BV1z3NY66EY1` | P48 | 48_控制流_重试机制 | 13m36s | 「控制流_重试机制」（配套 P49 retry_on 参数） |
| `s4-or-c4` | 四大工程化陷阱 | `BV1z3NY66EY1` | P44 | 44_控制流_限制循环步数 | 7m01s | 以「限制循环步数」切入最常见的失控陷阱 |
| `s4-or-c5` | 实践：带护栏的工作流 | `BV1z3NY66EY1` | P131 | 131_图设计模型_评估器_优化器 | 8m27s | 「图设计模型_评估器_优化器」＝带校验护栏的工作流 |

### s5-deploy ｜ 生产部署方案（优化部署）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s5-dep-c1` | FastAPI + Uvicorn API 服务 | `BV1zV2QBtE39` | P3 | 03-FastAPI基础入门-第一个FastAPI程序 | 13m35s | 第一个 FastAPI 程序（uvicorn 启动服务） |
| `s5-dep-c2` | Docker 容器化部署 | `BV1SmG3zAEkF` | P1 | 25. 通过Docker部署FastAPI应用程序 | 11m52s | 通过 Docker 部署 FastAPI 应用程序 |
| `s5-dep-c3` | Web 前端：Streamlit / Gradio | `BV1h1VbzHER2` | P124 | AI大模型开发-16-Streamlit开发对话网页 | 23m02s | Streamlit 开发对话网页 |
| `s5-dep-c4` | 消息队列与异步任务 | `BV1jg4y13718` | P1 | 01 celery的工作机制 | 16m00s | celery 工作机制＝消息队列＋异步任务（Python 栈通用） |
| `s5-dep-c5` | 微信 / 钉钉集成 | `BV1G66rBBEXT` | P1 | 把智能体配置到钉钉里，让AI员工入职群聊 | 7m01s | 把智能体接入钉钉群（微信侧见备用素材） |

### s5-observability ｜ 监控、调试与评估（优化部署）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s5-obs-c1` | 为什么 Agent 必须可观测 | `BV1Bq421A74G` | P70 | 5-4 日志记录、监控与可观测性 | 4m15s | 日志记录、监控与可观测性 |
| `s5-obs-c2` | LangSmith：官方监控工具 | `BV1BfC1YGEg2` | P1 | 【LangSmith】LLM应用调试测试监控神器 - LangSmith初体验（纯干货） | 19m22s | LangSmith 初体验：调试＋测试＋监控 |
| `s5-obs-c3` | 日志、监控与错误追踪 | `BV1Bq421A74G` | P69 | 5-3 实施 RAG 评估策略 | 7m29s | 实施 RAG 评估策略（日志/评估） |
| `s5-obs-c4` | 评估：RAG 检索质量 | `BV1Bq421A74G` | P44 | 2-8 评估检索 | 8m25s | 评估检索 |
| `s5-obs-c5` | 评估：Agent 执行效果与成本 | `BV1Bq421A74G` | P71 | 5-5 定制化评估 | 5m10s | 定制化评估 |

### s5-performance ｜ 性能优化与成本控制（优化部署）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s5-perf-c1` | Prompt 优化省 Token | `BV1xr3Mz2EXD` | P16 | 16.大模型之提示词工程-Prompt调优 | 9m39s | Prompt 调优（省 Token） |
| `s5-perf-c2` | 缓存策略 | `BV1z3NY66EY1` | P53 | 53_控制流_缓存实例演示 | 15m27s | 「控制流_缓存实例演示」＝Agent 侧缓存策略 |
| `s5-perf-c3` | 并行执行与吞吐 | `BV19H4y1a7me` | P1 | Ai模型并发请求详解，1QPS最高支持日活4000人 | 5m09s | 模型并发请求与吞吐容量估算（1 QPS 支撑日活 4000） |
| `s5-perf-c4` | 流式输出与首字延迟 | `BV1Bq421A74G` | P74 | 5-8 延迟 vs 响应质量 | 4m39s | 延迟 vs 响应质量 |
| `s5-perf-c5` | 成本度量与预算控制 | `BV1Bq421A74G` | P72 | 5-6 量化 | 7m48s | 量化（成本控制手段） |

### s5-security ｜ 安全与可控性（优化部署）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s5-sec-c1` | Prompt 注入防护 | `BV1xr3Mz2EXD` | P21 | 21.大模型之提示词工程-防止Prompt攻击 | 7m42s | 防止 Prompt 攻击 |
| `s5-sec-c2` | 输入过滤与输出审查 | `BV1ptXPYREpe` | P4 | 3-Moderation适度 | 8m43s | Moderation 内容审查 |
| `s5-sec-c3` | 权限控制与行为约束 | `BV1KSYx6zEZL` | P30 | 如何约束Agent行为 | 6m32s | 「如何约束 Agent 行为」＝行为约束与权限边界 |
| `s5-sec-c4` | 敏感信息保护 | `BV1dM411n7Nz` | P1 | 【IT老齐287】Spring Boot如何实现数据脱敏 | 8m15s | 数据脱敏落地（后端通用实践，思路可迁移） |
| `s5-sec-c5` | 安全加固实践 | `BV1Bq421A74G` | P75 | 5-9 安全性 | 5m21s | 安全性专题 |

### s6-cs-agent ｜ 项目二：智能客服 / 业务 Agent（项目实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s6-cs-c1` | 需求与角色设计 | `BV1xr3Mz2EXD` | P5 | 5、结合Agent实现智能决策与自动化任务执行 | 16m15s | 结合 Agent 实现智能决策与自动化任务 |
| `s6-cs-c2` | 多工具调用与 RAG 作为工具 | `BV1z3NY66EY1` | P101 | 101_工具节点_手动调用工具案例代码上 | 14m52s | 工具节点：手动调用工具（多工具编排），替换与原阶段重复的分P |
| `s6-cs-c3` | 多轮记忆与会话管理 | `BV1z3NY66EY1` | P78 | 78_持久化_长期记忆数据库存储 | 16m57s | 长期记忆落库＝多轮会话管理，替换与原阶段重复的分P |
| `s6-cs-c4` | Human-in-the-Loop 审批 | `BV1z3NY66EY1` | P86 | 86_中断_HITL案例演示 | 13m34s | 「中断_HITL 案例演示」＝人工审批落地 |
| `s6-cs-c5` | 循环刹车与成本控制 | `BV1z3NY66EY1` | P45 | 45_控制流_主动退出 | 14m08s | 「控制流_主动退出」＝循环刹车，替换与原阶段重复的分P |
| `s6-cs-c6` | 部署、演示与复盘 | `BV1z3NY66EY1` | P100 | 100_项目部署_大模型agent部署 | 11m15s | 项目部署与演示＝部署/复盘，替换与原阶段重复的分P |
### s6-rag-project ｜ 项目一：RAG 知识库问答系统（项目实战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s6-rag-c1` | 项目规划与技术选型 | `BV1xr3Mz2EXD` | P30 | 30.大模型之RAG-RAG系统搭建流程(上) | 7m48s | RAG 系统搭建流程（上） |
| `s6-rag-c2` | 文档处理 pipeline | `BV1xr3Mz2EXD` | P31 | 31.大模型之RAG-RAG系统搭建流程(下) | 6m20s | RAG 系统搭建流程（下） |
| `s6-rag-c3` | 问答：检索 + 引用溯源 | `BV1xr3Mz2EXD` | P22 | 22.大模型之提示实战-智能学员辅导系统-StreamLit界面绘制 | 12m37s | 完整问答系统与界面演示（近似） |
| `s6-rag-c4` | Agentic RAG 增强 | `BV1Bq421A74G` | P64 | 4-9 智能体驱动型 RAG | 6m16s | 智能体驱动型 RAG |
| `s6-rag-c5` | SSE 流式与前端演示 | `BV1xr3Mz2EXD` | P23 | 23.大模型之提示实战-智能学员辅导系统-完成和大模型的交互 | 10m59s | 完成与大模型的交互（流式前端） |
| `s6-rag-c6` | Docker 部署与文档 | `BV146X5Y4E9R` | P1 | 【小白学AI】Docker Desktop部署Ollama和OpenWebUI本地部署大模型，B站最强教程！超简单小白也能轻松上手实操！带你少走99%弯路~ | 23m43s | Docker Desktop 部署 Ollama＋OpenWebUI＝RAG 项目容器化交付 |

### s7-career ｜ AI Agent 求职备战（求职备战）

| 章节 | 章节标题 | 建议 BV | 分P | 分P 标题 | 时长 | 匹配说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `s7-car-c1` | 简历与项目包装 | `BV1gwGt6fEdH` | P1 | AI大模型简历中的项目如何包装？【AI大模型就业必看】 | 28m15s | AI 大模型简历中的项目如何包装 |
| `s7-car-c2` | 高频面试题：基础概念 | `BV1aQMX6oEni` | P30 | 30.字节Agent面试核心概念与架构16问 | 6m56s | 字节 Agent 面试核心概念与架构 16 问 |
| `s7-car-c3` | 高频面试题：架构与技术实现 | `BV1aQMX6oEni` | P5 | 05.Agent七种主流架构 | 3m43s | Agent 七种主流架构（技术实现向） |
| `s7-car-c4` | 项目经验与难点复盘 | `BV1KSYx6zEZL` | P26 | 大模型Agent项目中，JSON 输出格式不稳定，怎么系统化解决 | 7m48s | 项目难点复盘：JSON 输出不稳定怎么系统化解决 |
| `s7-car-c5` | 技术趋势与行动清单 | `BV1KSYx6zEZL` | P16 | Agent系统学习路线 | 3m11s | Agent 系统学习路线（行动清单） |

## 四、统计与待补清单

- 已匹配：**125 / 125** 章节（覆盖率 100%）
- 待补：**0** 章节
- 涉及 BV 合集：**28 个**（全部经 B 站 `view` 接口核实存在、分P 可播）
- 同课程内重复分P：**0 组**（跨课程复用 1 组，见下）

**本轮补齐明细（42 条，全部为真实分P）**

| 课程 | 补齐章节数 | 主要素材 |
| --- | --- | --- |
| s2-agent-arch | 2 | Multi-Agent 核心概念速通 / 生产级 Agent 架构 |
| s3-langgraph | 5 | 尚硅谷 LangGraph（P9/P32/P65/P88）＋客服 Agent 系统设计 |
| s3-skills | 5 | 博学谷 Agent Skills（P10/P11/P14/P15）＋ iwenwiki |
| s4-metagpt-autogen | 5 | MetaGPT 设计理念 / AutoGen 入门 / 架构选型 |
| s4-multi-agent | 5 | OpenClaw 多 Agent（P1/P2/P4）/ 编排模式 / 适用场景 |
| s4-orchestration | 4 | LangGraph 控制流（P40/P44/P48）＋ 评估器-优化器 |
| s5-deploy | 4 | FastAPI / Docker / celery / 钉钉接入 |
| s5-observability | 1 | LangSmith 初体验 |
| s5-performance | 2 | LangGraph 节点缓存 / 模型并发与吞吐 |
| s5-security | 2 | Agent 行为约束 / 数据脱敏 |
| s6-cs-agent | 1 | LangGraph HITL 案例演示 |
| s6-rag-project | 1 | Docker 部署 Ollama＋OpenWebUI |
| s7-career | 5 | 简历包装 / 面试八股 / 项目难点 / 学习路线 |

> 说明：个别章节（如「四大工程化陷阱」「带护栏的工作流」「源码与设计思路学习」）
> 没有同名课程，选了**内容最接近的真实分P**，并在表中「匹配说明」列标注了口径，
> 便于后续有更贴合的素材时替换（替换只需改本表再重跑生成脚本）。
>
> 跨课程复用的 1 组：`BV1HeZNYMEyf` P4 同时用于 `s2-arch-c3`（Reflection）与 `s3-agc2`
> （代理推理循环）——两章本就同源（吴恩达《自主式 RAG》），内容高度重合，保留。

## 五、落库记录（已执行）

1. ✅ `backend/data/cms.db` → `courses.chapters[*].video_bv / video_page`：83 条写入精确分P，42 条清空（待补）；
2. ✅ `videos` 表 + `backend/data/processed/videos.json`：19 条换成真实分P并绑章节 id，5 条（整门课都缺素材）置空 + `is_active=0`；
3. ✅ `backend/data_pipeline/curriculum_2026.py`：`_apply_video_bv()` 与 `build_videos()` 已接 `video_mapping.py`，
   重新灌种子实测输出「精确 83 / 待补充 42 / 课程级兜底 0」，不会再退回占位；
4. ✅ 失效的 `BV18hWtzuErE` 已从 `BILIBILI_AGENT` 常量移除（换成 `BV1Bq421A74G`）。

### 第二批（2026-09-12）：补齐 42 个待补章节

1. ✅ 本表 42 行 `**待补**` → 真实 `BV + P号`（分P标题/时长取自 B 站接口）；
2. ✅ 重新生成 `backend/data_pipeline/video_mapping.py`（`VIDEO_MAP` 125 条，`PENDING` 清空）；
3. ✅ 重跑 `cd backend && python apply_video_mapping.py` 写入 `cms.db` 与 `videos.json`；
4. ✅ 前端「待补充」标签随之消失（实测：24 门课 / 125 章，无视频章节 0）；
5. ✅ 顺带消除 4 处跨阶段重复分P：`s6-cs-c2/c3/c5/c6` 改用 `BV1z3NY66EY1` 的
   P101（工具节点）/ P78（长期记忆）/ P45（主动退出）/ P100（项目部署），
   使「项目二」6 章各有独立视频；
6. ✅ 新增生成器 `backend/gen_video_mapping.py`：本表 → `video_mapping.py` 一键重建，
   并内置校验（章节 id 唯一、同课程内分P 不重复、章节集合与 `cms.db` 一致）。

**实测证据**
- `cd backend && py gen_video_mapping.py --check` → 「解析章节 125 个（课程 24 门）｜唯一 (BV,分P) 124 组｜待补 0 个；
  [提示] 跨课程复用 1 组」；
- `py -m data_pipeline.curriculum_2026` → 「章节视频映射：精确 125 条 / 待补充 0 条 / 课程级兜底 0 条」；
- 接口复核（含 `?limit=100`）→ 24 门课 125 章，`video_bv` 为空 0 条；
- 28 个 BV 逐个调 B 站 `view` 接口 → 全部 `code=0` 且用到的分P 均未越界；
- H5 实测（headless Chrome，`docs/evidence/h5-courseDetail-s3-langgraph.png`）：
  s3-langgraph 5 章均有 ▶，点第 1/2/3 章 iframe 依次为
  `player.bilibili.com/player.html?bvid=BV1z3NY66EY1&page=9 / 32 / 65`（每章确实不同）。

**代码侧配套改动**
- `backend/data_pipeline/video_mapping.py`（新增）：权威映射 + `player_url()` + `apply_video_mapping()`；
- `backend/gen_video_mapping.py`（新增）：从本表生成上面的模块 + 一致性校验（`--check` 只校验）；
- `backend/apply_video_mapping.py`（新增）：落库脚本，幂等，可随时重跑；
- 前端：章节列表无视频时显示「待补充」小标签、章节页显示「本章视频待补充」说明；
  视频页在「指定了 videoId 却查不到」时改为显示「暂无视频」（原先会错误地播第一个视频）；
  「在 B站观看 / 复制链接」现在会带上分P（`?p=N`）。

**回滚方式**：把 `courses.chapters[*].video_bv` 与 `video_page` 恢复为原来那 3 个 BV / 全 1 即可
（原值：阶段一 `BV1h1VbzHER2`、阶段二 `BV18hWtzuErE`（已失效）、阶段三 `BV1xr3Mz2EXD`），
或直接 `git revert` 本次提交后重跑种子。

> 本表已 100% 覆盖：125 / 125 章节均有真实可播视频。
> 后续新增/替换素材：改本表 → `cd backend && py gen_video_mapping.py` → `cd backend && python apply_video_mapping.py`。