"""
Seed data generator v2 - 零基础 AI 教学五阶段课程体系.

Replaces the original technical ML/DL courses with a beginner-friendly
five-stage curriculum matching the business review report requirements:
  认知 → 入门 → 进阶 → 实战 → 熟练

Usage:
    python -m backend.data_pipeline.seed_data
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DIR


# ============================================================
# Courses: 零基础五阶段课程体系
# ============================================================

COURSES = [
    # ===== 阶段一：认知 =====
    {
        "id": "stage-1-cognition",
        "title": "阶段一：AI认知入门 — 了解AI能做什么、不能做什么",
        "description": "从零开始认识AI，了解AI是什么、能帮我们做什么、有什么局限性。适合完全不会用AI的普通人，不需要任何技术背景。学完本阶段你将建立正确的AI认知，知道什么时候该用AI、什么时候不该用。",
        "topic": "认知", "difficulty": "beginner", "estimated_hours": 4,
        "lessons": 4, "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/stage1-cognition/300/200",
        "isFree": 1, "price": 0,
        "chapters": [
            {"id": "ch-cog-1", "title": "AI是什么？从日常生活中的AI说起", "content_summary": "用生活化例子解释AI：手机语音助手、拍照翻译、购物推荐都是AI。区分AI不是机器人、不是科幻电影里的东西，而是已经渗透到日常生活中的工具。", "duration_minutes": 30,
             "video_bv": "", "sections": [
                {"id": "sec-cog-1-1", "title": "你每天都在用AI，只是不知道", "content": "从拍照搜题、语音转文字、抖音推荐等日常场景切入，让零基础用户意识到AI就在身边。", "knowledge_points": ["AI的日常应用场景"], "case": "张同学用手机拍照翻译英文菜单——这背后就是AI"},
                {"id": "sec-cog-1-2", "title": "AI不是万能的：破除三个常见误区", "content": "AI不会思考、不会创造、不一定正确——用反例演示AI出错的场景，建立正确预期。", "knowledge_points": ["AI的局限性", "幻觉问题"], "case": "让AI算「林黛玉倒拔垂杨柳」——AI不会说这不可能"},
            ]},
            {"id": "ch-cog-2", "title": "AI能帮你做什么？覆盖学习/办公/写作/求职", "content_summary": "用真实案例展示AI在各场景的实用价值，让用户直观感受「原来AI可以这样帮我」。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-cog-2-1", "title": "学习场景：AI是你的免费私教", "content": "演示用AI解释概念、总结文章、翻译文献、出模拟题等学习场景。", "knowledge_points": ["AI辅助学习"], "case": "用AI把一篇英文论文总结成200字中文摘要"},
                {"id": "sec-cog-2-2", "title": "办公场景：周报/邮件/PPT不再头疼", "content": "展示用AI写周报、起草邮件、生成PPT大纲等办公提效案例。", "knowledge_points": ["AI办公提效"], "case": "5分钟用AI完成一份周报初稿"},
            ]},
            {"id": "ch-cog-3", "title": "AI的边界与风险：什么时候不能用AI", "content_summary": "了解AI的局限性：隐私安全、信息准确性、偏见问题，知道什么时候必须人工判断。", "duration_minutes": 30,
             "video_bv": "", "sections": [
                {"id": "sec-cog-3-1", "title": "AI会胡说八道：什么是幻觉", "content": "演示AI编造事实、给出错误信息的案例，教用户如何辨别和防范。", "knowledge_points": ["AI幻觉", "事实核查"], "case": "AI编造了一篇不存在的论文引用——如何识别"},
                {"id": "sec-cog-3-2", "title": "隐私安全：不要把秘密告诉AI", "content": "说明AI对话的隐私风险，哪些信息不应该输入AI工具。", "knowledge_points": ["隐私保护", "数据安全"], "case": "不要把身份证号、银行卡号、公司机密输入AI"},
            ]},
            {"id": "ch-cog-4", "title": "本章回顾：AI认知地图", "content_summary": "梳理本章知识体系，帮助用户建立完整的AI认知框架，为下一阶段学习做准备。", "duration_minutes": 20,
             "video_bv": "", "sections": [
                {"id": "sec-cog-4-1", "title": "认知测验：你知道AI能做什么吗？", "content": "互动问答回顾本章核心知识点，检测学习效果。", "knowledge_points": ["AI认知回顾"], "case": ""},
            ]},
        ]
    },

    # ===== 阶段二：入门 =====
    {
        "id": "stage-2-basics",
        "title": "阶段二：入门实践 — 认识主流AI工具，开始动手用",
        "description": "认识并学会使用主流AI工具：大模型对话（DeepSeek/豆包/Kimi）、AI写作、AI绘图、AI办公。本阶段以实操为主，每节课都有动手练习，学完就能独立使用常见AI工具解决日常问题。",
        "topic": "入门", "difficulty": "beginner", "estimated_hours": 6,
        "lessons": 5, "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/stage2-basics/300/200",
        "isFree": 1, "price": 0,
        "chapters": [
            {"id": "ch-basic-1", "title": "大模型对话入门：和AI好好聊天", "content_summary": "手把手教你打开DeepSeek/豆包/Kimi，进行第一次对话。介绍基本交互方式：直接提问、追问、纠错。", "duration_minutes": 40,
             "video_bv": "", "sections": [
                {"id": "sec-basic-1-1", "title": "注册即用：三个免费AI工具的对比与选择", "content": "演示DeepSeek、豆包、Kimi的注册和使用，对比各自特点，帮用户选择适合自己的工具。", "knowledge_points": ["主流AI工具", "免费使用"], "case": "三款工具同时问「帮我解释一下什么是机器学习」——看谁回答更易懂"},
                {"id": "sec-basic-1-2", "title": "第一个AI对话：从「你好」到「帮我写个通知」", "content": "逐步引导用户完成第一个有实际价值的AI对话，体验从模糊需求到满意结果的完整流程。", "knowledge_points": ["AI对话基础", "追问技巧"], "case": "从模糊说「帮我写点东西」到得到一份可用的会议通知"},
            ]},
            {"id": "ch-basic-2", "title": "AI写作初体验：从零基础到写出可用文本", "content_summary": "教你用AI写朋友圈文案、通知公告、简单总结，0门槛上手AI写作。", "duration_minutes": 40,
             "video_bv": "", "sections": [
                {"id": "sec-basic-2-1", "title": "朋友圈文案、节日祝福：AI帮你搞定社交文案", "content": "实操：用AI生成朋友圈文案、节日祝福语、活动邀请函等日常社交文本。", "knowledge_points": ["AI写作基础", "社交文案"], "case": "用AI写一条春节拜年朋友圈——温暖又有文采"},
                {"id": "sec-basic-2-2", "title": "邮件和通知：工作场景的AI写作入门", "content": "实操：用AI写工作邮件、会议通知、简单汇报，学习基本的写作指令。", "knowledge_points": ["工作邮件", "通知文案"], "case": "用AI把一段口语化的需求变成正式的工作邮件"},
            ]},
            {"id": "ch-basic-3", "title": "AI绘图初体验：用文字生成图片", "content_summary": "入门AI绘图，了解主流AI绘图工具，学会用文字描述生成你想要的图片。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-basic-3-1", "title": "一句话出图：AI绘图工具入门", "content": "介绍主流AI绘图工具（如即梦、通义万相等），演示用文字生成第一张AI图片。", "knowledge_points": ["AI绘图工具", "文生图基础"], "case": "输入「一只戴着墨镜的橘猫在沙滩上喝椰子水」——看看AI能画出什么"},
                {"id": "sec-basic-3-2", "title": "描述技巧：如何让AI画出你想要的图", "content": "教基础描述技巧：主体+场景+风格+细节，让AI按你的想象出图。", "knowledge_points": ["绘图提示词基础"], "case": "分别用简单描述和详细描述生成同一主题的图片——对比区别"},
            ]},
            {"id": "ch-basic-4", "title": "AI办公初体验：文档/表格/PPT一键提效", "content_summary": "用AI处理常见的办公文档：PDF总结、Excel公式、PPT大纲生成。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-basic-4-1", "title": "AI帮你读文档：PDF和长文章一键总结", "content": "演示将PDF/长文章发给AI，让它帮你总结要点、提取关键信息。", "knowledge_points": ["文档总结", "信息提取"], "case": "把一份30页的报告丢给AI→5分钟内得到500字精准摘要"},
                {"id": "sec-basic-4-2", "title": "AI帮你做表格：不会公式也能处理数据", "content": "演示用AI写Excel公式、分析数据、生成图表思路。", "knowledge_points": ["Excel提效", "数据辅助分析"], "case": "告诉AI表格里有什么数据、想算什么→AI直接给出可复制使用的公式"},
            ]},
            {"id": "ch-basic-5", "title": "阶段回顾与实操测验", "content_summary": "综合练习：用AI完成一个完整的日常任务（写文案+做图+总结文档），检验入门阶段学习成果。", "duration_minutes": 30,
             "video_bv": "", "sections": [
                {"id": "sec-basic-5-1", "title": "综合实操：用AI完成一个完整的日常任务", "content": "任务：为公司团建活动写邀请函+做宣传图+整理活动流程。综合运用本阶段所学技能。", "knowledge_points": ["综合实操"], "case": ""},
            ]},
        ]
    },

    # ===== 阶段三：进阶 =====
    {
        "id": "stage-3-advanced",
        "title": "阶段三：提示词进阶 — 写出高质量提示词，让AI更懂你",
        "description": "从「能用AI」升级到「用好AI」。掌握万能四段式提示词框架、角色限定法、链式追问等核心技巧，让AI的输出质量提升一个档次。本阶段是学习效果的分水岭。",
        "topic": "进阶", "difficulty": "intermediate", "estimated_hours": 8,
        "lessons": 5, "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/stage3-advanced/300/200",
        "isFree": 1, "price": 0,
        "chapters": [
            {"id": "ch-adv-1", "title": "万能四段式提示词：清晰/角色/场景/限制", "content_summary": "揭示高质量提示词的核心框架：①说清楚要什么 ②给AI一个角色 ③描述使用场景 ④设定输出限制。掌握这个框架就掌握了80%的提示词技巧。", "duration_minutes": 45,
             "video_bv": "", "sections": [
                {"id": "sec-adv-1-1", "title": "为什么你的AI回答总是不满意？问题出在提问方式", "content": "对比「帮我写个方案」和「你是一名资深活动策划师，请为大学生AI体验日活动写一份活动方案...」——同样的AI，不同的结果。", "knowledge_points": ["提示词质量对结果的影响"], "case": "同一个需求，模糊提问 vs 结构化提问——质量天差地别"},
                {"id": "sec-adv-1-2", "title": "四段式框架拆解：清晰+角色+场景+限制", "content": "逐段拆解万能提示词模板，每段配上正反案例，让用户彻底理解为什么要这样写。", "knowledge_points": ["四段式提示词框架"], "case": "用框架重写「帮我写个PPT」→「你是一名资深咨询顾问。我需要向领导汇报Q3工作成果。请生成一份10页PPT大纲，每页包含标题+3个要点。风格专业简洁，数据导向。」"},
            ]},
            {"id": "ch-adv-2", "title": "角色限定法：让AI扮演专家，输出质量翻倍", "content_summary": "学会用角色设定大幅提升AI输出质量。从「你是XX专家」到具体的专业背景、工作习惯、输出要求，让AI像真正的行业专家一样思考和回答。", "duration_minutes": 40,
             "video_bv": "", "sections": [
                {"id": "sec-adv-2-1", "title": "给AI一个身份：角色设定的魔力", "content": "演示同一问题在无角色 vs 有角色设定下的回答质量差异。从面试官到律师到老师——角色决定回答角度。", "knowledge_points": ["角色设定技巧"], "case": "问「如何准备面试」→ 不加角色泛泛而谈 vs 设定「你是有10年经验的HR总监」→ 给出面试官视角的专业建议"},
                {"id": "sec-adv-2-2", "title": "进阶角色设定：不只是职位，还有风格和场景", "content": "教用户给AI设定语气风格、专业深度、目标读者等更细致的角色参数。", "knowledge_points": ["角色粒度控制"], "case": "设定「你是科普作家，用初中生能听懂的语言解释量子计算」"},
            ]},
            {"id": "ch-adv-3", "title": "AI长文本结构化输出：让AI给你排版好的文档", "content_summary": "学会让AI输出有结构、有格式、可直接使用的内容：Markdown表格、分类列表、分步骤教程、对比分析。", "duration_minutes": 40,
             "video_bv": "", "sections": [
                {"id": "sec-adv-3-1", "title": "让AI输出表格和列表：格式化的力量", "content": "教用户通过指令让AI输出表格、分类列表等结构化内容，提升信息的可读性和可用性。", "knowledge_points": ["结构化输出", "格式控制"], "case": "对比「介绍三款AI工具」的纯文本输出 vs 表格输出（工具名/价格/特点/适用场景）"},
                {"id": "sec-adv-3-2", "title": "分步骤输出和对比分析：让AI帮你理清思路", "content": "教用户让AI产出分步骤教程、SWOT分析、利弊对比等结构化的分析内容。", "knowledge_points": ["分步教程", "对比分析"], "case": "让AI用SWOT框架分析「大学生学AI的前景」"},
            ]},
            {"id": "ch-adv-4", "title": "链式追问：把一次对话变成深度辅导", "content_summary": "学会多轮对话策略：追问、反问、纠错、深挖——把AI从一个「一次性回答工具」变成「持续对话的导师」。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-adv-4-1", "title": "不要满足于第一轮回答：追问让答案好10倍", "content": "演示4种追问技巧：「能不能更具体？」「举个例子？」「用更简单的语言再说一遍」「如果场景变了呢？」", "knowledge_points": ["多轮追问", "深度对话"], "case": "从AI给出一个笼统的学习建议，通过3轮追问得到一份可执行的周学习计划"},
                {"id": "sec-adv-4-2", "title": "纠错与引导：AI说错了怎么办", "content": "教用户识别AI错误并有效纠正，把AI从错误方向引导回正轨。", "knowledge_points": ["错误识别", "对话纠偏"], "case": "AI给了一个过时的信息→用户指出「这个数据是2023年的，请用最新数据」→AI重新回答"},
            ]},
            {"id": "ch-adv-5", "title": "阶段回顾与提示词实战", "content_summary": "用真实场景出题，让用户独立完成提示词设计和多轮对话。检验进阶阶段学习成果。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-adv-5-1", "title": "实战考核：给定场景，写出最优提示词", "content": "场景题：你需要在班级群里发起一个AI学习小组，请用四段式框架+角色设定写一份招募文案。", "knowledge_points": ["综合实战"], "case": ""},
            ]},
        ]
    },

    # ===== 阶段四：实战 =====
    {
        "id": "stage-4-practice",
        "title": "阶段四：场景实战 — 用AI解决工作与学习中的真实问题",
        "description": "将AI应用于学习、办公、写作、求职四大真实场景。每节课都是一次完整的实操项目，学完就能把AI融入日常工作和学习中，真正实现效率提升。",
        "topic": "实战", "difficulty": "intermediate", "estimated_hours": 10,
        "lessons": 5, "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/stage4-practice/300/200",
        "isFree": 1, "price": 0,
        "chapters": [
            {"id": "ch-prac-1", "title": "周报自动生成：从流水账到结构化周报", "content_summary": "实战项目：建立个人周报生成工作流。只需输入本周的关键事项关键词，AI自动输出格式规范、重点突出、数据量化的专业周报。", "duration_minutes": 50,
             "video_bv": "", "sections": [
                {"id": "sec-prac-1-1", "title": "建立你的周报提示词模板", "content": "设计一个可复用的周报提示词模板，包含角色、格式、关键维度、字数等约束，每次只需替换本周事项即可。", "knowledge_points": ["提示词模板设计", "周报写作框架"], "case": "模板示例：「你是一名项目经理。请根据以下本周工作事项生成周报：1.项目进度 2.遇到的问题 3.下周计划。格式：每项包含3-5条要点，每条不超过20字，数据量化优先。」"},
                {"id": "sec-prac-1-2", "title": "进阶：让周报突出你的贡献", "content": "教用户如何在提示词中引导AI突出个人贡献和成果，让周报不只是流水账，而是有力的工作汇报。", "knowledge_points": ["成果展示", "数据量化"], "case": "同样的事项，对比「普通周报」和「突出贡献版周报」的差异"},
            ]},
            {"id": "ch-prac-2", "title": "活动策划AI工作流：从创意到执行方案", "content_summary": "实战项目：用AI完成一场完整活动的策划——主题创意、流程设计、物料清单、预算估算、风险预案。", "duration_minutes": 55,
             "video_bv": "", "sections": [
                {"id": "sec-prac-2-1", "title": "第一步：让AI帮你头脑风暴活动创意", "content": "用AI生成10个活动主题和创意方案，然后通过追问筛选和优化最佳方案。", "knowledge_points": ["创意生成", "方案筛选"], "case": "策划一场「校园AI体验日」——从10个创意中逐步聚焦到最终方案"},
                {"id": "sec-prac-2-2", "title": "第二步：从创意到可执行方案", "content": "让AI把选定的创意展开为完整执行方案：时间线、人员分工、物料清单、预算表、应急预案。", "knowledge_points": ["执行方案", "项目管理"], "case": "AI输出一份包含时间线/分工/预算的完整活动执行手册"},
            ]},
            {"id": "ch-prac-3", "title": "PPT文案批量生成：把大纲变成精美PPT", "content_summary": "实战项目：从一句话主题到完整PPT大纲再到每页文案，建立AI+PPT的高效工作流。", "duration_minutes": 50,
             "video_bv": "", "sections": [
                {"id": "sec-prac-3-1", "title": "从零到PPT大纲：结构化你的内容", "content": "给定一个主题，用AI生成逻辑清晰、层次分明的PPT大纲，教你如何审查和调整AI生成的结构。", "knowledge_points": ["PPT结构化", "大纲设计"], "case": "主题「大学生如何用AI提升学习效率」→ AI生成12页PPT大纲→ 用户审核和调整"},
                {"id": "sec-prac-3-2", "title": "每页文案批量生成：风格统一的PPT内容", "content": "让AI按照统一风格和格式为每一页生成详细文案，包括标题、要点、数据和过渡语。", "knowledge_points": ["文案批量生成", "风格统一"], "case": "以「苹果发布会风格」为每一页生成简洁有力的PPT文案"},
            ]},
            {"id": "ch-prac-4", "title": "AI求职助手：简历优化+模拟面试+岗位分析", "content_summary": "实战项目：用AI全面提升求职竞争力——简历诊断与优化、模拟面试练习、岗位JD分析与匹配。", "duration_minutes": 55,
             "video_bv": "", "sections": [
                {"id": "sec-prac-4-1", "title": "简历优化：让AI帮你诊断简历问题", "content": "把你的简历给AI，让它从HR视角指出问题并给出修改建议。对比修改前后的效果。", "knowledge_points": ["简历诊断", "HR视角"], "case": "一份在校生简历→AI指出「缺乏量化成果」「描述太笼统」等问题→给出具体修改方案"},
                {"id": "sec-prac-4-2", "title": "模拟面试：AI当面试官，帮你提前演练", "content": "让AI扮演面试官进行模拟面试，覆盖自我介绍、行为面试、技术问答等环节，并给出改进反馈。", "knowledge_points": ["面试模拟", "结构化回答"], "case": "设定AI为「某互联网公司产品经理面试官」，进行一轮15分钟的模拟面试"},
            ]},
            {"id": "ch-prac-5", "title": "阶段回顾：建立你的个人AI效率工具箱", "content_summary": "总结前四个阶段学到的AI技能，帮用户建立属于自己的AI提示词库和使用习惯，让AI真正融入日常工作流。", "duration_minutes": 30,
             "video_bv": "", "sections": [
                {"id": "sec-prac-5-1", "title": "你的AI效率手册：整理属于你自己的提示词库", "content": "引导用户回顾和整理自己最常用的提示词模板，建立个人的AI效率工具箱。", "knowledge_points": ["个人知识管理"], "case": ""},
            ]},
        ]
    },

    # ===== 阶段五：熟练 =====
    {
        "id": "stage-5-mastery",
        "title": "阶段五：通向熟练 — AI自动化流程与综合应用",
        "description": "从单次使用AI进步到建立自动化工作流。学习组合使用多个AI工具完成复杂任务，建立持续优化的AI使用习惯。本阶段帮你从「会用AI」升级到「善用AI」，让AI成为你工作和学习中的得力助手。",
        "topic": "熟练", "difficulty": "advanced", "estimated_hours": 8,
        "lessons": 4, "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/stage5-mastery/300/200",
        "isFree": 1, "price": 0,
        "chapters": [
            {"id": "ch-mas-1", "title": "AI自动化流程搭建：一次设置，持续提效", "content_summary": "学会设计可复用的AI工作流：把高频重复任务变成标准化提示词模板，实现「输入关键信息→AI自动输出完整成果」。", "duration_minutes": 45,
             "video_bv": "", "sections": [
                {"id": "sec-mas-1-1", "title": "识别你工作流中的AI机会点", "content": "教你分析自己的日常工作，识别哪些环节可以用AI提效，哪些需要人工判断。", "knowledge_points": ["工作流分析", "AI机会识别"], "case": "分析一个大学生的一天→识别至少8个可以用AI提效的场景"},
                {"id": "sec-mas-1-2", "title": "设计你的第一个AI自动化模板", "content": "动手设计一个覆盖完整流程的AI提示词模板：以「课程论文写作助手」为例——从选题建议→大纲生成→分段起草→润色检查。", "knowledge_points": ["提示词链设计", "自动化模板"], "case": "设计一套论文写作提示词链，每条提示词有明确的输入输出和衔接逻辑"},
            ]},
            {"id": "ch-mas-2", "title": "综合场景实战：完成一个端到端的AI项目", "content_summary": "组合运用认知→入门→进阶→实战四个阶段的全部技能，完成一个完整的综合项目。", "duration_minutes": 60,
             "video_bv": "", "sections": [
                {"id": "sec-mas-2-1", "title": "综合项目：策划+文案+设计+汇报一条龙", "content": "任务：用AI从零完成一个「校园AI科普讲座」的策划、宣传文案、海报设计思路、PPT和演讲稿。展示AI全链路协作的真实效率。", "knowledge_points": ["多工具协作", "全链路AI应用"], "case": "从第一个提示词「帮我头脑风暴一个吸引大学生的AI科普讲座主题」到最终完整的活动方案+宣传素材+PPT"},
                {"id": "sec-mas-2-2", "title": "项目复盘：哪些做得好，哪些可以更好", "content": "反思整个项目的AI使用过程，总结经验和改进点，建立持续优化的习惯。", "knowledge_points": ["复盘方法", "持续优化"], "case": ""},
            ]},
            {"id": "ch-mas-3", "title": "保持学习：AI在快速进化，你也需要", "content_summary": "介绍AI领域的最新动态获取方式、持续学习的方法论，以及如何跟上AI工具更新的步伐。", "duration_minutes": 35,
             "video_bv": "", "sections": [
                {"id": "sec-mas-3-1", "title": "信息源与学习方法：如何持续提升你的AI能力", "content": "推荐高质量AI资讯来源和学习方法，建立持续学习的习惯。", "knowledge_points": ["持续学习", "信息获取"], "case": ""},
                {"id": "sec-mas-3-2", "title": "从学员到导师：把你会的教给别人", "content": "鼓励用户分享学习成果到社区，在教别人的过程中深化自己的理解。介绍分享技巧。", "knowledge_points": ["知识分享", "社区贡献"], "case": ""},
            ]},
            {"id": "ch-mas-4", "title": "结业项目：打造你的AI能力展示作品", "content_summary": "用AI辅助完成一个代表你最高水平的综合项目，验证五阶段学习成果，获得结业认证。", "duration_minutes": 50,
             "video_bv": "", "sections": [
                {"id": "sec-mas-4-1", "title": "结业项目选题指南", "content": "提供多个结业项目选题方向：个人AI学习助手、AI求职工具包、AI读书笔记系统、AI日报生成器等。", "knowledge_points": ["项目选题", "能力展示"], "case": ""},
                {"id": "sec-mas-4-2", "title": "提交与评审：获得你的能力等级认证", "content": "说明结业项目提交流程和评审标准，通过后获得能力等级认证。", "knowledge_points": ["认证标准"], "case": ""},
            ]},
        ]
    },
]


# ============================================================
# Assessment Questions: 零基础AI能力测评 (更新为6维度)
# ============================================================

ASSESSMENT_QUESTIONS = [
    # ---- 维度1：AI基础认知 ----
    {
        "id": "q-001", "dimension": "AI基础认知",
        "question": "以下哪项最准确地描述了当前AI工具（如DeepSeek、豆包）的能力？",
        "options": ["能理解和生成文字，但可能会有错误或编造内容", "像人一样真正理解和思考问题", "所有回答都是100%准确的", "只能处理数学计算"],
        "correct_answer": 0, "explanation": "当前AI工具基于大语言模型，能够理解和生成文字，但不是真正「思考」，也可能出现「幻觉」编造不准确的内容。",
        "topic": "AI认知", "difficulty": "beginner"
    },
    {
        "id": "q-002", "dimension": "AI基础认知",
        "question": "在使用AI工具时，以下哪种做法是安全的？",
        "options": ["不输入身份证号、银行卡号等个人敏感信息", "把公司机密文件直接发给AI做总结", "在AI对话中透露自己的各种密码", "让AI帮你记住所有账号密码"],
        "correct_answer": 0, "explanation": "AI对话不是私密的，输入的内容可能被用于模型训练。绝不应该在AI对话中输入个人敏感信息、密码或公司机密。",
        "topic": "AI安全", "difficulty": "beginner"
    },
    {
        "id": "q-003", "dimension": "AI基础认知",
        "question": "什么是AI的「幻觉」问题？",
        "options": ["AI会编造看似合理但实际上不存在的事实或数据", "AI的屏幕显示出现了重影", "用户对AI产生了依赖心理", "AI运行速度突然变慢"],
        "correct_answer": 0, "explanation": "AI「幻觉」是指AI生成的内容看起来很有道理但实际上是编造的，比如虚构论文引用、编造统计数据等。学会辨别幻觉是使用AI的基本功。",
        "topic": "AI局限性", "difficulty": "beginner"
    },
    {
        "id": "q-004", "dimension": "AI基础认知",
        "question": "以下哪个场景最适合用AI来帮忙？",
        "options": ["把一篇长文章总结成200字要点", "判断朋友说的是不是真心话", "决定今天应该穿什么衣服", "替你向老板请假"],
        "correct_answer": 0, "explanation": "AI擅长处理信息型任务如总结、翻译、分类等。但涉及情感判断、个人偏好决策、需要真实身份的行为，AI不应替代人的判断。",
        "topic": "AI应用边界", "difficulty": "beginner"
    },

    # ---- 维度2：AI工具使用 ----
    {
        "id": "q-005", "dimension": "AI工具使用",
        "question": "当你对AI的第一个回答不满意时，最好的做法是？",
        "options": ["追问、补充细节或换一种方式重新提问", "直接放弃，换一个AI工具", "接受这个答案，不再尝试", "自己手动完成"],
        "correct_answer": 0, "explanation": "AI对话是一个迭代过程。通过追问补充细节、纠正方向、要求改进，往往能将第一次不满意的回答优化为高质量的输出。",
        "topic": "AI对话技巧", "difficulty": "beginner"
    },
    {
        "id": "q-006", "dimension": "AI工具使用",
        "question": "让AI帮你写一封正式邮件，以下哪个指令效果最好？",
        "options": ["「你是一名行政主管。请给全体同事写一封关于周五下午团建活动的通知邮件。要求：正式但不生硬，包含时间地点注意事项，150字以内。」", "「写个团建邮件」", "「帮我发邮件给同事」", "「邮件」"],
        "correct_answer": 0, "explanation": "好的提示词包含四个要素：清晰的任务说明、角色设定、具体要求和格式限制。越具体，AI的输出越接近你的期望。",
        "topic": "提示词质量", "difficulty": "beginner"
    },
    {
        "id": "q-007", "dimension": "AI工具使用",
        "question": "在DeepSeek/豆包/Kimi等工具中，「上下文」指的是什么？",
        "options": ["当前对话中之前的所有消息，AI能记住并参考", "用户的地理位置信息", "AI的训练数据总量", "网页的HTML代码"],
        "correct_answer": 0, "explanation": "上下文是AI在当前对话中能「记住」的信息范围。多轮对话就是利用了上下文，AI会参考之前的交流来给出更贴切的回答。",
        "topic": "对话机制", "difficulty": "beginner"
    },

    # ---- 维度3：提示词能力 ----
    {
        "id": "q-008", "dimension": "提示词能力",
        "question": "「万能四段式提示词」框架包含哪四个部分？",
        "options": ["清晰目标 + 角色设定 + 场景描述 + 输出限制", "标题 + 正文 + 结尾 + 署名", "问题 + 答案 + 例子 + 总结", "输入 + 处理 + 输出 + 反馈"],
        "correct_answer": 0, "explanation": "四段式提示词=①清晰说明你要什么②给AI设定一个专业角色③描述使用场景和目标受众④对输出格式/长度/风格做出限制。",
        "topic": "提示词框架", "difficulty": "intermediate"
    },
    {
        "id": "q-009", "dimension": "提示词能力",
        "question": "使用「角色限定法」写提示词，以下哪个角色设定最可能产生高质量的专业回答？",
        "options": ["「你是一名有15年经验的资深产品经理，曾主导过3款百万用户级产品。」", "「你是一个产品经理。」", "「你懂产品。」", "「帮我做产品分析」"],
        "correct_answer": 0, "explanation": "角色设定越具体（经验年限、专业领域、过往成就），AI的输出就越专业和精准。模糊的角色设定效果大打折扣。",
        "topic": "角色限定", "difficulty": "intermediate"
    },
    {
        "id": "q-010", "dimension": "提示词能力",
        "question": "想让AI输出一个格式清晰的对比表格，最好的做法是？",
        "options": ["在提示词中明确指定「请用表格形式输出，包含以下列：...」", "先让AI写文字，再手动复制到Excel里排版", "用复杂的技术术语描述需求", "让AI自己决定输出格式"],
        "correct_answer": 0, "explanation": "AI完全能按你的要求输出表格、列表、分步教程等结构化格式——前提是你在提示词中明确指定了格式。直接说「用表格输出」即可。",
        "topic": "格式控制", "difficulty": "intermediate"
    },
    {
        "id": "q-011", "dimension": "提示词能力",
        "question": "链式追问的核心价值是什么？",
        "options": ["通过多轮对话逐步深化和优化AI的回答，最终得到高质量结果", "让AI生成更长的文本", "测试AI的响应速度", "增加对话的趣味性"],
        "correct_answer": 0, "explanation": "链式追问（多轮对话）是把一次性问答升级为深度辅导的关键技巧。通过「追问→纠错→深挖」逐步把模糊粗糙的回答打磨精准。",
        "topic": "多轮对话", "difficulty": "intermediate"
    },

    # ---- 维度4：场景应用 ----
    {
        "id": "q-012", "dimension": "场景应用",
        "question": "用AI写周报时，以下哪种输入方式效果最好？",
        "options": ["提供本周关键事项关键词+期望的周报格式+突出成果的方向", "只输入「写周报」三个字", "把整周的聊天记录直接发给AI", "让AI自己编造工作内容"],
        "correct_answer": 0, "explanation": "给AI提供关键信息（本周做了什么）和明确要求（格式、重点、风格），AI才能产出符合你实际工作情况的周报，而不是模板套话。",
        "topic": "办公应用", "difficulty": "intermediate"
    },
    {
        "id": "q-013", "dimension": "场景应用",
        "question": "用AI辅助求职时，以下哪个用法最有效？",
        "options": ["让AI从HR视角诊断你的简历，并针对具体岗位JD给出优化建议", "让AI帮你编造工作经历", "用AI生成一封千篇一律的求职信发给所有公司", "完全依赖AI做职业规划决策"],
        "correct_answer": 0, "explanation": "AI是求职的得力辅助工具——可以诊断简历问题、模拟面试、分析岗位匹配度，但不应该编造信息或替代你的真实判断。",
        "topic": "求职应用", "difficulty": "intermediate"
    },
    {
        "id": "q-014", "dimension": "场景应用",
        "question": "用AI辅助写课程论文时，正确的做法是？",
        "options": ["用AI帮助头脑风暴选题、生成大纲、优化表达，但核心观点和研究由你完成", "让AI从零写完整篇论文并直接提交", "用AI改写别人的论文来交作业", "完全不用AI，因为所有老师都禁止"],
        "correct_answer": 0, "explanation": "AI是论文写作的好帮手——可以协助选题、架构、润色，但核心研究、分析和观点应该来自你自己。直接让AI代写既不符合学术诚信也无法真正学到东西。",
        "topic": "学习应用", "difficulty": "intermediate"
    },
    {
        "id": "q-015", "dimension": "场景应用",
        "question": "策划一场活动时，AI最适合帮你做什么？",
        "options": ["生成创意方案、梳理流程清单、起草宣传文案", "代替你预订场地和联系嘉宾", "代替你到现场执行活动", "帮你决定活动预算的具体金额"],
        "correct_answer": 0, "explanation": "AI擅长策划阶段的信息工作——创意发散、方案结构化、文案起草。但涉及实际联系、执行决策、预算审批等需要真实人际互动和判断的环节，还是需要人来做。",
        "topic": "策划应用", "difficulty": "intermediate"
    },

    # ---- 维度5：AI工作流 ----
    {
        "id": "q-016", "dimension": "AI工作流",
        "question": "什么是「AI工作流」？",
        "options": ["把多个AI使用步骤串联成一个标准化的提效流程", "AI的底层计算流程", "一种编程语言", "公司内部的AI使用规定"],
        "correct_answer": 0, "explanation": "AI工作流是指将频繁重复的任务设计成标准化流程：准备工作→提示词模板→AI生成→人工审核→优化输出，一次设计、反复使用。",
        "topic": "工作流概念", "difficulty": "advanced"
    },
    {
        "id": "q-017", "dimension": "AI工作流",
        "question": "设计AI自动化模板时，最重要的考虑是什么？",
        "options": ["模板的可复用性：输入变量清晰、输出格式标准化", "让模板尽可能复杂以展示技术", "完全不需人工介入", "使用尽可能多的AI工具"],
        "correct_answer": 0, "explanation": "好的AI自动化模板应该在「标准化」和「灵活性」之间平衡：关键信息作为变量输入、输出格式统一、但允许根据具体情况调整。",
        "topic": "自动化设计", "difficulty": "advanced"
    },
    {
        "id": "q-018", "dimension": "AI工作流",
        "question": "在AI协作中，「人机分工」的核心原则是什么？",
        "options": ["AI处理信息型、重复型工作；人做判断、决策和创意把关", "把所有工作都交给AI", "AI做所有决策", "完全不用AI，纯手工"],
        "correct_answer": 0, "explanation": "最佳的AI协作模式是人机互补：AI擅长信息处理、内容生成、格式整理等；人负责方向判断、质量把关、创意决策。各司其职效率最高。",
        "topic": "人机协作", "difficulty": "advanced"
    },

    # ---- 维度6：AI思维 ----
    {
        "id": "q-019", "dimension": "AI思维",
        "question": "下面哪种思维方式最符合「AI思维」？",
        "options": ["遇到重复性任务时，先想「这个能否设计成AI工作流自动完成？」", "AI可以解决所有问题，不需要动脑", "遇到问题先自己硬扛，实在不行再求助", "只用AI做娱乐消遣"],
        "correct_answer": 0, "explanation": "AI思维是培养一种习惯：遇到任务时先判断AI能否辅助，把AI视为日常效率工具而非神秘黑科技。",
        "topic": "思维习惯", "difficulty": "advanced"
    },
    {
        "id": "q-020", "dimension": "AI思维",
        "question": "当AI给出一个看似完美的方案时，你应该？",
        "options": ["批判性审视：检查是否符合实际、有无遗漏、逻辑是否自洽", "直接照搬执行", "因为来自AI所以不信任", "转发给其他人让他们决定"],
        "correct_answer": 0, "explanation": "AI的输出应该作为「初稿」而非「定稿」。批判性思维是AI时代最重要的能力之一——审视、验证、调整AI的输出才能得到最佳结果。",
        "topic": "批判性思维", "difficulty": "advanced"
    },
]


# ============================================================
# Knowledge Items: 零基础AI教学知识库 (替换技术向内容)
# ============================================================

KNOWLEDGE_ITEMS = [
    # ---- AI认知 ----
    {"id": "kb-cog-01", "source": "course", "topic": "认知", "title": "日常生活中的AI应用", "content": "AI已经渗透到日常生活的方方面面：手机拍照时的场景识别、购物App的推荐算法、导航软件的路线规划、社交媒体的内容推荐、语音助手的语音识别。这些背后都是AI技术在工作，只是用户往往意识不到。", "difficulty": "beginner", "tags": ["AI日常", "应用场景"]},
    {"id": "kb-cog-02", "source": "course", "topic": "认知", "title": "AI能做什么与不能做什么", "content": "AI擅长：信息总结、文字生成、翻译、分类、模式识别、数据分析。AI不擅长：真正的创造、情感理解、道德判断、需要真实世界体验的任务。AI的输出需要人类验证，不能盲目信任。", "difficulty": "beginner", "tags": ["AI能力边界", "批判性思维"]},
    {"id": "kb-cog-03", "source": "course", "topic": "认知", "title": "AI幻觉：当AI编造事实", "content": "AI幻觉（Hallucination）是指AI生成看似合理但实际不存在或不准确的内容。例如：编造不存在的论文引用、虚构统计数据、混淆人物和事件。识别幻觉的方法是：关键事实交叉验证、对数字保持警惕、用多个来源核实。", "difficulty": "beginner", "tags": ["AI幻觉", "事实核查"]},
    {"id": "kb-cog-04", "source": "course", "topic": "认知", "title": "AI时代的隐私安全", "content": "使用AI工具时的安全原则：不要输入身份证号、银行卡号、密码等敏感信息；不要上传公司机密文件；了解你使用的AI工具的隐私政策；企业使用AI应建立内部使用规范。AI对话内容可能被用于模型训练。", "difficulty": "beginner", "tags": ["隐私安全", "数据保护"]},

    # ---- AI工具入门 ----
    {"id": "kb-basic-01", "source": "course", "topic": "入门", "title": "主流免费AI工具对比", "content": "DeepSeek（国产免费，推理能力强，支持长文本）、豆包（字节跳动出品，中文理解好，适合日常对话）、Kimi（月之暗面，擅长长文阅读和总结）、通义千问（阿里出品，功能全面）。选择合适的工具取决于你的具体需求：日常问答选豆包，深度分析选DeepSeek，长文阅读选Kimi。", "difficulty": "beginner", "tags": ["AI工具", "免费工具"]},
    {"id": "kb-basic-02", "source": "course", "topic": "入门", "title": "第一次AI对话：从模糊到清晰", "content": "很多人第一次用AI时只说「帮我写点东西」「给我点建议」——太模糊了。好的AI对话应该：①清楚说明你要什么 ②提供必要的背景信息 ③说明期望的格式和长度。比如不要只说「写个通知」，而是说「请帮我写一份班级活动通知，时间本周六下午2点，地点教学楼301，内容为AI学习经验分享，约150字」。", "difficulty": "beginner", "tags": ["AI对话", "提问技巧"]},
    {"id": "kb-basic-03", "source": "course", "topic": "入门", "title": "AI写作入门：从朋友圈到工作邮件", "content": "AI写作的实用场景：朋友圈文案（节日祝福、活动宣传）、工作邮件（会议通知、汇报总结）、简单公文（通知、公告）。关键技巧：给AI示例参考风格、指定目标读者、明确字数限制。", "difficulty": "beginner", "tags": ["AI写作", "文案生成"]},
    {"id": "kb-basic-04", "source": "course", "topic": "入门", "title": "AI绘图入门指南", "content": "主流AI绘图工具：即梦（字节跳动）、通义万相（阿里）、文心一格（百度）。写绘图提示词的基本公式：主体描述 + 场景/背景 + 风格/画风 + 细节元素 + 画质要求。例如：一只橘猫（主体），在阳光下的沙滩上（场景），日系插画风格（风格），戴着墨镜喝着椰子水（细节），高清精细（画质）。", "difficulty": "beginner", "tags": ["AI绘图", "文生图"]},
    {"id": "kb-basic-05", "source": "course", "topic": "入门", "title": "AI办公：文档与表格提效", "content": "AI可以大幅提升办公效率：PDF长文档一键总结、Excel公式自动生成、会议纪要整理、PPT大纲生成。核心原则是「把格式化的、重复的信息处理工作交给AI，把判断和决策留给自己」。", "difficulty": "beginner", "tags": ["AI办公", "效率提升"]},

    # ---- 提示词进阶 ----
    {"id": "kb-adv-01", "source": "course", "topic": "进阶", "title": "万能四段式提示词框架", "content": "高质量提示词的四段式公式：①清晰目标（你要AI做什么）②角色设定（AI扮演什么专家）③场景描述（在什么情境下，给谁看）④输出限制（格式、字数、风格要求）。示例：「请帮我写一份新员工入职培训计划（目标）。你是一名有10年经验的HR培训经理（角色）。受众是刚毕业的应届生，培训周期为1周（场景）。请输出5天每天的培训主题和内容要点，用表格呈现（限制）。」", "difficulty": "intermediate", "tags": ["提示词框架", "四段式"]},
    {"id": "kb-adv-02", "source": "course", "topic": "进阶", "title": "角色限定法的艺术", "content": "角色限定（Role Prompting）通过给AI一个具体身份来大幅提升输出质量。角色越具体效果越好：「你是律师」不如「你是一名专注劳动法的资深律师，有15年执业经验」。可以组合多个维度：专业身份+经验年限+工作风格+目标受众偏好。", "difficulty": "intermediate", "tags": ["角色限定", "提示词技巧"]},
    {"id": "kb-adv-03", "source": "course", "topic": "进阶", "title": "结构化输出：让AI给你排版", "content": "AI可以直接输出表格（Markdown格式）、分类列表、分步教程、SWOT分析等结构化内容。关键是在提示词中明确输出格式要求：「请用表格对比」「请分步骤列出」「请按SWOT框架分析」。结构化输出让AI的结果更清晰可用，减少后期整理时间。", "difficulty": "intermediate", "tags": ["结构化输出", "格式控制"]},
    {"id": "kb-adv-04", "source": "course", "topic": "进阶", "title": "链式追问：把一次对话变成深度辅导", "content": "不要满足于AI的第一轮回答。有效的追问策略：①「能更具体吗？」→要求细节 ②「举个例子」→要求实例化 ③「用更简单的语言再说一遍」→降低难度 ④「如果场景变了（描述新场景），你建议怎么做？」→拓展应用。通过3-5轮追问，输出质量能提升10倍。", "difficulty": "intermediate", "tags": ["多轮对话", "追问技巧"]},

    # ---- 场景实战 ----
    {"id": "kb-prac-01", "source": "course", "topic": "实战", "title": "AI周报生成工作流", "content": "高效的AI周报生成流程：①整理本周关键事项（3-5条）②使用标准化的周报提示词模板（角色=项目经理/团队负责人，格式=进度+问题+计划，风格=数据导向）③AI生成初稿④人工补充具体数据和细节⑤最终润色发布。一次设计模板可长期复用。", "difficulty": "intermediate", "tags": ["周报", "办公工作流"]},
    {"id": "kb-prac-02", "source": "course", "topic": "实战", "title": "AI活动策划全流程", "content": "用AI策划活动的完整链路：①头脑风暴→生成10个创意方向 ②筛选最优方案→基于约束条件（预算/时间/人数）评估 ③细化执行方案→时间线、分工、物料、预算 ④起草宣传文案→针对不同渠道定制风格 ⑤生成应急预案→考虑常见风险场景。每个环节都可以用AI加速，但关键决策需要人工判断。", "difficulty": "intermediate", "tags": ["活动策划", "项目管理"]},
    {"id": "kb-prac-03", "source": "course", "topic": "实战", "title": "AI辅助PPT制作流程", "content": "AI+PPT高效工作流：①用AI从一句话主题生成完整PPT大纲（逻辑结构）②用AI为每一页生成详细文案（统一风格）③手动将文案导入PPT并设计视觉（AI辅助排版建议）④用AI生成演讲备注和过渡语。AI不替代PPT设计软件，但能替代80%的文案工作。", "difficulty": "intermediate", "tags": ["PPT制作", "内容生成"]},
    {"id": "kb-prac-04", "source": "course", "topic": "实战", "title": "AI求职全链路辅助", "content": "AI求职工具包：①简历诊断→让AI从HR视角审查简历，指出模糊描述、缺少量化成果等问题 ②岗位匹配→把简历和JD发给AI，让它分析匹配度和差距 ③模拟面试→让AI扮演面试官进行针对性模拟 ④面试问题准备→让AI根据JD预测可能的问题并准备答案。AI是辅助而非替代——最终展示的是你真实的能力。", "difficulty": "intermediate", "tags": ["求职", "面试准备"]},

    # ---- AI工作流与思维 ----
    {"id": "kb-mas-01", "source": "course", "topic": "熟练", "title": "设计个人AI自动化工作流", "content": "AI工作流设计原则：①识别高频重复任务（周报/邮件/方案等）②拆解任务的标准步骤③设计每个步骤的提示词模板④定义输入变量和输出格式⑤串联形成端到端流程⑥持续迭代优化。一个好的AI工作流应该让90%的工作由AI完成初稿，人只做10%的审核和定制化调整。", "difficulty": "advanced", "tags": ["自动化", "工作流设计"]},
    {"id": "kb-mas-02", "source": "course", "topic": "熟练", "title": "人机协作的最佳实践", "content": "人机协作的黄金法则：AI负责广度（信息搜集、方案发散、格式整理），人负责深度（判断什么最重要、做决策、确保准确性）。典型协作流程：AI生成初稿→人审核标注→AI根据反馈修改→人最终确认。在重复循环中逐步优化，效率远高于纯人工或纯AI。", "difficulty": "advanced", "tags": ["人机协作", "效率方法论"]},
    {"id": "kb-mas-03", "source": "course", "topic": "熟练", "title": "AI时代的学习方法论", "content": "在AI快速进化的时代持续学习的方法：①关注AI领域头部信息源（官方博客、技术社区）②每周花30分钟亲手体验一款新AI工具③建立个人的AI提示词库并持续优化④加入AI学习社群交流经验⑤定期复盘自己的AI使用效率并寻找优化点。关键不是追每一个新工具，而是建立持续学习和适应的习惯。", "difficulty": "advanced", "tags": ["持续学习", "学习方法"]},
]


# ============================================================
# Projects: 零基础AI实操项目 (替换技术向项目)
# ============================================================

PROJECTS = [
    {
        "id": "project-0",
        "title": "实战项目一：个人AI周报生成工作流",
        "description": "设计并建立属于你自己的AI周报自动生成流程。从整理本周事项→AI生成→优化完善→发布，形成一个可每周复用的标准化工作流。产出物：你个人的周报提示词模板 + 一份示例周报。",
        "tech_stack": ["AI对话", "提示词设计", "文档"], "difficulty": "beginner", "estimated_hours": 3,
        "topics_covered": ["AI办公", "工作流设计"], "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/project-0/300/200",
        "isFree": 1, "price": 0,
    },
    {
        "id": "project-1",
        "title": "实战项目二：活动策划全流程实战",
        "description": "用AI从零完成一场校园/社区活动的完整策划：主题创意→方案细化→物料清单→宣传文案→执行流程。产出物：完整的活动策划方案文档（含时间线、预算、分工、应急预案）。",
        "tech_stack": ["AI对话", "策划", "项目管理"], "difficulty": "intermediate", "estimated_hours": 4,
        "topics_covered": ["活动策划", "全链路AI"], "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/project-1/300/200",
        "isFree": 1, "price": 0,
    },
    {
        "id": "project-2",
        "title": "实战项目三：AI求职竞争力提升方案",
        "description": "用AI全面提升你的求职准备：简历诊断与优化→目标岗位JD分析→模拟面试→面试问题准备。产出物：优化后的简历 + 个性化面试准备手册。",
        "tech_stack": ["AI对话", "简历优化", "面试模拟"], "difficulty": "intermediate", "estimated_hours": 4,
        "topics_covered": ["求职", "AI辅助"], "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/project-2/300/200",
        "isFree": 1, "price": 0,
    },
    {
        "id": "project-3",
        "title": "实战项目四：个人AI提示词库建设",
        "description": "系统整理你学到的所有提示词技巧，建立属于你自己的分类提示词库（学习/办公/写作/生活四大类）。每类至少5条经过验证的高质量提示词。产出物：个人AI提示词手册。",
        "tech_stack": ["提示词设计", "知识管理"], "difficulty": "beginner", "estimated_hours": 3,
        "topics_covered": ["提示词工程", "知识管理"], "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/project-3/300/200",
        "isFree": 1, "price": 0,
    },
    {
        "id": "project-4",
        "title": "实战项目五：结业综合项目",
        "description": "综合运用五阶段全部技能，完成一个端到端的AI项目。可选方向：AI学习笔记系统、AI日报生成器、AI读书助手、AI课程设计等。产出物：完整的项目方案+提示词链+示例输出。",
        "tech_stack": ["综合应用", "AI工作流"], "difficulty": "advanced", "estimated_hours": 6,
        "topics_covered": ["全链路实战", "项目综合"], "source": "seed-v2",
        "coverImg": "https://picsum.photos/seed/project-4/300/200",
        "isFree": 1, "price": 0,
    },
]


# ============================================================
# Learning Paths: 四类用户学习路径
# ============================================================

LEARNING_PATHS = [
    {
        "id": "path-0",
        "direction": "完全不会AI的小白",
        "title": "学习路径：从零开始学AI（小白推荐）",
        "description": "推荐给完全没接触过AI的用户。按认知→入门→进阶→实战→熟练的顺序，从零建立AI能力。",
        "total_weeks": 10,
        "nodes": [
            {"id": "path-0-0", "title": "AI认知入门", "type": "course", "items": ["stage-1-cognition"]},
            {"id": "path-0-1", "title": "认识主流AI工具", "type": "course", "items": ["stage-2-basics"]},
            {"id": "path-0-2", "title": "提示词进阶技巧", "type": "course", "items": ["stage-3-advanced"]},
            {"id": "path-0-3", "title": "场景实战练习", "type": "course", "items": ["stage-4-practice"]},
            {"id": "path-0-4", "title": "实战项目：AI周报工作流", "type": "project", "items": ["project-0"]},
            {"id": "path-0-5", "title": "通往熟练之路", "type": "course", "items": ["stage-5-mastery"]},
        ],
    },
    {
        "id": "path-1",
        "direction": "想系统学AI的人",
        "title": "学习路径：系统掌握AI应用（深度推荐）",
        "description": "推荐给想系统全面学习AI的学员。除了五阶段课程外，额外强化提示词和自动化能力。",
        "total_weeks": 12,
        "nodes": [
            {"id": "path-1-0", "title": "AI认知入门", "type": "course", "items": ["stage-1-cognition"]},
            {"id": "path-1-1", "title": "认识主流AI工具", "type": "course", "items": ["stage-2-basics"]},
            {"id": "path-1-2", "title": "提示词进阶技巧", "type": "course", "items": ["stage-3-advanced"]},
            {"id": "path-1-3", "title": "场景实战练习", "type": "course", "items": ["stage-4-practice"]},
            {"id": "path-1-4", "title": "实战项目：活动策划", "type": "project", "items": ["project-1"]},
            {"id": "path-1-5", "title": "实战项目：AI求职", "type": "project", "items": ["project-2"]},
            {"id": "path-1-6", "title": "通往熟练之路", "type": "course", "items": ["stage-5-mastery"]},
            {"id": "path-1-7", "title": "结业项目", "type": "project", "items": ["project-4"]},
        ],
    },
    {
        "id": "path-2",
        "direction": "想用AI提效的职场人",
        "title": "学习路径：AI办公提效（职场推荐）",
        "description": "推荐给想用AI提升工作效率的职场人士。重点学习提示词技巧和办公场景实战，快速见效。",
        "total_weeks": 8,
        "nodes": [
            {"id": "path-2-0", "title": "AI认知入门（快速过）", "type": "course", "items": ["stage-1-cognition"]},
            {"id": "path-2-1", "title": "认识主流AI工具", "type": "course", "items": ["stage-2-basics"]},
            {"id": "path-2-2", "title": "提示词进阶技巧", "type": "course", "items": ["stage-3-advanced"]},
            {"id": "path-2-3", "title": "场景实战：办公+PPT", "type": "course", "items": ["stage-4-practice"]},
            {"id": "path-2-4", "title": "实战项目：AI周报+个人提示词库", "type": "project", "items": ["project-0", "project-3"]},
        ],
    },
    {
        "id": "path-3",
        "direction": "想做AI项目的人",
        "title": "学习路径：AI项目实战（进阶推荐）",
        "description": "推荐给有一定基础、想通过完成项目来深化AI技能的学员。以项目驱动学习，最终产出可展示的作品。",
        "total_weeks": 10,
        "nodes": [
            {"id": "path-3-0", "title": "AI认知+工具快速入门", "type": "course", "items": ["stage-1-cognition", "stage-2-basics"]},
            {"id": "path-3-1", "title": "提示词进阶+场景实战", "type": "course", "items": ["stage-3-advanced", "stage-4-practice"]},
            {"id": "path-3-2", "title": "实战项目：活动策划", "type": "project", "items": ["project-1"]},
            {"id": "path-3-3", "title": "实战项目：AI求职", "type": "project", "items": ["project-2"]},
            {"id": "path-3-4", "title": "熟练+结业项目", "type": "course", "items": ["stage-5-mastery"]},
            {"id": "path-3-5", "title": "结业综合项目", "type": "project", "items": ["project-4"]},
        ],
    },
]


def run():
    """Generate all seed data files."""
    print("=" * 60)
    print("Generating zero-basics AI teaching dataset v2 (seed data)")
    print("=" * 60)

    # Knowledge base
    kb_path = PROCESSED_DIR / "knowledge_base.json"
    KNOWLEDGE_ITEMS.sort(key=lambda x: (x["source"], x["id"]))
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_ITEMS, f, ensure_ascii=False, indent=2)
    print(f"  Knowledge base: {len(KNOWLEDGE_ITEMS)} items -> {kb_path}")

    # Assessment questions
    q_path = PROCESSED_DIR / "assessment_questions.json"
    with open(q_path, "w", encoding="utf-8") as f:
        json.dump(ASSESSMENT_QUESTIONS, f, ensure_ascii=False, indent=2)
    print(f"  Assessment questions: {len(ASSESSMENT_QUESTIONS)} -> {q_path}")

    # Courses
    c_path = PROCESSED_DIR / "courses.json"
    with open(c_path, "w", encoding="utf-8") as f:
        json.dump(COURSES, f, ensure_ascii=False, indent=2)
    print(f"  Courses: {len(COURSES)} -> {c_path}")

    # Enriched courses (same data)
    ec_path = PROCESSED_DIR / "enriched_courses.json"
    enriched = []
    for c in COURSES:
        enriched.append({
            **c,
            "enTitle": c["title"],
            "enDescription": c["description"],
            "category": c["topic"],
            "duration": c["estimated_hours"] * 60,
            "progress": 0,
        })
    with open(ec_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f"  Enriched courses: {len(enriched)} -> {ec_path}")

    # Projects
    p_path = PROCESSED_DIR / "projects.json"
    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(PROJECTS, f, ensure_ascii=False, indent=2)
    print(f"  Projects: {len(PROJECTS)} -> {p_path}")

    # Enriched projects
    ep_path = PROCESSED_DIR / "enriched_projects.json"
    enriched_proj = []
    for p in PROJECTS:
        enriched_proj.append({
            **p,
            "enTitle": p["title"],
            "enDescription": p["description"],
            "coverImg": p.get("cover_img", p.get("coverImg", "")),
            "techStack": p.get("tech_stack", []),
            "estimatedHours": p.get("estimated_hours", 0),
            "stepCount": p.get("step_count", len(p.get("steps", []))),
            "step_count": len(p.get("steps", [])),
            "status": "available",
            "progress": 0,
        })
    with open(ep_path, "w", encoding="utf-8") as f:
        json.dump(enriched_proj, f, ensure_ascii=False, indent=2)
    print(f"  Enriched projects: {len(enriched_proj)} -> {ep_path}")

    # Learning paths
    lp_path = PROCESSED_DIR / "learning_paths.json"
    with open(lp_path, "w", encoding="utf-8") as f:
        json.dump(LEARNING_PATHS, f, ensure_ascii=False, indent=2)
    print(f"  Learning paths: {len(LEARNING_PATHS)} -> {lp_path}")

    # Enriched learning paths
    elp_path = PROCESSED_DIR / "enriched_learning_paths.json"
    enriched_paths = []
    for lp in LEARNING_PATHS:
        enriched_paths.append({
            **lp,
            "totalWeeks": lp.get("total_weeks", 0),
            "currentWeek": lp.get("current_week", 0),
            "current_week": lp.get("current_week", 0),
            "description": lp.get("description", ""),
        })
    with open(elp_path, "w", encoding="utf-8") as f:
        json.dump(enriched_paths, f, ensure_ascii=False, indent=2)
    print(f"  Enriched learning paths: {len(enriched_paths)} -> {elp_path}")

    print()
    print("Seed data v2 generation complete!")
    print(f"  Total: {len(KNOWLEDGE_ITEMS)} knowledge items, {len(ASSESSMENT_QUESTIONS)} questions, {len(COURSES)} courses, {len(PROJECTS)} projects, {len(LEARNING_PATHS)} paths")


if __name__ == "__main__":
    run()
