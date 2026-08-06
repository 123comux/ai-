"""Fix course-6 (Computer Vision) and fix course-3/course-4 mappings."""
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "cms.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Fix course-3: should be NLP (not Data Science)
chapters_course3 = [
    {
        "id": "ch-3-1",
        "title": "第一章：NLP 基础与文本处理",
        "duration_minutes": 45,
        "summary": "理解自然语言处理的核心任务，掌握文本预处理和特征提取方法。",
        "video_bv": "BV16G41167p1",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-3-1-1",
                "title": "1.1 NLP 核心任务",
                "content": "NLP 研究人与计算机之间的语言交互，涵盖理解、生成、翻译等核心任务。",
                "knowledge_points": [
                    "文本分类：情感分析、垃圾邮件过滤",
                    "信息提取：命名实体识别、关系抽取",
                    "机器翻译：中英互译",
                    "对话系统：问答、闲聊、任务型对话",
                    "文本生成：摘要、写作、代码生成"
                ],
                "case": "智能客服：用户发消息 → 情感分析（是否愤怒）→ 意图识别（查询订单）→ 槽位填充（订单号）→ 生成回复。"
            },
            {
                "id": "sec-3-1-2",
                "title": "1.2 文本预处理",
                "content": "原始文本充满噪声，需要经过清洗才能用于模型训练。",
                "knowledge_points": [
                    "分词：中文 Jieba/THULAC，英文空格/规则",
                    "停用词去除：过滤「的、了、the、is」等无意义词",
                    "词形还原：还原动词时态、名词复数",
                    "文本清洗：HTML 标签、特殊字符、多余空格",
                    "标准化：全角转半角、简繁转换"
                ],
                "case": "评论情感分析：爬取电商评论 → 去除 HTML → 分词 → 去停用词 → 词形还原 → 用 BERT 分类 → 统计正面负面比例。"
            },
            {
                "id": "sec-3-1-3",
                "title": "1.3 词向量与嵌入",
                "content": "将文本转为数值向量，是计算机处理自然语言的前提。",
                "knowledge_points": [
                    "One-Hot 编码：简单但稀疏、维度大",
                    "TF-IDF：衡量词的重要性",
                    "Word2Vec：CBOW 和 Skip-gram 模型",
                    "GloVe：全局词向量",
                    "预训练词嵌入：直接使用"
                ],
                "case": "同义词检测：Word2Vec 学会「国王 - 男人 + 女人 ≈ 女王」，因为它从海量文本中学到了词汇的语义关系。"
            }
        ]
    },
    {
        "id": "ch-3-2",
        "title": "第二章：NLP 深度学习模型",
        "duration_minutes": 55,
        "summary": "掌握 BERT、GPT 等预训练模型在 NLP 任务中的应用。",
        "video_bv": "BV16G41167p1",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-3-2-1",
                "title": "2.1 BERT 与预训练语言模型",
                "content": "BERT 通过完形填空任务预训练，成为现代 NLP 的基础。",
                "knowledge_points": [
                    "BERT 架构：Transformer 编码器",
                    "预训练任务：MLM（Masked Language Model）",
                    "下游微调：分类、QA、命名实体",
                    "RoBERTa、ALBERT 等改进模型",
                    "Hugging Face 使用"
                ],
                "case": "法律文书分析：用 BERT 微调做合同条款分类 → 自动识别风险条款 → 生成审核报告。节省法务人员 70% 审核时间。"
            },
            {
                "id": "sec-3-2-2",
                "title": "2.2 文本生成与大语言模型",
                "content": "从 GPT 系列到 LLaMA，理解生成式语言模型的工作原理。",
                "knowledge_points": [
                    "GPT 系列演进：GPT-1 → GPT-2 → GPT-3 → GPT-4",
                    "自回归生成：逐 token 预测",
                    "采样策略：Greedy、Top-K、Top-P、Temperature",
                    "Instruction Tuning：让模型理解指令",
                    "RLHF：人类反馈强化学习"
                ],
                "case": "AI 写作助手：输入大纲 → GPT 生成初稿 → 人工修改润色。可用于新闻稿、营销文案、技术文档等场景。"
            }
        ]
    }
]

