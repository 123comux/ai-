"""扩充五阶段课程体系：在现有 5 门主课基础上新增 8 门场景课，共 13 门。

对齐《商业评审报告》4.3 各阶段课程样例：
- 认知：AI 的边界与风险
- 入门：AI 写作初体验 / AI 绘图·办公初体验
- 进阶：万能四段式提示词 / AI 长文本结构化输出
- 实战：周报自动生成 / 活动策划 AI 工作流 / PPT 文案批量生成

幂等：课程 id 已存在于 courses.json / cms.db 时跳过，可重复运行。
同时合并进 courses.json 与 enriched_courses.json，并入库 cms.db（courses 表）。
"""
import json
import os
import sqlite3

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BACKEND, "data", "processed")
DB_PATH = os.path.join(BACKEND, "data", "cms.db")

# ---------- 8 门新场景课 ----------

NEW_COURSES = [
    {
        "id": "stage-1-boundary",
        "title": "AI 的边界与风险 — 什么时候该用、什么时候该防",
        "description": "AI 不是万能魔法。本课帮你建立对 AI 的清醒认知：它会犯错、会泄露隐私、会让人过度依赖。学完你会知道哪些场景要大胆用 AI，哪些场景要谨慎甚至不用。",
        "topic": "认知",
        "difficulty": "beginner",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage1-boundary/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-bnd-1",
                "title": "AI 会犯错：幻觉与误导",
                "content_summary": "AI 会一本正经地编造事实（幻觉），也会自信地给出错误答案。学会识别和核实是 AI 时代的基本功。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-bnd-1-1",
                        "title": "什么是幻觉：AI 如何一本正经地胡说",
                        "content": "AI 生成内容时可能凭空编造不存在的书、人物或数据，且语气非常自信。这是概率生成的固有缺陷，不是 bug。",
                        "knowledge_points": ["幻觉现象", "AI 的自信不等于正确"],
                        "case": "让 AI 介绍一本并不存在的书，它会编出书名、作者和简介，看起来完全合理。"
                    },
                    {
                        "id": "sec-bnd-1-2",
                        "title": "核实三步法：重要信息必须验证",
                        "content": "对重要结论，用「交叉验证、追原始来源、找权威依据」三步核实，不把 AI 输出当最终答案。",
                        "knowledge_points": ["交叉验证", "溯源核实"],
                        "case": "AI 给出某个政策条款，去政府官网原文核对后再使用。"
                    }
                ]
            },
            {
                "id": "ch-bnd-2",
                "title": "数据与隐私：你输入了什么，就可能被记下",
                "content_summary": "你发给 AI 的内容可能被保存用于改进或训练。涉及隐私、机密的信息要有边界。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-bnd-2-1",
                        "title": "输入即交出：不要把机密喂给 AI",
                        "content": "身份证号、银行卡、商业机密、他人隐私等不要直接粘贴给 AI。先脱敏（把数字改成 XX）再使用。",
                        "knowledge_points": ["数据脱敏", "隐私边界"],
                        "case": "要写邮件模板时，把真实的客户手机号改成 138****1234 再交给 AI。"
                    },
                    {
                        "id": "sec-bnd-2-2",
                        "title": "保护自己的数据资产",
                        "content": "对话历史会被保存，敏感资料不进免费公共工具；企业数据用私有化部署或关闭数据存储的版本。",
                        "knowledge_points": ["数据留存", "私有化部署"],
                        "case": "公司内部项目文档使用企业版 AI，避免上传到公共免费工具。"
                    }
                ]
            },
            {
                "id": "ch-bnd-3",
                "title": "依赖与判断力：AI 是副驾，方向盘在你手里",
                "content_summary": "过度依赖 AI 会弱化自己的思考与判断。关键是「先有自己的框架，再用 AI 提效」。",
                "duration_minutes": 20,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-bnd-3-1",
                        "title": "依赖陷阱：越方便越要警惕",
                        "content": "当「让 AI 直接给答案」变成习惯，遇到 AI 不在的场景就会束手无策。保留核心能力，AI 做放大器而非替代品。",
                        "knowledge_points": ["过度依赖", "能力退化"],
                        "case": "先自己起草大纲，再让 AI 扩写；而不是把一句话丢给 AI 等它全包。"
                    },
                    {
                        "id": "sec-bnd-3-2",
                        "title": "批判性使用：AI 建议要过脑",
                        "content": "把 AI 当「见多识广的助手」，它的每个建议都要经过你自己的判断和场景校验再采用。",
                        "knowledge_points": ["批判性思维", "人工审核"],
                        "case": "AI 给的活动方案，对照预算和现场条件逐条评估，删掉不现实的环节。"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-2-writing",
        "title": "AI 写作初体验 — 把想法变成好文案",
        "description": "从一句话描述到完整文章，手把手带你用 AI 写作文案。覆盖扩写、改写、标题、朋友圈、工作文档等高频场景，学完立刻能用。",
        "topic": "入门",
        "difficulty": "beginner",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage2-writing/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-wri-1",
                "title": "一句话起步：把模糊想法变成清晰段落",
                "content_summary": "写作的第一步是描述清楚。用「主题 + 用途 + 读者 + 语气」四要素让 AI 写出可用的初稿。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wri-1-1",
                        "title": "四要素描述法",
                        "content": "告诉 AI 你写什么主题、给谁看、用来干嘛、什么语气，输出质量立刻提升。",
                        "knowledge_points": ["主题", "读者", "用途", "语气"],
                        "case": "「帮我写一段 200 字的产品介绍：给大学生看，用于社团招新推文，语气活泼。」"
                    },
                    {
                        "id": "sec-wri-1-2",
                        "title": "从 1 句话扩到 1 段话",
                        "content": "给 AI 一个核心观点，让它扩写成有论据、有例子、有收尾的完整段落。",
                        "knowledge_points": ["观点", "论据", "例子", "收尾"],
                        "case": "「AI 能帮你省时间，请扩写成一段 150 字的观点阐述，加一个生活例子。」"
                    }
                ]
            },
            {
                "id": "ch-wri-2",
                "title": "改写润色：把普通变出彩",
                "content_summary": "AI 最擅长的不是从零写，而是把已有的内容改得更好：更口语、更专业、更精炼。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wri-2-1",
                        "title": "三种常用改写指令",
                        "content": "「口语化改写」「专业化改写」「精简到一半」三种指令覆盖多数场景。",
                        "knowledge_points": ["口语化", "专业化", "精简"],
                        "case": "把一段书面语通知改成群里的口语提醒，大家一眼看懂。"
                    },
                    {
                        "id": "sec-wri-2-2",
                        "title": "消灭啰嗦：让 AI 帮你瘦身",
                        "content": "给 AI 原文和字数上限，让它保留所有关键信息、删掉废话。",
                        "knowledge_points": ["信息保留", "字数控制"],
                        "case": "把 800 字的报告摘要精简到 150 字，用于邮件正文。"
                    }
                ]
            },
            {
                "id": "ch-wri-3",
                "title": "标题与文案速成",
                "content_summary": "标题决定点击率，文案决定转化。学会用 AI 批量产出多个标题和朋友圈/推文文案再挑选。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wri-3-1",
                        "title": "一次出 10 个标题再挑",
                        "content": "让 AI 围绕同一主题产出多个风格的标题（数字型、悬念型、利益型），人工选最合适的。",
                        "knowledge_points": ["标题风格", "批量生成"],
                        "case": "「为『零基础学 AI』课程写 10 个小红书标题，风格活泼，带 emoji。」"
                    },
                    {
                        "id": "sec-wri-3-2",
                        "title": "朋友圈 / 社群文案模板",
                        "content": "把想表达的事 + 目标动作交给 AI，得到适合朋友圈或社群的分段文案。",
                        "knowledge_points": ["场景文案", "行动号召"],
                        "case": "「我完成了 AI 训练营，帮我写一条朋友圈：分享收获，欢迎朋友来问。」"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-2-media",
        "title": "AI 绘图·办公初体验 — 一张图、一份表、一页 PPT",
        "description": "AI 不只聊天。本课带你体验 AI 画图、做表格、出 PPT 大纲，把「文本 AI」升级成「全能工作台」。",
        "topic": "入门",
        "difficulty": "beginner",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage2-media/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-med-1",
                "title": "AI 绘图入门：描述即创作",
                "content_summary": "用一段描述生成图片，理解「主体 + 风格 + 细节 + 画质」的构图公式。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-med-1-1",
                        "title": "文生图四要素",
                        "content": "主体（画什么）+ 风格（什么画风）+ 细节（光线/颜色/构图）+ 画质（高清/写实）组合成一张好图。",
                        "knowledge_points": ["主体", "风格", "细节", "画质"],
                        "case": "「一只戴眼镜的橘猫，水彩风格，逆光，高清细节丰富。」"
                    },
                    {
                        "id": "sec-med-1-2",
                        "title": "改图与迭代：不满意就重画",
                        "content": "在描述里加词、删词、换风格，反复迭代直到满意；把参考图作为输入让 AI 换风格。",
                        "knowledge_points": ["迭代生成", "风格迁移"],
                        "case": "第一版太写实 → 加「二次元、扁平插画」→ 得到更适合海报的图。"
                    }
                ]
            },
            {
                "id": "ch-med-2",
                "title": "AI 处理表格与数据",
                "content_summary": "把凌乱的数据交给 AI，让它整理成表、做汇总、算指标、解读趋势。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-med-2-1",
                        "title": "文字转表格",
                        "content": "把一段描述性文字让 AI 转成结构化表格，自动补齐字段。",
                        "knowledge_points": ["结构化", "表格生成"],
                        "case": "「把 3 个候选方案对比，转成一张优缺点的对比表格。」"
                    },
                    {
                        "id": "sec-med-2-2",
                        "title": "数据解读与汇总",
                        "content": "给 AI 一份数据摘要，让它算占比、找异常、给结论，再帮忙写成汇报文字。",
                        "knowledge_points": ["数据分析", "结论提炼"],
                        "case": "「本月销售额 12 万、上月 9 万，帮我分析增长来源并写一句话总结。」"
                    }
                ]
            },
            {
                "id": "ch-med-3",
                "title": "AI 出 PPT 大纲与演示思路",
                "content_summary": "PPT 的难点是结构和逻辑，不是排版。让 AI 先出大纲和分页要点，再逐页展开。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-med-3-1",
                        "title": "一句话出大纲",
                        "content": "告诉 AI 汇报主题、时长、听众，让它产出「目录 + 每页标题 + 每页要点」。",
                        "knowledge_points": ["大纲", "分页结构"],
                        "case": "「做一份 10 分钟的项目汇报 PPT，听众是部门领导，先出大纲和每页要点。」"
                    },
                    {
                        "id": "sec-med-3-2",
                        "title": "逐页展开与配图建议",
                        "content": "选中某一页要点，让 AI 扩成演讲词和配图描述，前后衔接自然。",
                        "knowledge_points": ["逐页展开", "演讲词"],
                        "case": "把「数据页」展开成 3 句口头汇报 + 建议配一张趋势图。"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-3-prompt4",
        "title": "万能四段式提示词 — 清晰 / 角色 / 场景 / 限制",
        "description": "提示词质量决定 AI 输出质量。本课精讲万能四段式：任务清晰、角色设定、场景目标、限制格式，配合大量正反例，让你一次写对。",
        "topic": "进阶",
        "difficulty": "intermediate",
        "estimated_hours": 3,
        "lessons": 4,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage3-prompt4/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-p4-1",
                "title": "第一段：清晰的任务描述",
                "content_summary": "告诉 AI「具体做什么、做到什么程度」，把模糊需求翻译成可执行的指令。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-p4-1-1",
                        "title": "动词 + 对象 + 标准",
                        "content": "用「改写（动词）+ 这段文案（对象）+ 控制在 100 字内（标准）」的句式替代「帮我改一下」。",
                        "knowledge_points": ["动词化指令", "量化标准"],
                        "case": "反例「写个文案」→ 正例「为咖啡新品写 3 条小红书文案，每条 80 字内，突出冷萃口感」。"
                    },
                    {
                        "id": "sec-p4-1-2",
                        "title": "一次只做一件事",
                        "content": "提示词越聚焦输出越稳。多任务拆成多条提示词分别执行，避免互相干扰。",
                        "knowledge_points": ["任务拆分", "聚焦"],
                        "case": "「先总结要点」和「再写标题」分两次提问，比一次要两个都做好更可靠。"
                    }
                ]
            },
            {
                "id": "ch-p4-2",
                "title": "第二段：角色设定",
                "content_summary": "给 AI 一个专业身份，输出风格和专业度立刻不同。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-p4-2-1",
                        "title": "常见角色：专家 / 教练 / 审稿人",
                        "content": "「你是 X 领域的专家」「你是我的面试官」「你是严格的审稿人」——角色决定视角和标准。",
                        "knowledge_points": ["角色扮演", "视角切换"],
                        "case": "「你是一位 10 年经验的 HR，帮我审这份简历并指出 3 个可改进点。」"
                    },
                    {
                        "id": "sec-p4-2-2",
                        "title": "角色 + 立场绑定",
                        "content": "角色之外再说明立场和顾虑，让 AI 输出更贴合你的真实处境。",
                        "knowledge_points": ["立场绑定", "场景代入"],
                        "case": "「你是资深运营，但我预算只有 2000 元，方案要控制成本。」"
                    }
                ]
            },
            {
                "id": "ch-p4-3",
                "title": "第三段：场景与目标",
                "content_summary": "说明「用在哪里、给谁看、达到什么效果」，AI 才能给出可落地的方案。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-p4-3-1",
                        "title": "场景决定语言",
                        "content": "同样内容，朋友圈、工作邮件、汇报 PPT 的写法和详略完全不同，告诉 AI 场景。",
                        "knowledge_points": ["场景适配", "表达方式"],
                        "case": "「把这个通知分别写成：群消息（短）、正式邮件（严谨）、海报（吸睛）。」"
                    },
                    {
                        "id": "sec-p4-3-2",
                        "title": "目标决定取舍",
                        "content": "说清最终目的（说服/告知/教育/娱乐），AI 会围绕目标组织内容。",
                        "knowledge_points": ["目标导向", "内容取舍"],
                        "case": "「目标是让读者点击报名，请突出 3 个最吸引人的卖点，弱化细节。」"
                    }
                ]
            },
            {
                "id": "ch-p4-4",
                "title": "第四段：限制与格式",
                "content_summary": "字数、条数、格式、禁用的词——约束越具体，输出越可控。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-p4-4-1",
                        "title": "输出格式约定",
                        "content": "明确要「分点列表 / 表格 / JSON / 标题结构」，AI 严格照做。",
                        "knowledge_points": ["格式指令", "结构化输出"],
                        "case": "「用表格输出 5 个方案，列：方案、优点、缺点、成本。」"
                    },
                    {
                        "id": "sec-p4-4-2",
                        "title": "负面限制：不许做什么",
                        "content": "「不要用『提升』『赋能』这类空词」「不要超过 3 条」「不要编数据」——负面约束同样关键。",
                        "knowledge_points": ["负面约束", "禁用语"],
                        "case": "「写产品卖点，禁用空洞形容词，只写可量化的功能点，最多 3 条。」"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-3-structure",
        "title": "AI 长文本结构化输出 — 让 AI 输出又长又稳",
        "description": "AI 一写长就容易跑偏、重复、虎头蛇尾。本课教你分步引导、格式约束、大纲先行，让 AI 稳定产出高质量长文。",
        "topic": "进阶",
        "difficulty": "intermediate",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage3-structure/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-stu-1",
                "title": "分步引导：让 AI 逐步思考",
                "content_summary": "一次要太多容易糊。拆成「先列要点 → 再展开 → 再润色」逐步引导，输出质量明显提升。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-stu-1-1",
                        "title": "思维链：先计划再执行",
                        "content": "让 AI 先列写作计划/大纲，确认后再展开，避免结构混乱。",
                        "knowledge_points": ["先计划后执行", "思维链"],
                        "case": "「先给我这篇文章的三段式大纲，我确认后再逐段展开。」"
                    },
                    {
                        "id": "sec-stu-1-2",
                        "title": "分段接力：一章节一提问",
                        "content": "长文拆成多个小节分别生成，最后拼装，每个小节质量更高、上下文更稳。",
                        "knowledge_points": ["分段生成", "上下文稳定"],
                        "case": "写 5000 字报告：分别让 AI 写「背景 / 现状 / 问题 / 建议」四段再合并。"
                    }
                ]
            },
            {
                "id": "ch-stu-2",
                "title": "格式约束：结构化输出信手拈来",
                "content_summary": "列表、表格、JSON、Markdown——用格式指令让 AI 输出可直接复用的结构化内容。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-stu-2-1",
                        "title": "表格与列表的妙用",
                        "content": "对比类、清单类内容用表格/列表输出，信息密度高且便于二次加工。",
                        "knowledge_points": ["表格输出", "清单"],
                        "case": "「把 3 款办公软件做成对比表：功能、价格、适合人群、上手难度。」"
                    },
                    {
                        "id": "sec-stu-2-2",
                        "title": "JSON 与代码结构",
                        "content": "需要给程序用或做模板时，让 AI 按固定字段输出 JSON，配合示例更稳定。",
                        "knowledge_points": ["JSON 输出", "字段约束"],
                        "case": "「输出 JSON：{title, summary, tags:[], action}，tags 最多 3 个。」"
                    }
                ]
            },
            {
                "id": "ch-stu-3",
                "title": "长文把控：大纲先行 + 防跑偏",
                "content_summary": "AI 写长文常见「开头惊艳结尾敷衍、中途重复」。用大纲锁定结构，用追问纠偏。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-stu-3-1",
                        "title": "大纲先行，锁死结构",
                        "content": "先让 AI 出带小标题的完整大纲，再按大纲逐节填充，避免内容重复和结构散乱。",
                        "knowledge_points": ["大纲驱动", "结构控制"],
                        "case": "写公众号长文：先定「5 个小标题」，每节 300 字，再统一润色。"
                    },
                    {
                        "id": "sec-stu-3-2",
                        "title": "纠偏与续写",
                        "content": "AI 跑偏时直接指出「第 3 节太啰嗦，重写并控制在 200 字」；结尾弱时让 AI 单独补一个有力收尾。",
                        "knowledge_points": ["定向纠偏", "单独收尾"],
                        "case": "「结尾太平淡，请重写一个带行动号召的收尾，不超过 100 字。」"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-4-weekly",
        "title": "周报自动生成 — 从零散记录到专业周报",
        "description": "周报是最该交给 AI 的重复劳动。本课带你建立「日常记录 → 一键成报 → 风格批量套用」的工作流，每周省下半小时。",
        "topic": "实战",
        "difficulty": "intermediate",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage4-weekly/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-wk-1",
                "title": "素材收集：把工作记录喂给 AI",
                "content_summary": "周报质量取决于素材。平时随手记「做了什么 + 进展 + 卡点」，周末直接喂给 AI。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wk-1-1",
                        "title": "随手记模板",
                        "content": "用「日期 + 事项 + 进展 + 下一步」的模板随手记录，一周后素材齐全。",
                        "knowledge_points": ["工作记录", "待办沉淀"],
                        "case": "「周一：对接客户 A，需求确认，等报价；周三：写方案初稿，完成 60%…」"
                    },
                    {
                        "id": "sec-wk-1-2",
                        "title": "素材转要点",
                        "content": "把零散记录交给 AI，让它先归类成「已完成 / 进行中 / 下周计划」三栏。",
                        "knowledge_points": ["信息归类", "三栏结构"],
                        "case": "「把下面 5 条工作记录归类成：已完成、进行中、下周计划。」"
                    }
                ]
            },
            {
                "id": "ch-wk-2",
                "title": "一键生成周报初稿",
                "content_summary": "用四段式提示词让 AI 把归类后的要点扩写成正式周报，突出成果与数字。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wk-2-1",
                        "title": "周报提示词套用",
                        "content": "「你是运营组长，把以下要点写成周报：每项一句话成果 + 尽量带数字，语气专业。」",
                        "knowledge_points": ["角色 + 成果量化"],
                        "case": "「把『完成 3 篇推文』扩写成『本周完成 3 篇推文，阅读量合计 1.2 万，环比提升 15%』。」"
                    },
                    {
                        "id": "sec-wk-2-2",
                        "title": "数字与成果提炼",
                        "content": "提示 AI 从记录里找可量化的数字，把「做了」升级成「做成了什么效果」。",
                        "knowledge_points": ["量化成果", "数据思维"],
                        "case": "记录里没有数字时，引导 AI 先问你要关键指标再生成。"
                    }
                ]
            },
            {
                "id": "ch-wk-3",
                "title": "风格固化：批量套用你的周报格式",
                "content_summary": "把领导认可的一版周报保存为风格范例，之后每周让 AI 照着写，风格稳定省心。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wk-3-1",
                        "title": "风格示例法",
                        "content": "给 AI 一份你满意的旧周报作为「参照格式」，新周报按同样结构和语气生成。",
                        "knowledge_points": ["Few-shot 示例", "风格迁移"],
                        "case": "「参考下面的上周周报格式，把我这周的新素材写成同样风格。」"
                    },
                    {
                        "id": "sec-wk-3-2",
                        "title": "多条周报批量生成",
                        "content": "一个人带多项目时，给 AI 多个项目的素材，一次生成对应份数的周报。",
                        "knowledge_points": ["批量生成", "多项目"],
                        "case": "「项目 A 和项目 B 的素材各给我，分别生成两份周报。」"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-4-planning",
        "title": "活动策划 AI 工作流 — 从一句话到落地方案",
        "description": "策划活动最耗时的是拆解和物料。本课用 AI 把「一句话需求」变成「可执行的活动方案 + 全套文案物料」。",
        "topic": "实战",
        "difficulty": "intermediate",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage4-planning/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pln-1",
                "title": "需求拆解：一句话到活动方案",
                "content_summary": "用四段式把模糊需求变成结构化方案：目标、人群、玩法、预算、时间。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pln-1-1",
                        "title": "五要素活动简报",
                        "content": "目标（拉新/促活）+ 人群 + 玩法 + 预算 + 时间，先让 AI 补齐这五个要素。",
                        "knowledge_points": ["目标人群", "玩法预算", "时间"],
                        "case": "「做一个线上读书打卡活动：目标促活，人群职场新人，预算 500 元，两周内上线。」"
                    },
                    {
                        "id": "sec-pln-1-2",
                        "title": "方案结构：让 AI 出目录",
                        "content": "让 AI 输出活动方案的完整大纲（背景/目标/玩法/流程/传播/预算/风险），再逐节展开。",
                        "knowledge_points": ["方案大纲", "逐节展开"],
                        "case": "「先给这份活动方案的大纲，我确认后逐节展开。」"
                    }
                ]
            },
            {
                "id": "ch-pln-2",
                "title": "流程设计：宣传 / 执行 / 复盘",
                "content_summary": "活动是时间线工程。让 AI 排好宣传期、执行期、复盘期的关键动作与分工。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pln-2-1",
                        "title": "三阶段执行表",
                        "content": "宣传期（预热/引爆）、执行期（落地/应急）、复盘期（数据/总结）各列关键动作与负责人。",
                        "knowledge_points": ["阶段拆解", "分工排期"],
                        "case": "「把活动排成三阶段执行表：每阶段 3 个关键动作 + 建议时间 + 负责人。」"
                    },
                    {
                        "id": "sec-pln-2-2",
                        "title": "风险预案",
                        "content": "让 AI 列出活动常见风险（报名少/现场乱/设备故障）和对应的预案。",
                        "knowledge_points": ["风险清单", "应急预案"],
                        "case": "「列出线上活动的 5 个风险点和应对预案。」"
                    }
                ]
            },
            {
                "id": "ch-pln-3",
                "title": "文案物料批量产出",
                "content_summary": "一稿多投：宣传文案、海报文案、群通知、主持词一次生成，风格统一。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pln-3-1",
                        "title": "一稿多改",
                        "content": "给 AI 一份活动介绍，让它分别改写成海报文案、公众号推文、社群通知、朋友圈文案。",
                        "knowledge_points": ["多场景改写", "物料复用"],
                        "case": "「把这段活动介绍改写成 4 个版本：海报、推文、群通知、朋友圈。」"
                    },
                    {
                        "id": "sec-pln-3-2",
                        "title": "主持词与FAQ",
                        "content": "让 AI 生成活动开场主持词和常见问题 FAQ，减少临场失误。",
                        "knowledge_points": ["主持词", "FAQ"],
                        "case": "「为活动写 2 分钟开场主持词 + 10 条现场 FAQ。」"
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-4-ppt",
        "title": "PPT 文案批量生成 — 大纲到逐页一次成型",
        "description": "做 PPT 最花时间的是写文案和提炼要点。本课用 AI 从大纲到逐页文案批量产出，直接省下大半制作时间。",
        "topic": "实战",
        "difficulty": "intermediate",
        "estimated_hours": 2,
        "lessons": 3,
        "source": "seed-v3",
        "coverImg": "https://picsum.photos/seed/stage4-ppt/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-ppt-1",
                "title": "大纲先行：让 AI 出目录结构",
                "content_summary": "先有结构再谈美化。让 AI 根据主题、时长、听众产出完整目录与分页标题。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-ppt-1-1",
                        "title": "汇报 PPT 大纲公式",
                        "content": "「主题 + 时长 + 听众 + 结论先行」四要素，让 AI 产出「目录 + 每页标题 + 每页一句话要点」。",
                        "knowledge_points": ["结论先行", "分页结构"],
                        "case": "「做 15 分钟的新人入职培训 PPT，听众是运营岗，结论先行，先出目录。」"
                    },
                    {
                        "id": "sec-ppt-1-2",
                        "title": "按听众调整详略",
                        "content": "领导要看结论、同事要看方法、新人要看流程——告诉 AI 听众来调整每页内容侧重。",
                        "knowledge_points": ["听众分析", "内容侧重"],
                        "case": "「听众是决策层，每页先给结论，展开内容放备注里。」"
                    }
                ]
            },
            {
                "id": "ch-ppt-2",
                "title": "逐页文案与要点提炼",
                "content_summary": "把大纲拆成逐页，让 AI 为每一页提炼标题、要点和演讲备注。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-ppt-2-1",
                        "title": "一页三件套：标题 + 要点 + 备注",
                        "content": "让 AI 为每一页输出「一句标题 + 3 个要点 + 一段演讲备注」，信息层级清晰。",
                        "knowledge_points": ["信息层级", "演讲备注"],
                        "case": "「为『数据分析』这一页输出：标题、3 个要点、100 字演讲备注。」"
                    },
                    {
                        "id": "sec-ppt-2-2",
                        "title": "长文压缩成要点",
                        "content": "把大段报告文字交给 AI，压缩成适合放 PPT 的短语要点，每点一行。",
                        "knowledge_points": ["信息压缩", "一行一要点"],
                        "case": "「把这段 300 字的业务说明压缩成 3 条要点，每条不超过 15 字。」"
                    }
                ]
            },
            {
                "id": "ch-ppt-3",
                "title": "批量生成与润色",
                "content_summary": "目录确认后一次性批量生成全部页面文案，再统一润色语言风格。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-ppt-3-1",
                        "title": "整份批量生成",
                        "content": "把大纲贴给 AI，一次生成整份 PPT 的「每页标题 + 要点 + 备注」表格，复制即用。",
                        "knowledge_points": ["批量生成", "整份输出"],
                        "case": "「按这份大纲一次生成全部 12 页的文案，用表格输出。」"
                    },
                    {
                        "id": "sec-ppt-3-2",
                        "title": "统一风格润色",
                        "content": "全部页面生成后，让 AI 统一术语、统一动词、统一口气，避免风格漂移。",
                        "knowledge_points": ["风格统一", "术语一致"],
                        "case": "「把这份 PPT 文案统一成简洁干练的风格，术语前后一致。」"
                    }
                ]
            }
        ]
    }
]


