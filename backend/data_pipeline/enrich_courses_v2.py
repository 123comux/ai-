"""课程丰富 v2：加深现有 13 门课 + 新增 5 门实战项目课。

- DEEPEN：给现有课程追加新章节（每门 1~2 章，每章 2 小节），并给单小节回顾章补足 2 小节，
  同步更新 estimated_hours / lessons / duration。
- PROJECT_COURSES：5 门「从 0 到 1 做作品」实战课，对应 projects.json 的 project-0~4。

幂等：章节 id / 课程 id 已存在则跳过，可重复运行。
同时合并进 courses.json 与 enriched_courses.json。
"""
import json
import os

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BACKEND, "data", "processed")


# ============================================================
# 加深：每门课追加的章节（chapters 列表）
# ============================================================

DEEPEN = {
    "stage-1-cognition": {
        "estimated_hours": 6,
        "chapters": [
            {
                "id": "ch-cog-5",
                "title": "AI 的昨天、今天与明天：大模型到底是什么",
                "content_summary": "从下围棋到写文章，看懂 AI 的进化路线，理解大模型「概率生成」的本质，知道它到底能做什么、不能做什么。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-cog-5-1",
                        "title": "从下围棋到写文章：AI 的进化路线",
                        "content": "从规则系统、机器学习到深度学习、生成式大模型的演进脉络，解释「训练—预测」的基本原理，让用户理解为什么 AI 能「理解」语言。",
                        "knowledge_points": ["深度学习", "大模型", "生成式AI"],
                        "case": "2016 年 AlphaGo 战胜李世石 → 2023 年 ChatGPT 爆火 → 现在人人可用，这条路线只走了 7 年。"
                    },
                    {
                        "id": "sec-cog-5-2",
                        "title": "大模型能做什么、不能做什么",
                        "content": "大模型擅长语言理解、内容生成、信息整理；不擅长精确计算、实时信息、深度逻辑推理。建立「概率生成」而非「理解真知」的认知。",
                        "knowledge_points": ["大模型能力边界", "概率生成"],
                        "case": "大模型能写 1000 字文章却可能算不对 17×23 的精确答案——因为它本质上是在「猜下一个词」。"
                    }
                ]
            },
            {
                "id": "ch-cog-6",
                "title": "AI 时代的能力地图：你要学会的 5 项核心能力",
                "content_summary": "AI 时代最重要的不是和 AI 比会什么，而是知道哪些事交给 AI、哪些事自己来。人负责判断，AI 负责执行。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-cog-6-1",
                        "title": "人机协作的新分工",
                        "content": "AI 时代最重要的不是和 AI 比会什么，而是知道哪些事交给 AI、哪些事自己来。人负责判断与决策，AI 负责执行与初稿。",
                        "knowledge_points": ["人机分工", "决策权"],
                        "case": "同样一句「帮我做个方案」，会分工的人先想清楚目标再让 AI 出稿，结果质量完全不同。"
                    },
                    {
                        "id": "sec-cog-6-2",
                        "title": "你的五阶段学习路线图",
                        "content": "认知→入门→进阶→实战→熟练，每一阶段对应的能力目标和产出物，让用户带着地图开始学习。",
                        "knowledge_points": ["学习路径", "能力目标"],
                        "case": "阶段一建立认知，阶段二会用工具，阶段三写对提示词，阶段四做出成果，阶段五形成工作流。"
                    }
                ]
            }
        ],
        "extra_sections": {
            "ch-cog-4": [
                {
                    "id": "sec-cog-4-2",
                    "title": "认知自查清单",
                    "content": "用一份清单检验自己是否建立了正确认知：能说出 AI 的 3 个能做/3 个不能做，知道什么时候该用、什么时候不该用 AI。",
                    "knowledge_points": ["自查", "认知检验"],
                    "case": "对着清单逐项打勾，有拿不准的回到对应章节复习。"
                }
            ]
        }
    },
    "stage-2-basics": {
        "estimated_hours": 8,
        "chapters": [
            {
                "id": "ch-basic-6",
                "title": "更多 AI 工具全家桶：从三个到一整个工具箱",
                "content_summary": "认识更多国产大模型和垂直场景工具，建立「工具箱」思维：不同任务换不同工具，而不是一个工具走天下。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-basic-6-1",
                        "title": "国产大模型横向对比",
                        "content": "通义千问、文心一言、讯飞星火、腾讯混元等主流国产大模型的特点与适用场景，教用户按需求选工具。",
                        "knowledge_points": ["国产大模型", "工具选型"],
                        "case": "文档总结用通义、长文写作用 Kimi、多模态用文心——不同任务换不同工具。"
                    },
                    {
                        "id": "sec-basic-6-2",
                        "title": "垂直场景工具：翻译/会议/笔记/作图",
                        "content": "介绍各垂直场景的 AI 工具（翻译、会议纪要、录音转写、思维导图、设计出图），建立「工具箱」思维。",
                        "knowledge_points": ["垂直工具", "工具箱思维"],
                        "case": "开会用「通义听悟」自动转写，读论文用翻译插件，把杂活交给对应工具。"
                    }
                ]
            },
            {
                "id": "ch-basic-7",
                "title": "用好 AI 的三个好习惯",
                "content_summary": "记录复盘、交叉验证、建立工具箱——三个能长期拉开差距的使用习惯，让你从「会用」到「用好」。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-basic-7-1",
                        "title": "记录与复盘：让 AI 越用越懂你",
                        "content": "建立使用记录（什么问题、用了什么提示词、结果如何），定期复盘优化自己的提示词。",
                        "knowledge_points": ["使用记录", "复盘"],
                        "case": "把每次「调好的提示词」存进备忘录，一周后你就有自己的提示词小库。"
                    },
                    {
                        "id": "sec-basic-7-2",
                        "title": "交叉验证：重要信息多方核实",
                        "content": "重要事实类问题用两个以上工具互查、追原始来源，避免单点错误。",
                        "knowledge_points": ["交叉验证", "事实核查"],
                        "case": "问「2024 年大学生就业率」——用豆包、Kimi 各问一遍再核对官方来源。"
                    }
                ]
            }
        ],
        "extra_sections": {
            "ch-basic-5": [
                {
                    "id": "sec-basic-5-2",
                    "title": "工具实操自测",
                    "content": "三道自测题：用 AI 写一份通知、生成一张图、总结一篇长文，检验工具熟练度。",
                    "knowledge_points": ["实操自测", "工具熟练"],
                    "case": "30 分钟内独立完成三件小任务，作为入门阶段通过的标志。"
                }
            ]
        }
    },
    "stage-3-advanced": {
        "estimated_hours": 10,
        "chapters": [
            {
                "id": "ch-adv-6",
                "title": "提示词翻车现场：7 大常见错误与修正",
                "content_summary": "把最常见的提示词错误逐个拆解，配修正句式，让你一眼看出自己写的提示词哪里会翻车。",
                "duration_minutes": 40,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-adv-6-1",
                        "title": "一次要太多、太模糊、没限制",
                        "content": "拆解提示词最常见的三个错误：需求模糊、一次要多项、缺少格式/字数限制，并给出对应修正句式。",
                        "knowledge_points": ["模糊指令", "任务拆分", "输出限制"],
                        "case": "「帮我写个总结」→「把这段 500 字会议记录总结成 5 条要点，每条不超过 20 字」。"
                    },
                    {
                        "id": "sec-adv-6-2",
                        "title": "给错角色、没给示例、不纠正",
                        "content": "拆解另外四个错误：角色给错、缺少示例、AI 输出差但不追问纠正、把幻觉当真。",
                        "knowledge_points": ["角色设定", "示例输入", "追问纠错"],
                        "case": "让 AI 写演讲稿却忘了说听众是谁——补一句「听众是大一新生，语言要通俗」结果完全不同。"
                    }
                ]
            },
            {
                "id": "ch-adv-7",
                "title": "提示词库与模板管理：让你的好提示词沉淀下来",
                "content_summary": "把验证过的好提示词按四类沉淀成库、统一命名、持续迭代，让一次调优成为长期资产。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-adv-7-1",
                        "title": "四类提示词库的搭建",
                        "content": "按学习/办公/写作/生活四类整理已验证的提示词，统一命名（用途+版本），方便随时调用。",
                        "knowledge_points": ["知识管理", "模板沉淀"],
                        "case": "命名规则「周报模板 v3 · 运营岗 · 量化版」——一年后你还能秒懂这条模板是干嘛的。"
                    },
                    {
                        "id": "sec-adv-7-2",
                        "title": "模板迭代：给提示词做版本管理",
                        "content": "每次调优后另存为新版本，记录改动点和效果，让提示词库持续进化。",
                        "knowledge_points": ["版本迭代", "持续优化"],
                        "case": "v1 周报模板没人看，v2 加了「每条带数据」后领导反馈明显变好。"
                    }
                ]
            }
        ],
        "extra_sections": {
            "ch-adv-5": [
                {
                    "id": "sec-adv-5-2",
                    "title": "提示词改错练习",
                    "content": "给出 3 条错误提示词，让用户用四段式框架重写，对照参考答案检查差距。",
                    "knowledge_points": ["改错练习", "框架应用"],
                    "case": "把「写个活动方案」改写成含角色/场景/限制的完整提示词。"
                }
            ]
        }
    },
    "stage-4-practice": {
        "estimated_hours": 12,
        "chapters": [
            {
                "id": "ch-prac-6",
                "title": "AI 读书笔记与知识管理：把输入变成你的知识库",
                "content_summary": "用「喂全文→提炼结构→输出笔记」三步工作流读书，再把笔记拆成知识卡片对抗遗忘。",
                "duration_minutes": 45,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-prac-6-1",
                        "title": "三步读书笔记工作流",
                        "content": "喂全文→AI 提炼结构与金句→结合自己的理解输出笔记，形成「读—理—写」闭环。",
                        "knowledge_points": ["读书笔记", "信息提炼"],
                        "case": "读完《被讨厌的勇气》，让 AI 先出全书结构，再逐章追问重点，最后结合自己经历写 300 字感悟。"
                    },
                    {
                        "id": "sec-prac-6-2",
                        "title": "知识卡片与复习计划",
                        "content": "把笔记拆成知识卡片，用 AI 生成复习问题和间隔复习计划，对抗遗忘。",
                        "knowledge_points": ["知识卡片", "间隔复习"],
                        "case": "让 AI 基于你的笔记生成 10 道自测题，每周抽 3 题自测。"
                    }
                ]
            },
            {
                "id": "ch-prac-7",
                "title": "实战心法：判断这个任务该不该交给 AI",
                "content_summary": "不是所有任务都适合 AI。用「任务四象限 + 人机协作决策树」快速判断，把 AI 用在刀刃上。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-prac-7-1",
                        "title": "任务四象限：明确 AI 的用武之地",
                        "content": "按「重要度 × 风险度」划分任务：低风险重复任务放心交给 AI，高风险重要任务 AI 辅助+人审核。",
                        "knowledge_points": ["任务分类", "风险意识"],
                        "case": "群公告文案（低风险）直接让 AI 写；给客户的对账邮件（高风险）让 AI 起草但逐字人工核对。"
                    },
                    {
                        "id": "sec-prac-7-2",
                        "title": "人机协作决策树",
                        "content": "一套「要不要用 AI」的快速判断流程：有标准答案吗→容错度高吗→资料齐全吗→AI 能加速吗。",
                        "knowledge_points": ["决策树", "人机协作"],
                        "case": "计算工资（有标准答案、低容错）别交给 AI；写宣传文案（无标准答案、高容错）放心交给 AI。"
                    }
                ]
            }
        ],
        "extra_sections": {
            "ch-prac-5": [
                {
                    "id": "sec-prac-5-2",
                    "title": "工具箱检验：三个真实场景演练",
                    "content": "用周报/策划/PPT 三个场景各出一题，检验实战能力是否达到阶段目标。",
                    "knowledge_points": ["实战演练", "场景检验"],
                    "case": "在三个场景中各跑一遍完整 AI 工作流，检查产出物是否符合要求。"
                }
            ]
        }
    },
    "stage-5-mastery": {
        "estimated_hours": 10,
        "chapters": [
            {
                "id": "ch-mas-5",
                "title": "AI 工具组合拳：多工具串联完成复杂任务",
                "content_summary": "把复杂任务拆成「生成—整理—设计—呈现」多环节，每环用最合适的工具，用提示词把各环节衔接起来。",
                "duration_minutes": 45,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-mas-5-1",
                        "title": "一条龙工作流设计",
                        "content": "把复杂任务拆成「生成—整理—设计—呈现」多环节，每环用最合适的工具，用提示词把各环节衔接起来。",
                        "knowledge_points": ["工作流设计", "多工具协作"],
                        "case": "做一份调研汇报：AI 查资料→AI 整理成表格→AI 配图→AI 出 PPT 文案，环环相扣。"
                    },
                    {
                        "id": "sec-mas-5-2",
                        "title": "组合拳案例：从想法到发布会",
                        "content": "完整演示一个端到端多工具项目（校园 AI 活动策划），展示每个环节的工具与提示词。",
                        "knowledge_points": ["全链路实战", "案例拆解"],
                        "case": "一句话需求→Kimi 出方案→即梦出海报→AI 出演讲词→PPT 生成，全程不到 1 小时。"
                    }
                ]
            },
            {
                "id": "ch-mas-6",
                "title": "量化你的 AI 收益：让效率看得见",
                "content_summary": "用时间审计找到提效点，把验证有效的 AI 工作流固化成模板库+清单，量化省时与复用率。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-mas-6-1",
                        "title": "时间审计：找到你的 AI 提效点",
                        "content": "记录一周每天的任务耗时，找出重复性高、耗时长的环节，优先用 AI 替代。",
                        "knowledge_points": ["时间审计", "效率分析"],
                        "case": "一周发现写通知花了 3 小时→做成提示词模板→下周只花 20 分钟。"
                    },
                    {
                        "id": "sec-mas-6-2",
                        "title": "建立并迭代你的效率系统",
                        "content": "把验证有效的 AI 工作流固化成「模板库+清单」，定期复盘指标（省时、质量、复用率）持续优化。",
                        "knowledge_points": ["效率系统", "持续迭代"],
                        "case": "每月花 30 分钟复盘：哪些模板在用、哪些该淘汰、哪些新场景值得做模板。"
                    }
                ]
            }
        ]
    },
    "stage-1-boundary": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-bnd-4",
                "title": "AI 伦理与合规：用 AI 的边界意识",
                "content_summary": "版权、商用、学术诚信——用 AI 生成内容也有红线。学会分辨哪些能直接用、哪些需要人工再创作。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-bnd-4-1",
                        "title": "版权与原创：AI 生成内容的使用边界",
                        "content": "AI 生成内容涉及的版权、署名与商用问题；哪些场景可以直接用，哪些需人工再创作，避免侵权风险。",
                        "knowledge_points": ["版权意识", "商用边界"],
                        "case": "用 AI 生成的图片商用前，确认所用平台对商用与版权的条款。"
                    },
                    {
                        "id": "sec-bnd-4-2",
                        "title": "学术诚信：学生与职场人的红线",
                        "content": "作业、论文、报告场景下 AI 的使用边界：可辅助不可代做，引用 AI 内容需说明，避免学术不端。",
                        "knowledge_points": ["学术诚信", "使用规范"],
                        "case": "论文用 AI 润色语句可以，直接代写核心章节并隐瞒即属学术不端。"
                    }
                ]
            }
        ]
    },
    "stage-2-writing": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-wri-4",
                "title": "从文案到长文：AI 写作进阶实战",
                "content_summary": "短文案之外，AI 也能写长文。掌握「先骨架后血肉、分段扩写、风格统一」三步，稳稳产出千字文章。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wri-4-1",
                        "title": "先骨架后血肉：长文三段式",
                        "content": "定主题→出大纲→逐段展开，让 AI 先给标题结构再逐节填充，避免长文跑题。",
                        "knowledge_points": ["大纲先行", "逐段展开"],
                        "case": "写公众号文章：先让 AI 出 5 个小标题，确认后再每节 300 字扩写。"
                    },
                    {
                        "id": "sec-wri-4-2",
                        "title": "风格统一与发布前检查",
                        "content": "长文完成后统一术语与语气、检查逻辑断层，让 AI 扮演审稿人挑毛病，再定稿发布。",
                        "knowledge_points": ["风格统一", "审稿检查"],
                        "case": "让 AI 以「挑剔的编辑」身份指出文章 3 处问题，改完再发布。"
                    }
                ]
            }
        ]
    },
    "stage-2-media": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-med-4",
                "title": "AI 音视频与演示进阶",
                "content_summary": "从静态到动态：用 AI 生成视频脚本与配音，配合一键成片工具，把「文字→声音→视频」链路打通。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-med-4-1",
                        "title": "AI 配音与视频脚本",
                        "content": "用 AI 生成视频脚本、配音文案，配合免费配音工具产出口播视频，掌握「文字→声音→视频」的链路。",
                        "knowledge_points": ["视频脚本", "AI 配音"],
                        "case": "写一段 60 秒产品口播稿，用 AI 配音转语音，再配图成片。"
                    },
                    {
                        "id": "sec-med-4-2",
                        "title": "一键成片的思路",
                        "content": "剪辑软件 AI 功能、图文成片、自动字幕等工具的使用思路，降低视频制作门槛。",
                        "knowledge_points": ["一键成片", "自动字幕"],
                        "case": "用剪映「图文成片」把一篇科普文章直接转成带配音和字幕的视频。"
                    }
                ]
            }
        ]
    },
    "stage-3-prompt4": {
        "estimated_hours": 4,
        "chapters": [
            {
                "id": "ch-p4-5",
                "title": "四段式组合实战：一次写对复杂需求",
                "content_summary": "复杂任务拆成多个四段式提示词依次执行，再通过微调迭代让输出贴近预期，最后把好版本存进提示词库。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-p4-5-1",
                        "title": "复杂任务的分段组合",
                        "content": "把复杂需求拆成多个四段式提示词依次执行，每个提示词聚焦一个子任务，最后拼装成完整成果。",
                        "knowledge_points": ["任务分解", "提示词组合"],
                        "case": "求职信=角色段+任务段+场景段+限制段，拆成「写开头」「写经历」「写结尾」三步完成。"
                    },
                    {
                        "id": "sec-p4-5-2",
                        "title": "微调与迭代：让输出贴近你的预期",
                        "content": "基于 AI 初稿逐条反馈「哪里不对、怎么改」，两到三轮微调后得到满意结果，记录最终版本进库。",
                        "knowledge_points": ["迭代微调", "反馈机制"],
                        "case": "「第二段太空，请用 STAR 结构重写经历」「再压缩到 80 字」——两轮后得到可用版本。"
                    }
                ]
            }
        ]
    },
    "stage-3-structure": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-stu-4",
                "title": "长文审校与质量提升",
                "content_summary": "用一致性检查清单逐项核对 AI 长文，再让 AI 扮演审稿人自我挑错，双保险把质量拉满。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-stu-4-1",
                        "title": "一致性检查清单",
                        "content": "检查长文的事实一致性、术语统一、逻辑连贯、数据准确，用清单逐项核对 AI 输出。",
                        "knowledge_points": ["一致性", "质量清单"],
                        "case": "全文出现两处「2023 年」一处「2022 年」——让 AI 统一为最新版本并标注。"
                    },
                    {
                        "id": "sec-stu-4-2",
                        "title": "让 AI 自我审校",
                        "content": "让 AI 以审稿人身份对长文挑错、指出冗余、建议删改，人再最后拍板，双保险提升质量。",
                        "knowledge_points": ["自我审校", "双重校验"],
                        "case": "「你是一名严格的编辑，请指出这篇 2000 字文章 3 处逻辑问题和 2 处冗余段落。」"
                    }
                ]
            }
        ]
    },
    "stage-4-weekly": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-wk-4",
                "title": "周报进阶：向上汇报的艺术",
                "content_summary": "好周报不只是记录，更是汇报。学会结论先行、量化贡献，并把周报转化成 3 分钟口头汇报。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-wk-4-1",
                        "title": "结论先行：让领导 30 秒看到重点",
                        "content": "周报顶部放「本周核心结论」，每条成果量化、突出贡献，用 AI 辅助提炼。",
                        "knowledge_points": ["结论先行", "成果量化"],
                        "case": "「本周完成 3 件事」→「本周超额完成：上线 2 个功能，转化率提升 12%」。"
                    },
                    {
                        "id": "sec-wk-4-2",
                        "title": "从周报到周会口头汇报",
                        "content": "把周报浓缩成 3 分钟口头汇报框架（做了什么/遇到什么/要什么支持），AI 帮你提炼口语稿。",
                        "knowledge_points": ["口头汇报", "结构化表达"],
                        "case": "让 AI 把 500 字周报转成 3 句口头要点：成果 1 句、卡点 1 句、求助 1 句。"
                    }
                ]
            }
        ]
    },
    "stage-4-planning": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-pln-4",
                "title": "活动复盘：用数据说话",
                "content_summary": "活动结束不是终点。用五维度复盘模板整理数据、归因改进，把经验变成下一场的资产。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pln-4-1",
                        "title": "复盘模板：五个维度找差距",
                        "content": "目标达成率、参与度、成本、口碑、流程顺畅度五个维度，让 AI 帮你整理数据与结论。",
                        "knowledge_points": ["复盘框架", "数据整理"],
                        "case": "活动报名 200 人实到 150 人——让 AI 按五维度出复盘草稿，再补充事实。"
                    },
                    {
                        "id": "sec-pln-4-2",
                        "title": "归因与迭代：把经验变成下一场的资产",
                        "content": "区分可控/不可控因素，把有效经验沉淀成下一场活动的「优化清单」。",
                        "knowledge_points": ["归因分析", "经验沉淀"],
                        "case": "报名转化低是因为宣传启动晚（可控）而非天气（不可控）——下次提前 3 天预热。"
                    }
                ]
            }
        ]
    },
    "stage-4-ppt": {
        "estimated_hours": 3,
        "chapters": [
            {
                "id": "ch-ppt-4",
                "title": "PPT 视觉与演示：从能看到好看",
                "content_summary": "内容之外，用 AI 解决配图、版式与演示：生成配图描述、优化排版建议、准备讲稿与 Q&A 预案。",
                "duration_minutes": 25,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-ppt-4-1",
                        "title": "AI 配图与版式建议",
                        "content": "用 AI 生成配图描述、给出版式/配色/字体的优化建议，让 PPT 摆脱「白底黑字」。",
                        "knowledge_points": ["配图生成", "版式设计"],
                        "case": "让 AI 为「数据分析」页生成配图描述「柱状图配抽象插画，蓝白主色调」，再用即梦出图。"
                    },
                    {
                        "id": "sec-ppt-4-2",
                        "title": "演示辅助：讲稿与 Q&A 准备",
                        "content": "让 AI 生成每页演讲备注、可能的提问与回答预案，提升临场表现。",
                        "knowledge_points": ["演讲讲稿", "Q&A 预案"],
                        "case": "让 AI 扮演挑剔听众提 5 个刁钻问题，提前准备应答。"
                    }
                ]
            }
        ]
    }
}


