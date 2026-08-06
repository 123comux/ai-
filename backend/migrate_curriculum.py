"""
Course curriculum migration script.
Updates courses with detailed chapter structures.
"""
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "cms.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("Starting curriculum migration...")

# ============ 课程 0：AI 机器学习基础 ============
chapters_course0 = [
    {
        "id": "ch-0-1",
        "title": "第一章：机器学习入门",
        "duration_minutes": 45,
        "summary": "理解什么是机器学习、它能做什么，以及学习环境的搭建。",
        "video_bv": "BV1Bq421A74G",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-0-1-1",
                "title": "1.1 什么是机器学习",
                "content": "机器学习是让计算机从数据中自动学习规律，而不需要被显式编程的一门学科。它是人工智能的核心技术。",
                "knowledge_points": [
                    "机器学习定义：从数据中学习规律并做出预测的方法",
                    "机器学习 vs 传统编程：传统编程是人写规则，机器学习是机器从数据中归纳规则",
                    "机器学习三种类型：监督学习（有标签）、无监督学习（无标签）、强化学习（通过反馈学习）"
                ],
                "case": "垃圾邮件过滤：系统通过分析大量已标记的邮件（垃圾/正常），自动学习识别垃圾邮件的特征（如关键词、发件人等），然后对新邮件进行分类。"
            },
            {
                "id": "sec-0-1-2",
                "title": "1.2 机器学习的应用场景",
                "content": "机器学习已广泛应用于推荐系统、搜索引擎、自动驾驶、医疗诊断、自然语言处理等领域。",
                "knowledge_points": [
                    "推荐系统：电商网站根据用户浏览/购买历史推荐商品",
                    "图像识别：手机相册自动识别人脸、宠物、食物",
                    "语音助手：Siri、小爱同学理解并响应语音指令",
                    "医疗辅助：AI 辅助医生检测疾病（如肺部 CT 影像分析）"
                ],
                "case": "抖音推荐算法：你每次点赞、完播、评论都是在给模型「标注数据」，系统持续学习你的喜好，推荐越来越精准的视频。"
            },
            {
                "id": "sec-0-1-3",
                "title": "1.3 开发环境搭建",
                "content": "安装 Python、Anaconda、Jupyter Notebook，配置机器学习核心库。",
                "knowledge_points": [
                    "Python 3.8+：机器学习主流编程语言",
                    "NumPy：数值计算基础，高效多维数组运算",
                    "Pandas：数据处理与分析的瑞士军刀",
                    "Scikit-learn：经典机器学习算法库",
                    "Matplotlib/Seaborn：数据可视化"
                ],
                "case": "数据科学家的日常：用 Pandas 加载 CSV 数据 → 用 Matplotlib 画图表理解数据 → 用 Scikit-learn 训练模型 → 评估模型效果。"
            }
        ]
    },
    {
        "id": "ch-0-2",
        "title": "第二章：线性回归与梯度下降",
        "duration_minutes": 60,
        "summary": "实现最简单的机器学习算法——线性回归，理解损失函数和梯度下降优化原理。",
        "video_bv": "BV1Bq421A74G",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-0-2-1",
                "title": "2.1 线性回归原理",
                "content": "线性回归通过拟合一条直线（或超平面）来描述输入特征与输出之间的线性关系。",
                "knowledge_points": [
                    "假设函数：h(x) = w·x + b，w 是权重，b 是偏置",
                    "损失函数：衡量预测值与真实值之间的差距，常用均方误差（MSE）",
                    "目标：找到使损失最小的 w 和 b"
                ],
                "case": "房价预测模型：已知房屋面积、房间数等特征，预测房价。模型学到的权重可以理解为：面积每增加 1 平方米，房价平均增加多少。"
            },
            {
                "id": "sec-0-2-2",
                "title": "2.2 梯度下降优化",
                "content": "梯度下降是最基本的优化算法，通过沿梯度反方向更新参数来最小化损失。",
                "knowledge_points": [
                    "梯度：函数对参数的偏导数，表示损失变化最快的方向",
                    "学习率（α）：每次更新的步长，太大会发散，太小收敛慢",
                    "批量/随机/小批量梯度下降的区别",
                    "收敛条件：损失不再下降或达到迭代次数上限"
                ],
                "case": "想象你在山上蒙着眼，要走到山谷最低点。梯度下降就是：感受脚下坡度最陡的方向，迈出一步（步长就是学习率），重复直到感觉差不多平了。"
            },
            {
                "id": "sec-0-2-3",
                "title": "2.3 特征缩放与多项式特征",
                "content": "当特征值范围差异大时需要缩放；可以通过多项式特征拟合非线性关系。",
                "knowledge_points": [
                    "特征缩放：将特征缩放到相同范围",
                    "Min-Max 归一化：(x - min) / (max - min)",
                    "Z-Score 标准化：(x - mean) / std",
                    "多项式特征：添加 x²、x³ 等高阶项拟合曲线"
                ],
                "case": "预测房价时，面积（几十到几百）和房间数（1-5）范围差异大。不做缩放的话，面积的影响会被过度放大，梯度下降收敛很慢。"
            }
        ]
    },
    {
        "id": "ch-0-3",
        "title": "第三章：分类算法",
        "duration_minutes": 60,
        "summary": "学习逻辑回归、SVM、决策树等分类算法，解决「是或否」的问题。",
        "video_bv": "BV1Bq421A74G",
        "video_page": 3,
        "sections": [
            {
                "id": "sec-0-3-1",
                "title": "3.1 逻辑回归",
                "content": "逻辑回归将线性输出通过 Sigmoid 函数转为 0-1 概率，是最常用的二分类算法。",
                "knowledge_points": [
                    "Sigmoid 函数：σ(z) = 1/(1+e^(-z))，将任意值映射到 0-1",
                    "决策边界：当 σ(w·x + b) > 0.5 时判为正类",
                    "交叉熵损失：适合分类问题的损失函数",
                    "多分类：Softmax 回归（一对多策略）"
                ],
                "case": "邮件分类：一封邮件经过逻辑回归计算，得到「垃圾邮件」概率为 0.92，系统将其归为垃圾邮件。"
            },
            {
                "id": "sec-0-3-2",
                "title": "3.2 支持向量机 (SVM)",
                "content": "SVM 寻找使两类样本间隔最大的超平面，在小样本上表现优异。",
                "knowledge_points": [
                    "最大间隔分类器：寻找 margin 最大的决策边界",
                    "软间隔：允许部分样本违反边界",
                    "核函数：线性核、高斯核、多项式核",
                    "SVM 适合中小规模数据集"
                ],
                "case": "人脸识别：SVM 在高维特征空间中寻找不同人脸之间的最大间隔，实现高精度分类。"
            },
            {
                "id": "sec-0-3-3",
                "title": "3.3 决策树与随机森林",
                "content": "决策树像流程图一样做出一系列判断；随机森林通过多棵树投票提高准确率。",
                "knowledge_points": [
                    "信息增益/基尼不纯度：选择最佳分裂特征",
                    "过拟合与剪枝：树太深会过拟合",
                    "随机森林：多棵树 + 随机特征选择 → 投票",
                    "集成学习思想：多个弱分类器组合成强分类器"
                ],
                "case": "贷款审批：决策树依次判断「信用分 > 700?」→「收入稳定?」→「负债比 < 30%?」，最终给出批准或拒绝。"
            }
        ]
    },
    {
        "id": "ch-0-4",
        "title": "第四章：模型评估与选择",
        "duration_minutes": 50,
        "summary": "学会用正确的指标评估模型，掌握交叉验证和模型选择的方法。",
        "video_bv": "BV1Bq421A74G",
        "video_page": 4,
        "sections": [
            {
                "id": "sec-0-4-1",
                "title": "4.1 模型评估指标",
                "content": "不同问题需要不同的评估指标，选择合适的指标至关重要。",
                "knowledge_points": [
                    "准确率 (Accuracy)：正确预测数 / 总样本数",
                    "精确率 (Precision)：预测为正的样本中真正为正的比例",
                    "召回率 (Recall)：真正为正的样本中被正确预测的比例",
                    "F1-Score：精确率和召回率的调和平均",
                    "ROC 曲线与 AUC"
                ],
                "case": "疾病检测：假设 95% 的人是健康的。一个总说「健康」的模型准确率 95%，但毫无价值。应关注召回率。"
            },
            {
                "id": "sec-0-4-2",
                "title": "4.2 过拟合与欠拟合",
                "content": "模型复杂度与泛化能力的权衡是机器学习的永恒主题。",
                "knowledge_points": [
                    "过拟合：训练集好，测试集差（学到了噪声）",
                    "欠拟合：训练集和测试集都差（没学到规律）",
                    "偏差-方差权衡",
                    "正则化：L1/L2 防止过拟合"
                ],
                "case": "考试复习：过拟合 = 死记硬背答案；欠拟合 = 连基本概念都没掌握；正则化 = 理解原理。"
            },
            {
                "id": "sec-0-4-3",
                "title": "4.3 交叉验证与模型选择",
                "content": "使用交叉验证充分利用数据，选择最佳模型和超参数。",
                "knowledge_points": [
                    "K 折交叉验证：K 份数据轮流训练验证",
                    "超参数调优：网格搜索 vs 随机搜索",
                    "学习曲线：诊断过拟合/欠拟合",
                    "特征重要性分析"
                ],
                "case": "选择最佳分类器：用 5 折交叉验证分别测试逻辑回归、SVM、随机森林，比较平均 AUC。"
            }
        ]
    }
]