# Fix course-4: should be Data Science (not Computer Vision)
chapters_course4 = [
    {
        "id": "ch-4-1",
        "title": "第一章：Python 数据分析基础",
        "duration_minutes": 40,
        "summary": "掌握 NumPy 和 Pandas 两大核心库。",
        "video_bv": "BV15dA6eBECZ",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-4-1-1",
                "title": "1.1 NumPy 数值计算",
                "content": "NumPy 是科学计算的基础，提供高效多维数组。",
                "knowledge_points": [
                    "ndarray 创建：array()、zeros()、arange()",
                    "数组运算：逐元素运算、矩阵乘法",
                    "广播机制：不同形状数组的运算",
                    "索引与切片",
                    "reshape 与转置"
                ],
                "case": "图像处理：1080×1920 RGB 照片是 (1080,1920,3) 数组。用 NumPy 实现灰度转换、滤镜处理。"
            },
            {
                "id": "sec-4-1-2",
                "title": "1.2 Pandas 数据处理",
                "content": "Pandas 擅长处理表格型数据。",
                "knowledge_points": [
                    "DataFrame 创建：CSV、Excel、字典",
                    "数据清洗：缺失值、重复值、异常值",
                    "条件查询与筛选",
                    "groupby 分组聚合",
                    "merge/join 数据合并"
                ],
                "case": "销售分析：读 CSV → 清洗 → 按地区分组 → 统计销售额 → 找 Top-5 产品 → 生成报表。"
            }
        ]
    },
    {
        "id": "ch-4-2",
        "title": "第二章：数据可视化",
        "duration_minutes": 45,
        "summary": "使用 Matplotlib 和 Seaborn 生成专业图表。",
        "video_bv": "BV15dA6eBECZ",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-4-2-1",
                "title": "2.1 常用图表类型",
                "content": "选择正确的图表类型是有效传达洞察的第一步。",
                "knowledge_points": [
                    "折线图：展示趋势",
                    "柱状图：对比数值",
                    "散点图：变量关系",
                    "直方图：数据分布",
                    "饼图：占比（≤6类）"
                ],
                "case": "电商仪表盘：折线图展示 GMV 趋势 → 柱状图对比品类 → 散点图分析广告 ROI → 饼图展示流量来源。"
            },
            {
                "id": "sec-4-2-2",
                "title": "2.2 美化与定制",
                "content": "通过样式、颜色、标注让图表更专业。",
                "knowledge_points": [
                    "主题与样式：seaborn.set_style()",
                    "中文支持：设置字体",
                    "标注与注释",
                    "子图布局：subplot",
                    "高清导出：savefig"
                ],
                "case": "汇报图表：暗色主题 → 中文标签 → 关键点红色标注 → 趋势线注释 → 300dpi PNG 用于 PPT。"
            }
        ]
    }
]