# ============================================================
# 新增：5 门实战项目课（对应 projects.json project-0~4）
# ============================================================

PROJECT_COURSES = [
    {
        "id": "project-course-1",
        "title": "作品实战：从 0 到 1 做出你的 AI 周报工作流",
        "description": "这是你的第一个作品课。跟练完成「随手记录 → 一键成报 → 风格固化」的完整周报自动化工作流，最终产出一份标准周报 + 可复用提示词模板，直接进入你的作品集。",
        "topic": "实战",
        "difficulty": "beginner",
        "estimated_hours": 3,
        "source": "project-course",
        "coverImg": "https://picsum.photos/seed/project-course-1/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pc1-1",
                "title": "第一步：搭建你的周报素材库",
                "content_summary": "周报质量取决于素材。先建立随手记模板，再让 AI 帮你归类，素材齐了周报就成功了一半。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc1-1-1",
                        "title": "随手记模板：让素材不丢失",
                        "content": "用「日期+事项+进展+下一步」四栏随手记录一周工作，这一步决定周报质量。",
                        "knowledge_points": ["工作记录", "待办沉淀"],
                        "case": "「周一：对接客户 A，需求确认，等报价；周三：方案初稿 60%…」"
                    },
                    {
                        "id": "sec-pc1-1-2",
                        "title": "素材归类：交给 AI 分三栏",
                        "content": "把零散记录交给 AI 归类成「已完成/进行中/下周计划」，产出素材清单。",
                        "knowledge_points": ["信息归类", "三栏结构"],
                        "case": "「把下面 5 条记录归类：已完成、进行中、下周计划。」"
                    }
                ]
            },
            {
                "id": "ch-pc1-2",
                "title": "第二步：一键成报的提示词工程",
                "content_summary": "用四段式写周报提示词：角色 + 任务 + 格式 + 限制，并引导 AI 提炼可量化成果。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc1-2-1",
                        "title": "周报提示词模板 v1",
                        "content": "用四段式写周报提示词：角色（运营/项目负责人）+任务（把要点写成周报）+格式（成果量化）+限制（每项一句话）。",
                        "knowledge_points": ["提示词模板", "角色设定"],
                        "case": "「你是项目负责人，把以下要点写成周报：每项成果带数字，语气专业。」"
                    },
                    {
                        "id": "sec-pc1-2-2",
                        "title": "数字与成果提炼",
                        "content": "提示 AI 从记录找可量化数据，把「做了」升级成「做成了什么效果」，并让 AI 先追问缺的关键数字。",
                        "knowledge_points": ["量化成果", "数据思维"],
                        "case": "「本周完成 3 篇推文」→「完成 3 篇推文，阅读量合计 1.2 万，环比 +15%」。"
                    }
                ]
            },
            {
                "id": "ch-pc1-3",
                "title": "第三步：验收迭代，固化你的作品",
                "content_summary": "按检查清单验收周报质量，把验证过的提示词固化为模板，周报成品存进作品集。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc1-3-1",
                        "title": "验收检查清单",
                        "content": "用清单核对周报：结论是否靠前、成果是否量化、格式是否一致、有无错别字。",
                        "knowledge_points": ["验收清单", "质量检查"],
                        "case": "逐项勾选后把不合格处丢回 AI 重写。"
                    },
                    {
                        "id": "sec-pc1-3-2",
                        "title": "固化模板 & 存进作品集",
                        "content": "把最终验证过的提示词存为「周报模板 v1」备用，周报成品导出存进作品集。",
                        "knowledge_points": ["模板固化", "作品交付"],
                        "case": "每周只改素材，20 分钟出周报，作品集里多一份可展示的成果。"
                    }
                ]
            }
        ]
    },
    {
        "id": "project-course-2",
        "title": "作品实战：AI 活动策划全流程",
        "description": "用 AI 从一句话需求完成一场完整活动策划：需求拆解 → 方案框架 → 流程与物料批量产出，最终交付一份可直接执行的策划方案文档。",
        "topic": "实战",
        "difficulty": "intermediate",
        "estimated_hours": 4,
        "source": "project-course",
        "coverImg": "https://picsum.photos/seed/project-course-2/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pc2-1",
                "title": "第一步：需求拆解成方案框架",
                "content_summary": "用五要素简报把一句话需求结构化，再让 AI 输出方案完整大纲，确认后逐节展开。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc2-1-1",
                        "title": "五要素简报",
                        "content": "目标+人群+玩法+预算+时间五要素补齐，让 AI 帮你结构化需求。",
                        "knowledge_points": ["目标人群", "玩法预算"],
                        "case": "「线上读书打卡：目标促活、人群职场新人、预算 500、两周上线」"
                    },
                    {
                        "id": "sec-pc2-1-2",
                        "title": "让 AI 出方案目录",
                        "content": "让 AI 输出方案完整大纲（背景/目标/玩法/流程/传播/预算/风险），确认后再逐节展开。",
                        "knowledge_points": ["方案大纲", "逐节展开"],
                        "case": "「先出这份活动方案的大纲，我确认后逐节展开。」"
                    }
                ]
            },
            {
                "id": "ch-pc2-2",
                "title": "第二步：流程设计与物料批量产出",
                "content_summary": "把方案落成三阶段执行表，再一稿多改批量产出海报、推文、群通知等全套物料。",
                "duration_minutes": 40,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc2-2-1",
                        "title": "三阶段执行表",
                        "content": "宣传/执行/复盘三阶段各列关键动作+时间+负责人，形成可执行计划。",
                        "knowledge_points": ["阶段拆解", "分工排期"],
                        "case": "「把活动排成三阶段执行表：每阶段 3 个动作+建议时间+负责人。」"
                    },
                    {
                        "id": "sec-pc2-2-2",
                        "title": "一稿多改物料",
                        "content": "给 AI 一份活动介绍，改写海报/推文/群通知/朋友圈四版文案，风格统一。",
                        "knowledge_points": ["多场景改写", "物料复用"],
                        "case": "「把这段介绍改写成 4 个版本：海报、推文、群通知、朋友圈。」"
                    }
                ]
            },
            {
                "id": "ch-pc2-3",
                "title": "第三步：整合成稿，交付你的方案",
                "content_summary": "把各环节内容拼装成完整方案，补风险预案，按「可执行性」验收后作为作品交付。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc2-3-1",
                        "title": "方案整合与风险预案",
                        "content": "把各环节内容拼装成完整方案，补风险预案与应急预案。",
                        "knowledge_points": ["方案整合", "应急预案"],
                        "case": "列出 5 个风险点+对应预案，附在方案末尾。"
                    },
                    {
                        "id": "sec-pc2-3-2",
                        "title": "验收与作品化",
                        "content": "按「可执行性」验收方案（别人拿到能照做），整理成作品集里的完整文档。",
                        "knowledge_points": ["可执行性", "作品交付"],
                        "case": "让一个没参与的人读方案 5 分钟能复述怎么做，就算合格。"
                    }
                ]
            }
        ]
    },
    {
        "id": "project-course-3",
        "title": "作品实战：AI 求职竞争力提升",
        "description": "用 AI 完成一份高质量求职材料：简历优化 → 岗位分析 → 模拟面试 → 面试手册，把求职准备变成可交付的作品集。",
        "topic": "实战",
        "difficulty": "intermediate",
        "estimated_hours": 4,
        "source": "project-course",
        "coverImg": "https://picsum.photos/seed/project-course-3/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pc3-1",
                "title": "第一步：简历诊断与优化",
                "content_summary": "让 AI 以 HR 视角诊断简历问题，用 STAR 结构量化改写每条经历。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc3-1-1",
                        "title": "HR 视角诊断",
                        "content": "把简历给 AI，让它以 HR 视角指出问题（缺量化、描述笼统、亮点不突出）。",
                        "knowledge_points": ["简历诊断", "HR 视角"],
                        "case": "AI 指出「缺乏量化成果」「经历描述太笼统」并给出修改建议。"
                    },
                    {
                        "id": "sec-pc3-1-2",
                        "title": "量化改写：把经历写成成果",
                        "content": "用 STAR 结构让 AI 重写每条经历，补数字与结果。",
                        "knowledge_points": ["STAR 结构", "量化改写"],
                        "case": "「负责社团招新」→「策划并执行招新，报名 200 人，转化率 60%」。"
                    }
                ]
            },
            {
                "id": "ch-pc3-2",
                "title": "第二步：岗位分析与模拟面试",
                "content_summary": "拆解目标岗位 JD 找差距，再让 AI 扮演面试官实战演练并复盘。",
                "duration_minutes": 40,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc3-2-1",
                        "title": "目标岗位 JD 拆解",
                        "content": "让 AI 分析目标岗位 JD：核心要求、打分点、你与岗位的差距。",
                        "knowledge_points": ["JD 分析", "能力差距"],
                        "case": "把招聘 JD 贴给 AI，输出「岗位要什么/你缺什么/怎么补」三栏。"
                    },
                    {
                        "id": "sec-pc3-2-2",
                        "title": "模拟面试实战",
                        "content": "让 AI 扮演面试官模拟面试（自我介绍/行为面试/追问），并给出改进反馈。",
                        "knowledge_points": ["模拟面试", "结构化回答"],
                        "case": "设定「某互联网公司产品岗面试官」，进行 15 分钟模拟并复盘。"
                    }
                ]
            },
            {
                "id": "ch-pc3-3",
                "title": "第三步：沉淀面试手册，交付作品",
                "content_summary": "整理高频问题 STAR 答案，打包成完整求职材料包，随时可投递。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc3-3-1",
                        "title": "高频问题清单与 STAR 答案",
                        "content": "让 AI 出该岗位 10 个高频问题，你逐一用 STAR 准备答案，AI 帮忙打磨。",
                        "knowledge_points": ["问题清单", "STAR 答案"],
                        "case": "「产品岗最常问的 10 个问题+每题 STAR 框架答案模板」"
                    },
                    {
                        "id": "sec-pc3-3-2",
                        "title": "求职作品包整理",
                        "content": "把优化后的简历、面试手册、模拟面复盘整理成一份完整求职材料包。",
                        "knowledge_points": ["作品整理", "求职交付"],
                        "case": "材料包=简历+面试手册+自我介绍 1 分钟版，随时可投递。"
                    }
                ]
            }
        ]
    },
    {
        "id": "project-course-4",
        "title": "作品实战：搭建你的个人 AI 提示词库",
        "description": "系统整理学到的提示词技巧，建一个分类清晰、每条验证过的个人提示词库，最终产出「我的 AI 提示词手册」，长期复用。",
        "topic": "实战",
        "difficulty": "beginner",
        "estimated_hours": 3,
        "source": "project-course",
        "coverImg": "https://picsum.photos/seed/project-course-4/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pc4-1",
                "title": "第一步：盘点与分类你的提示词",
                "content_summary": "把散落的提示词按四类整理、统一命名与字段规范，让库从第一天就可检索。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc4-1-1",
                        "title": "四类整理法",
                        "content": "学习/办公/写作/生活四类盘点已有提示词，同类合并、去重。",
                        "knowledge_points": ["分类整理", "知识盘点"],
                        "case": "把备忘录里 20 条零散提示词分成四类，同类并一条。"
                    },
                    {
                        "id": "sec-pc4-1-2",
                        "title": "命名与模板规范",
                        "content": "统一命名「用途+场景+版本」，固定模板字段（角色/任务/格式/限制），便于检索调用。",
                        "knowledge_points": ["命名规范", "模板字段"],
                        "case": "「读书笔记模板 v2 · 非虚构 · 三栏式」"
                    }
                ]
            },
            {
                "id": "ch-pc4-2",
                "title": "第二步：打磨与验证每条提示词",
                "content_summary": "每条提示词配正反例、跑多次验证稳定性，确保能真正复用。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc4-2-1",
                        "title": "正反例打磨",
                        "content": "给每条提示词配一个反例（没写好会怎样）和正例（完整四段式），让模板更健壮。",
                        "knowledge_points": ["正反例", "模板打磨"],
                        "case": "反例「总结文章」→ 正例「用 5 条要点总结，每条带原文页码」"
                    },
                    {
                        "id": "sec-pc4-2-2",
                        "title": "效果验证：真的能复用吗",
                        "content": "用不同输入跑 3 次同一提示词，验证输出稳定性，不稳定则补限制条件。",
                        "knowledge_points": ["效果验证", "稳定性"],
                        "case": "周报模板连续 3 周输出格式一致才算达标。"
                    }
                ]
            },
            {
                "id": "ch-pc4-3",
                "title": "第三步：成册发布，沉淀你的作品",
                "content_summary": "把验证过的提示词整理成带目录与说明的手册，并建立持续更新机制。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc4-3-1",
                        "title": "手册排版与索引",
                        "content": "把验证过的提示词整理成带目录、分类、使用说明的手册文档。",
                        "knowledge_points": ["文档编排", "索引设计"],
                        "case": "用 AI 生成手册目录与每类使用说明，导出成 Markdown 或文档。"
                    },
                    {
                        "id": "sec-pc4-3-2",
                        "title": "持续更新机制",
                        "content": "建立「用完即录、每月复盘」的更新习惯，让提示词库与你的能力同步成长。",
                        "knowledge_points": ["持续更新", "复盘机制"],
                        "case": "每月花 30 分钟：新增、淘汰、合并提示词。"
                    }
                ]
            }
        ]
    },
    {
        "id": "project-course-5",
        "title": "结业作品：端到端 AI 综合项目",
        "description": "五阶段能力的综合大考。选择一个真实课题，用提示词链 + 多工具组合完成一个端到端项目，产出可展示、可评审的完整作品，冲击结业认证。",
        "topic": "实战",
        "difficulty": "advanced",
        "estimated_hours": 6,
        "source": "project-course",
        "coverImg": "https://picsum.photos/seed/project-course-5/300/200",
        "isFree": 1,
        "price": 0,
        "chapters": [
            {
                "id": "ch-pc5-1",
                "title": "第一步：选题与方案设计",
                "content_summary": "从多个方向选题并评估可行性，用 AI 帮你产出完整项目方案。",
                "duration_minutes": 35,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc5-1-1",
                        "title": "选题方向与可行性",
                        "content": "从「个人 AI 学习助手/求职工具包/读书笔记系统/AI 日报」等方向选题，评估需求、资料与产出物。",
                        "knowledge_points": ["项目选题", "可行性评估"],
                        "case": "选「AI 读书笔记系统」，明确输入输出与使用场景。"
                    },
                    {
                        "id": "sec-pc5-1-2",
                        "title": "项目方案文档",
                        "content": "用四段式让 AI 帮你产出项目方案：目标、功能拆解、技术路线（用的工具）、交付物。",
                        "knowledge_points": ["方案设计", "功能拆解"],
                        "case": "方案=背景/功能清单/工具链/里程碑/验收标准。"
                    }
                ]
            },
            {
                "id": "ch-pc5-2",
                "title": "第二步：搭建提示词链",
                "content_summary": "把项目拆成多个子任务，每条子任务配一条提示词并衔接起来，跑通后修正限制条件。",
                "duration_minutes": 40,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc5-2-1",
                        "title": "分步提示词设计",
                        "content": "把项目拆成多个子任务，每个子任务一条提示词，明确输入输出与衔接。",
                        "knowledge_points": ["提示词链", "任务衔接"],
                        "case": "读书系统=「提取结构」→「生成笔记」→「出知识卡片」→「生成复习题」四步链。"
                    },
                    {
                        "id": "sec-pc5-2-2",
                        "title": "链路测试与修正",
                        "content": "用真实输入跑完整链路，检查每步输出是否符合预期，修正衔接与限制条件。",
                        "knowledge_points": ["链路测试", "迭代修正"],
                        "case": "跑 3 本书，发现笔记步太啰嗦→加字数限制→输出更精炼。"
                    }
                ]
            },
            {
                "id": "ch-pc5-3",
                "title": "第三步：全流程执行与打磨",
                "content_summary": "多工具组合完成项目各环节，以用户视角检查可用性并迭代打磨。",
                "duration_minutes": 45,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc5-3-1",
                        "title": "多工具组合执行",
                        "content": "对话/表格/绘图/演示工具组合完成项目各环节，记录每环工具与提示词。",
                        "knowledge_points": ["多工具协作", "全链路执行"],
                        "case": "AI 生成 + 表格整理 + 即梦配图 + 剪映成片，一套走完。"
                    },
                    {
                        "id": "sec-pc5-3-2",
                        "title": "质量打磨与体验优化",
                        "content": "以「用户视角」检查产出物可用性，迭代打磨至稳定可靠。",
                        "knowledge_points": ["质量打磨", "可用性"],
                        "case": "找一个同学试用你的读书系统，收集反馈改进 3 处。"
                    }
                ]
            },
            {
                "id": "ch-pc5-4",
                "title": "第四步：提交与评审",
                "content_summary": "整理成作品展示页，对照结业评审标准自检后提交，冲击结业认证。",
                "duration_minutes": 30,
                "video_bv": "",
                "sections": [
                    {
                        "id": "sec-pc5-4-1",
                        "title": "作品展示页",
                        "content": "整理项目方案、提示词链、示例输出、成果截图成一份展示文档。",
                        "knowledge_points": ["作品展示", "交付整理"],
                        "case": "展示页=一句话介绍+功能演示+提示词链+你的复盘。"
                    },
                    {
                        "id": "sec-pc5-4-2",
                        "title": "对照评审标准自检",
                        "content": "对照结业评审标准逐项自检（完成度/质量/创新/表达），达标后提交评审。",
                        "knowledge_points": ["评审标准", "自检"],
                        "case": "用清单核对后提交，等待评审反馈。"
                    }
                ]
            }
        ]
    }
]