cur.execute("UPDATE courses SET chapters=? WHERE id='course-0'", (json.dumps(chapters_course0, ensure_ascii=False),))
print("  Updated course-0: AI 机器学习基础")

# ============ 课程 1：深度学习 ============
chapters_course1 = [
    {
        "id": "ch-1-1",
        "title": "第一章：神经网络基础",
        "duration_minutes": 45,
        "summary": "理解生物神经元到人工神经元的演进，搭建你的第一个神经网络。",
        "video_bv": "BV1LxPMzGEvF",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-1-1-1",
                "title": "1.1 感知机与多层感知机",
                "content": "人工神经元模拟生物神经元的工作方式，通过组合形成强大的计算能力。",
                "knowledge_points": [
                    "生物神经元：树突接收 → 细胞体处理 → 轴突传递",
                    "感知机：最简单的人工神经元",
                    "多层感知机 (MLP)：输入层 → 隐藏层 → 输出层",
                    "通用逼近定理：足够深的 MLP 可以逼近任何函数"
                ],
                "case": "异或问题：单层感知机无法解决 XOR（非线性），但两层感知机就可以。这说明了深度网络的必要性。"
            },
            {
                "id": "sec-1-1-2",
                "title": "1.2 激活函数",
                "content": "激活函数给网络引入非线性，是神经网络的灵魂。",
                "knowledge_points": [
                    "Sigmoid：输出 0-1，适合二分类输出层",
                    "Tanh：输出 -1 到 1，零中心化",
                    "ReLU：max(0, x)，缓解梯度消失",
                    "LeakyReLU：解决 ReLU「神经元死亡」",
                    "选择建议：隐藏层用 ReLU"
                ],
                "case": "为什么不用 Sigmoid 做隐藏层？输入较大时梯度趋近于 0，深层网络训练困难。ReLU 在正区间梯度恒为 1。"
            },
            {
                "id": "sec-1-1-3",
                "title": "1.3 反向传播算法",
                "content": "反向传播是训练神经网络的核心算法，高效计算每个参数的梯度。",
                "knowledge_points": [
                    "计算图：表示神经网络的所有计算步骤",
                    "链式法则：从输出层向输入层逐层计算梯度",
                    "参数更新：w = w - α * ∂Loss/∂w",
                    "PyTorch 自动微分：autograd"
                ],
                "case": "网络预测数字「7」但实际是「3」，损失很大。反向传播告诉每个神经元「你应该多或少激活」，调整权重，最终学会正确预测。"
            }
        ]
    },
    {
        "id": "ch-1-2",
        "title": "第二章：卷积神经网络 (CNN)",
        "duration_minutes": 60,
        "summary": "CNN 是图像领域的王者，掌握卷积、池化、经典架构。",
        "video_bv": "BV1F4411y7o7",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-1-2-1",
                "title": "2.1 卷积操作详解",
                "content": "卷积是 CNN 的核心操作，通过滑动窗口提取图像的局部特征。",
                "knowledge_points": [
                    "卷积核：学习的特征提取器",
                    "步长/填充：控制特征图大小",
                    "感受野：输出特征图对应的输入区域",
                    "多通道：RGB 三通道 → 卷积核也有三通道"
                ],
                "case": "边缘检测：3×3 卷积核中心是 1 周围是 -1，滑动过图像时在边缘输出高值。CNN 通过训练自动学习这些核。"
            },
            {
                "id": "sec-1-2-2",
                "title": "2.2 池化与经典架构",
                "content": "池化减少特征图尺寸，经典架构包括 LeNet、AlexNet、VGG、ResNet。",
                "knowledge_points": [
                    "最大/平均池化：减少计算量",
                    "Dropout：随机丢弃神经元防过拟合",
                    "ResNet 残差连接：解决深层网络退化",
                    "迁移学习：用预训练模型 + 微调"
                ],
                "case": "图像分类：下载 CIFAR-10 → 用预训练 ResNet50 → 替换全连接层 → 冻结前面层只训练新层 → 准确率 90%+。"
            }
        ]
    },
    {
        "id": "ch-1-3",
        "title": "第三章：序列模型与 Transformer",
        "duration_minutes": 60,
        "summary": "从 RNN 到 LSTM 再到 Transformer，理解现代 NLP 的核心架构。",
        "video_bv": "BV1fGeAz6Eie",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-1-3-1",
                "title": "3.1 RNN 与 LSTM",
                "content": "循环神经网络处理序列数据，LSTM 解决了长距离依赖问题。",
                "knowledge_points": [
                    "RNN：对序列每个元素做相同操作",
                    "梯度消失：长序列训练困难",
                    "LSTM：输入门、遗忘门、输出门",
                    "GRU：简化版 LSTM"
                ],
                "case": "文本生成：给 LSTM 一个开头，它根据学到的语料继续生成。每个词的生成都依赖前面所有词。"
            },
            {
                "id": "sec-1-3-2",
                "title": "3.2 Transformer 架构",
                "content": "Transformer 抛弃循环，用注意力机制实现并行化，是大模型的基础。",
                "knowledge_points": [
                    "自注意力机制：每个 token 关注序列中所有其他 token",
                    "QKV：Query/Key/Value 计算注意力",
                    "多头注意力：并行学习多种注意力模式",
                    "位置编码：补充序列顺序信息",
                    "Encoder-Decoder 架构"
                ],
                "case": "翻译：输入「我喜欢机器学习」，编码器处理每个词，解码器生成「I love machine learning」。"
            },
            {
                "id": "sec-1-3-3",
                "title": "3.3 BERT 与 GPT 对比",
                "content": "理解两大预训练模型家族的设计理念和适用场景差异。",
                "knowledge_points": [
                    "BERT：双向编码器，擅长理解",
                    "GPT：单向解码器，擅长生成",
                    "预训练任务：MLM vs 因果语言模型",
                    "Fine-tuning：在下游任务上微调"
                ],
                "case": "智能客服：BERT 理解用户问题（意图识别），GPT 生成自然回复。"
            }
        ]
    }
]

