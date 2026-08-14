"""2026 AI Agent 应用开发课程体系种子生成器。

依据《2026年最新AIAgent应用开发学习路线零基础到精通一条龙》7 阶段结构，
生成 24 门课程（含章节/小节/知识点/案例）、24 条配套教学视频、7 个学习方向、
以及按新课程 ID 重排的学习路径，直接写出 backend/data/processed/*.json。

用法：
    python -m data_pipeline.curriculum_2026          # 写入 processed/*.json
    python -m database                                # 重建 SQLite 数据库
"""
import json
import os

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")

# 各阶段映射到的真实教学视频（来自学习路线「学习资源」章节）
BILIBILI_BLACKHORSE = "BV1h1VbzHER2"   # 黑马 Python+AI 大模型（阶段一）
BILIBILI_AGENT = "BV18hWtzuErE"        # 2025 AI Agent 智能体全套（阶段二/四）
BILIBILI_LANGCHAIN = "BV1xr3Mz2EXD"    # 2025 最好的 LangChain Agent 实战（阶段三/五）

DOC_RAG = "https://python.langchain.com/docs/tutorials/rag/"
DOC_MCP = "https://modelcontextprotocol.io"
DOC_LANGGRAPH = "https://langchain-ai.github.io/langgraph/"
DOC_METAGPT = "https://github.com/geekan/MetaGPT"
DOC_AUTOGEN = "https://microsoft.github.io/autogen/"
DOC_LANGSMITH = "https://docs.smith.langchain.com/"
DOC_LANGCHAIN_ZH = "https://www.langchain.asia/"
DOC_DEPLOY = "https://mgoods.taobao.com/t/aijiaocheng_17011/98fd81d1836eb4d0c3c777ae26dcae9a.html"
DOC_YUPI_PROJECTS = "https://www.codefather.cn/post/1797431216467001345"
DOC_MIANSHIYA = "https://www.mianshiya.com/bank/1906189461556076546"


def _sec(sec_id, title, content, knowledge_points, case=""):
    return {"id": sec_id, "title": title, "content": content,
            "knowledge_points": knowledge_points, "case": case}


def _ch(ch_id, title, summary, duration, sections, video_bv="", video_page=1):
    return {"id": ch_id, "title": title, "content_summary": summary,
            "duration_minutes": duration, "video_bv": video_bv,
            "video_page": video_page, "sections": sections}


def _course(cid, title, description, topic, difficulty, hours, chapters, video_bv=""):
    """组装课程 dict；lessons=小节总数。video_bv 为 B 站 BV 时灌到每章（章节页内嵌播放器）。"""
    lessons = sum(len(ch["sections"]) for ch in chapters)
    if video_bv:
        for ch in chapters:
            if not ch.get("video_bv"):
                ch["video_bv"] = video_bv
    return {
        "id": cid, "title": title, "description": description,
        "topic": topic, "difficulty": difficulty, "estimated_hours": hours,
        "lessons": lessons, "source": "curriculum-2026",
        "coverImg": f"https://picsum.photos/seed/{cid}/300/200",
        "isFree": 1, "price": 0, "chapters": chapters,
    }


# =====================================================================
# 阶段一：AI 大模型基础
# =====================================================================
STAGE1_COURSES = [
    _course(
        "s1-llm-basics", "大模型基础概念：认识 LLM",
        "从零理解大语言模型（LLM）是什么、如何工作，掌握主流模型与选型思路，建立对模型能力和局限的正确认知，为后续 Agent 开发打好地基。",
        "大模型基础", "beginner", 6,
        [
            _ch("s1-llm-c1", "什么是大语言模型（LLM）", "用一句话和例子讲清 LLM 的本质：一个学会『接话』的概率模型，以及它能做什么、不能做什么。", 30, [
                _sec("s1-llm-c1-s1", "LLM 是一台『接话机器』", "LLM 的核心机制是根据上文预测下一个最可能的词/Token，逐字生成完整回复。它不是真正理解，而是学习到了海量文本中的统计规律。这一认知决定你如何看待它的输出：永远是『最可能』而非『最正确』。",
                    ["LLM 定义", "自回归生成", "概率预测"],
                    "让 LLM 写一段工作总结，你会发现它总能把句子接得很通顺，但具体数字可能靠编——这就是『接话』与『理解』的区别。"),
                _sec("s1-llm-c1-s2", "LLM 能做什么、不能做什么", "LLM 擅长：文本生成、总结、翻译、改写、代码、头脑风暴、结构化提取。不擅长：精确计算、实时信息、事实核查、多步复杂推理、长上下文保持。明确能力边界，才不会用错地方。",
                    ["LLM 能力边界", "适用场景"]),
            ]),
            _ch("s1-llm-c2", "Transformer 架构入门", "不用啃数学，用直觉理解 Transformer 的两个核心部件：注意力机制与位置编码，知道『并行训练 + 海量数据』为什么能造出 GPT/Claude。", 35, [
                _sec("s1-llm-c2-s1", "注意力机制：让模型学会『看哪里』", "自注意力让每个词在看上下文时，对不同位置分配不同权重。例如『苹果』是水果还是公司，由上下文决定。这是 Transformer 相比 RNN 能并行训练的关键。",
                    ["注意力机制", "自注意力", "并行训练"]),
                _sec("s1-llm-c2-s2", "从 Transformer 到大模型", "预训练（预测下一个词）→ 指令微调（听懂人话）→ 对齐（符合人类偏好），三步构建出现代大模型。理解这条流水线，你就明白『提示词』为何重要。",
                    ["预训练", "指令微调", "对齐"]),
            ]),
            _ch("s1-llm-c3", "主流大模型与选型", "横向对比 GPT、Claude、文心一言、通义千问、DeepSeek、GLM 等，学会按任务场景选择合适的模型。", 30, [
                _sec("s1-llm-c3-s1", "海外与国产大模型概览", "OpenAI GPT-4o 系列、Anthropic Claude 系列、Google Gemini；国产：文心一言、通义千问、Kimi、DeepSeek、智谱 GLM。各有擅长领域与定价。",
                    ["主流模型", "模型对比"]),
                _sec("s1-llm-c3-s2", "选型四要素", "按 ①任务类型 ②成本预算 ③数据隐私（国内合规）④上下文长度 选模型。写代码可用 Claude/GPT，中文创作可用通义/Kimi，私有数据优先本地模型。",
                    ["模型选型", "成本与合规"],
                    "做一个中文客服知识库，选国产模型可规避出海数据合规风险，成本也低一半。"),
            ]),
            _ch("s1-llm-c4", "Token 与上下文窗口", "理解 Token 是计费和能力的双单位：tokenizer 如何切词、上下文窗口多长、超窗会丢什么、如何估算成本。", 30, [
                _sec("s1-llm-c4-s1", "Token 是什么", "Token 是文本的最小计费单元，约 1 个汉字≈1-2 token、1 个英文单词≈1-1.5 token。输入+输出都按 Token 计费，估算成本先算 Token。",
                    ["Token", "计费"]),
                _sec("s1-llm-c4-s2", "上下文窗口与超窗处理", "上下文窗口=模型一次能看到的全部 Token。超出会被截断，导致『失忆』。工程上通过滑动窗口、摘要压缩、向量检索来控制上下文占用。",
                    ["上下文窗口", "截断", "滑动窗口"]),
            ]),
            _ch("s1-llm-c5", "模型能力与局限性", "系统梳理幻觉、知识截止、推理能力上限、偏见等问题，建立『AI 会犯错』的工程心态，学会校验与降级策略。", 30, [
                _sec("s1-llm-c5-s1", "幻觉与知识过时", "幻觉=模型一本正经地编造事实；知识截止=不知道训练后的新事件。对策：给上下文（RAG）、要求引用、人工复核关键信息。",
                    ["幻觉", "知识截止"],
                    "让模型报今天日期或最新政策，它常会编——这类信息必须由系统实时提供。"),
                _sec("s1-llm-c5-s2", "推理上限与偏见", "复杂多步推理（数学、逻辑）仍是短板；训练数据偏见会让输出有倾向。工程上：拆解任务、增加校验步骤、敏感场景人工兜底。",
                    ["推理上限", "偏见"]),
            ]),
        ],
        video_bv=BILIBILI_BLACKHORSE,
    ),
    _course(
        "s1-prompt", "Prompt Engineering 提示词工程",
        "提示词是与大模型沟通的唯一语言。系统掌握 Prompt 基础、Few-shot、思维链、角色扮演与优化技巧，让 AI 输出稳定、高质量、可复现。",
        "大模型基础", "beginner", 8,
        [
            _ch("s1-prompt-c1", "Prompt 基础：一句话说清任务", "掌握写好一条提示词的要素：明确任务、提供上下文、指定输出格式，用『清晰、具体、可执行』三原则。", 30, [
                _sec("s1-prompt-c1-s1", "好 Prompt 的三要素", "①任务动词清晰（总结/改写/生成/分类）②给足背景上下文 ③明确输出格式（列表/表格/字数）。缺一，输出就飘。",
                    ["Prompt 三要素", "任务动词", "输出格式"]),
                _sec("s1-prompt-c1-s2", "常见坑：模糊与期望错位", "『写得好一点』『帮我看看』这类模糊指令必然得到平庸输出。把期望量化：长度、风格、受众、语气、禁忌。",
                    ["模糊指令", "期望管理"]),
            ]),
            _ch("s1-prompt-c2", "Few-shot Learning：给示例", "在提示词里给 2-3 个输入输出示例（Few-shot），让模型模仿格式与风格，是提升稳定性的最便宜手段。", 35, [
                _sec("s1-prompt-c2-s1", "示例的作用与写法", "示例教会模型『什么是好的输出』，尤其是格式与风格模仿。示例要覆盖正常情况+一个边界情况，避免模型只会照抄。",
                    ["Few-shot", "示例设计"],
                    "让 AI 把客户差评分类为『物流/质量/态度』，给 3 条带标签示例，准确率立刻提升。"),
                _sec("s1-prompt-c2-s2", "示例的成本与取舍", "每个示例都占 Token、都会计费。示例少而精：选最典型、最能界定边界的样例，控制总量。",
                    ["Few-shot 成本"]),
            ]),
            _ch("s1-prompt-c3", "Chain of Thought 思维链", "引导模型『先想再答』：在提示中要求分步推理，显著提升数学、逻辑、多步任务的表现。", 35, [
                _sec("s1-prompt-c3-s1", "思维链的原理", "直接要答案容易错；让模型先写出推理步骤再给结论，相当于把『思考过程』外显，减少一步到位的跳步错误。",
                    ["思维链", "CoT", "分步推理"]),
                _sec("s1-prompt-c3-s2", "CoT 的三种用法", "①零样本触发（『让我们一步步思考』）②给一条示例思路 ③要求结构化输出思考+答案。注意：在不需要推理的场景用 CoT 反而浪费 Token。",
                    ["零样本 CoT", "结构化思考"]),
            ]),
            _ch("s1-prompt-c4", "角色扮演与场景化", "给模型一个专业角色（律师/导师/面试官）加场景约束，激活对应知识域与语气，让输出更贴合目标读者。", 30, [
                _sec("s1-prompt-c4-s1", "角色设定的写法", "『你是一位有 10 年经验的资深后端面试官』比『帮我出题』输出专业得多。角色+经验年限+专业领域+输出语气，四件套。",
                    ["角色扮演", "角色设定"]),
                _sec("s1-prompt-c4-s2", "场景化约束", "设定场景（给 12 岁孩子讲）、约束（不要用术语）、风格（口语化/正式）共同决定输出适配度。",
                    ["场景化", "受众约束"]),
            ]),
            _ch("s1-prompt-c5", "Prompt 优化与迭代", "把写 Prompt 当成迭代开发：基线→测试→诊断→改进，学会追问『哪里不满意、怎么改』。", 35, [
                _sec("s1-prompt-c5-s1", "迭代方法论", "先写一版快速跑通，再针对输出问题逐项优化：结果不全→加要求；格式乱→加示例；风格不对→加角色。记录每次改动。",
                    ["Prompt 迭代", "诊断改进"]),
                _sec("s1-prompt-c5-s2", "提示词模板化", "把可复用提示词抽象成模板（占位符替换），沉淀成团队资产。这也是 Agent Skills 思想的雏形。",
                    ["提示词模板", "可复用"]),
            ]),
        ],
        video_bv=BILIBILI_BLACKHORSE,
    ),
    _course(
        "s1-api-dev", "大模型 API 调用与 AI 开发规范",
        "从网页对话走向代码调用：掌握 OpenAI/国产大模型 API、关键参数、流式输出、错误处理，并养成 API Key 管理、脚本结构、依赖管理等工程化习惯。",
        "大模型基础", "beginner", 8,
        [
            _ch("s1-api-c1", "OpenAI API 快速上手", "用最小代码完成一次 Chat Completion 调用，理解 messages 结构（system/user/assistant）与响应体。", 35, [
                _sec("s1-api-c1-s1", "第一次调用", "通过 openai SDK 或 HTTP POST 调用 /chat/completions，入参 model、messages，出参 choices[0].message.content。",
                    ["OpenAI API", "Chat Completions", "messages 结构"]),
                _sec("s1-api-c1-s2", "system / user / assistant 分工", "system 设定行为基调，user 是用户输入，assistant 是历史回复。多轮对话就是不断追加这三类消息。",
                    ["system prompt", "多轮对话"]),
            ]),
            _ch("s1-api-c2", "国产大模型 API", "以阿里云百炼、智谱 GLM、DeepSeek 为例，对比国产 API 的接入方式与差异，学会一套代码适配多家。", 35, [
                _sec("s1-api-c2-s1", "国产 API 与 OpenAI 兼容", "多数国产平台提供 OpenAI 兼容接口，只需换 base_url 与 key 即可切换，是 Agent 开发中切换模型的标准姿势。",
                    ["国产大模型 API", "OpenAI 兼容"]),
                _sec("s1-api-c2-s2", "多模型接入抽象", "把『模型名+base_url+key』做成配置，用工厂函数返回统一调用接口，业务代码不感知底层换了哪家。",
                    ["模型抽象", "多供应商"]),
            ]),
            _ch("s1-api-c3", "关键参数：temperature / top_p / max_tokens", "逐参数讲解对输出的影响：温度控制随机性、top_p 核采样、max_tokens 限长，学会按场景调参。", 30, [
                _sec("s1-api-c3-s1", "temperature 与 top_p", "temperature 越高越随机、越低越确定；top_p 按概率累积裁剪候选。两者不要同时调，固定一个。写代码用低温，创意用高温。",
                    ["temperature", "top_p"]),
                _sec("s1-api-c3-s2", "max_tokens 与停止符", "max_tokens 限制生成长度并直接决定成本；stop 序列让模型在遇到指定词时提前停止，是结构化输出的常用手段。",
                    ["max_tokens", "stop 序列"]),
            ]),
            _ch("s1-api-c4", "流式输出与错误处理", "用 stream=True 实现打字机式逐字输出（SSE），处理超时、限流、上下文长度超限等常见异常并重试。", 40, [
                _sec("s1-api-c4-s1", "流式输出", "开启 stream 后以增量 chunks 接收，逐块渲染。前端 SSE 体验更好，也让用户感知『在思考』。",
                    ["流式输出", "SSE"]),
                _sec("s1-api-c4-s2", "错误处理与重试", "429 限流→退避重试；400 参数错→检查请求；超时→加大 timeout 或拆分请求；context length 超限→截断或压缩历史。",
                    ["限流重试", "异常处理", "上下文超限"]),
            ]),
            _ch("s1-api-c5", "AI 开发规范：从脚本到工程", "API Key 走环境变量禁硬编码、脚本按『输入→处理→输出』组织、用 venv 与 requirements.txt 管依赖，这是后续所有项目的基石。", 35, [
                _sec("s1-api-c5-s1", "API Key 管理与 .env", "用 python-dotenv 从 .env 读 key，gitignore 排除。硬编码密钥=事故，任何提交前都检查。",
                    ["API Key 管理", "环境变量", ".env"],
                    "误把带 key 的 .env 提交到 GitHub，几分钟内就会被爬虫盗用产生账单。"),
                _sec("s1-api-c5-s2", "脚本结构与依赖管理", "输入→处理→输出 的清晰分层；用虚拟环境+requirements.txt 锁依赖，让项目在任何机器一键可跑。",
                    ["脚本结构", "虚拟环境", "依赖管理"]),
            ]),
        ],
        video_bv=BILIBILI_BLACKHORSE,
    ),
    _course(
        "s1-ollama", "Ollama 本地模型部署",
        "在本地免费跑大模型：安装 Ollama、拉取 qwen2.5 等模型、用 Python/HTTP 调用，把『不花钱用 AI + 数据不出本地』变成开发常态。",
        "大模型基础", "beginner", 5,
        [
            _ch("s1-ollama-c1", "本地模型 vs 云端 API", "对比两者的适用场景：本地免费、无限调用、数据私密、可离线调试；云端更强、更稳、可扩展。开发用本地，上线用云端。", 30, [
                _sec("s1-ollama-c1-s1", "各有所长的取舍", "本地优势：免费、无限调用、数据不出本地、适合反复调试；云端优势：能力更强、并发稳定、免运维。",
                    ["本地 vs 云端", "适用场景"]),
                _sec("s1-ollama-c1-s2", "开发工作流定位", "开发期所有 Demo 先用本地模型跑通，上线前再切云端 API——成本最低、迭代最快。",
                    ["开发工作流"]),
            ]),
            _ch("s1-ollama-c2", "安装 Ollama 与拉取模型", "跨平台安装 Ollama，用 ollama pull/run 拉取并运行 qwen2.5:7b 等模型，体验命令行对话。", 35, [
                _sec("s1-ollama-c2-s1", "安装与常用命令", "ollama pull <model> 下载、ollama run <model> 对话、ollama list 查看本地模型、ollama ps 看运行中。",
                    ["Ollama 安装", "pull", "run"]),
                _sec("s1-ollama-c2-s2", "选模型与量化", "小参数模型（qwen2.5:7b）够日常调试；显存够可上 14b/32b。了解 Q4/Q8 量化对显存与效果的影响。",
                    ["模型选择", "量化"]),
            ]),
            _ch("s1-ollama-c3", "Python / HTTP 调用本地模型", "Ollama 默认提供 OpenAI 兼容接口，用 Python 一行切换本地模型；掌握 /api/chat 原生接口。", 35, [
                _sec("s1-ollama-c3-s1", "OpenAI 兼容调用", "base_url 指向 http://localhost:11434/v1，代码与云端几乎一致——这是它最大的价值：换一行配置就能本地跑。",
                    ["OpenAI 兼容", "localhost:11434"]),
                _sec("s1-ollama-c3-s2", "原生 API 与流式", "直接 POST /api/chat 支持流式返回；适合需要精细控制本地推理的场景。",
                    ["Ollama API", "流式"]),
            ]),
            _ch("s1-ollama-c4", "本地调试的完整工作流", "把 Ollama 接入你的第一个脚本：加载文档→提问→本地回答，为阶段三手写 RAG 的 Embedding 与推理做准备。", 35, [
                _sec("s1-ollama-c4-s1", "第一个本地 AI 脚本", "读取本地 .md 文件，拼进 system prompt，调用本地模型做总结/问答，数据全程不出机器。",
                    ["本地脚本", "数据不出本地"]),
                _sec("s1-ollama-c4-s2", "Ollama Embedding 与后续衔接", "Ollama 也提供 embedding 模型（nomic-embed-text 等），阶段三 RAG 会复用本地 Embedding，本章先留个印象。",
                    ["Ollama Embedding", "RAG 衔接"]),
            ]),
        ],
        video_bv=BILIBILI_BLACKHORSE,
    ),
]