def _enrich_course(c):
    """把裸课程转成 enriched_courses 形态（含 enTitle/enDescription/category/duration/progress）。"""
    return {
        **c,
        "enTitle": c["title"],
        "enDescription": c.get("description", ""),
        "category": c.get("topic", ""),
        "duration": c.get("estimated_hours", 0) * 60,
        "progress": 0,
    }


def _sync_duration(c):
    """保持 lessons = 章节数、duration = estimated_hours * 60。"""
    if "chapters" in c:
        c["lessons"] = len(c["chapters"])
    if "estimated_hours" in c and "duration" in c:
        c["duration"] = c["estimated_hours"] * 60
    return c


def apply_deepen(course):
    """对单个课程对象追加加深章节/小节，幂等；返回是否发生变更。"""
    spec = DEEPEN.get(course.get("id"))
    if not spec:
        return False
    changed = False
    existing_ch = {ch.get("id") for ch in course.get("chapters", [])}
    for new_ch in spec["chapters"]:
        if new_ch["id"] not in existing_ch:
            course["chapters"].append(new_ch)
            existing_ch.add(new_ch["id"])
            changed = True
    extra = spec.get("extra_sections", {})
    for ch in course.get("chapters", []):
        secs = extra.get(ch.get("id"))
        if not secs:
            continue
        existing_sec = {s.get("id") for s in ch.get("sections", [])}
        for new_sec in secs:
            if new_sec["id"] not in existing_sec:
                ch["sections"].append(new_sec)
                changed = True
    if "estimated_hours" in spec and course.get("estimated_hours") != spec["estimated_hours"]:
        course["estimated_hours"] = spec["estimated_hours"]
        changed = True
    if changed:
        _sync_duration(course)
    return changed