cur.execute("UPDATE courses SET chapters=? WHERE id='course-1'", (json.dumps(chapters_course1, ensure_ascii=False),))
print("  Updated course-1: 深度学习与神经网络")

# ============ 课程 2：LLM 应用开发 ============
chapters_course2 = [
    {
        "id": "ch-2-1",
        "title": "第一章：Prompt Engineering",
        "duration_minutes": 50,
        "summary": "掌握与大模型对话的艺术，设计高质量的提示词。",
        "video_bv": "BV1Esx5zXEPB",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-2-1-1",
                "title": "1.1 Prompt 基础原则",
                "content": "好的 Prompt 应该清晰、具体、有上下文。",
                "knowledge_points": [
                    "清晰明确：直接说明任务",
                    "提供上下文：补充背景信息",
                    "指定角色：让模型扮演专家",
                    "给出示例：few-shot 引导",
                    "分步思考：要求 CoT 推理"
                ],
                "case": "差：「写点东西」→ 好：「你是资深技术写作者。用通俗易懂的语言写一篇 500 字博客，介绍 Transformer，含一个类比。」"
            },
            {
                "id": "sec-2-1-2",
                "title": "1.2 高级 Prompt 技巧",
                "content": "掌握 Chain-of-Thought、Role-based 等高级提示技术。",
                "knowledge_points": [
                    "CoT：让模型展示推理过程",
                    "Few-shot：提供示例引导",
                    "Role-based：指定角色身份",
                    "Structured Output：要求 JSON 格式",
                    "迭代优化：根据输出调整 Prompt"
                ],
                "case": "数学题：先让模型「一步一步思考」，再要求「给出最终答案」。CoT 可显著提升推理准确率。"
            }
        ]
    },
    {
        "id": "ch-2-2",
        "title": "第二章：RAG 检索增强生成",
        "duration_minutes": 60,
        "summary": "构建 RAG 系统，让大模型基于你的私有知识回答问题。",
        "video_bv": "BV1Esx5zXEPB",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-2-2-1",
                "title": "2.1 RAG 核心概念",
                "content": "RAG = 检索 + 生成，从知识库找到相关信息作为上下文。",
                "knowledge_points": [
                    "向量化：文本 → 高维向量",
                    "向量数据库：FAISS、ChromaDB",
                    "相似度搜索：余弦相似度",
                    "Prompt 组装：问题 + 检索结果",
                    "优点：知识可更新、可溯源、减幻觉"
                ],
                "case": "企业知识库问答：员工提问 → 检索 3 个相关文档 → 拼接进 Prompt → LLM 生成答案 + 附上文档来源。"
            },
            {
                "id": "sec-2-2-2",
                "title": "2.2 RAG 系统搭建",
                "content": "使用 Python 搭建完整的 RAG 系统。",
                "knowledge_points": [
                    "文档分块：500 字 + 50 字重叠",
                    "Embedding 模型：BGE-M3 等",
                    "检索优化：HyDE、重排序",
                    "评估：Faithfulness、Answer Relevance",
                    "框架：LangChain / LlamaIndex"
                ],
                "case": "技术文档问答：加载 Markdown → 分块 → BGE-M3 向量化 → 存入 ChromaDB → 用户提问检索 Top-3 → 拼接 Prompt 调用 LLM。"
            }
        ]
    },
    {
        "id": "ch-2-3",
        "title": "第三章：Agent 与工具使用",
        "duration_minutes": 55,
        "summary": "让 LLM 自主规划任务、调用工具、多步推理。",
        "video_bv": "BV1Esx5zXEPB",
        "video_page": 3,
        "sections": [
            {
                "id": "sec-2-3-1",
                "title": "3.1 Agent 基础",
                "content": "Agent = LLM + 工具 + 记忆 + 规划。",
                "knowledge_points": [
                    "ReAct：推理 → 行动 → 观察循环",
                    "工具定义：函数描述 + 参数 Schema",
                    "Function Calling：LLM 决定调用时机",
                    "Memory：短期 + 长期记忆",
                    "Planning：分解复杂任务"
                ],
                "case": "数据分析 Agent：用户说「分析上月销售数据」→ 分解为：查数据 → 处理 → 画图表 → 写报告。"
            },
            {
                "id": "sec-2-3-2",
                "title": "3.2 LangChain 实践",
                "content": "使用 LangChain 框架快速构建 LLM 应用。",
                "knowledge_points": [
                    "Chain 组合：PromptChain、SequentialChain",
                    "@tool 装饰器定义工具",
                    "Agent Executor：核心运行循环",
                    "LCEL：表达式语言",
                    "常用工具：搜索、数据库、代码执行"
                ],
                "case": "智能研究助手：整合搜索 API + 代码执行器 + 文档生成器。用户提问后，Agent 搜索 → 验证 → 写报告。"
            }
        ]
    }
]