# =====================================================================
# 阶段二：Agent 基础概念
# =====================================================================
STAGE2_COURSES = [
    _course(
        "s2-agent-core", "AI Agent 核心概念",
        "理解 AI Agent 的本质：从『被动回答』到『主动执行』。掌握感知、推理、决策、执行四大核心能力，理清 Agent 与 LLM 的区别与应用场景。",
        "Agent基础", "beginner", 6,
        [
            _ch("s2-core-c1", "什么是 AI Agent", "给 Agent 一个清晰定义：能感知环境、自主决策、调用工具、执行任务达成目标的智能体，是 LLM 之上的一层『行为能力』。", 30, [
                _sec("s2-core-c1-s1", "从聊天机器人到智能体", "聊天机器人只『说』，Agent 会『做』：查数据、调接口、规划步骤、交付结果。这是 AI 应用的分水岭。",
                    ["AI Agent 定义", "被动 vs 主动"]),
                _sec("s2-core-c1-s2", "Agent 的组成", "一个 Agent = LLM（大脑）+ 工具（手脚）+ 记忆（经验）+ 规划（策略），四者协作完成复杂任务。",
                    ["Agent 组成", "LLM+工具+记忆"]),
            ]),
            _ch("s2-core-c2", "Agent 的核心能力", "拆解感知（理解输入/环境）、推理（分析拆解）、决策（选工具选步骤）、执行（调用动作）四大能力，理解它们如何串成闭环。", 35, [
                _sec("s2-core-c2-s1", "感知与推理", "感知：把用户意图、环境状态转成模型可处理的信息；推理：拆解任务、生成方案、判断前提是否满足。",
                    ["感知 Perception", "推理 Reasoning"]),
                _sec("s2-core-c2-s2", "决策与执行", "决策：从候选工具/动作中选择最优；执行：真正调用工具并把结果回填上下文。四步构成 Agent 的一次工作循环。",
                    ["决策 Decision", "执行 Action"]),
            ]),
            _ch("s2-core-c3", "Agent 与 LLM 的区别", "LLM 是能力引擎，Agent 是封装了引擎的自动化系统。理解『裸调 API』与『Agent 化』在工程上的差异。", 30, [
                _sec("s2-core-c3-s1", "三问区分 LLM 应用与 Agent", "是否调用外部工具？是否多步规划？是否自主决策？全否=普通 LLM 应用，有=Agent。",
                    ["Agent vs LLM", "判定标准"]),
                _sec("s2-core-c3-s2", "为什么需要 Agent 这一层", "LLM 单次输出无法完成『查库存+算折扣+下单』这类多步任务；Agent 层提供循环、工具、记忆、异常处理，让 LLM 真正可用。",
                    ["Agent 层价值"]),
            ]),
            _ch("s2-core-c4", "Agent 的应用场景", "盘点智能客服、代码助手、数据分析、自动化运营、知识问答等典型场景，明确每个场景 Agent 解决了什么问题。", 30, [
                _sec("s2-core-c4-s1", "高频落地场景", "客服（查单+售后+引导）、办公自动化（取数→分析→成文）、研发助手（查代码→改代码→跑测试）。",
                    ["应用场景", "智能客服", "办公自动化"]),
                _sec("s2-core-c4-s2", "场景适配判断", "判断标准：任务是否需要多步、是否要访问外部系统、是否允许自主执行。不满足就退回普通问答，省成本省风险。",
                    ["场景判断"]),
            ]),
            _ch("s2-core-c5", "动手：搭一个最小 Agent", "不引入框架，用『LLM+一个函数』实现最小的工具调用循环，亲手体会 Agent 的工作流程。", 40, [
                _sec("s2-core-c5-s1", "手工循环实现", "LLM 输出结构化工具调用→执行本地函数→把结果送回 LLM→LLM 给出最终回答。约 30 行代码跑通。",
                    ["最小 Agent", "手写循环"]),
                _sec("s2-core-c5-s2", "理解循环与边界", "这个最小实现缺少终止条件、错误处理、记忆——你会在阶段二到四逐步补齐，这就是 Agent 工程化的起点。",
                    ["工程化起点"]),
            ]),
        ],
        video_bv=BILIBILI_AGENT,
    ),
    _course(
        "s2-agent-arch", "Agent 架构模式",
        "掌握 Agent 的经典架构：ReAct（核心）、Plan and Execute、Reflection、Multi-Agent，理解不同架构解决什么问题、何时选用。",
        "Agent基础", "intermediate", 8,
        [
            _ch("s2-arch-c1", "ReAct：推理与行动交替", "ReAct 是最经典模式：Thought（推理）→ Action（行动）→ Observation（观察）→ 再推理……循环直到完成任务。", 40, [
                _sec("s2-arch-c1-s1", "ReAct 循环拆解", "每一步：模型先想（我要查天气 API）→ 调用工具（Action）→ 看到结果（Observation）→ 根据结果决定下一步。",
                    ["ReAct", "Thought-Action-Observation"],
                    "问『北京明天穿什么』：Agent 查天气→看到 25℃→推断穿短袖→回答，中间完成了一次工具调用。"),
                _sec("s2-arch-c1-s2", "为什么 ReAct 有效", "把推理与行动外显成文字，让模型在『想』和『做』之间来回修正，比一次直接给答案可靠得多。",
                    ["ReAct 原理"]),
            ]),
            _ch("s2-arch-c2", "Plan and Execute：先规划再执行", "先让 LLM 产出完整计划，再逐个执行步骤；适合任务可预见的场景，减少中途反复。", 35, [
                _sec("s2-arch-c2-s1", "两阶段架构", "Planner 先生成步骤清单，Executor 逐个执行；相比 ReAct 的边走边想，计划型更省 Token、更可控。",
                    ["Plan and Execute", "Planner"]),
                _sec("s2-arch-c2-s2", "适用与局限", "适用：流程明确的任务；局限：执行中计划需调整时灵活性差，可结合 ReAct 做局部修正。",
                    ["适用场景", "局限性"]),
            ]),
            _ch("s2-arch-c3", "Reflection：自我反思", "生成答案后让 Agent 自我批评并改进，形成『生成→反思→修正』闭环，提升质量但增加成本。", 35, [
                _sec("s2-arch-c3-s1", "反思机制", "第一遍输出→要求模型以评审者视角找问题→根据批评重新生成。适合质量要求高的场景（代码、长文）。",
                    ["Reflection", "自我反思"]),
                _sec("s2-arch-c3-s2", "反思的成本控制", "每次反思都是一次 LLM 调用。设定反思轮次上限，避免无限自我怀疑。",
                    ["成本控制"]),
            ]),
            _ch("s2-arch-c4", "Multi-Agent 模式概览", "介绍多 Agent 协作的几种模式（监督者/层级/流水线/网络/群聊），理解『什么时候才需要多个 Agent』。", 35, [
                _sec("s2-arch-c4-s1", "多 Agent 的价值", "分工协作：角色冲突（PM vs 开发）、并行加速、独立审查（生成+检查）。",
                    ["多 Agent", "分工协作"]),
                _sec("s2-arch-c4-s2", "『单 Agent 哪里不够』原则", "能用单 Agent 解决就别上多 Agent——多 Agent 意味着更高成本、延迟与调试难度。细节留到阶段四。",
                    ["单 Agent 优先", "多 Agent 代价"]),
            ]),
            _ch("s2-arch-c5", "架构选型实战", "给一个真实任务，练习选择合适架构：客服→ReAct+工具；报表→Plan-Execute；代码→Reflection+测试。", 40, [
                _sec("s2-arch-c5-s1", "按任务特征选架构", "确定性流程选 Plan-Execute；探索性任务选 ReAct；质量敏感加 Reflection；并行子任务才考虑多 Agent。",
                    ["架构选型"]),
                _sec("s2-arch-c5-s2", "组合与混合", "生产系统常混合：外层 Plan-Execute，内层步骤用 ReAct，输出前套 Reflection。架构是手段不是教条。",
                    ["混合架构"]),
            ]),
        ],
        video_bv=BILIBILI_AGENT,
    ),
    _course(
        "s2-tool-calling", "工具调用 Tool Calling",
        "Agent 的核心能力是『让 LLM 使用工具』。深入理解 Function Calling 原理、工具定义、参数解析、执行与结果返回，动手实现天气查询 Agent。",
        "Agent基础", "intermediate", 8,
        [
            _ch("s2-tool-c1", "Function Calling 原理", "LLM 本身不执行代码，它负责『决定调哪个函数、传什么参数』，真正执行由你的程序完成。", 35, [
                _sec("s2-tool-c1-s1", "从对话到函数调用", "把工具描述（名称+参数 schema）塞进请求，模型返回结构化调用请求（function_call），而不是直接执行。",
                    ["Function Calling", "结构化调用"]),
                _sec("s2-tool-c1-s2", "调用闭环", "收到调用请求→程序执行→把结果作为工具消息送回模型→模型基于结果继续。这就是 Agent 的『手』。",
                    ["调用闭环"]),
            ]),
            _ch("s2-tool-c2", "工具定义与描述", "工具的描述质量直接决定模型能否正确选用——描述不清=选错工具=任务失败。学习写好工具声明。", 35, [
                _sec("s2-tool-c2-s1", "工具 schema 结构", "name、description、parameters（JSON Schema 定义各参数类型/必填/枚举）。描述要说明『何时用、参数含义』。",
                    ["工具 schema", "JSON Schema"]),
                _sec("s2-tool-c2-s2", "描述的艺术", "『获取指定城市的实时天气，参数 city 为城市名』比『查询天气』精准得多。写清楚边界：什么情况用它、参数怎么传。",
                    ["工具描述", "边界"],
                    "两个工具『查天气』『查机票』描述相似时，模型常选错——在描述里写清触发条件可大幅改善。"),
            ]),
            _ch("s2-tool-c3", "工具参数解析", "处理模型可能给错的参数：类型转换、必填缺失、非法值，学会容错与校验。", 30, [
                _sec("s2-tool-c3-s1", "参数校验与容错", "模型可能传空、传错类型、传不存在的城市。在工具入口做校验，返回友好错误而不是抛异常。",
                    ["参数校验", "容错"]),
                _sec("s2-tool-c3-s2", "重试与澄清", "参数不完整时，可让 Agent 反问用户补充，或重试一次调用，而非直接失败。",
                    ["重试", "澄清"]),
            ]),
            _ch("s2-tool-c4", "工具执行与结果返回", "执行工具、把结果结构化回填给模型，注意结果格式对后续推理的影响（太长要截断）。", 30, [
                _sec("s2-tool-c4-s1", "结果回传格式", "工具结果作为 tool 消息返回，模型据此继续推理。结果要结构化、可读，别让模型去解析一团乱文本。",
                    ["结果回传", "tool 消息"]),
                _sec("s2-tool-c4-s2", "长结果与截断", "API 返回可能很长（上千行），超出窗口会爆。按需截断、摘要，只回传与当前问题相关的部分。",
                    ["结果截断"]),
            ]),
            _ch("s2-tool-c5", "实战：天气查询 Agent", "端到端实现一个『问天气』Agent：定义天气工具→接入 LLM→跑通完整循环→处理边界情况。", 40, [
                _sec("s2-tool-c5-s1", "完整实现", "FastAPI 或纯脚本：定义 get_weather(city)→配置 tool→循环调用→输出自然语言回答。",
                    ["天气 Agent", "端到端实现"]),
                _sec("s2-tool-c5-s2", "扩展练习", "给 Agent 加第二个工具（查城市坐标），让它学会按需选择；再加一个『找不到城市』的兜底回答。",
                    ["多工具", "兜底"]),
            ]),
        ],
        video_bv=BILIBILI_AGENT,
    ),
    _course(
        "s2-memory", "Agent 记忆系统",
        "让 Agent 记住历史与知识：区分短期记忆（对话历史）与长期记忆（向量数据库），掌握记忆的检索与更新，用 Chroma 落地长期记忆。",
        "Agent基础", "intermediate", 7,
        [
            _ch("s2-mem-c1", "为什么要记忆", "LLM 无状态，每次对话都是『失忆』。记忆系统让 Agent 记住上下文、用户偏好与领域知识，是实用化前提。", 30, [
                _sec("s2-mem-c1-s1", "无状态问题的三种解法", "①把历史拼进上下文（短期）②向量检索相关记忆（长期）③外部数据库存事实（结构化）。",
                    ["记忆动机", "无状态"]),
                _sec("s2-mem-c1-s2", "记忆的分层", "短期=本次对话的完整记录；长期=跨对话沉淀的知识与偏好。两者配合：短期保流畅，长期保积累。",
                    ["短期记忆", "长期记忆"]),
            ]),
            _ch("s2-mem-c2", "短期记忆：对话历史", "如何组织 messages 历史：保留多长、何时截断、如何压缩，避免上下文爆炸。", 35, [
                _sec("s2-mem-c2-s1", "历史管理与滑动窗口", "保留最近 N 轮，超出用摘要压缩或用向量检索替换，保证上下文窗口始终可控。",
                    ["滑动窗口", "历史截断"]),
                _sec("s2-mem-c2-s2", "会话隔离", "多用户/多会话之间隔离历史，用 session_id 区分，别把 A 的对话串给 B。",
                    ["会话隔离", "session_id"]),
            ]),
            _ch("s2-mem-c3", "长期记忆：向量数据库", "引入 Embedding 与向量检索：把知识切成块、向量化入库，提问时检索相关片段注入上下文。", 40, [
                _sec("s2-mem-c3-s1", "向量化与相似度检索", "文本→向量（Embedding）→按余弦相似度检索 top-k。这正是阶段三 RAG 的技术底座，先建立直觉。",
                    ["Embedding", "相似度检索"]),
                _sec("s2-mem-c3-s2", "Chroma 快速上手", "Chroma 是零配置的本地向量库：collection.add 存向量与元数据，query 检索。几十行代码可跑。",
                    ["Chroma", "向量库"]),
            ]),
            _ch("s2-mem-c4", "记忆的检索与更新", "不是所有历史都有用：按相关性检索、按时效加权、写入时去重更新，设计记忆的『写→读→更』闭环。", 35, [
                _sec("s2-mem-c4-s1", "检索策略", "query 向量化→检索 top-k→按得分/时效排序；可加元数据过滤（只看某个主题）。",
                    ["记忆检索", "top-k"]),
                _sec("s2-mem-c4-s2", "写入与更新", "用户纠正了某个信息？更新旧记忆而非重复插入，避免冲突。可用『覆盖+版本』策略。",
                    ["记忆更新"]),
            ]),
            _ch("s2-mem-c5", "综合记忆 Agent", "把短期+长期记忆整合进一个 Agent：多轮对话记住用户偏好，跨会话记得历史结论。", 40, [
                _sec("s2-mem-c5-s1", "记忆整合架构", "启动时：检索长期记忆注入 system；对话中：历史走滑动窗口；结束时：提炼要点写回长期记忆。",
                    ["记忆整合"]),
                _sec("s2-mem-c5-s2", "成本与隐私权衡", "长期记忆存储与检索有成本，且涉及隐私——敏感信息不入库、按用户隔离、可删除。",
                    ["隐私", "成本"]),
            ]),
        ],
        video_bv=BILIBILI_AGENT,
    ),
]