def merge_into_json(path):
    """把新课程合并进 json，按 id 去重，幂等。"""
    if os.path.exists(path):
        data = json.load(open(path, encoding="utf-8"))
    else:
        data = []
    existing_ids = {c["id"] for c in data}
    added = 0
    for c in NEW_COURSES:
        if c["id"] not in existing_ids:
            data.append(c)
            existing_ids.add(c["id"])
            added += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return added


def seed_db():
    """把新课程 INSERT 进 cms.db courses 表（id 已存在则跳过）。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    existing = {r["id"] for r in conn.execute("SELECT id FROM courses").fetchall()}
    added = 0
    for c in NEW_COURSES:
        if c["id"] in existing:
            continue
        conn.execute(
            "INSERT INTO courses (id, title, description, cover_img, topic, difficulty, "
            "estimated_hours, lessons, progress, is_free, price, source, chapters) "
            "VALUES (?,?,?,?,?,?,?,?,0,?,?,?,?)",
            (
                c["id"], c["title"], c["description"], c["coverImg"], c["topic"],
                c["difficulty"], c["estimated_hours"], c["lessons"],
                c.get("isFree", 1), c.get("price", 0), c.get("source", "seed-v3"),
                json.dumps(c["chapters"], ensure_ascii=False),
            ),
        )
        existing.add(c["id"])
        added += 1
    conn.commit()
    rows = conn.execute("SELECT id, title FROM courses").fetchall()
    total_ch = sum(
        len(json.loads(r["chapters"])) if r["chapters"] else 0
        for r in conn.execute("SELECT chapters FROM courses").fetchall()
    )
    conn.close()
    return added, len(rows), total_ch


if __name__ == "__main__":
    n_json = merge_into_json(os.path.join(PROCESSED, "courses.json"))
    n_enr = merge_into_json(os.path.join(PROCESSED, "enriched_courses.json"))
    n_db, total, total_ch = seed_db()
    print(f"courses.json +{n_json}  enriched_courses.json +{n_enr}  cms.db +{n_db}")
    print(f"课程总数: {total}  总章节数: {total_ch}")