cur.execute("UPDATE courses SET chapters=? WHERE id='course-2'", (json.dumps(chapters_course2, ensure_ascii=False),))
print("  Updated course-2: LLM 应用开发实战")

# ============ 课程 3：数据科学 ============
chapters_course3 = [
    {
        "id": "ch-3-1",
        "title": "第一章：Python 数据分析基础",
        "duration_minutes": 40,
        "summary": "掌握 NumPy 和 Pandas 两大核心库。",
        "video_bv": "BV15dA6eBECZ",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-3-1-1",
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
                "id": "sec-3-1-2",
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
        "id": "ch-3-2",
        "title": "第二章：数据可视化",
        "duration_minutes": 45,
        "summary": "使用 Matplotlib 和 Seaborn 生成专业图表。",
        "video_bv": "BV15dA6eBECZ",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-3-2-1",
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
                "id": "sec-3-2-2",
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

cur.execute("UPDATE courses SET chapters=? WHERE id='course-3'", (json.dumps(chapters_course3, ensure_ascii=False),))
print("  Updated course-3: 数据科学实战")

# ============ 课程 4：计算机视觉 ============
chapters_course4 = [
    {
        "id": "ch-4-1",
        "title": "第一章：图像处理基础",
        "duration_minutes": 45,
        "summary": "理解图像的数字表示，掌握常用处理技术。",
        "video_bv": "BV1F4411y7o7",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-4-1-1",
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
                "id": "sec-4-1-2",
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
        "id": "ch-4-2",
        "title": "第二章：深度学习视觉应用",
        "duration_minutes": 55,
        "summary": "使用预训练模型实现分类、检测、分割。",
        "video_bv": "BV1F4411y7o7",
        "video_page": 3,
        "sections": [
            {
                "id": "sec-4-2-1",
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
                "id": "sec-4-2-2",
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

cur.execute("UPDATE courses SET chapters=? WHERE id='course-4'", (json.dumps(chapters_course4, ensure_ascii=False),))
print("  Updated course-4: 计算机视觉入门")

# ============ 课程 5：Python ============
chapters_course5 = [
    {
        "id": "ch-5-1",
        "title": "第一章：Python 基础语法",
        "duration_minutes": 40,
        "summary": "快速掌握 Python 核心语法。",
        "video_bv": "BV1c4411e7bE",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-5-1-1",
                "title": "1.1 变量、数据类型与控制流",
                "content": "Python 动态类型系统。",
                "knowledge_points": [
                    "变量命名规则",
                    "基本类型：int/float/str/bool",
                    "列表、字典、元组、集合",
                    "if/elif/else",
                    "for/while 循环"
                ],
                "case": "温度转换器：读取摄氏温度 → 转换华氏温度 → 格式化输出。涉及类型转换、格式化字符串。"
            },
            {
                "id": "sec-5-1-2",
                "title": "1.2 函数与模块",
                "content": "封装代码为函数，使用模块组织代码。",
                "knowledge_points": [
                    "def 定义函数",
                    "默认/可变参数",
                    "返回多个值",
                    "import 导入",
                    "虚拟环境 venv"
                ],
                "case": "数据处理工具：封装读取 CSV、清洗数据、生成统计的函数。"
            }
        ]
    },
    {
        "id": "ch-5-2",
        "title": "第二章：面向对象编程",
        "duration_minutes": 50,
        "summary": "使用类和对象编写结构化代码。",
        "video_bv": "BV1r4411k7De",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-5-2-1",
                "title": "2.1 类与对象",
                "content": "Python 面向对象核心。",
                "knowledge_points": [
                    "class 定义",
                    "__init__ 构造方法",
                    "self 指向实例",
                    "封装、继承、多态",
                    "魔法方法"
                ],
                "case": "学生管理系统：Student 类（姓名、成绩）→ School 类管理多个 Student。"
            },
            {
                "id": "sec-5-2-2",
                "title": "2.2 常用设计模式",
                "content": "学习常见设计模式。",
                "knowledge_points": [
                    "单例模式",
                    "工厂模式",
                    "观察者模式",
                    "上下文管理器 with",
                    "装饰器 @decorator"
                ],
                "case": "日志系统：装饰器实现日志记录；单例实现全局配置。"
            }
        ]
    }
]

cur.execute("UPDATE courses SET chapters=? WHERE id='course-5'", (json.dumps(chapters_course5, ensure_ascii=False),))
print("  Updated course-5: Python 编程与工具")

# ============ 课程 7：强化学习 ============
chapters_course7 = [
    {
        "id": "ch-7-1",
        "title": "第一章：强化学习基础",
        "duration_minutes": 40,
        "summary": "理解强化学习框架：智能体、环境、状态、动作、奖励。",
        "video_bv": "BV1Lhx5zUEgG",
        "video_page": 1,
        "sections": [
            {
                "id": "sec-7-1-1",
                "title": "1.1 MDP 与 Bellman 方程",
                "content": "强化学习的数学基础是马尔可夫决策过程。",
                "knowledge_points": [
                    "MDP 五元组：状态/动作/转移/奖励/折扣",
                    "价值函数 V(s) 和 Q(s,a)",
                    "Bellman 递推方程",
                    "探索与利用权衡"
                ],
                "case": "走格子游戏：智能体在 4×4 网格移动，目标是终点。学习最优路径。"
            },
            {
                "id": "sec-7-1-2",
                "title": "1.2 动态规划求解",
                "content": "用 Value Iteration 和 Policy Iteration 求解 MDP。",
                "knowledge_points": [
                    "价值迭代 Bellman 最优方程",
                    "策略迭代：评估 + 改进",
                    "收敛条件",
                    "计算复杂度"
                ],
                "case": "网格世界：价值迭代计算每个格子的价值 → 选择最优邻居 → 最短路径。"
            }
        ]
    },
    {
        "id": "ch-7-2",
        "title": "第二章：无模型强化学习",
        "duration_minutes": 50,
        "summary": "环境模型未知时，使用蒙特卡洛和时序差分方法。",
        "video_bv": "BV1Lhx5zUEgG",
        "video_page": 2,
        "sections": [
            {
                "id": "sec-7-2-1",
                "title": "2.1 Q-Learning 算法",
                "content": "最经典的无模型强化学习算法。",
                "knowledge_points": [
                    "Q-Learning 更新规则",
                    "ε-greedy 探索策略",
                    "Q 表维护",
                    "SARSA vs Q-Learning",
                    "收敛条件"
                ],
                "case": "Atari 游戏：游戏状态 → 选择动作 → 获得奖励 → 更新 Q 值 → 分数超过人类。"
            },
            {
                "id": "sec-7-2-2",
                "title": "2.2 深度强化学习",
                "content": "神经网络近似 Q 函数，处理高维状态。",
                "knowledge_points": [
                    "DQN：深度 Q 网络",
                    "经验回放 Experience Replay",
                    "目标网络 Target Network",
                    "Double DQN",
                    "Policy Gradient"
                ],
                "case": "自动驾驶：摄像头像素 → DQN 输出 Q 值 → 选择加速/刹车/转向 → 仿真训练。"
            }
        ]
    }
]

cur.execute("UPDATE courses SET chapters=? WHERE id='course-7'", (json.dumps(chapters_course7, ensure_ascii=False),))
print("  Updated course-7: 强化学习入门")

conn.commit()

# Verify
rows = cur.execute("SELECT id, title FROM courses").fetchall()
print(f"\n=== Updated {len(rows)} Courses ===")
for row in rows:
    ch_row = cur.execute("SELECT chapters FROM courses WHERE id=?", (row['id'],)).fetchone()
    ch_data = json.loads(ch_row['chapters']) if ch_row['chapters'] else []
    has_sections = len(ch_data) > 0 and 'sections' in ch_data[0] if ch_data else False
    print(f"  {row['id']}: {row['title']} ({len(ch_data)} chapters) {'✅' if has_sections else '⚠️'}")

conn.close()
print("\nMigration complete!")