def merge_project_courses(target, raw: bool):
    """把 5 门实战课 upsert 进课程列表（按 id 幂等，存在则整体替换为最新形态）。

    raw=True 写入 courses.json 的裸形态；raw=False 写入 enriched 的完整形态。
    返回新增数。
    """
    by_id = {c.get("id"): c for c in target}
    added = 0
    for c in PROJECT_COURSES:
        form = dict(c) if raw else _enrich_course(c)
        _sync_duration(form)
        if c["id"] in by_id:
            target[target.index(by_id[c["id"]])] = form
        else:
            target.append(form)
            added += 1
    return added


def main():
    courses_path = os.path.join(PROCESSED, "courses.json")
    enriched_path = os.path.join(PROCESSED, "enriched_courses.json")

    courses = json.load(open(courses_path, encoding="utf-8"))
    enriched = json.load(open(enriched_path, encoding="utf-8"))

    deepen_counts = {"courses": 0, "enriched": 0}
    for file_courses, name in ((courses, "courses"), (enriched, "enriched")):
        for c in file_courses:
            if apply_deepen(c):
                deepen_counts[name] += 1
            if c.get("id") in DEEPEN:
                _sync_duration(c)

    # 新增章节数（按新章节 id 前缀统计，仅作展示）
    new_chapter_ids = {ch["id"] for ch in (
        ch for c in PROJECT_COURSES for ch in c["chapters"]
    )}
    for spec in DEEPEN.values():
        new_chapter_ids.update(ch["id"] for ch in spec["chapters"])
    new_chapter_count = 0
    for c in enriched:
        for ch in c.get("chapters", []):
            if ch["id"] in new_chapter_ids:
                new_chapter_count += 1

    new_course_courses = merge_project_courses(courses, raw=True)
    new_course_enriched = merge_project_courses(enriched, raw=False)

    json.dump(courses, open(courses_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(enriched, open(enriched_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"courses.json     : {len(courses)} 门课")
    print(f"enriched_courses : {len(enriched)} 门课")
    print(f"加深课程数: {deepen_counts['courses']}")
    print(f"新增实战课: {new_course_courses} / {new_course_enriched}")
    print(f"新增章节: {new_chapter_count}")


if __name__ == "__main__":
    main()