# Fix course-6: Computer Vision (not NLP)
chapters_course6 = [
    {
        "id": "ch-6-1",
        "title": "第一章：图像处理基础",
        "duration_minutes": 45,
        "summary": "理解图像的数字表示，掌握常用处理技术。",
        "video_bv": "BV1oE421w7rB",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-6-1-1",
                "title": "1.1 图像表示与操作",
                "content": "图像本质上是多维数组。",
                "knowledge_points": [
                    "像素与分辨率",
                    "色彩空间：RGB/BGR/HSV",
                    "通道操作",
                    "几何变换：缩放、旋转、仿射",
                    "OpenCV 基础"
                ],
                "case": "文档扫描：拍摄 → 透视变换校正 → 灰度化 → 二值化 → 干净文档图像。"
            },
            {
                "id": "sec-6-1-2",
                "title": "1.2 特征提取",
                "content": "从图像中提取特征点、边缘、纹理。",
                "knowledge_points": [
                    "边缘检测：Sobel、Canny",
                    "特征点：Harris、SIFT、ORB",
                    "特征描述子",
                    "特征匹配",
                    "应用：图像拼接"
                ],
                "case": "全景图：多张照片 → SIFT 特征 → 匹配 → 变换矩阵 → 拼接。手机全景模式原理。"
            }
        ]
    },
    {
        "id": "ch-6-2",
        "title": "第二章：深度学习视觉应用",
        "duration_minutes": 55,
        "summary": "使用预训练模型实现分类、检测、分割。",
        "video_bv": "BV1oE421w7rB",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-6-2-1",
                "title": "2.1 图像分类与目标检测",
                "content": "图像分类判断「是什么」，目标检测回答「在哪里」。",
                "knowledge_points": [
                    "图像分类：整图 → 一个类别",
                    "目标检测：YOLO、Faster R-CNN",
                    "边界框 Bounding Box",
                    "预训练模型使用",
                    "微调 Fine-tuning"
                ],
                "case": "智能安防：摄像头 → YOLO 检测人/车 → 识别遗留物品 → 触发警报。"
            },
            {
                "id": "sec-6-2-2",
                "title": "2.2 图像分割与 OCR",
                "content": "语义分割精确定位，OCR 识别文字。",
                "knowledge_points": [
                    "语义分割：每像素一个类别",
                    "实例分割：区分同类实例",
                    "OCR：PaddleOCR、Tesseract",
                    "PaddlePaddle 框架",
                    "场景文本检测"
                ],
                "case": "AI 文档助手：拍摄名片 → 版面分析 → OCR 识别 → 提取姓名/电话 → 存入通讯录。"
            }
        ]
    }
]

# Also update titles/descriptions for all courses
course_updates = [
    ("course-3", "自然语言处理", "掌握 NLP 核心技术，包括文本处理、词向量、BERT、文本生成等。", "NLP", chapters_course3),
    ("course-4", "数据科学实战", "从零掌握 Python 数据分析全流程，包括数据清洗、可视化、统计分析。", "Data Science", chapters_course4),
    ("course-6", "计算机视觉入门", "从图像基础到目标检测，掌握计算机视觉的核心技术。", "Computer Vision", chapters_course6),
]

for cid, title, desc, topic, chapters in course_updates:
    cur.execute("""
        UPDATE courses SET title=?, description=?, topic=?, chapters=? WHERE id=?
    """, (title, desc, topic, json.dumps(chapters, ensure_ascii=False), cid))
    print(f"  Fixed {cid}: {title} ({len(chapters)} chapters)")

# Also fix course-0 and course-1 titles to Chinese
cur.execute("UPDATE courses SET title='AI 机器学习基础', description='从零掌握机器学习核心算法，包括线性回归、分类、决策树等经典模型。' WHERE id='course-0'")
cur.execute("UPDATE courses SET title='深度学习与神经网络', description='掌握深度神经网络的核心架构，包括 CNN、RNN、Transformer。' WHERE id='course-1'")
cur.execute("UPDATE courses SET title='LLM 应用开发实战', description='掌握 Prompt Engineering、RAG、Agent 等大模型应用开发核心技术。' WHERE id='course-2'")
cur.execute("UPDATE courses SET title='Python 编程与工具', description='掌握 Python 编程语言及其在 AI 开发中的应用。' WHERE id='course-5'")
cur.execute("UPDATE courses SET title='强化学习入门', description='理解强化学习的基本概念，掌握 Q-Learning、DQN 等核心算法。' WHERE id='course-7'")

conn.commit()

# Verify
rows = cur.execute("SELECT id, title, topic FROM courses").fetchall()
print(f"\n=== Final Course List ===")
for row in rows:
    ch_row = cur.execute("SELECT chapters FROM courses WHERE id=?", (row['id'],)).fetchone()
    ch_data = json.loads(ch_row['chapters']) if ch_row['chapters'] else []
    has_sections = len(ch_data) > 0 and 'sections' in ch_data[0] if ch_data else False
    print(f"  {row['id']}: {row['title']} [{row['topic']}] ({len(ch_data)} chapters) {'✅' if has_sections else '⚠️'}")

conn.close()
print("\nDone!")