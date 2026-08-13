# 2026年最新AIAgent应用开发学习路线零基础到精通一条龙（万人收藏⭐️）

> 编程导航学习网站：[学编程、做项目、拿 Offer！](https://www.codefather.cn)
> 
> 企业高频面试题库：[开始刷题，面试遇原题！](https://www.mianshiya.com)
>
> 精选简历模板大全：[1 分钟搞定简历！](https://www.laoyujianli.com)
>
> AI 资源导航网站：[获取最新 AI 黑科技！](https://ai.codefather.cn)
>
> 1 对 1 模拟面试：[随时随地提升面试能力](https://ai.mianshiya.com)



AI Agent 应用开发求职高频面试题：[开始刷题](https://www.mianshiya.com/bank/1821834688998707201)

⭐️ 推荐先观看 [鱼皮的保姆级 AI 指南视频](https://www.bilibili.com/video/BV1i9Z8YhEja/)，快速掌握程序员必知必会的 AI 概念、AI 工具、AI 开发技术、AI 编程技巧。



## 开篇介绍

AI Agent（人工智能代理）是近年最热门的技术方向之一，它代表了人工智能从 “被动回答” 到 “主动执行” 的重大跨越。简单来说，AI Agent 就是能够感知环境、自主决策、执行任务的智能体，它不仅能理解你的需求，还能调用各种工具、规划执行步骤、与其他 Agent 协作，最终完成复杂的任务。从智能客服到代码助手、从自动化运营到智能决策系统，AI Agent 正在重塑各个行业的工作方式。

AI Agent 是基于大语言模型（LLM）构建的智能应用系统，它具备感知、推理、决策和执行的能力。和传统的聊天机器人不同，AI Agent 能够主动调用工具（如搜索引擎、数据库、API）、制定计划、记忆上下文、自我反思和迭代优化。它就像一个智能助手，不仅能回答问题，还能帮你完成实际的工作任务。

**为什么要学 AI Agent 开发？**

首先，AI Agent 是 AI 应用的下一个里程碑。掌握 Agent 开发技术，意味着你能够开发出真正实用的 AI 应用，而不仅仅是一个简单的对话系统。

其次，市场需求巨大。从企业智能助手到个人效率工具，从自动化流程到智能决策系统，各行各业都需要 AI Agent 技术。

根据今年的市场调研，AI Agent 开发工程师的薪资普遍在 30-80 万，优秀的人才更是供不应求。

![](https://pic.yupi.icu/1/image-20251203124901058.png)

而且 AI Agent 技术栈相对友好，有 Python 基础或 Java 基础，以及有 AI 基础知识的开发者可以快速上手。


想要快速掌握 AI Agent 开发，**强烈建议学习鱼皮的 AI 项目教程**！

鱼皮的 [AI 超级智能体项目](https://www.codefather.cn/course/1915010091721236482) 和 [AI 零代码应用生成平台](https://www.codefather.cn/course/1948291549923344386) 都深度实战了 AI Agent 技术，从工具调用到 AI 智能体开发，从 RAG 知识库到 LangGraph4j 工作流编排，涵盖了 AI Agent 开发的核心技术。

![](https://pic.yupi.icu/1/1753332332820-9ec614de-65a2-496d-b9b2-dc89c20d06c9-20251203125930236.png)

跟着项目实战学习，不仅能快速上手 AI Agent 开发，还能积累完整的项目经验，给简历加分！

💡 本路线可以结合鱼皮的 AI 项目一起学习，边看路线理论、边跟项目实战，效果最佳。



### 就业方向

学习 AI Agent 开发可以从事多个方向的工作：

1. AI Agent 开发工程师：负责开发和优化 AI Agent 应用，包括 Agent 架构设计、工具集成、Prompt 优化等工作。
2. AI 应用工程师：基于 Agent 技术开发各类 AI 应用，如智能客服、代码助手、数据分析工具等。
3. AI 产品经理：负责 AI Agent 产品的规划和设计，需要深入理解 Agent 技术的能力和限制。
4. AI 架构师：负责企业级 AI Agent 系统的架构设计，包括多 Agent 协作、工具编排、安全控制等。
5. AI 技术专家：深入研究 Agent 技术的前沿方向，如自主学习、多模态 Agent、具身智能等。



### 学习路线图

![AI Agent 应用开发学习路线思维导图](https://pic.yupi.icu/roadmap/ai-agent-application-development-roadmap.png)



## 阶段 1：AI 大模型基础（10-20 天，仅供参考）

### 学习目标

了解 AI 大模型的基本概念和使用方法，为 Agent 开发打下基础。



### 知识点

**大模型基础概念【必学】：**

- 什么是大语言模型（LLM）
- Transformer 架构
- 主流大模型（GPT、Claude、文心一言、通义千问等）
- Token 和上下文窗口
- 模型能力和局限性

**Prompt Engineering【必学】：**

- Prompt 基础
- Few-shot Learning
- Chain of Thought（思维链）
- 角色扮演
- Prompt 优化技巧

**API 调用【必学】：**

- OpenAI API
- 国产大模型 API（文心、通义、Kimi 等）
- API 参数（temperature、top_p、max_tokens）
- 流式输出
- 错误处理

**Skills — AI 开发规范【必学】：**

- API Key 管理：从环境变量 / `.env` 读取，禁止硬编码
- 脚本结构：输入 → 处理 → 输出，养成工程化习惯
- Python 依赖管理与虚拟环境

**Ollama 本地部署【必学】：**

- 本地模型 vs 云端 API 的区别和适用场景
- 安装 Ollama，拉取并运行本地模型（如 `qwen2.5:7b`）
- 通过 Python/HTTP 调用本地 Ollama API（兼容 OpenAI 格式）
- 本地模型的优势：免费无限调用、数据不出本地、适合开发调试

> 💡 **实践**：装好 Ollama 后跑一个本地模型对话，感受一下"不花钱也能用 AI"。
> ```bash
> ollama pull qwen2.5:7b
> ollama run qwen2.5:7b
> ```


### 学习重点

1）如果你完全不了解 AI 大模型，关于 AI 大模型应用开发的详细学习，可以查看 [AI 大模型应用开发学习路线](https://www.codefather.cn/course/1789189862986850306/section/1912024009574629377)。这个阶段只是快速入门，不需要深入学习，重点是理解大模型的基本原理和使用方法。

2）Prompt Engineering 是使用大模型的基础技能，也是 Agent 开发的核心技能之一。关于 Prompt Engineering 提示词工程的详细学习，可以查看 [Prompt Engineering 提示词工程学习路线](https://www.codefather.cn/course/1789189862986850306/section/1990748694684676098)。要多练习编写 Prompt，理解如何通过 Prompt 引导模型完成特定任务。建议使用 ChatGPT 或国产大模型的网页版进行练习。

3）API 调用是 Agent 开发的基本操作。要熟悉主流大模型的 API 接口，能够使用 Python 调用 API 进行文本生成。建议申请 OpenAI API 或国产大模型的 API key，动手实践。

4）不要在这个阶段花费太长时间。Agent 开发不需要深入了解模型训练和微调，主要是应用层面的开发。掌握基础概念和 API 调用即可。

5）Ollama 本地部署可大幅降低学习成本。开发调试时用本地模型（免费），正式上线时切到云端 API。建议尽早安装 Ollama，后续所有 Demo 都可以先在本地跑通。


### 学习资源

- ⭐ [AI 大模型应用开发学习路线](https://www.codefather.cn/course/1789189862986850306/section/1912024009574629377)：完整的 AI 学习路线
- ⭐ [AI 导航](https://ai.codefather.cn/)：鱼皮出品，AI 工具和资源大全
- [Ollama 官网](https://ollama.com)：本地模型部署工具
- [黑马 Python+AI 大模型零基础到项目实战](https://www.bilibili.com/video/BV1h1VbzHER2)：比较新的视频教程
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)：官方文档
- [阿里云百炼](https://bailian.console.aliyun.com/)：国产大模型平台



## 阶段 2：Agent 基础概念（10-25 天，仅供参考）

### 学习目标

理解 AI Agent 的核心概念和工作原理，掌握 Agent 的基本架构。



### 知识点

**Agent 核心概念【必学】：**

- 什么是 AI Agent
- Agent 的核心能力
  - 感知（Perception）
  - 推理（Reasoning）
  - 决策（Decision Making）
  - 执行（Action）
- Agent 和 LLM 的区别
- Agent 的应用场景

**Agent 架构模式【必学】：**

- ReAct（Reasoning and Acting）
- Plan and Execute
- Reflection（反思）
- Multi-Agent（多 Agent 协作）

**工具调用（Tool Calling）【必学】：**

- Function Calling
- 工具定义和描述
- 工具参数解析
- 工具执行和结果返回

**记忆系统（Memory）【必学】：**

- 短期记忆（对话历史）
- 长期记忆（向量数据库）
- 记忆检索和更新



### 学习建议

1）Agent 的核心是让 LLM 能够 **使用工具**。要深入理解 Tool Calling 的原理：通过 Function Calling 让模型生成结构化的工具调用请求，然后执行工具并将结果返回给模型。这个循环是 Agent 的基础。

2）ReAct 是最经典的 Agent 架构模式，理解 ReAct 对理解 Agent 至关重要。

ReAct 的核心思想是：推理（Thought）→ 行动（Action）→ 观察（Observation）→ 推理……，形成一个循环。建议阅读 ReAct 相关文章并实现一个简单的 ReAct Agent。

![](https://pic.yupi.icu/1/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F06f2cf46-df40-48f9-a798-931222b0f70a_590x592.jpeg)

3）记忆系统让 Agent 能够记住历史对话和知识。短期记忆一般是对话历史，长期记忆需要使用向量数据库（如 Chroma、Pinecone）存储。理解如何设计记忆系统，如何检索相关记忆，对开发实用的 Agent 非常重要。

4）建议动手实现一个最简单的 Agent：能够调用天气查询工具的 Agent。通过实践理解 Agent 的工作流程，比单纯看理论要有效得多。



### 学习资源

- ⭐ [2025 AI Agent 智能体全套教程](https://www.bilibili.com/video/BV18hWtzuErE/)：从 0 开始手把手搭建
- [AI Agent 智能体开发教程](https://zhuanlan.zhihu.com/p/1928437328675841858)：深入浅出
- [2025 最新 LangChain Agent 教程](https://www.explinks.com/blog/yq-latest-langchain-agent-tutorial-for-2025-from-beginner-to-mastery/)：从入门到精通



## 阶段 3：Agent 开发实战（20-40 天，仅供参考）

在掌握了 Agent 基础概念后，这个阶段将通过实际开发来巩固技能。**核心理念：先手写理解原理，再用框架提高效率。**


### 学习目标

掌握 Agent 开发的实际技能，能够开发功能完整的 Agent 应用。


### 3.1 RAG — 检索增强生成 ★核心重点

> RAG 是市场需求最大的 AI 应用方向（企业知识库、智能客服、文档问答），**建议先手写一个完整 RAG pipeline，后面再用 LangChain 重写**。

**RAG 解决的问题**：大模型知识过时、容易幻觉、不了解私有数据。

**RAG 完整流程**：
```
加载文档 → 切分文本 → 生成向量 → 存入向量库 → 检索相关片段 → 交给模型回答
```

**知识点**：

- 文档加载：PDF、Markdown、Word 等格式的解析
- 文本分块策略：`chunk_size`、`overlap`、语义完整性
- Embedding 原理：文本 → 向量 → 语义相似度搜索
- 向量数据库：Chroma 基础使用、持久化、相似度检索
- 引用溯源：检索结果带来源，回答中标注出处
- 进阶优化：查询改写、混合检索、Rerank、HyDE

```
用户提问 → 文本向量化 → 在向量库中搜索相似片段 → 把片段 + 问题一起发给模型 → 模型基于片段回答
```

> 💡 **实践项目（求职作品级）**：企业知识库问答系统
> - 技术栈：FastAPI + Chroma + OpenAI/Ollama Embedding
> - 功能：上传文档 → 自动解析分块向量化 → 用户提问 → 检索 + 回答 → 引用溯源
> - 部署：Docker 容器化，能在服务器上跑起来

**学习顺序**：先手写 → 再 LangChain → 最后 LangGraph（Agentic RAG），每个阶段都有能跑的项目。


### 3.2 MCP — Model Context Protocol

> MCP 是新兴的模型-工具通信协议，**重在概念理解，不需要大量代码**。

**MCP 解决的问题**：让模型以统一协议访问外部工具、文件、数据库和服务，避免每个工具都写一套对接代码。

**核心架构**：Client ↔ MCP Server ↔ 外部工具

**知识点**：
- MCP 与普通 Function Calling / Tool Calling 的关系
- 使用现成的 MCP Server（文件系统、数据库、GitHub 等）
- MCP 在 Agent 工具生态中的位置
- MCP 与 A2A（Agent-to-Agent）协议的角色区分

> 学习资源：[MCP 官方文档](https://modelcontextprotocol.io)


### 3.3 Agent Skills — 能力技能化

**核心思想**：把 Agent 能力拆成可复用、可组合的技能模块，而不是把所有能力都塞进一个大 Prompt。

**知识点**：
- Skill 的定义：面向 Agent 的能力封装（输入 → 处理 → 输出）
- Skill 的描述和边界：直接决定 Agent 能否正确选用
- 多个 Skill 如何协作完成复杂任务
- Skill 与工具调用、文件处理、RAG 之间的关系

> 💡 **关键体会**：Skill 的描述质量直接影响 Agent 的表现——描述不清 = 选错工具 = 任务失败。


### 3.4 LangChain 框架 ★核心重点

> 把前面手写的 RAG 和 Agent 用 LangChain 重新组织，从"理解原理"进入"框架化开发"。分 RAG 和 Agent 两条线。

**LangChain RAG 线**：
- Document Loaders：`TextLoader`、`PyPDFLoader`、`DirectoryLoader`
- Text Splitters：`RecursiveCharacterTextSplitter`（重点）
- Embeddings：`OllamaEmbeddings`、`OpenAIEmbeddings`
- Vector Stores：Chroma、FAISS、持久化、`as_retriever()`
- Retrieval Chain：`create_stuff_documents_chain`、`create_retrieval_chain`
- 引用溯源：metadata 从加载到检索结果一路传递

**LangChain Agent 线**：
- Tool 定义：`@tool` 装饰器、docstring、参数 schema
- AgentExecutor：执行循环、最大迭代、调试和中间步骤
- Memory：`RunnableWithMessageHistory`（新版 API）
- 把 Retriever 包装成 Tool，让 Agent 使用 RAG


### 3.5 LangGraph 框架 ★进阶核心

> 用 LangGraph 把 RAG 和 Agent 从黑盒流程拆成可控的状态图，实现条件路由、循环、自纠错、持久化和人工介入。

**核心三件套**：State（状态）、Node（节点）、Edge（边）

**LangGraph Agent 线**：
- `StateGraph`、`START`、`END`、`add_messages`
- 条件路由：`add_conditional_edges`
- 手搓 ReAct Agent：`agent` 节点 + `tools` 节点 + `ToolNode` + 条件边循环
- Checkpointer：`MemorySaver` + `thread_id` 实现多轮状态记忆
- Human-in-the-Loop：`interrupt_before` 实现人工审批

**LangGraph RAG（Agentic RAG）线**：
- 传统 RAG 是直线流程，容易"垃圾进垃圾出"
- 用图重写：`retrieve → grade → rewrite → generate → check`
- 文档评分：判断检索结果是否相关
- 查询重写：检索不准时改写问题再检索
- 自纠错 RAG：幻觉检测和回答质量检测
- 循环刹车：`retry_count` 防止无限循环

> 💡 **实践项目**：完整客服 Agent「小 G」
> - RAG 工具 + 业务工具 + 敏感操作审批 + 多轮记忆
> - 技术栈：FastAPI + LangGraph + Chroma + OpenAI/Ollama + Docker


### 学习建议

1）**先手写、再框架化**：阶段 2 理解 Agent 原理，阶段 3 手写 RAG 和 Agent，然后用 LangChain 重写，最后用 LangGraph 升级。每一步都体会框架解决了什么问题。

2）RAG 要花够时间，做出一个完整的、能部署的项目。这是面试中最能展示能力的项目类型。

3）LangChain 的抽象层次高，初学者会觉得复杂。建议从最简单的 Chain 开始，逐步理解设计理念。

4）LangGraph 是进阶内容。只有当你觉得 LangChain 的 AgentExecutor 不够灵活时，才需要用 LangGraph 做更精细的控制。

5）MCP 和 Agent Skills 了解概念即可，重点把 RAG 和 Agent 做深做透。


### 经典面试题

1. 什么是 AI Agent？Agent 和 LLM 有什么区别？
2. ReAct 架构的工作原理是什么？
3. 如何实现 Agent 的工具调用？
4. Agent 的记忆系统如何设计？
5. 如何优化 Agent 的性能和准确性？
6. RAG 的完整流程是什么？如何优化检索质量？
7. LangChain 和 LangGraph 有什么区别？什么时候用哪个？
8. 什么是 MCP？它和 Function Calling 有什么关系？


### 学习资源

- ⭐ [2025 最好的 LangChain Agent 实战教程](https://www.bilibili.com/video/BV1xr3Mz2EXD/)：从零打造 AI 旅游助手
- [LangChain 中文文档](https://www.langchain.asia/)：官方中文文档
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)：Agent 编排框架
- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)
- [Chroma 文档](https://docs.trychroma.com)
- [MCP 官方文档](https://modelcontextprotocol.io)



## 阶段 4：多 Agent 系统（15-35 天，仅供参考）

多 Agent 系统是 Agent 技术的高级应用。通过多个 Agent 协作，可以完成更复杂的任务。比如软件开发 Agent 系统，可以由产品经理 Agent、架构师 Agent、程序员 Agent、测试 Agent 等协作完成软件开发。

![](https://pic.yupi.icu/1/ml-17975-image001.jpg)



### 学习目标

掌握多 Agent 协作系统的设计与实现，能够构建复杂的 Agent 应用。



### 知识点

**多 Agent 架构【必学】：**

- 多 Agent 协作模式
  - Supervisor（监督者调度）：一个主管 Agent 分配任务给多个执行 Agent
  - Hierarchical（层级式）：多层 Agent 树状结构，逐级分解任务
  - Pipeline（流水线）：Agent 按顺序处理，前一个输出是后一个输入
  - Network（网状）：Agent 自由通信，平等协作
  - Group Chat（群聊）：所有 Agent 在一个对话中共同决策
- Agent 通信机制：消息传递、结构化 JSON、共享黑板、结论式交接
- 任务分配和协调：静态分解、动态分解、Map-Reduce
- Agent 角色设计

**什么时候需要多 Agent？**
- 工具太多，单个 Agent 难以选择 → 按工具分组
- 角色冲突 → 不同 Agent 负责不同角色
- 任务可并行 → 多个 Agent 同时执行
- 需要独立审查 → 一个 Agent 生成，另一个 Agent 检查

**多 Agent 的代价 ⚠️**：
- 成本上升（多个 Agent 调用多次 LLM）
- 延迟变高（串行调用）
- 调试困难（错误可能级联放大）
- 上下文爆炸（Agent 间传递过多信息）

> 💡 **原则**：能用单 Agent 解决的，不要上多 Agent。先问自己"单 Agent 哪里不够？"

**MetaGPT 框架【建议学】：**

- MetaGPT 架构
- 软件开发 Agent
- 多角色协作
- 工作流编排

**AutoGen 框架【建议学】：**

- AutoGen 架构
- 对话式 Agent
- 群聊模式
- 自定义 Agent

**Agent 编排【必学】：**

- 工作流设计
- 条件分支
- 循环和迭代
- 错误处理和重试



### 学习建议

1）MetaGPT 是多 Agent 系统的代表作，它模拟了软件公司的工作流程，通过多个 Agent 的协作完成软件开发。建议研究 MetaGPT 的源代码，理解多 Agent 系统的设计思路。

2）AutoGen 是微软开源的多 Agent 框架，支持对话式的 Agent 协作。AutoGen 的设计更加灵活，适合构建各种类型的多 Agent 应用。建议学习 AutoGen 的使用方法，尝试构建自己的多 Agent 系统。

3）Agent 编排是多 Agent 系统的关键。要设计好 Agent 之间的协作流程，明确每个 Agent 的职责，设计好通信机制。LangGraph 提供了强大的编排能力，建议使用 LangGraph 构建复杂的多 Agent 系统。

4）**工程化陷阱必须重视**：死循环（Agent 反复调用同一工具）、责任扩散（Agent 多了没人负责）、上下文爆炸（传递过多信息）、级联失败（一个 Agent 出错导致后续全部出错）。牢记：必须设置终止条件、日志、评估和成本控制。

5）这个阶段不需要做完整项目，搭一个简单 demo 能讲清原理即可（如 CrewAI 或 LangGraph 的 Supervisor 模式）。



### 学习资源

- [MetaGPT GitHub](https://github.com/geekan/MetaGPT)：开源多 Agent 框架
- [AutoGen 官方文档](https://microsoft.github.io/autogen/)：微软多 Agent 框架



## 阶段 5：Agent 优化和部署（10-30 天，仅供参考）


Agent 优化和部署是提升应用性能和稳定性的重要环节，包括性能调优、成本优化以及生产环境部署等内容。



### 学习目标

掌握 Agent 的优化技巧和部署方法，能够开发生产级的 Agent 应用。



### 知识点

**性能优化【必学】：**

- Prompt 优化
- 缓存策略
- 并行执行
- 流式输出
- 成本控制

**安全和可控性【必学】：**

- 输入过滤
- 输出审查
- 权限控制
- 敏感信息保护
- Agent 行为约束

**监控和调试【必学】：**

- LangSmith
- 日志分析
- 性能监控
- 错误追踪
- A/B 测试

**部署方案【必学】：**

- API 服务部署（FastAPI + Uvicorn）
- Docker 容器化部署：编写 Dockerfile，一键部署
- Web 应用部署（Streamlit / Gradio 快速搭建前端）
- 消息队列集成
- 微信/钉钉集成

**评估与测试【建议学】：**

- RAG 检索质量评估（检索准确率、召回率）
- Agent 执行效果评估（任务完成率、平均步数）
- Token 成本监控


### 学习建议

1）性能优化对生产环境的 Agent 至关重要。要关注响应时间、成本、准确率等指标。常见的优化方法包括：优化 Prompt 减少 Token 消耗、使用缓存避免重复调用、并行执行提高效率等。

2）安全性是 Agent 应用必须考虑的问题。Agent 可能会执行危险操作（如删除文件、调用付费 API），必须有严格的权限控制。要对用户输入进行过滤，对 Agent 的行为进行约束，对输出进行审查。

3）LangSmith 是 LangChain 官方的监控和调试工具，强烈建议使用。LangSmith 可以记录 Agent 的每一步执行过程，帮助你分析问题、优化性能。对于生产环境的 Agent，监控和日志是必不可少的。

4）Agent 的部署方式有多种：可以部署为 API 服务供其他应用调用，可以开发 Web 界面供用户使用，可以集成到微信、钉钉等平台。要根据实际需求选择合适的部署方式。

5）**Docker 部署是必备技能**：项目要能 Docker 一键部署，面试时能现场演示。至少掌握 Dockerfile 编写和 docker-compose 的基本使用。



### 学习资源

- [LangSmith 文档](https://docs.smith.langchain.com/)：官方监控工具
- [Agent 部署最佳实践](https://mgoods.taobao.com/t/aijiaocheng_17011/98fd81d1836eb4d0c3c777ae26dcae9a.html)：2025 最新指南



## 阶段 6：项目实战（20-50 天，仅供参考）

### 学习目标

通过完整的项目实践，综合运用所学知识，积累 Agent 开发经验。



### 学习建议

1）这个阶段的核心是**整合前面所有知识**，做出 1-2 个能部署、能展示的完整项目。不要追求数量，把一个场景做深做透。

2）**推荐项目组合**（二选一或都做）：

**项目一：RAG 知识库问答系统（展示 RAG + LangChain/LangGraph 能力）**
```
技术栈：FastAPI + LangChain/LangGraph + Chroma + OpenAI/Ollama + Docker
亮点：完整文档处理 pipeline、引用溯源、评分/重写/自纠错（Agentic RAG）、
      流式输出（SSE）、Docker 一键部署、简单前端（Streamlit/Gradio）
```

**项目二：智能客服/业务 Agent（展示 Agent 能力）**
```
技术栈：FastAPI + LangGraph + Chroma + OpenAI/Ollama + Docker
亮点：多工具调用、RAG 作为工具、多轮记忆、敏感操作人工审批（Human-in-the-Loop）、
      循环刹车与成本控制
```

3）**项目要求（面试标准）**：
- 代码放 GitHub，README 写清楚架构和使用方法
- 能 Docker 一键部署（`docker-compose up`）
- 有简单前端可演示
- 能讲清技术选型和架构设计
- 能说明为什么这样设计（而不是"教程就是这么写的"）

4）关注用户体验。Agent 的响应速度、准确性、易用性都很重要。要收集用户反馈，不断优化 Prompt 和工具，提升 Agent 的能力。

5）建议将项目开源或写成技术博客。这不仅能帮助别人，也能作为你的作品展示给面试官。在简历上能展示一个完整的 Agent 项目，会大大提升你的竞争力。

6）可以参考鱼皮的 AI 项目教程，学习如何开发高质量的 AI 应用。鱼皮的 [项目实战教程](https://www.codefather.cn/post/1797431216467001345) 提供了很多实用的开发经验和技巧。



### 项目推荐

**鱼皮原创 Spring AI 技术栈项目：**

- ⭐ [AI 超级智能体项目（26年最新）](https://www.codefather.cn/course/1915010091721236482)：Spring Boot 3 + Spring AI，实战 AI 恋爱大师 + 拥有自主规划能力的超级智能体，涵盖 RAG、Tool Calling、MCP、AI 智能体等核心技术

**鱼皮原创 LangChain4j 技术栈项目：**

- [AI 零代码应用生成平台（25年最新）](https://www.codefather.cn/course/1948291549923344386)：LangChain4j + LangGraph4j，实战 AI 智能体、工作流编排，微服务架构
- [智能面试刷题平台](https://www.codefather.cn/course/1813803565348171777)：LangChain4j，实战 AI 面试官、题目推荐、AI 评分
- [AI 答题应用平台](https://www.codefather.cn/course/1829027861542105089)：LangChain4j，实战 AI 应用开发、SSE 实时推送、RxJava 响应式编程
- [智能 BI 项目](https://www.codefather.cn/course/1790980531403927553)：LangChain4j + AI 图表生成，实战异步化 + 线程池 + RabbitMQ

**其他项目方向：**

- 智能客服 Agent
- 代码生成和审查 Agent
- SQL 查询助手 Agent
- 文档问答 Agent
- 自动化运营 Agent



### 学习资源

- ⭐ [鱼皮的 AI 项目教程合集](https://www.codefather.cn/post/1797431216467001345)：原创项目实战



## 阶段 7：求职备战

### 学习目标

熟练掌握 AI Agent 开发常见面试题，准备好简历和项目经历，顺利通过面试。



### 学习建议

1）准备项目：简历上一定要有 AI Agent 项目经历，最好是完整的、可以在线访问的 Agent 应用。面试时可能会要求演示你的 Agent 项目，建议提前准备好项目的演示视频和介绍文档。

2）准备简历：建议使用 [老鱼简历](https://www.laoyujianli.com/) 快速制作简历，有很多现成的模板直接拿来套，节省时间。

![老鱼简历网站简历模板大全](https://pic.yupi.icu/1/%E8%80%81%E9%B1%BC%E7%AE%80%E5%8E%86%E7%BD%91%E7%AB%99%E7%AE%80%E5%8E%86%E6%A8%A1%E6%9D%BF%E5%A4%A7%E5%85%A8.png)

关于如何写好简历，推荐学习鱼皮的 [保姆级写简历指南](https://www.codefather.cn/course/1802644557818343425)。

3）多刷面试题：AI Agent 的面试题主要包括 Agent 基础概念、架构设计、工具调用、RAG 等。建议使用 [面试鸭](https://www.mianshiya.com/) 刷题，重点关注 AI Agent、LangChain 等关键词。

![面试鸭刷题神器热门八股文](https://pic.yupi.icu/1/%E9%9D%A2%E8%AF%95%E9%B8%AD%E5%88%B7%E9%A2%98%E7%A5%9E%E5%99%A8%E7%83%AD%E9%97%A8%E5%85%AB%E8%82%A1%E6%96%87.png)

4）AI Agent 技术发展很快，要关注最新的技术趋势和应用案例。了解 OpenAI、Anthropic、国内大厂在 Agent 方向的最新进展。

更多求职干货：[编程导航求职干货分享](https://www.codefather.cn/learn?category=76&type=2)



### 经典面试题

**基础概念：**

1. 什么是 AI Agent？Agent 和普通的 LLM 应用有什么区别？
2. Agent 的核心能力有哪些？
3. 什么是 ReAct 架构？如何工作的？
4. Agent 的记忆系统如何设计？
5. 什么是 Function Calling？如何实现？

**架构设计：**

1. 如何设计一个智能客服 Agent？
2. 多 Agent 系统如何协作？
3. 如何让 Agent 调用外部工具？
4. 如何设计 Agent 的工作流？
5. 如何保证 Agent 的可控性和安全性？

**技术实现：**

1. LangChain 和 LangGraph 有什么区别？
2. 如何优化 Agent 的性能？
3. 如何调试 Agent 的执行过程？
4. RAG 和 Agent 如何结合？
5. 如何处理 Agent 的错误和异常？

**项目经验：**

1. 你开发过哪些 Agent 应用？详细说说。
2. 项目中遇到过什么技术难点？如何解决的？
3. 如何优化 Agent 的准确性和响应速度？
4. 如何评估 Agent 的性能？
5. Agent 上线后遇到过哪些问题？



### 面试题库

- ⭐ [AI 面试题 - 面试鸭](https://www.mianshiya.com/bank/1906189461556076546)
- [LangChain 面试题 - 面试鸭](https://www.mianshiya.com/bank/1991427331415080961)



### 求职资源

- ⭐ [鱼皮的保姆级求职指南](https://www.codefather.cn/course/job)：从简历到面试的完整指南
- ⭐ [鱼皮的保姆级写简历指南](https://www.codefather.cn/course/1802644557818343425)：如何写出高质量简历
- [编程导航的求职干货分享](https://www.codefather.cn/learn?category=76&type=2)：求职经验和技巧
- [老鱼简历](https://www.laoyujianli.com/)：写简历工具 + 简历模板大全
- [真实面经大全](https://www.codefather.cn/job/experience)：了解真实的面试流程
- [几百场真实面试视频](https://www.codefather.cn/mockInterview)：观看他人的面试过程
- [1 对 1 模拟面试](https://ai.mianshiya.com/)：AI 模拟面试练习
- [面试题讲解视频](https://space.bilibili.com/3546383483144655)：面试鸭官方题解



## 更多资源

### 知识总结

- ⭐ [编程导航](https://www.codefather.cn/)：学习路线、项目教程、面试题、编程资源一站式平台
- ⭐ [AI 导航](https://ai.codefather.cn/)：AI 工具和资源大全
- [AI 大模型应用开发学习路线](https://www.codefather.cn/course/1789189862986850306/section/1912024009574629377)：完整的 AI 学习路线

### Agent 资源

- [LangChain 官方文档](https://python.langchain.com/)：最权威的文档
- [LangChain 中文文档](https://www.langchain.asia/)：中文学习资源
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)：Agent 编排框架

### 开源项目

- [MetaGPT](https://github.com/geekan/MetaGPT)：多 Agent 协作框架
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)：自主 Agent
- [AutoGen](https://github.com/microsoft/autogen)：微软多 Agent 框架


## 总体时间规划

| 阶段 | 内容 | 时间 | 难度 | 优先级 |
|------|------|------|------|--------|
| 1 | AI 大模型基础 + Ollama | 1-2 周 | ⭐ | 必学 |
| 2 | Agent 基础概念 | 1-2 周 | ⭐⭐ | 必学 |
| 3 | RAG + MCP + Agent Skills + LangChain/LangGraph | 3-5 周 | ⭐⭐⭐ | 核心重点 |
| 4 | 多 Agent 系统 | 1-2 周 | ⭐⭐⭐⭐ | 了解为主 |
| 5 | 优化和部署 | 1-2 周 | ⭐⭐⭐ | 必学 |
| 6 | 项目实战 | 2-3 周 | ⭐⭐⭐⭐ | 必做 |
| 7 | 求职备战 | 1-2 周 | ⭐⭐⭐ | 必做 |

**总计：约 2.5-3.5 个月（每天投入 4-6 小时）**

> **主线**：先理解模型和 RAG → 再掌握 Agent 和工具调用 → 最后用 LangChain / LangGraph 把能力组织成可维护、可扩展的真实应用。


## 求职方向参考

你的背景（Python + FastAPI + AI 应用）适合的岗位：

| 岗位 | 核心要求 | 你的优势 |
|------|---------|---------|
| RAG 工程师 | RAG pipeline、向量数据库、文档处理 | 后端工程化能力 + FastAPI |
| LLM 应用开发 | API 集成、Agent 开发、Prompt Engineering | Python 全栈 + 项目经验 |
| AI 平台开发 | 内部 AI 平台搭建、API 网关、模型管理 | 后端架构经验 + FastAPI |
| AI 全栈工程师 | 前后端 + AI 能力整合 | 后端扎实 + AI 应用能力 |


## 学习建议

1. **每个阶段都要有产出**：不是看完文档就行，要有能跑的代码和能演示的项目
2. **RAG 和 Agent 是绝对核心**：这两块各花充足时间，做出求职级别的项目
3. **先手写、再框架化**：先理解原理，再用 LangChain/LangGraph 重写，体会框架解决了什么
4. **结合后端优势**：FastAPI + LangChain/LangGraph + Chroma 这个组合面试很加分
5. **不要贪多**：MCP、多 Agent 了解概念即可，把核心技能做深做透
6. **项目要能部署**：Docker 容器化，GitHub 上有完整代码和文档，面试时能现场演示


## 相关知识（做项目时遇到再学）

| 知识 | 说明 | 什么时候会用到 |
|------|------|--------------|
| AI 应用安全 | Prompt 注入防护、内容审核、敏感信息过滤 | 项目上线时必须考虑 |
| 评估与测试 | 评估 RAG 检索质量、Agent 执行效果 | 做 RAG/Agent 项目时 |
| 日志与监控 | LangSmith、日志记录、Token 成本监控 | 生产环境部署时 |
| 异步与并发 | Python asyncio，高并发下的 AI 调用 | FastAPI 项目优化时 |
| 缓存策略 | 相同问题缓存回答，省 Token 省钱 | 生产环境成本优化 |
| 多模态 | 图片、音频、视频输入处理 | 加分项，面试有亮点 |

**这些不需要单独学，做项目过程中遇到了再学就行。**


## 写在最后

AI Agent 是 AI 应用开发的未来方向，掌握 Agent 技术将让你在 AI 浪潮中 “遥遥领先”。

学习 AI Agent 开发要先打好 AI 大模型基础，理解 LLM 的能力和使用方法。深入学习 Agent 的核心概念和架构模式，特别是 ReAct 和工具调用。掌握 LangChain、LangGraph 等主流框架的使用。进阶学习多 Agent 系统和复杂工作流的设计。通过完整的项目实践，积累开发经验。

AI Agent 技术发展很快，要保持学习和关注最新动态。多看文章资讯、多看开源项目、多动手实践（有能力的同学还可以多读读论文）。

此外，还可以积极参加 AI 社区的讨论，分享你的经验和作品，对外输出是倒逼自己输入知识的最好方式，共勉！

![](https://pic.yupi.icu/1/%E9%B1%BC%E7%9A%AE%E6%84%9F%E8%B0%A2.png)




## 程序员必备资源

1）程序员学习交流圈：[极客教程、实战项目、求职宝典](https://www.codefather.cn)

2）程序员面试八股文：[实习/校招/社招高频考点、企业真题解析](https://www.mianshiya.com)

3）程序员写简历神器：[专业模板、丰富例句、直通面试](https://www.laoyujianli.com)

4）AI 知识资源大全：[前沿技术、最新 AI 资讯、提示词大全](https://ai.codefather.cn)

5）1 对 1 模拟面试：[实习/校招/社招面试拿 Offer 必备](https://ai.mianshiya.com)