# =====================================================================
# 阶段三：Agent 开发实战（核心重点）
# =====================================================================
STAGE3_COURSES = [
    _course(
        "s3-rag", "RAG 检索增强生成（手写 pipeline）",
        "市场需求最大的 AI 方向。手写一个完整 RAG：文档加载→分块→向量化→入库→检索→回答→引用溯源，并进阶到查询改写、混合检索、Rerank、HyDE。",
        "开发实战", "intermediate", 12,
        [
            _ch("s3-rag-c1", "RAG 解决的问题", "大模型知识过时、容易幻觉、不了解私有数据——RAG 用『检索+生成』把真实资料喂给模型回答。", 35, [
                _sec("s3-rag-c1-s1", "三大痛点", "知识截止（不知道新事件）、幻觉（编造）、私有数据（不了解你的文档）。RAG 让回答基于可追溯的真实资料。",
                    ["RAG 动机", "幻觉", "私有数据"]),
                _sec("s3-rag-c1-s2", "RAG 完整流程总览", "加载文档→切分文本→生成向量→存入向量库→检索相关片段→交给模型回答。本章先记住这条主线。",
                    ["RAG 流程"]),
            ]),
            _ch("s3-rag-c2", "文档加载与文本分块", "解析 PDF/Markdown/Word 等格式，用合适的 chunk_size 与 overlap 切分，保住语义完整性。", 45, [
                _sec("s3-rag-c2-s1", "多格式文档加载", "PDF（PyPDF）、Markdown、Word 各自解析方案；分块前先清洗：去页眉页脚、合并表格。",
                    ["文档加载", "PDF/MD/Word"]),
                _sec("s3-rag-c2-s2", "分块策略", "chunk_size（每块字数）与 overlap（相邻重叠）权衡：太小丢上下文，太大稀释相关性；按段落/标题切分更保语义。",
                    ["chunk_size", "overlap", "语义完整性"]),
            ]),
            _ch("s3-rag-c3", "Embedding 与向量数据库", "理解『文本→向量→语义相似』，用 Chroma 建库、持久化、做相似度检索。", 45, [
                _sec("s3-rag-c3-s1", "Embedding 原理", "把文本映射为高维向量，语义相近的文本向量距离近。这是『语义搜索』区别于『关键词搜索』的关键。",
                    ["Embedding", "语义相似度"]),
                _sec("s3-rag-c3-s2", "Chroma 建库与检索", "collection.add(documents, metadatas) 入库；collection.query(query_texts) 检索。设置 persist 目录实现持久化。",
                    ["Chroma", "持久化", "相似度检索"]),
            ]),
            _ch("s3-rag-c4", "检索 + 回答 + 引用溯源", "把检索到的片段与问题一起交给模型，并让回答标注来源，实现可验证的问答。", 40, [
                _sec("s3-rag-c4-s1", "拼装上下文回答", "把 top-k 片段拼进 system/user，约束『仅基于资料回答，资料不足就说不清楚』，能显著减少幻觉。",
                    ["检索问答", "上下文拼装"]),
                _sec("s3-rag-c4-s2", "引用溯源", "片段带元数据（来源文档、页码），要求模型在回答中标注出处；前端可展示引用来源，提升可信度。",
                    ["引用溯源", "元数据"]),
            ]),
            _ch("s3-rag-c5", "检索质量进阶优化", "查询改写、混合检索、Rerank 重排、HyDE——一套让『检得准』的组合拳。", 45, [
                _sec("s3-rag-c5-s1", "查询改写与混合检索", "先让 LLM 把模糊问题改写成更优检索词；关键词+向量混合召回，互补召回不足。",
                    ["查询改写", "混合检索"]),
                _sec("s3-rag-c5-s2", "Rerank 与 HyDE", "Rerank：对召回结果用交叉编码器精排；HyDE：先让模型生成假设答案再检索，提升召回相关性。",
                    ["Rerank", "HyDE"]),
            ]),
            _ch("s3-rag-c6", "实践：企业知识库问答系统", "用 FastAPI+Chroma+本地 Embedding 手写完整 RAG 服务：上传文档→分块向量化→问答→引用溯源。", 60, [
                _sec("s3-rag-c6-s1", "系统架构", "FastAPI 三个接口：上传文档（解析+入库）、问答（检索+生成+引用）、状态查询。Docker 化部署。",
                    ["企业知识库", "FastAPI+Chroma"]),
                _sec("s3-rag-c6-s2", "面试展示要点", "能讲清每个环节的选择：为什么这么分块、为什么用本地 Embedding、引用如何传递——这是求职作品级项目。",
                    ["项目作品", "技术选型"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s3-mcp", "MCP 模型上下文协议",
        "MCP 让模型以统一协议访问外部工具、文件、数据库和服务，避免每个工具写一套对接代码。理解 Client↔Server 架构并会使用现成 Server。",
        "开发实战", "intermediate", 5,
        [
            _ch("s3-mcp-c1", "为什么需要 MCP", "传统集成每个工具都要专门写对接（不同鉴权、不同协议）。MCP 定义统一标准：一次对接，处处复用。", 35, [
                _sec("s3-mcp-c1-s1", "集成的痛点", "工具越来越多，每个都写一遍『鉴权+参数+错误处理』，代码重复且难维护。",
                    ["集成痛点"]),
                _sec("s3-mcp-c1-s2", "MCP 的承诺", "把工具能力封装成标准化的 MCP Server，任何支持 MCP 的客户端（Agent/IDE）都能即插即用。",
                    ["MCP 价值", "标准化"]),
            ]),
            _ch("s3-mcp-c2", "核心架构：Client ↔ Server ↔ 工具", "理解 MCP 三角色：Client（Agent 侧）发起请求，Server 暴露工具，底层接外部资源（文件/DB/API）。", 40, [
                _sec("s3-mcp-c2-s1", "协议分层", "Client↔Server 走 JSON-RPC，Server 把文件系统、数据库、GitHub 等包装成可调用的工具暴露给 Agent。",
                    ["MCP 架构", "JSON-RPC"]),
                _sec("s3-mcp-c2-s2", "工具、资源与提示词", "MCP 定义三类能力：tools（可执行操作）、resources（可读取数据）、prompts（可复用模板）。",
                    ["tools/resources/prompts"]),
            ]),
            _ch("s3-mcp-c3", "使用现成的 MCP Server", "快速体验：接入文件系统 Server、数据库 Server、GitHub Server，让 Agent 直接操作真实资源。", 40, [
                _sec("s3-mcp-c3-s1", "常用现成 Server", "文件系统（读写本地文件）、数据库（执行 SQL）、GitHub（查仓库/提 PR）、搜索、浏览器等社区 Server 众多。",
                    ["现成 MCP Server", "文件系统/数据库/GitHub"]),
                _sec("s3-mcp-c3-s2", "配置与调试", "在配置里声明用哪些 Server、暴露哪些工具；注意权限边界——给 Agent 的文件写权限有风险。",
                    ["Server 配置", "权限"]),
            ]),
            _ch("s3-mcp-c4", "MCP 在 Agent 生态中的位置", "理清 MCP 与 Function Calling、以及 MCP 与 A2A 的角色区分，别把协议与产品搞混。", 30, [
                _sec("s3-mcp-c4-s1", "MCP vs Function Calling", "Function Calling 是模型的能力（决定调哪个函数），MCP 是工具的分发标准（工具怎么被对接）。两者互补：MCP 帮你把工具标准化供 Function Calling 调用。",
                    ["MCP vs Function Calling"]),
                _sec("s3-mcp-c4-s2", "MCP 与 A2A 的角色", "MCP 管『Agent↔工具』，A2A（Agent-to-Agent）管『Agent↔Agent』。一个连工具，一个连同行。",
                    ["MCP vs A2A"]),
            ]),
            _ch("s3-mcp-c5", "动手：接一个文件系统 Server", "把文件系统 MCP Server 接入一个最小 Agent，让它完成『读文件→总结→写新文件』的闭环任务。", 45, [
                _sec("s3-mcp-c5-s1", "最小集成", "启动文件系统 Server→Agent 配置声明→提问让 Agent 读取并总结一个本地文件。",
                    ["MCP 集成"]),
                _sec("s3-mcp-c5-s2", "安全的边界", "只暴露需要操作的目录；Agent 的执行结果人工可审；理解『工具越强，约束越要严』。",
                    ["MCP 安全"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s3-skills", "Agent Skills 能力技能化",
        "把 Agent 能力拆成可复用、可组合的技能模块，而不是把所有能力塞进一个大 Prompt。理解 Skill 的定义、描述边界与协作方式。",
        "开发实战", "intermediate", 5,
        [
            _ch("s3-skills-c1", "为什么要有 Skill", "大 Prompt 塞满能力：又长又乱、难维护、还容易让模型选错。Skill 把能力按『输入→处理→输出』封装成独立模块。", 30, [
                _sec("s3-skills-c1-s1", "大 Prompt 的弊端", "把所有能力写进一个 Prompt：上下文占用大、互相干扰、改一处全受影响。",
                    ["大 Prompt 弊端"]),
                _sec("s3-skills-c1-s2", "Skill 的思想", "把『写周报』『做摘要』『翻译』各自封装成技能，Agent 按需调用，能力可组合、可复用。",
                    ["Skill 定义", "封装"]),
            ]),
            _ch("s3-skills-c2", "Skill 的描述与边界", "Skill 的描述质量直接决定 Agent 能否正确选用——描述不清=选错工具=任务失败。", 35, [
                _sec("s3-skills-c2-s1", "怎么描述一个 Skill", "明确：输入格式、处理逻辑、输出格式、适用场景、边界（不做什么）。描述是 Agent 选它的依据。",
                    ["Skill 描述", "输入输出"]),
                _sec("s3-skills-c2-s2", "边界的价值", "写清楚『此技能不处理 X』，避免 Agent 拿它硬套不合适的任务；边界越清晰，选用越准。",
                    ["Skill 边界"]),
            ]),
            _ch("s3-skills-c3", "多 Skill 协作", "复杂任务由多个 Skill 串联/并联完成：前一个 Skill 的输出是下一个的输入，Agent 负责编排。", 35, [
                _sec("s3-skills-c3-s1", "组合模式", "串联（摘要→翻译→润色）、条件选择（按类型选 Skill）、并行（同时做多项）。",
                    ["多 Skill 协作", "编排"]),
                _sec("s3-skills-c3-s2", "编排的责任", "Agent 判断何时用哪个 Skill、如何传参、如何汇总——Skill 是零件，编排是装配。",
                    ["Skill 编排"]),
            ]),
            _ch("s3-skills-c4", "Skill 与工具、RAG 的关系", "理清三个概念：Skill 是能力封装、Tool 是外部动作、RAG 是知识注入，三者如何配合。", 30, [
                _sec("s3-skills-c4-s1", "概念辨析", "Skill=『会做一件事』的封装；Tool=调用外部系统的接口；RAG=给 Agent 补知识。Skill 内部可以调用 Tool，也可以走 RAG。",
                    ["Skill vs Tool vs RAG"]),
                _sec("s3-skills-c4-s2", "组合示例", "『企业问答』Skill = 内部做 RAG 检索 + 可能调用企业系统 Tool；对外是一个统一能力。",
                    ["组合示例"]),
            ]),
            _ch("s3-skills-c5", "实践：沉淀你自己的 Skill", "把一个重复任务（如周报生成）封装成 Skill 模板，验证描述质量对 Agent 表现的影响。", 40, [
                _sec("s3-skills-c5-s1", "封装流程", "定义输入→写处理提示词→定输出格式→写描述与边界→测试 Agent 正确调用。",
                    ["Skill 落地"]),
                _sec("s3-skills-c5-s2", "质量验证", "对比『描述清晰 vs 描述模糊』两种 Skill，观察 Agent 选用的正确率——你会深刻体会描述的重要性。",
                    ["描述质量验证"]),
            ]),
        ],
        video_bv=BILIBILI_LANGCHAIN,
    ),
    _course(
        "s3-langchain", "LangChain 框架",
        "把前面手写的 RAG 与 Agent 用 LangChain 重新组织，从『理解原理』进入『框架化开发』。分 RAG 线与 Agent 线两条主线掌握。",
        "开发实战", "advanced", 12,
        [
            _ch("s3-lc-c1", "LangChain 设计思想", "LangChain 用『组件+链』抽象 LLM 应用：数据、模型、记忆、工具可插拔，链把流程串起来。", 35, [
                _sec("s3-lc-c1-s1", "组件化思维", "Model、Retriever、Tool、Memory 都是可替换组件，配置化组合——这正是框架比手写强的核心。",
                    ["LangChain 组件"]),
                _sec("s3-lc-c1-s2", "手写 vs 框架", "手写让你懂原理，框架让你提效率。理解框架帮你省了什么：样板代码、协议处理、组合能力。",
                    ["手写 vs 框架"]),
            ]),
            _ch("s3-lc-c2", "LangChain RAG 线：Loaders 与 Splitters", "用标准 Loader 加载文档，用 RecursiveCharacterTextSplitter 做智能分块，为建库做准备。", 40, [
                _sec("s3-lc-c2-s1", "Document Loaders", "TextLoader、PyPDFLoader、DirectoryLoader 批量加载，统一成 Document 对象（含 metadata）。",
                    ["Document Loaders", "metadata"]),
                _sec("s3-lc-c2-s2", "RecursiveCharacterTextSplitter", "递归按分隔符切分，兼顾结构与长度；掌握 chunk_size/overlap 参数，这是 LangChain 最常用的 Splitter。",
                    ["RecursiveCharacterTextSplitter", "chunk_size"]),
            ]),
            _ch("s3-lc-c3", "LangChain RAG 线：Embeddings 与 VectorStores", "用 OllamaEmbeddings/OpenAIEmbeddings 向量化，把块存入 Chroma/FAISS 并持久化。", 40, [
                _sec("s3-lc-c3-s1", "Embeddings 接入", "一行切换本地（OllamaEmbeddings）或云端（OpenAIEmbeddings）Embedding，与前面手写呼应。",
                    ["Embeddings", "OllamaEmbeddings"]),
                _sec("s3-lc-c3-s2", "VectorStores 与检索器", "Chroma.from_documents 建库、持久化目录；store.as_retriever() 得到可用的检索器。",
                    ["Chroma/FAISS", "as_retriever"]),
            ]),
            _ch("s3-lc-c4", "LangChain RAG 线：Retrieval Chain", "用 create_stuff_documents_chain + create_retrieval_chain 组装问答链，并让 metadata 一路传递实现引用溯源。", 40, [
                _sec("s3-lc-c4-s1", "两条链的配合", "retrieval_chain 负责『检索→喂给文档链』，stuff_documents_chain 负责『拼装+生成』；understanding 关键在检索结果的引用保留。",
                    ["create_retrieval_chain", "stuff 文档链"]),
                _sec("s3-lc-c4-s2", "引用溯源贯穿", "metadata 从加载→切分→入库→检索→回答一路保留，输出带来源。与手写版的效果对齐。",
                    ["引用溯源", "metadata 传递"]),
            ]),
            _ch("s3-lc-c5", "LangChain Agent 线：Tool 与 AgentExecutor", "用 @tool 装饰器定义工具，用 AgentExecutor 跑执行循环，调试中间步骤。", 45, [
                _sec("s3-lc-c5-s1", "@tool 定义工具", "函数+docstring+类型注解，自动生成工具 schema；docstring 就是给模型的描述。",
                    ["@tool", "工具 schema"]),
                _sec("s3-lc-c5-s2", "AgentExecutor", "执行循环、最大迭代次数、日志与中间步骤调试；理解它与手写循环的对应关系。",
                    ["AgentExecutor", "迭代控制"]),
            ]),
            _ch("s3-lc-c6", "LangChain Agent 线：Memory 与 RAG 工具", "用 RunnableWithMessageHistory 管理多轮记忆，把 Retriever 包装成 Tool 让 Agent 用 RAG。", 40, [
                _sec("s3-lc-c6-s1", "记忆组件", "RunnableWithMessageHistory 绑定 session，实现多轮对话记忆（新版 API）。",
                    ["RunnableWithMessageHistory", "多轮记忆"]),
                _sec("s3-lc-c6-s2", "Retriever 即 Tool", "retriever 包装成检索工具注册给 Agent——Agent 就能自主决定何时查知识库，这是知识问答 Agent 的标配。",
                    ["Retriever as Tool"]),
            ]),
            _ch("s3-lc-c7", "LangChain 综合：知识问答 Agent", "把 RAG 线+Agent 线合起来：一个能自主检索、可多轮对话、带引用的问答 Agent。", 50, [
                _sec("s3-lc-c7-s1", "整合架构", "Agent 持有检索工具与业务工具，记忆走 RunnableWithMessageHistory，输出带引用。",
                    ["LangChain 综合"]),
                _sec("s3-lc-c7-s2", "局限与下一步", "AgentExecutor 是黑盒，循环控制不细——这正是阶段三下一课 LangGraph 要解决的。",
                    ["AgentExecutor 局限"]),
            ]),
        ],
        video_bv=BILIBILI_LANGCHAIN,
    ),
    _course(
        "s3-langgraph", "LangGraph 框架",
        "用 LangGraph 把 RAG 和 Agent 从黑盒流程拆成可控状态图：State/Node/Edge、条件路由、循环、自纠错、持久化、人工介入。",
        "开发实战", "advanced", 12,
        [
            _ch("s3-lg-c1", "核心三件套：State / Node / Edge", "LangGraph 把 Agent 建模成一张图：State 是共享数据，Node 是处理单元，Edge 决定流转。", 40, [
                _sec("s3-lg-c1-s1", "State 与 add_messages", "State 是全局状态对象；add_messages 是常用 reducer，把多轮消息自动追加合并。",
                    ["StateGraph", "add_messages"]),
                _sec("s3-lg-c1-s2", "Node 与 Edge", "Node 是一个函数（输入 State 返回新 State）；Edge 连接节点，START/END 是图的出入口。",
                    ["Node/Edge", "START/END"]),
            ]),
            _ch("s3-lg-c2", "条件路由与手搓 ReAct", "用 add_conditional_edges 实现『要不要调工具』的判断，搭出 agent 节点+tools 节点+ToolNode+条件边的 ReAct 循环。", 50, [
                _sec("s3-lg-c2-s1", "条件路由", "根据 Agent 输出是否含工具调用，路由到 tools 节点还是直接结束；这是循环控制的关键。",
                    ["add_conditional_edges", "条件路由"]),
                _sec("s3-lg-c2-s2", "手搓 ReAct", "agent 节点（LLM 决策）→ 条件边 → ToolNode（执行工具）→ 回 agent 节点；比 AgentExecutor 更透明可控。",
                    ["手搓 ReAct", "ToolNode"]),
            ]),
            _ch("s3-lg-c3", "Checkpointer：多轮状态记忆", "用 MemorySaver + thread_id 让 Agent 跨轮记住状态，实现持久化对话。", 40, [
                _sec("s3-lg-c3-s1", "Checkpointer 原理", "检查点机制在每次节点执行后保存 State，thread_id 区分不同会话。",
                    ["Checkpointer", "MemorySaver"]),
                _sec("s3-lg-c3-s2", "thread_id 会话隔离", "不同 thread_id 互不干扰；恢复历史状态让多轮任务续跑。",
                    ["thread_id"]),
            ]),
            _ch("s3-lg-c4", "Human-in-the-Loop：人工审批", "用 interrupt_before 在关键节点暂停，等人工确认后再继续——敏感操作必须人工把关。", 40, [
                _sec("s3-lg-c4-s1", "中断机制", "interrupt_before 在指定节点前暂停执行，把待审批内容交给用户，批准后从断点续跑。",
                    ["interrupt_before", "人工审批"]),
                _sec("s3-lg-c4-s2", "审批场景", "支付、删除、发消息等高风险动作前加审批；未批准则回滚或终止。",
                    ["审批场景"]),
            ]),
            _ch("s3-lg-c5", "LangGraph 综合：客服 Agent「小 G」", "把 RAG 工具+业务工具+敏感操作审批+多轮记忆整合成一个完整客服 Agent。", 55, [
                _sec("s3-lg-c5-s1", "系统设计", "FastAPI+LangGraph+Chroma：检索工具、业务工具、审批边、Checkpointer 记忆，状态图化编排。",
                    ["客服 Agent", "LangGraph 综合"]),
                _sec("s3-lg-c5-s2", "与阶段五衔接", "图的可视化与日志便于阶段五的监控与评估；Docker 部署留到项目实战。",
                    ["工程化衔接"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s3-agentic-rag", "Agentic RAG 进阶",
        "传统 RAG 是直线流程，容易『垃圾进垃圾出』。用图重写为 retrieve→grade→rewrite→generate→check 的自纠错 RAG，加入评分、重写、幻觉检测与循环刹车。",
        "开发实战", "advanced", 9,
        [
            _ch("s3-agc1", "传统 RAG 的局限", "直线检索：查不准→答得错，且没有质量反馈。理解『垃圾进垃圾出』问题。", 30, [
                _sec("s3-agc1-s1", "三个失效场景", "检索无结果、检索到不相关、文档本身过时——直线流程都会直接输出错误答案。",
                    ["RAG 失效", "检索质量"]),
                _sec("s3-agc1-s2", "从直线到图", "在检索后加『评分』，不合格就『改写重查』，回答后加『检查』——让流程有反馈闭环。",
                    ["Agentic RAG", "闭环"]),
            ]),
            _ch("s3-agc2", "核心循环：retrieve → grade → rewrite → generate → check", "搭建带评分与重写节点的 RAG 图，检索不准时自动改写问题再查。", 45, [
                _sec("s3-agc2-s1", "五节点流水线", "retrieve 检索→grade 评分相关性→rewrite 改写查询→generate 生成→check 质量检查，不合格回炉。",
                    ["retrieve/grade/rewrite", "generate/check"]),
                _sec("s3-agc2-s2", "用 LangGraph 实现", "每个环节是一个 Node，条件边决定『合格继续 / 不合格改写重查』。与阶段三 LangGraph 课直接衔接。",
                    ["LangGraph 实现"]),
            ]),
            _ch("s3-agc3", "文档评分与查询重写", "用 LLM 判断检索结果是否相关；不相关时改写问题再检索，避免无谓重试。", 40, [
                _sec("s3-agc3-s1", "文档评分", "让模型对每个检索片段打分/判断相关性，只把合格片段送入生成，或触发重查。",
                    ["文档评分", "相关性判断"]),
                _sec("s3-agc3-s2", "查询重写", "原始问题检索效果差时，让 LLM 改写为更精准的查询词；可限定改写轮数。",
                    ["查询重写"]),
            ]),
            _ch("s3-agc4", "自纠错：幻觉检测与回答检查", "生成后做质量检查：答案是否基于资料、是否矛盾；不达标则重生成或降级回答。", 40, [
                _sec("s3-agc4-s1", "幻觉检测", "检查回答中的关键论断能否在检索资料中找到依据；找不到的标记为存疑。",
                    ["幻觉检测"]),
                _sec("s3-agc4-s2", "回答质量检查", "完整性、一致性、是否答非所问；不合格触发重生成，最多 N 轮。",
                    ["回答检查", "重生成"]),
            ]),
            _ch("s3-agc5", "循环刹车与成本控制", "Agentic RAG 的循环必须设终止条件：retry_count 上限，防止无限重试烧 Token。", 35, [
                _sec("s3-agc5-s1", "retry_count 刹车", "改写/重生成都设最大次数，超限后走兜底：直接回答『未找到相关资料』。",
                    ["retry_count", "循环刹车"]),
                _sec("s3-agc5-s2", "成本核算", "每次循环=多次 LLM 调用。评估在质量提升与成本之间取舍，必要时只在低置信度场景开自纠错。",
                    ["成本控制"]),
            ]),
            _ch("s3-agc6", "实践：自纠错 RAG 服务", "把 Agentic RAG 封装成 FastAPI 服务，支持检索可视化与质量报告，作为知识库项目的进阶版。", 50, [
                _sec("s3-agc6-s1", "服务化", "接口：问答（含检索轨迹）、单独检索、质量统计；LangSmith 可接入后续观察每一步。",
                    ["Agentic RAG 服务"]),
                _sec("s3-agc6-s2", "与项目实战衔接", "这是阶段六『RAG 知识库问答系统』的核心升级，先把自纠错能力打磨扎实。",
                    ["项目衔接"]),
            ]),
        ],
        video_bv="",
    ),
]

# =====================================================================
# 阶段四：多 Agent 系统
# =====================================================================
STAGE4_COURSES = [
    _course(
        "s4-multi-agent", "多 Agent 架构与协作",
        "掌握多 Agent 协作模式（监督者/层级/流水线/网状/群聊）、通信机制、任务分配与角色设计，理解『什么时候才需要多 Agent』及其代价。",
        "多Agent", "advanced", 8,
        [
            _ch("s4-ma-c1", "五种协作模式", "Supervisor（监督者调度）、Hierarchical（层级分解）、Pipeline（流水线）、Network（网状）、Group Chat（群聊）。", 40, [
                _sec("s4-ma-c1-s1", "监督者与层级", "Supervisor：一个主管把任务分给多个执行 Agent；Hierarchical：多层树状逐级分解。",
                    ["Supervisor", "Hierarchical"]),
                _sec("s4-ma-c1-s2", "流水线/网状/群聊", "Pipeline 前输出后输入；Network 自由通信平等协作；Group Chat 所有 Agent 一起讨论决策。",
                    ["Pipeline", "Network", "Group Chat"]),
            ]),
            _ch("s4-ma-c2", "通信机制与任务分配", "消息传递、结构化 JSON、共享黑板、结论式交接；静态/动态分解与 Map-Reduce。", 40, [
                _sec("s4-ma-c2-s1", "通信方式", "结构化 JSON 最稳（字段明确可校验）；共享黑板适合并行写入；结论式交接减少信息量。",
                    ["通信机制", "JSON 消息", "共享黑板"]),
                _sec("s4-ma-c2-s2", "任务分配", "静态分解（预定义分工）vs 动态分解（运行时拆）；可并行的子任务用 Map-Reduce。",
                    ["任务分配", "Map-Reduce"]),
            ]),
            _ch("s4-ma-c3", "角色设计与何时需要多 Agent", "角色怎么划分不重叠、不遗漏；用『单 Agent 哪里不够』原则判断要不要上多 Agent。", 35, [
                _sec("s4-ma-c3-s1", "角色设计", "按『职责不重叠、接口清晰』划分；典型如 PM/架构师/程序员/测试四角色分工。",
                    ["Agent 角色", "职责划分"]),
                _sec("s4-ma-c3-s2", "触发信号", "工具太多难选→按工具分组；角色冲突→分工；可并行→并行；需独立审查→生成+检查。",
                    ["多 Agent 时机"]),
            ]),
            _ch("s4-ma-c4", "多 Agent 的代价 ⚠️", "成本上升、延迟变高、调试困难、上下文爆炸、级联失败——上多 Agent 前先算清这笔账。", 35, [
                _sec("s4-ma-c4-s1", "五大代价", "多次 LLM 调用成本、串行延迟、错误级联放大、Agent 间传递过多信息、责任不清晰。",
                    ["多 Agent 代价", "级联失败"]),
                _sec("s4-ma-c4-s2", "务实原则", "能用单 Agent 解决的不要上多 Agent；先问『单 Agent 哪里不够』，再决定架构。",
                    ["务实原则"]),
            ]),
            _ch("s4-ma-c5", "实践：Supervisor 最小 Demo", "用 LangGraph 的 Supervisor 模式搭一个『主管+两个执行 Agent』的 Demo，体会编排与通信。", 50, [
                _sec("s4-ma-c5-s1", "Supervisor Demo", "主管 Agent 根据问题把任务派给『检索 Agent』或『计算 Agent』，汇总结果给用户。",
                    ["Supervisor Demo", "LangGraph"]),
                _sec("s4-ma-c5-s2", "讲清原理即可", "本阶段不需要完整项目，能讲清架构、职责与通信即可；深入实战留给阶段六。",
                    ["学习定位"]),
            ]),
        ],
        video_bv=BILIBILI_AGENT,
    ),
    _course(
        "s4-metagpt-autogen", "MetaGPT 与 AutoGen 框架",
        "研究多 Agent 框架代表作：MetaGPT 模拟软件公司流程，AutoGen 支持对话式群聊协作；理解设计思路与选型。",
        "多Agent", "advanced", 7,
        [
            _ch("s4-fw-c1", "MetaGPT：模拟软件公司", "MetaGPT 用角色扮演多 Agent 协作完成软件开发：产品经理→架构师→程序员→测试，输出标准化文档。", 45, [
                _sec("s4-fw-c1-s1", "核心思想", "让每个角色 Agent 像公司里的岗位一样工作，用结构化文档（PRD/接口文档/代码）作为交接物。",
                    ["MetaGPT", "软件公司模拟"]),
                _sec("s4-fw-c1-s2", "架构与角色", "角色定义、SOP 工作流、结构化输出；研究源码理解它如何约束每个 Agent 的产出。",
                    ["MetaGPT 架构"]),
            ]),
            _ch("s4-fw-c2", "AutoGen：对话式多 Agent", "微软开源框架，Agent 之间通过对话协作，支持群聊模式与自定义 Agent，设计更灵活。", 45, [
                _sec("s4-fw-c2-s1", "对话式协作", "Agent 之间直接对话协商，而非固定流程；群聊模式让多个 Agent 在一个会话中讨论。",
                    ["AutoGen", "对话式协作", "群聊"]),
                _sec("s4-fw-c2-s2", "自定义与扩展", "定义自己的 Agent、角色、终止条件；适合需要灵活协商的场景。",
                    ["自定义 Agent"]),
            ]),
            _ch("s4-fw-c3", "框架对比与选型", "LangGraph（图编排）/ MetaGPT（软件流程）/ AutoGen（对话协商）/ CrewAI（角色团队）——按任务形态选。", 40, [
                _sec("s4-fw-c3-s1", "选型对照", "流程明确→LangGraph；软件开发→MetaGPT；自由协商→AutoGen；固定角色团队→CrewAI。",
                    ["框架选型"]),
                _sec("s4-fw-c3-s2", "不要过度选型", "多数业务单 Agent+工具就够；多 Agent 框架是特定场景的武器，别为用而用。",
                    ["务实选型"]),
            ]),
            _ch("s4-fw-c4", "源码与设计思路学习", "读 MetaGPT 的 SOP 约束与 AutoGen 的对话循环，学习成熟框架的工程化设计。", 40, [
                _sec("s4-fw-c4-s1", "MetaGPT 源码要点", "看它如何用结构化输出约束角色、如何定义角色间交接物、如何控制迭代。",
                    ["源码学习"]),
                _sec("s4-fw-c4-s2", "AutoGen 源码要点", "看对话循环如何终止、消息如何路由、群聊如何仲裁。",
                    ["AutoGen 设计"]),
            ]),
            _ch("s4-fw-c5", "Demo：一个多 Agent 小任务", "用任一框架实现『写需求→生成方案→评审』三角色小任务，跑通并观察协作过程。", 50, [
                _sec("s4-fw-c5-s1", "搭建 Demo", "定义角色 Agent 与交接逻辑，跑一个简单任务并打印每个 Agent 的产出。",
                    ["多 Agent Demo"]),
                _sec("s4-fw-c5-s2", "成本观察", "记录一次任务的 Token 消耗与耗时——直观感受多 Agent 的代价。",
                    ["成本观察"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s4-orchestration", "Agent 编排与工程化陷阱",
        "设计 Agent 工作流：条件分支、循环迭代、错误处理与重试；重视死循环、责任扩散、上下文爆炸、级联失败四大工程化陷阱。",
        "多Agent", "advanced", 7,
        [
            _ch("s4-or-c1", "工作流设计", "把任务拆成可编排的步骤图：明确入口、分支、循环与出口，Agent 编排与业务流程对齐。", 40, [
                _sec("s4-or-c1-s1", "从需求到流程", "梳理任务状态机：哪些步骤可并行、哪些有依赖、哪些需要人工介入，画出流程。",
                    ["工作流设计", "状态机"]),
                _sec("s4-or-c1-s2", "编排载体", "LangGraph 的图、或简单状态循环；关键是可读、可改、可观测。",
                    ["编排实现"]),
            ]),
            _ch("s4-or-c2", "条件分支与循环迭代", "在流程中加入 if/else 与循环：重试、回溯、多轮修正，避免流程死板。", 40, [
                _sec("s4-or-c2-s1", "分支", "按结果分流：检索有无结果、校验是否通过、审批是否批准。",
                    ["条件分支"]),
                _sec("s4-or-c2-s2", "循环与迭代", "重试失败步骤、质量不合格回炉、多轮修正；每个循环都要有终止条件。",
                    ["循环迭代"]),
            ]),
            _ch("s4-or-c3", "错误处理与重试", "LLM 调用会失败、工具会异常——设计优雅降级：重试、退避、兜底、人工接管。", 35, [
                _sec("s4-or-c3-s1", "错误分类处理", "瞬时错误（超时/限流）重试；逻辑错误（参数非法）修正；致命错误（鉴权失败）转人工。",
                    ["错误处理", "降级"]),
                _sec("s4-or-c3-s2", "兜底策略", "多次失败后给用户明确的兜底回答或转人工，别让用户面对白屏或无限转圈。",
                    ["兜底"]),
            ]),
            _ch("s4-or-c4", "四大工程化陷阱", "死循环（反复调用同一工具）、责任扩散（Agent 多了没人负责）、上下文爆炸（传递过多信息）、级联失败（一环出错全链崩）。", 40, [
                _sec("s4-or-c4-s1", "识别与防范", "终止条件+调用去重防死循环；明确 owner 防责任扩散；信息精简+摘要防上下文爆炸；错误隔离+熔断防级联失败。",
                    ["工程化陷阱", "死循环", "级联失败"]),
                _sec("s4-or-c4-s2", "必备的工程护栏", "日志记录每一步、设置预算上限、评估每轮质量、失败熔断——这是生产级 Agent 的底线。",
                    ["护栏", "熔断"]),
            ]),
            _ch("s4-or-c5", "实践：带护栏的工作流", "给上一课 Supervisor Demo 加终止条件、日志、错误兜底与预算上限，对比加固前后的行为。", 50, [
                _sec("s4-or-c5-s1", "加固 Demo", "给 Agent 加 max_steps、工具调用去重、失败重试与兜底回答，观察异常场景下的表现。",
                    ["工程加固"]),
                _sec("s4-or-c5-s2", "沉淀清单", "把护栏项整理成 checklist：终止条件/日志/评估/成本控制——阶段五会系统化展开。",
                    ["工程清单"]),
            ]),
        ],
        video_bv="",
    ),
]

# =====================================================================
# 阶段五：Agent 优化和部署
# =====================================================================
STAGE5_COURSES = [
    _course(
        "s5-performance", "性能优化与成本控制",
        "让 Agent 更快、更省：Prompt 优化减少 Token、缓存避免重复调用、并行执行提吞吐、流式输出降首字延迟、成本度量与预算。",
        "优化部署", "intermediate", 7,
        [
            _ch("s5-perf-c1", "Prompt 优化省 Token", "精简系统提示词、去冗余示例、压缩历史——最直接的成本手段，也是质量与成本的平衡。", 35, [
                _sec("s5-perf-c1-s1", "Token 审计", "一次请求=系统+历史+工具+输出，逐项估算；发现大头：历史累积、冗余描述、超长工具 schema。",
                    ["Token 审计", "成本构成"]),
                _sec("s5-perf-c1-s2", "精简方法", "系统提示词只留必要约束；示例少而精；历史滑动窗口+摘要；工具 schema 精简描述。",
                    ["Prompt 精简"]),
            ]),
            _ch("s5-perf-c2", "缓存策略", "相同或相似问题命中缓存直接返回，省时省钱：精确缓存、语义缓存、中间结果缓存。", 35, [
                _sec("s5-perf-c2-s1", "精确与语义缓存", "完全相同请求走 Redis 精确缓存；相似语义走向量相似命中（Embedding 缓存）。",
                    ["缓存策略", "语义缓存"]),
                _sec("s5-perf-c2-s2", "缓存什么", "检索结果（同库少重查）、高重复问答、工具调用结果——注意缓存时效与隐私。",
                    ["缓存内容"]),
            ]),
            _ch("s5-perf-c3", "并行执行与吞吐", "独立子任务并发调用 LLM/工具，用 asyncio 或线程池；控制并发上限防止限流。", 35, [
                _sec("s5-perf-c3-s1", "并行化改造", "把『逐条处理』改成『并发处理』，配合信号量限制并发，吞吐翻倍且不触限流。",
                    ["并行执行", "asyncio"]),
                _sec("s5-perf-c3-s2", "超时与退避", "给每个调用设超时，失败按指数退避重试，避免慢调用拖垮整体。",
                    ["超时", "退避"]),
            ]),
            _ch("s5-perf-c4", "流式输出与首字延迟", "SSE 流式让用户先看到开头再等完整结果，感知上快很多；理解首 Token 延迟与总耗时的区别。", 30, [
                _sec("s5-perf-c4-s1", "流式接入", "Agent 的中间步骤也能流式（先报告思考再逐步输出），前端逐字渲染。",
                    ["流式输出", "SSE"]),
                _sec("s5-perf-c4-s2", "延迟指标", "TTFT（首字延迟）决定体感，完整输出决定任务；不同场景优化目标不同。",
                    ["TTFT", "延迟指标"]),
            ]),
            _ch("s5-perf-c5", "成本度量与预算控制", "建立 Token 与费用计量，设置调用预算、超限熔断；用成本看板持续观测。", 35, [
                _sec("s5-perf-c5-s1", "度量", "记录每次调用的模型/输入/输出 Token 与费用，按用户、接口、功能聚合。",
                    ["成本度量"]),
                _sec("s5-perf-c5-s2", "预算与熔断", "单会话/单用户预算上限，超限降级（更小模型/拒绝复杂任务），防止失控账单。",
                    ["预算控制", "熔断"]),
            ]),
        ],
        video_bv=BILIBILI_LANGCHAIN,
    ),
    _course(
        "s5-security", "安全与可控性",
        "Agent 会执行真实操作，安全是底线：输入过滤（Prompt 注入防护）、输出审查、权限控制、敏感信息保护、行为约束。",
        "优化部署", "intermediate", 7,
        [
            _ch("s5-sec-c1", "Prompt 注入防护", "恶意用户/文档中的指令可能劫持 Agent。理解注入原理并做输入过滤与指令隔离。", 45, [
                _sec("s5-sec-c1-s1", "注入是什么", "在用户输入或检索文档里夹带『忽略之前的指令』，诱导 Agent 执行未授权动作。",
                    ["Prompt 注入", "原理"]),
                _sec("s5-sec-c1-s2", "防护手段", "输入清洗、系统指令强调边界、把不可信内容与指令区分标签、关键动作需二次确认。",
                    ["注入防护", "指令隔离"]),
            ]),
            _ch("s5-sec-c2", "输入过滤与输出审查", "入口过滤危险内容，出口审查敏感输出；多模态内容（图片）同样要审。", 40, [
                _sec("s5-sec-c2-s1", "输入过滤", "按规则或模型对输入做安全分类，拦截恶意/违规请求，记录审计日志。",
                    ["输入过滤", "内容安全"]),
                _sec("s5-sec-c2-s2", "输出审查", "生成内容过审：违规词、敏感信息、隐私数据泄漏检测；不合格拦截或重生成。",
                    ["输出审查"]),
            ]),
            _ch("s5-sec-c3", "权限控制与行为约束", "Agent 调工具、访问数据都要最小权限；约束它『能做什么、不能做什么』。", 40, [
                _sec("s5-sec-c3-s1", "最小权限", "给 Agent 的凭据只授权必要范围（只读、指定目录/表）；敏感操作走人工审批（Human-in-the-Loop）。",
                    ["最小权限", "授权"]),
                _sec("s5-sec-c3-s2", "行为约束", "在工具层做白名单/黑名单、限制高危命令、设置执行预算——从工具实现上兜底，不依赖模型自觉。",
                    ["行为约束", "白名单"]),
            ]),
            _ch("s5-sec-c4", "敏感信息保护", "用户隐私、密钥、内部数据不进上下文/不落日志；回答不泄露敏感字段。", 35, [
                _sec("s5-sec-c4-s1", "数据脱敏", "入上下文前对手机号、身份证、密钥等脱敏；日志同样不记录原始敏感数据。",
                    ["脱敏", "隐私"]),
                _sec("s5-sec-c4-s2", "合规意识", "数据不出域（本地模型）、删除策略、用户授权——把合规做成工程的一部分。",
                    ["合规"]),
            ]),
            _ch("s5-sec-c5", "安全加固实践", "对一个客服 Agent 做安全审计：注入、越权、敏感数据泄漏逐项测试并加固。", 50, [
                _sec("s5-sec-c5-s1", "攻击演练", "构造注入 prompt、越权请求、敏感探测，观察 Agent 是否守住边界。",
                    ["安全测试", "攻击演练"]),
                _sec("s5-sec-c5-s2", "加固清单", "输入过滤/输出审查/最小权限/人工审批/脱敏/审计日志——形成可复用的安全 checklist。",
                    ["安全清单"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s5-observability", "监控、调试与评估",
        "生产 Agent 必须有眼睛：用 LangSmith 记录每一步执行，配合日志、性能监控、错误追踪；用指标评估 RAG 检索质量与 Agent 执行效果。",
        "优化部署", "intermediate", 8,
        [
            _ch("s5-obs-c1", "为什么 Agent 必须可观测", "Agent 多步自主执行，出错难定位；没有 trace 就没有办法排查与优化。", 30, [
                _sec("s5-obs-c1-s1", "黑盒问题", "一次错误可能是『检索错了/工具错了/生成错了』任一步；无日志=靠猜。",
                    ["可观测性", "定位难"]),
                _sec("s5-obs-c1-s2", "trace 的价值", "记录每次 LLM 调用、工具调用、中间状态，回放还原问题现场。",
                    ["trace"]),
            ]),
            _ch("s5-obs-c2", "LangSmith：官方监控工具", "用 LangSmith 记录 Agent 的执行轨迹、成本与延迟，支持回放与对比。", 45, [
                _sec("s5-obs-c2-s1", "接入与看板", "一行配置接入，自动采集 LLM 调用/工具/成本；Web 看板查看 trace 与统计。",
                    ["LangSmith", "接入"]),
                _sec("s5-obs-c2-s2", "回放与调试", "查看单个 trace 的每一步输入输出，定位问题节点；多版本对比评估改动效果。",
                    ["回放调试"]),
            ]),
            _ch("s5-obs-c3", "日志、监控与错误追踪", "结构化日志、关键指标（延迟/成功率/成本）、错误告警与追踪系统。", 35, [
                _sec("s5-obs-c3-s1", "结构化日志", "统一日志格式（含 request_id），把 Agent 步骤、工具结果、异常写入可查询的日志。",
                    ["结构化日志"]),
                _sec("s5-obs-c3-s2", "监控告警", "成功率下降、延迟升高、成本激增触发告警；错误带堆栈与上下文便于追踪。",
                    ["监控告警"]),
            ]),
            _ch("s5-obs-c4", "评估：RAG 检索质量", "用检索准确率、召回率等指标评估检索质量；建评估集持续回归。", 40, [
                _sec("s5-obs-c4-s1", "检索指标", "准确率（检到的相关/检出总量）、召回率（检到的相关/应检总量）；结合人工标注评估集。",
                    ["检索准确率", "召回率"]),
                _sec("s5-obs-c4-s2", "评估集与回归", "固化一批标准问答对，每次改动跑一遍，防止优化 A 破坏 B。",
                    ["评估集", "回归"]),
            ]),
            _ch("s5-obs-c5", "评估：Agent 执行效果与成本", "任务完成率、平均步数、Token 成本、人工干预率——多指标看 Agent 健康度。", 35, [
                _sec("s5-obs-c5-s1", "效果指标", "任务完成率、平均步数（步数多=效率低）、工具调用成功率、用户反馈。",
                    ["Agent 效果", "任务完成率"]),
                _sec("s5-obs-c5-s2", "成本与 A/B 测试", "Token 成本监控；Prompt/工具/模型改动用 A/B 对比，用数据说话。",
                    ["Token 成本", "A/B 测试"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s5-deploy", "生产部署方案",
        "把 Agent 变成线上服务：FastAPI+Uvicorn API、Docker 容器化、Streamlit/Gradio 前端、消息队列、微信/钉钉集成。",
        "优化部署", "intermediate", 8,
        [
            _ch("s5-dep-c1", "FastAPI + Uvicorn API 服务", "用 FastAPI 把 Agent 封装成可并发、可流式的 HTTP 服务，理解路由、依赖注入与生命周期。", 40, [
                _sec("s5-dep-c1-s1", "Agent 服务化", "把 Agent 循环封装进 FastAPI 接口，支持流式响应（SSE）与异步并发。",
                    ["FastAPI", "Agent 服务"]),
                _sec("s5-dep-c1-s2", "生产配置", "Uvicorn workers、超时、限流、CORS；环境变量管理模型选择与密钥。",
                    ["Uvicorn", "生产配置"]),
            ]),
            _ch("s5-dep-c2", "Docker 容器化部署", "编写 Dockerfile、docker-compose 一键部署；Docker 是面试必考，项目要能现场演示。", 45, [
                _sec("s5-dep-c2-s1", "Dockerfile", "分层镜像：装依赖→拷代码→启动命令；.dockerignore 排除无关文件。",
                    ["Dockerfile", "镜像分层"]),
                _sec("s5-dep-c2-s2", "docker-compose", "编排 API+数据库+向量库多个容器；环境变量注入密钥；健康检查与重启策略。",
                    ["docker-compose", "编排"]),
            ]),
            _ch("s5-dep-c3", "Web 前端：Streamlit / Gradio", "不写复杂前端，用 Streamlit 或 Gradio 快速搭演示界面，让 Agent 能被点着用。", 35, [
                _sec("s5-dep-c3-s1", "Streamlit 快速搭建", "输入框→调用 API→展示回答与引用，几十行代码出一个可演示页面。",
                    ["Streamlit"]),
                _sec("s5-dep-c3-s2", "Gradio 与多模态", "Gradio 对文件/图片/语音交互更友好，适合多模态 Demo。",
                    ["Gradio"]),
            ]),
            _ch("s5-dep-c4", "消息队列与异步任务", "长耗时任务（大批量处理）丢进消息队列异步消费，避免请求超时。", 35, [
                _sec("s5-dep-c4-s1", "异步化场景", "批量文档处理、定时任务、慢 Agent——用队列解耦，前端轮询或回调拿结果。",
                    ["消息队列", "异步任务"]),
                _sec("s5-dep-c4-s2", "队列选型", "RabbitMQ/Celery/Redis 队列按规模选；至少理解『入队→消费→结果存储』模型。",
                    ["队列选型"]),
            ]),
            _ch("s5-dep-c5", "微信 / 钉钉集成", "把 Agent 接入微信/钉钉机器人或企业应用，成为员工可用的内部助手。", 40, [
                _sec("s5-dep-c5-s1", "微信生态集成", "微信客服/公众号/企业微信回调→Agent→回复；理解消息签名与回调安全。",
                    ["微信集成"]),
                _sec("s5-dep-c5-s2", "钉钉与飞书", "钉钉/飞书机器人 webhook 收发消息；企业内部机器人是最常见的 Agent 落地形态。",
                    ["钉钉集成"]),
            ]),
        ],
        video_bv="",
    ),
]

# =====================================================================
# 阶段六：项目实战
# =====================================================================
STAGE6_COURSES = [
    _course(
        "s6-rag-project", "项目一：RAG 知识库问答系统",
        "求职作品级项目：FastAPI + LangChain/LangGraph + Chroma + 本地 Embedding + Docker，实现完整文档处理 pipeline、引用溯源、Agentic RAG 自纠错、SSE 流式与一键部署。",
        "项目实战", "advanced", 14,
        [
            _ch("s6-rag-c1", "项目规划与技术选型", "从需求出发定架构：功能清单、技术栈选择与理由、目录结构与数据流。", 40, [
                _sec("s6-rag-c1-s1", "需求与范围", "上传文档→自动分块向量化→问答带引用→检索可视化→部署演示；MVP 先行，再叠加 Agentic RAG。",
                    ["需求分析", "MVP"]),
                _sec("s6-rag-c1-s2", "技术选型理由", "FastAPI（后端）+LangGraph（编排）+Chroma（向量）+本地 Ollama（省钱+隐私）——每个选择都要能讲出理由。",
                    ["技术选型"]),
            ]),
            _ch("s6-rag-c2", "文档处理 pipeline", "实现上传→解析→分块→向量化→入库的完整链路，含格式兼容与进度反馈。", 45, [
                _sec("s6-rag-c2-s1", "加载与清洗", "支持 PDF/MD/Word/纯文本，清洗页眉页脚，保留 metadata 供引用。",
                    ["文档加载", "清洗"]),
                _sec("s6-rag-c2-s2", "分块与入库", "按章节智能分块，向量化写入 Chroma；幂等处理重复上传（按文档 hash 去重）。",
                    ["分块", "向量入库"]),
            ]),
            _ch("s6-rag-c3", "问答：检索 + 引用溯源", "检索相关片段，拼装上下文回答，答案标注出处；前端展示引用来源。", 40, [
                _sec("s6-rag-c3-s1", "检索问答", "检索 top-k→基于资料生成→约束『资料不足要明说』，减少幻觉。",
                    ["检索问答"]),
                _sec("s6-rag-c3-s2", "引用溯源", "回答携带来源片段与位置；前端点击引用可查看原文，提升可信度。",
                    ["引用溯源"]),
            ]),
            _ch("s6-rag-c4", "Agentic RAG 增强", "给系统加评分/重写/自纠错：检索结果评分、查询重写、答案质量检查与循环刹车。", 50, [
                _sec("s6-rag-c4-s1", "自纠错闭环", "retrieve→grade→rewrite→generate→check 图化，不合格自动回炉。",
                    ["Agentic RAG"]),
                _sec("s6-rag-c4-s2", "质量与成本平衡", "retry_count 刹车；低置信才触发重查，控制 Token 成本。",
                    ["循环刹车"]),
            ]),
            _ch("s6-rag-c5", "SSE 流式与前端演示", "答案流式输出（SSE），用 Streamlit 或小程序页做可演示界面。", 40, [
                _sec("s6-rag-c5-s1", "SSE 流式", "后端分块推流，前端逐字渲染；流式是面试亮点也是体验刚需。",
                    ["SSE", "流式输出"]),
                _sec("s6-rag-c5-s2", "演示界面", "文档上传+问答+引用展示，一键清空重建知识库；演示要顺、要快。",
                    ["前端演示"]),
            ]),
            _ch("s6-rag-c6", "Docker 部署与文档", "编写 Dockerfile 与 docker-compose，一键部署；README 讲清架构、用法与演示路径。", 45, [
                _sec("s6-rag-c6-s1", "容器化", "API+向量库+（可选）本地模型编排成 docker-compose up 即可运行。",
                    ["Docker", "docker-compose"]),
                _sec("s6-rag-c6-s2", "README 与展示", "架构图、接口说明、截图、演示视频；能讲清『为什么这样设计』是面试加分点。",
                    ["项目文档"]),
            ]),
        ],
        video_bv="",
    ),
    _course(
        "s6-cs-agent", "项目二：智能客服 / 业务 Agent",
        "展示 Agent 核心能力的求职项目：FastAPI + LangGraph + Chroma，实现多工具调用、RAG 作为工具、多轮记忆、敏感操作人工审批、循环刹车与成本控制。",
        "项目实战", "advanced", 14,
        [
            _ch("s6-cs-c1", "需求与角色设计", "定义客服场景：服务范围、工具集、业务规则、敏感操作清单与审批流。", 40, [
                _sec("s6-cs-c1-s1", "场景定义", "以电商/教育等具体场景为例：查订单、查课程、退换货规则、转人工。",
                    ["场景定义"]),
                _sec("s6-cs-c1-s2", "工具与边界", "列出 Agent 可调工具（订单查询/价格查询/发送通知…）及『绝不自动执行』的高危操作。",
                    ["工具集", "行为边界"]),
            ]),
            _ch("s6-cs-c2", "多工具调用与 RAG 作为工具", "实现多个业务工具，并把知识库检索封装成 RAG 工具，Agent 自主决定查哪个。", 45, [
                _sec("s6-cs-c2-s1", "业务工具", "订单查询、优惠计算、工单创建等 @tool，参数与描述精雕细琢。",
                    ["业务工具"]),
                _sec("s6-cs-c2-s2", "RAG 即工具", "知识库 retriever 包装成『查规则』工具，Agent 需要规则时主动检索——客服标准打法。",
                    ["RAG as Tool"]),
            ]),
            _ch("s6-cs-c3", "多轮记忆与会话管理", "用 LangGraph Checkpointer 实现跨轮记忆，用户前文信息（订单号、诉求）贯穿对话。", 40, [
                _sec("s6-cs-c3-s1", "多轮记忆", "thread_id 会话、状态抽取（记录用户订单号与诉求）、跨轮引用。",
                    ["多轮记忆"]),
                _sec("s6-cs-c3-s2", "会话治理", "会话超时清理、记忆去隐私化（不存敏感字段）、多用户隔离。",
                    ["会话治理"]),
            ]),
            _ch("s6-cs-c4", "Human-in-the-Loop 审批", "退款、发货、改单等敏感操作必须人工审批：Agent 生成申请→人工确认→执行。", 45, [
                _sec("s6-cs-c4-s1", "审批流", "interrupt_before 拦截高危动作，前端展示待审批项，批准后从断点续跑。",
                    ["人工审批", "Human-in-the-Loop"]),
                _sec("s6-cs-c4-s2", "审批与权限", "审批人角色、审计留痕；未批准则告知用户并终止。",
                    ["审批权限"]),
            ]),
            _ch("s6-cs-c5", "循环刹车与成本控制", "设置 Agent 最大步数、工具调用去重、预算上限；异常时优雅降级。", 35, [
                _sec("s6-cs-c5-s1", "护栏", "max_steps、工具去重、预算熔断、失败兜底——阶段四的清单在此落地。",
                    ["循环刹车", "护栏"]),
                _sec("s6-cs-c5-s2", "成本观测", "接入 LangSmith 记录每次调用成本；按会话统计 Token 消耗。",
                    ["成本控制"]),
            ]),
            _ch("s6-cs-c6", "部署、演示与复盘", "Docker 部署；准备演示脚本（正常路径+敏感审批路径+异常路径）；写清架构与设计决策。", 45, [
                _sec("s6-cs-c6-s1", "部署演示", "docker-compose up 一键起；演示三场景：普通咨询、需审批操作、知识库问答。",
                    ["部署演示"]),
                _sec("s6-cs-c6-s2", "复盘输出", "写技术博客/README：为什么用 LangGraph、为什么 RAG 做工具、审批如何设计——讲透设计取舍。",
                    ["复盘", "技术博客"]),
            ]),
        ],
        video_bv="",
    ),
]

# =====================================================================
# 阶段七：求职备战
# =====================================================================
STAGE7_COURSES = [
    _course(
        "s7-career", "AI Agent 求职备战",
        "把技术转化为 Offer：打磨简历与项目包装、吃透高频面试题（概念/架构/技术/项目）、讲清技术选型、准备作品演示，把握 Agent 技术趋势。",
        "求职备战", "beginner", 6,
        [
            _ch("s7-car-c1", "简历与项目包装", "把 RAG/客服 Agent 项目写进简历：量化成果、讲清个人贡献、突出技术难点与解法。", 40, [
                _sec("s7-car-c1-s1", "简历写法", "STAR 结构、量化指标（检索准确率提升/成本下降）、避免流水账；项目在线可访问是最强证明。",
                    ["简历", "STAR"]),
                _sec("s7-car-c1-s2", "作品集准备", "GitHub 代码规范、README 完整、演示视频/截图；准备一份项目介绍文档。",
                    ["作品集"]),
            ]),
            _ch("s7-car-c2", "高频面试题：基础概念", "Agent vs LLM、核心能力、ReAct、记忆系统、Function Calling——概念题要能一句话答清再展开。", 40, [
                _sec("s7-car-c2-s1", "概念题攻略", "每个概念准备『一句话定义+一个例子+一个工程点』，面试官会追问细节。",
                    ["Agent/LLM", "ReAct", "Function Calling"]),
                _sec("s7-car-c2-s2", "记忆与工具题", "记忆系统如何设计、工具调用如何实现——结合你做的项目讲，别背八股。",
                    ["记忆系统", "工具调用"]),
            ]),
            _ch("s7-car-c3", "高频面试题：架构与技术实现", "多 Agent 协作、工作流设计、可控性与安全、LangChain vs LangGraph、RAG 与 Agent 结合、性能优化与调试。", 45, [
                _sec("s7-car-c3-s1", "架构题", "如何设计智能客服 Agent、如何保证可控安全——用你项目的取舍回答。",
                    ["架构设计", "安全性"]),
                _sec("s7-car-c3-s2", "技术实现题", "LangChain vs LangGraph、RAG 与 Agent 结合、如何优化与调试——答出『我做过+遇到过什么坑』。",
                    ["LangChain/LangGraph", "优化调试"]),
            ]),
            _ch("s7-car-c4", "项目经验与难点复盘", "『你开发过哪些 Agent 应用』是必考题：讲清架构、难点、踩过的坑、如何评估效果。", 40, [
                _sec("s7-car-c4-s1", "项目讲述模板", "背景→架构→我负责什么→难点与解法→效果与反思；控制在 3 分钟。",
                    ["项目讲述"]),
                _sec("s7-car-c4-s2", "常见追问", "为什么用 LangGraph 不用 AgentExecutor？检索质量怎么评估？成本怎么控？——提前备好。",
                    ["追问准备"]),
            ]),
            _ch("s7-car-c5", "技术趋势与行动清单", "关注 OpenAI/Anthropic/国内大厂在 Agent 方向进展；规划自己的学习与求职节奏。", 35, [
                _sec("s7-car-c5-s1", "保持敏感", "MCP/A2A、Agentic 工具、多模态 Agent 是热点；多读文章与开源项目保持更新。",
                    ["技术趋势"]),
                _sec("s7-car-c5-s2", "行动清单", "简历→项目在线→刷题→模拟面试→内推；用面试鸭刷 AI Agent 题库，1v1 模拟面试练手感。",
                    ["求职行动", "面试鸭"]),
            ]),
        ],
        video_bv="",
    ),
]

ALL_STAGE_COURSES = {
    1: STAGE1_COURSES, 2: STAGE2_COURSES, 3: STAGE3_COURSES, 4: STAGE4_COURSES,
    5: STAGE5_COURSES, 6: STAGE6_COURSES, 7: STAGE7_COURSES,
}

# 每门课的视频观看资源映射
VIDEO_RESOURCE = {
    "s1-llm-basics": (BILIBILI_BLACKHORSE, "阶段一 · AI 大模型基础（黑马 Python+AI 大模型）"),
    "s1-prompt": (BILIBILI_BLACKHORSE, "阶段一 · AI 大模型基础（黑马 Python+AI 大模型）"),
    "s1-api-dev": (BILIBILI_BLACKHORSE, "阶段一 · AI 大模型基础（黑马 Python+AI 大模型）"),
    "s1-ollama": (BILIBILI_BLACKHORSE, "阶段一 · AI 大模型基础（黑马 Python+AI 大模型）"),
    "s2-agent-core": (BILIBILI_AGENT, "阶段二 · Agent 基础概念（2025 AI Agent 智能体全套）"),
    "s2-agent-arch": (BILIBILI_AGENT, "阶段二 · Agent 基础概念（2025 AI Agent 智能体全套）"),
    "s2-tool-calling": (BILIBILI_AGENT, "阶段二 · Agent 基础概念（2025 AI Agent 智能体全套）"),
    "s2-memory": (BILIBILI_AGENT, "阶段二 · Agent 基础概念（2025 AI Agent 智能体全套）"),
    "s3-rag": (DOC_RAG, "阶段三 · RAG（LangChain RAG 官方教程）"),
    "s3-mcp": (DOC_MCP, "阶段三 · MCP（MCP 官方文档）"),
    "s3-skills": (BILIBILI_LANGCHAIN, "阶段三 · Agent Skills（LangChain Agent 实战）"),
    "s3-langchain": (BILIBILI_LANGCHAIN, "阶段三 · LangChain（LangChain Agent 实战）"),
    "s3-langgraph": (DOC_LANGGRAPH, "阶段三 · LangGraph（官方文档）"),
    "s3-agentic-rag": (DOC_LANGGRAPH, "阶段三 · Agentic RAG（LangGraph 官方文档）"),
    "s4-multi-agent": (BILIBILI_AGENT, "阶段四 · 多 Agent（2025 AI Agent 智能体全套）"),
    "s4-metagpt-autogen": (DOC_METAGPT, "阶段四 · MetaGPT（GitHub）"),
    "s4-orchestration": (DOC_AUTOGEN, "阶段四 · 编排（AutoGen 官方文档）"),
    "s5-performance": (BILIBILI_LANGCHAIN, "阶段五 · 性能优化（LangChain Agent 实战）"),
    "s5-security": (DOC_LANGCHAIN_ZH, "阶段五 · 安全（LangChain 中文文档）"),
    "s5-observability": (DOC_LANGSMITH, "阶段五 · 监控评估（LangSmith 官方文档）"),
    "s5-deploy": (DOC_DEPLOY, "阶段五 · 部署（Agent 部署最佳实践）"),
    "s6-rag-project": (DOC_YUPI_PROJECTS, "阶段六 · RAG 知识库项目（鱼皮 AI 项目教程合集）"),
    "s6-cs-agent": (DOC_YUPI_PROJECTS, "阶段六 · 智能客服项目（鱼皮 AI 项目教程合集）"),
    "s7-career": (DOC_MIANSHIYA, "阶段七 · 求职备战（面试鸭 AI 面试题）"),
}

STAGE_TITLE = {
    1: "阶段一：AI 大模型基础", 2: "阶段二：Agent 基础概念", 3: "阶段三：Agent 开发实战",
    4: "阶段四：多 Agent 系统", 5: "阶段五：优化和部署", 6: "阶段六：项目实战", 7: "阶段七：求职备战",
}

# 观看路径：阶段间衔接说明（写入视频 description 的观看指引）
VIEWING_PATH = {
    1: "观看路径：本阶段为入门基石，建议先学完【大模型基础→Prompt→API→Ollama】四课，再进入阶段二。",
    2: "观看路径：掌握 Agent 核心概念与工具调用后，即可进入阶段三的 RAG 与框架实战。",
    3: "观看路径：阶段三是核心重点，按【RAG→MCP→Skills→LangChain→LangGraph→Agentic RAG】顺序学习，每课都动手跑通代码。",
    4: "观看路径：了解多 Agent 架构与框架即可，重点理解『何时该用多 Agent』及其代价，随后进入阶段五。",
    5: "观看路径：阶段五把前面积累的 Agent 打磨成生产级：性能、安全、监控、部署四项缺一不可。",
    6: "观看路径：综合运用全部知识做 1-2 个可部署项目，是求职最有力的作品，完成后进入阶段七求职。",
    7: "观看路径：最后冲刺：改简历、刷面试题、打磨项目讲述，准备拿 Offer。",
}

# 每门课的核心知识点（视频 coreInfo 用）
COURSE_CORE_INFO = {
    "s1-llm-basics": ["大语言模型 LLM", "Transformer 架构", "主流模型选型", "Token 与上下文窗口", "模型能力与局限"],
    "s1-prompt": ["Prompt 基础", "Few-shot Learning", "Chain of Thought 思维链", "角色扮演", "Prompt 优化迭代"],
    "s1-api-dev": ["OpenAI/国产 API", "temperature/top_p/max_tokens", "流式输出", "错误处理", "API Key 管理", "依赖管理"],
    "s1-ollama": ["Ollama 本地部署", "qwen2.5 本地模型", "OpenAI 兼容调用", "数据不出本地", "开发调试工作流"],
    "s2-agent-core": ["AI Agent 定义", "感知/推理/决策/执行", "Agent vs LLM", "应用场景"],
    "s2-agent-arch": ["ReAct 架构", "Plan and Execute", "Reflection 反思", "Multi-Agent 概览", "架构选型"],
    "s2-tool-calling": ["Function Calling", "工具定义与描述", "参数解析", "执行与结果返回", "天气查询 Agent"],
    "s2-memory": ["短期记忆", "长期记忆", "向量数据库 Chroma", "记忆检索与更新"],
    "s3-rag": ["文档加载", "文本分块", "Embedding", "Chroma 向量库", "引用溯源", "查询改写/混合检索/Rerank/HyDE", "企业知识库实践"],
    "s3-mcp": ["MCP 协议", "Client↔Server↔工具", "现成 MCP Server", "MCP vs Function Calling", "MCP 与 A2A"],
    "s3-skills": ["Skill 定义", "描述与边界", "多 Skill 协作", "Skill 与工具/RAG 关系"],
    "s3-langchain": ["Document Loaders", "Text Splitters", "Embeddings/VectorStores", "Retrieval Chain", "@tool", "AgentExecutor", "Memory", "Retriever as Tool"],
    "s3-langgraph": ["State/Node/Edge", "条件路由", "手搓 ReAct", "Checkpointer 记忆", "Human-in-the-Loop"],
    "s3-agentic-rag": ["retrieve→grade→rewrite→generate→check", "文档评分", "查询重写", "幻觉检测", "循环刹车"],
    "s4-multi-agent": ["五种协作模式", "通信机制", "任务分配", "角色设计", "多 Agent 代价"],
    "s4-metagpt-autogen": ["MetaGPT", "AutoGen", "群聊模式", "框架选型"],
    "s4-orchestration": ["工作流设计", "条件分支", "循环迭代", "错误处理重试", "工程化陷阱"],
    "s5-performance": ["Prompt 优化省 Token", "缓存策略", "并行执行", "流式输出", "成本控制"],
    "s5-security": ["Prompt 注入防护", "输入过滤", "输出审查", "权限控制", "敏感信息保护"],
    "s5-observability": ["LangSmith", "日志分析", "性能监控", "错误追踪", "RAG 检索质量评估", "Agent 效果评估"],
    "s5-deploy": ["FastAPI+Uvicorn", "Docker 容器化", "Streamlit/Gradio", "消息队列", "微信/钉钉集成"],
    "s6-rag-project": ["文档处理 pipeline", "引用溯源", "Agentic RAG", "SSE 流式", "Docker 一键部署"],
    "s6-cs-agent": ["多工具调用", "RAG as Tool", "多轮记忆", "Human-in-the-Loop", "循环刹车与成本控制"],
    "s7-career": ["简历与作品集", "高频面试题", "技术选型讲解", "项目讲述", "技术趋势"],
}


def build_videos():
    """为 24 门课各生成一条配套视频。"""
    videos = []
    for stage, courses in ALL_STAGE_COURSES.items():
        for co in courses:
            cid = co["id"]
            url, source_name = VIDEO_RESOURCE[cid]
            if url.startswith("BV"):
                url = f"https://www.bilibili.com/video/{url}"
            description = (
                f"本视频对应课程《{co['title']}》，属于{STAGE_TITLE[stage]}。"
                f"资源来源：{source_name}。覆盖知识点：{'、'.join(COURSE_CORE_INFO.get(cid, []))}。"
                f"{VIEWING_PATH[stage]}"
            )
            videos.append({
                "id": f"video-{cid}",
                "title": f"{STAGE_TITLE[stage]} · {co['title']} · 配套视频",
                "subtitle": STAGE_TITLE[stage],
                "description": description,
                "coreInfo": COURSE_CORE_INFO.get(cid, []),
                "narrative": "",
                "visual": "",
                "quality": {},
                "url": url,
                "coverUrl": co["coverImg"],
                "duration": sum(ch.get("duration_minutes", 0) for ch in co["chapters"]) * 60,
                "chapter": "",
                "courseId": cid,
            })
    return videos


def build_directions():
    """7 个学习方向（学习页分类筛选用）。"""
    return [
        {"name": "阶段一 · AI 大模型基础", "description": "LLM 概念、Prompt、API 调用、Ollama 本地部署", "color": "#165dff", "topic_key": "大模型基础", "sort_order": 1},
        {"name": "阶段二 · Agent 基础概念", "description": "Agent 核心能力、架构模式、工具调用、记忆系统", "color": "#7c3aed", "topic_key": "Agent基础", "sort_order": 2},
        {"name": "阶段三 · Agent 开发实战", "description": "RAG、MCP、Agent Skills、LangChain、LangGraph", "color": "#00b42a", "topic_key": "开发实战", "sort_order": 3},
        {"name": "阶段四 · 多 Agent 系统", "description": "多 Agent 架构、MetaGPT/AutoGen、编排与工程化", "color": "#ff7d00", "topic_key": "多Agent", "sort_order": 4},
        {"name": "阶段五 · 优化和部署", "description": "性能优化、安全可控、监控评估、生产部署", "color": "#f53f3f", "topic_key": "优化部署", "sort_order": 5},
        {"name": "阶段六 · 项目实战", "description": "RAG 知识库问答、智能客服 Agent 求职作品", "color": "#00a0c0", "topic_key": "项目实战", "sort_order": 6},
        {"name": "阶段七 · 求职备战", "description": "简历作品集、高频面试题、项目讲述", "color": "#ff6b81", "topic_key": "求职备战", "sort_order": 7},
    ]


def build_learning_paths():
    """按 7 阶段顺序组织的学习路径（供首页/学习路径页展示与解锁）。

    每个课程节点同时给 items（课程 id 列表）与 courseId（首个课程，供前端跳转）。
    """
    paths = []

    def _stage_node(pid, stage, course_ids):
        cids = list(course_ids)
        return {
            "id": f"{pid}-{stage}",
            "title": STAGE_TITLE[stage],
            "type": "course",
            "items": cids,
            "courseId": cids[0] if cids else None,
        }

    # 主路径：完整 7 阶段
    main_nodes = []
    for stage, courses in ALL_STAGE_COURSES.items():
        main_nodes.append(_stage_node("path-2026", stage, [c["id"] for c in courses]))
    paths.append({
        "id": "path-2026",
        "direction": "AI Agent 应用开发",
        "title": "学习路线：零基础到精通 AI Agent 开发",
        "description": "依据《2026 最新 AI Agent 应用开发学习路线》，7 阶段循序渐进：大模型基础→Agent 概念→开发实战→多 Agent→优化部署→项目实战→求职备战。",
        "total_weeks": 12, "totalWeeks": 12, "current_week": 0, "currentWeek": 0,
        "nodes": main_nodes,
    })
    # 3 条方向化路径（差异化选课，复用阶段课程）
    variants = [
        ("path-2026-rag", "RAG 知识库方向", "偏重检索增强与知识库，主攻 RAG 与 Agentic RAG。",
         [1, 2, 3, 5, 6], {"s3-rag", "s3-langchain", "s3-langgraph", "s3-agentic-rag"}),
        ("path-2026-agent", "智能体应用方向", "偏重智能体能力与工具调用，主攻 Agent 与客服场景。",
         [1, 2, 3, 4, 5, 6], {"s2-tool-calling", "s3-langgraph", "s4-multi-agent", "s6-cs-agent"}),
        ("path-2026-fullstack", "全栈 AI 应用方向", "覆盖应用全链路：开发 + 部署 + 项目交付。",
         [1, 2, 3, 4, 5, 6, 7], {"s3-langchain", "s5-deploy", "s6-rag-project", "s7-career"}),
    ]
    for pid, title, desc, stage_list, extra in variants:
        vnodes = []
        for stage in stage_list:
            courses = ALL_STAGE_COURSES[stage]
            cids = [c["id"] for c in courses if c["id"] in extra] if stage == 3 else [c["id"] for c in courses]
            if not cids:
                cids = [courses[0]["id"]]
            vnodes.append(_stage_node(pid, stage, cids))
        paths.append({
            "id": pid,
            "direction": title,
            "title": title,
            "description": desc,
            "total_weeks": 10, "totalWeeks": 10, "current_week": 0, "currentWeek": 0,
            "nodes": vnodes,
        })
    return paths


def _apply_section_enrich(all_courses):
    """把 course_content.SECTION_ENRICH 的详实内容合并到每个小节（按小节 id 覆盖）。"""
    try:
        from data_pipeline.course_content import SECTION_ENRICH
    except Exception:
        SECTION_ENRICH = {}
    applied = 0
    for co in all_courses:
        for ch in co.get("chapters", []):
            for sec in ch.get("sections", []):
                e = SECTION_ENRICH.get(sec["id"])
                if not e:
                    continue
                if e.get("content"):
                    sec["content"] = e["content"]
                if e.get("case"):
                    sec["case"] = e["case"]
                if e.get("knowledge_points"):
                    sec["knowledge_points"] = e["knowledge_points"]
                applied += 1
    print(f"  [curriculum-2026] 小节内容扩充已应用：{applied}/{sum(len(ch['sections']) for c in all_courses for ch in c['chapters'])}")
    return all_courses


# =====================================================================
# 实战项目分步指南（project steps）
# 每个项目 5 步：title / desc / guide（操作指引）/ acceptance（验收标准）
# =====================================================================
PROJECT_STEPS = {
    "project-0": [  # 个人AI周报生成工作流（入门）
        {"title": "明确周报内容与格式", "desc": "确定周报需要包含的板块（本周工作/成果/问题/下周计划），明确目标读者与格式。",
         "guide": "先列出一份你想要的周报模板，标注每个板块要写什么；参考一份真实周报反推结构。",
         "acceptance": "产出一份含各板块标题的周报模板。"},
        {"title": "设计可复用的提示词模板", "desc": "把周报生成规则写成带占位符的提示词模板，含角色、任务、格式与约束。",
         "guide": "用阶段一的四段式提示词方法写：角色（资深运营）+ 任务（按模板生成周报）+ 格式（分点）+ 占位符 {本周事项}。",
         "acceptance": "有一条包含占位符的完整周报提示词模板。"},
        {"title": "随手记录本周事项", "desc": "把本周完成的工作、数据、遇到的问题随手记录下来，作为周报素材。",
         "guide": "用手机备忘录或文档随手记，每天 2-3 条：做了什么、结果如何、卡在哪。",
         "acceptance": "积累至少 10 条本周事项记录。"},
        {"title": "生成并迭代优化周报", "desc": "把事项填入提示词让 AI 生成周报，对照模板检查并迭代优化。",
         "guide": "AI 生成后逐板块核对是否完整；缺板块/缺数据就补充提示词再生成，直到满意。",
         "acceptance": "生成一份完整周报并人工修订定稿。"},
        {"title": "沉淀为每周复用流程", "desc": "把模板与流程固化，形成每周可复用的标准化工作流。",
         "guide": "把提示词模板保存为可复用文件，写清每周『收集→填入→生成→修订』的使用步骤。",
         "acceptance": "有完整的周报工作流文档 + 一份示例周报。"},
    ],
    "project-3": [  # 个人AI提示词库建设（入门）
        {"title": "盘点你的高频任务", "desc": "梳理你日常反复做的任务（写文案、做总结、起标题等），作为提示词库的收录对象。",
         "guide": "列出 5-10 个你每周都会做的任务，标注使用场景与目标读者。",
         "acceptance": "有一份高频任务清单。"},
        {"title": "为每个任务写一条优质提示词", "desc": "针对每个高频任务，用角色+任务+格式+约束四段式写一条提示词。",
         "guide": "每条提示词都要能直接复用，把会变的参数用占位符标出。",
         "acceptance": "至少为 3 个任务各写一条完整提示词。"},
        {"title": "测试与迭代提示词", "desc": "实际运行每条提示词，根据输出质量迭代优化，记录有效版本。",
         "guide": "每个任务跑 2-3 次，对比输出差异；效果不稳就补示例或调整约束。",
         "acceptance": "3 条提示词各有一次有效输出记录。"},
        {"title": "建立提示词库结构", "desc": "按场景/任务给提示词分类归档，建立目录与索引。",
         "guide": "用文件夹或文档按『任务类型』分类，每条带用途说明与示例输出。",
         "acceptance": "有结构清晰的提示词库（分类 + 索引）。"},
        {"title": "持续沉淀与分享", "desc": "把验证有效的提示词沉淀入库，形成可持续积累的个人资产。",
         "guide": "每周新增 1-2 条，标注来源与效果；可整理成文档对外分享。",
         "acceptance": "完成提示词库整理，附一份示例输出。"},
    ],
    "project-1": [  # 活动策划全流程实战（进阶）
        {"title": "明确活动目标与受众", "desc": "确定活动要达成的目标（拉新/转化/品牌）与目标受众画像。",
         "guide": "写出活动的核心目标、衡量指标（如报名人数）、目标人群特征。",
         "acceptance": "有一页活动目标与受众说明。"},
        {"title": "用 AI 生成活动方案初稿", "desc": "把活动需求喂给 AI，生成包含主题、形式、流程、预算的完整方案初稿。",
         "guide": "提示词要点：活动类型、受众、预算范围、输出格式（方案书分节）。",
         "acceptance": "生成一份结构化活动方案初稿。"},
        {"title": "拆解执行任务与时间表", "desc": "把方案拆成可执行的任务清单，排定时间表与负责人。",
         "guide": "用 AI 辅助把方案拆成『物料/宣传/现场/复盘』四线任务，标注截止时间。",
         "acceptance": "有一份带时间线的任务清单。"},
        {"title": "生成宣传物料文案", "desc": "用 AI 批量生成活动宣传文案（海报文案、公众号、朋友圈等）。",
         "guide": "按不同渠道分别写提示词，保持口径一致，突出活动亮点。",
         "acceptance": "至少 3 条不同渠道的宣传文案。"},
        {"title": "活动复盘与沉淀", "desc": "活动结束后汇总数据，用 AI 辅助生成复盘报告，沉淀可复用模板。",
         "guide": "输入活动数据（报名/到场/转化）与过程记录，让 AI 输出复盘要点与改进建议。",
         "acceptance": "一份含数据与改进建议的复盘报告。"},
    ],
    "project-2": [  # AI求职竞争力提升方案（进阶）
        {"title": "做一次自我能力盘点", "desc": "梳理你的技能、项目、经历，明确目标岗位与差距。",
         "guide": "列出目标岗位的核心要求，对照自己的技能逐项打分，找出差距。",
         "acceptance": "有一份能力盘点与差距清单。"},
        {"title": "用 AI 优化简历", "desc": "把简历初稿交给 AI，用 STAR 原则改写，突出量化成果。",
         "guide": "提示词要点：目标岗位、简历原文、要求按 STAR 量化改写、控制一页。",
         "acceptance": "一份按 STAR 量化改写的简历。"},
        {"title": "准备项目与作品集", "desc": "把学习中的项目整理成可展示的作品（GitHub/演示/说明）。",
         "guide": "检查项目是否可复现、有 README、能演示；补齐缺失部分。",
         "acceptance": "至少一个可在线访问/可演示的项目。"},
        {"title": "AI 模拟面试练习", "desc": "用 AI 扮演面试官模拟面试，针对薄弱环节反复练习。",
         "guide": "让 AI 按目标岗位出题并追问，把你的回答喂回去让它点评改进。",
         "acceptance": "完成至少 3 轮模拟面试并记录改进点。"},
        {"title": "制定求职行动计划", "desc": "把求职拆成可执行的步骤（投递/内推/面试/复盘）并按周推进。",
         "guide": "写一份四周行动计划：每周投递量、面试复盘、简历迭代节奏。",
         "acceptance": "一份按周排期的求职行动计划。"},
    ],
    "project-4": [  # 结业综合项目（高级）
        {"title": "确定结业项目方向", "desc": "选择一个能综合运用全部技能的项目方向（推荐 RAG 知识库或智能客服 Agent）。",
         "guide": "结合自身兴趣与目标岗位选择方向，明确项目要解决的问题与验收标准。",
         "acceptance": "一页项目立项说明（方向/目标/范围/技术栈）。"},
        {"title": "完成技术选型与架构设计", "desc": "确定技术栈并画出系统架构，讲清每个技术选择的理由。",
         "guide": "写清 FastAPI/LangGraph/Chroma 等选型理由、数据流与模块划分。",
         "acceptance": "一份含架构图与选型理由的设计文档。"},
        {"title": "实现核心功能并加工程护栏", "desc": "实现项目核心链路，接入日志、错误处理、预算、安全等工程护栏。",
         "guide": "按阶段四的工程清单逐项落实：终止条件、日志、失败兜底、敏感操作审批。",
         "acceptance": "核心功能可运行 + 工程护栏清单逐项落地。"},
        {"title": "容器化部署与演示", "desc": "用 Docker 部署项目，准备一套可现场演示的流程。",
         "guide": "写好 Dockerfile/compose 与 README，预演『上传→问答→演示』的完整脚本。",
         "acceptance": "docker-compose up 一键可跑 + 一份演示脚本。"},
        {"title": "项目复盘与作品输出", "desc": "写技术博客/README 复盘设计取舍与踩坑，形成求职作品。",
         "guide": "讲清为什么这么设计、遇到什么坑、效果如何，配架构图与数据。",
         "acceptance": "完整的项目文档（README/博客）与展示素材。"},
    ],
}


def _enrich_projects():
    """为项目补充分步指南（steps）：读 seed_data 生成的项目，合并 PROJECT_STEPS 后写回。"""
    projects = None
    for name in ("enriched_projects.json", "projects.json"):
        path = os.path.join(PROCESSED_DIR, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                projects = json.load(f)
            break
    if projects is None:
        print("  [curriculum-2026] 未找到项目数据，跳过 steps 补充")
        return
    applied = 0
    for p in projects:
        steps = PROJECT_STEPS.get(p.get("id"))
        if steps:
            p["steps"] = steps
            p["stepCount"] = len(steps)
            p["step_count"] = len(steps)
            applied += 1
    for name in ("enriched_projects.json", "projects.json"):
        with open(os.path.join(PROCESSED_DIR, name), "w", encoding="utf-8") as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
    print(f"  [curriculum-2026] 项目步骤已补充：{applied}/{len(projects)}")


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    all_courses = [c for stage in range(1, 8) for c in ALL_STAGE_COURSES[stage]]
    all_courses = _apply_section_enrich(all_courses)
    courses_path = os.path.join(PROCESSED_DIR, "enriched_courses.json")
    with open(courses_path, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    videos_path = os.path.join(PROCESSED_DIR, "videos.json")
    videos = build_videos()
    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    paths = build_learning_paths()
    paths_path = os.path.join(PROCESSED_DIR, "enriched_learning_paths.json")
    with open(paths_path, "w", encoding="utf-8") as f:
        json.dump(paths, f, ensure_ascii=False, indent=2)
    # DB 灌入读 learning_paths.json，API 路由读 enriched_learning_paths.json，两份保持一致
    with open(os.path.join(PROCESSED_DIR, "learning_paths.json"), "w", encoding="utf-8") as f:
        json.dump(paths, f, ensure_ascii=False, indent=2)

    # 同步 courses.json 基础版（部分旧逻辑读它），内容一致
    with open(os.path.join(PROCESSED_DIR, "courses.json"), "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    _enrich_projects()

    print(f"[curriculum-2026] 写入 {len(all_courses)} 门课程、{len(videos)} 条视频、"
          f"{len(build_directions())} 个方向、{len(build_learning_paths())} 条学习路径 → {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
