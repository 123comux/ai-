# AI 模型训练方案

## Context（背景）

当前小程序后端已下载 15,105 条真实 AI 教育数据（StudyChat 16,851 条辅导对话 + FineWeb-Edu 1,000 条教育内容），但这些数据仅用于 JSON 文件搜索和规则匹配，**没有任何真正的 AI 模型**。

用户要用这些数据训练三个 AI 模型，让小程序具备真正的 AI 能力：
1. **AI 导师对话模型** — 能回答学生 AI 相关问题
2. **能力测评模型** — 根据学生提问内容自动评估能力水平
3. **课程推荐模型** — 根据学生兴趣智能推荐课程

**硬件**：RTX 4060 Laptop, 8GB 显存, CUDA 12.7

---

## 方案概览

### 模型 1：AI 导师对话模型（LoRA 微调）

| 项目 | 选择 |
|------|------|
| 基座模型 | Qwen2.5-1.5B-Instruct（阿里开源，中文友好） |
| 微调方法 | LoRA 4bit 量化微调（QLoRA） |
| 训练数据 | StudyChat 16,851 条 prompt-response 对 |
| 显存占用 | ~5 GB（8GB 够用） |
| 预计训练时间 | 1-2 小时 |
| 部署方式 | 后端 API `/api/tutor/chat` |

**数据格式转换**：StudyChat 的 `prompt` → `response` 转为 Qwen 的 ChatML 对话格式：
```
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
{response}<|im_end|>
```

### 模型 2：能力测评模型（BERT 分类器）

| 项目 | 选择 |
|------|------|
| 基座模型 | bert-base-chinese（110M 参数） |
| 任务类型 | 文本分类（输入学生提问 → 输出知识领域 + 难度） |
| 训练数据 | StudyChat 数据（用 topic + interaction_count 自动标注） |
| 显存占用 | ~2.5 GB |
| 预计训练时间 | 20-30 分钟 |
| 部署方式 | 后端 API `/api/assessment/analyze` |

**自动标注策略**：
- **知识领域**（从 prompt 内容关键词分类）：机器学习、深度学习、数据科学、编程基础、数学统计
- **难度等级**（按 interaction_count 划分）：< 5 次 = beginner, 5-10 = intermediate, > 10 = advanced

### 模型 3：课程推荐模型

| 项目 | 选择 |
|------|------|
| 方法 | TF-IDF + 余弦相似度（基于内容推荐） |
| 训练数据 | knowledge_base.json 15,105 条 |
| 计算资源 | CPU 即可，不需要 GPU |
| 预计训练时间 | < 1 分钟 |
| 部署方式 | 后端 API `/api/recommend/courses` |

---

## 实施步骤

### Step 1：安装训练依赖

在 `backend/requirements.txt` 中追加：
```
torch==2.4.0
transformers==4.44.0
peft==0.12.0
bitsandbytes==0.43.3
accelerate==0.33.0
scikit-learn==1.5.1
```

执行 `pip install` 安装。

### Step 2：创建训练目录结构

```
backend/
├── training/
│   ├── __init__.py
│   ├── prepare_tutor_data.py      # StudyChat → ChatML 训练格式
│   ├── prepare_assessment_data.py # StudyChat → 分类标注数据
│   ├── train_tutor.py             # LoRA 微调 Qwen2.5-1.5B
│   ├── train_assessment.py        # 微调 BERT 分类器
│   ├── build_recommender.py       # 构建 TF-IDF 推荐模型
│   └── utils.py                   # 通用工具函数
├── models/                        # 训练好的模型存放
│   ├── tutor/                     # Qwen LoRA adapter
│   ├── assessment/                # BERT 分类器
│   └── recommender/               # TF-IDF 矢量（joblib 序列化）
```

### Step 3：AI 导师对话模型训练

**文件**：`backend/training/prepare_tutor_data.py` + `train_tutor.py`

1. 读取 `data/raw/studychat/studychat.jsonl`
2. 过滤掉过短（prompt < 10 字符）和过长（> 1024 token）的数据
3. 转为 ChatML 格式，保存为 `data/processed/tutor_train.jsonl`
4. 使用 QLoRA 配置微调：
   - 4bit 量化（bitsandbytes）
   - LoRA rank=8, alpha=16
   - batch_size=2, gradient_accumulation=4
   - learning_rate=2e-4
   - max_seq_length=1024
   - epochs=3
5. 保存 LoRA adapter 到 `models/tutor/`

### Step 4：能力测评模型训练

**文件**：`backend/training/prepare_assessment_data.py` + `train_assessment.py`

1. 读取 StudyChat 数据
2. 用关键词匹配自动标注知识领域（ML/DL/DataSci/Programming/Math）
3. 用 interaction_count 标注难度等级
4. 8:2 划分训练集/验证集
5. 微调 bert-base-chinese：
   - max_length=256
   - batch_size=16
   - epochs=5
   - 多任务输出：领域分类（5类）+ 难度分类（3类）
6. 保存模型到 `models/assessment/`

### Step 5：课程推荐模型构建

**文件**：`backend/training/build_recommender.py`

1. 读取 `data/processed/knowledge_base.json`
2. 对每条内容的 title + content 做 TF-IDF 向量化
3. 用 scikit-learn 的 `TfidfVectorizer` + `cosine_similarity`
4. 序列化保存到 `models/recommender/tfidf_model.joblib`

### Step 6：后端 API 集成

**新增路由文件**：`backend/routers/ai.py`

```
POST /api/tutor/chat        → AI 导师对话（流式返回）
POST /api/assessment/analyze → 能力分析（输入学生提问内容）
GET  /api/recommend/courses  → 课程推荐（基于学生兴趣）
```

**新增服务文件**：
- `backend/services/tutor_service.py` — 加载 Qwen LoRA 模型，生成回答
- `backend/services/assessment_ai_service.py` — 加载 BERT 模型，分类预测
- `backend/services/recommend_service.py` — 加载 TF-IDF 模型，推荐课程

**修改**：`backend/main.py` 注册新路由

### Step 7：前端对接

修改 `src/services/api.ts`，新增三个 API 调用函数：
- `askTutor(question)` → POST `/api/tutor/chat`
- `analyzeAbility(content)` → POST `/api/assessment/analyze`
- `getRecommendedCourses(interest)` → GET `/api/recommend/courses`

---

## 关键文件清单

| 操作 | 文件路径 |
|------|---------|
| 修改 | `backend/requirements.txt`（追加训练依赖） |
| 新建 | `backend/training/__init__.py` |
| 新建 | `backend/training/utils.py` |
| 新建 | `backend/training/prepare_tutor_data.py` |
| 新建 | `backend/training/train_tutor.py` |
| 新建 | `backend/training/prepare_assessment_data.py` |
| 新建 | `backend/training/train_assessment.py` |
| 新建 | `backend/training/build_recommender.py` |
| 新建 | `backend/routers/ai.py` |
| 新建 | `backend/services/tutor_service.py` |
| 新建 | `backend/services/assessment_ai_service.py` |
| 新建 | `backend/services/recommend_service.py` |
| 修改 | `backend/main.py`（注册 ai 路由） |
| 修改 | `src/services/api.ts`（新增 AI API 调用） |

---

## 验证方案

1. **模型训练验证**：
   - 每个训练脚本完成后输出 loss 曲线和评估指标
   - 导师模型：抽样 5 条测试问题，检查回答质量
   - 测评模型：输出验证集准确率（目标 > 70%）
   - 推荐模型：输入 "machine learning"，检查返回的课程相关性

2. **API 集成验证**：
   ```bash
   # AI 导师
   curl -X POST http://localhost:8000/api/tutor/chat \
     -H "Content-Type: application/json" \
     -d '{"question":"什么是梯度下降？"}'

   # 能力分析
   curl -X POST http://localhost:8000/api/assessment/analyze \
     -H "Content-Type: application/json" \
     -d '{"content":"我想了解神经网络的反向传播"}'

   # 课程推荐
   curl "http://localhost:8000/api/recommend/courses?interest=deep+learning"
   ```

3. **端到端验证**：通过小程序预览，测试 AI 导师对话和能力分析功能

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| 8GB 显存不足 | Qwen 用 4bit 量化 + 小 batch size；BERT 用 max_length=256 |
| 训练时间过长 | 先用 1000 条数据试跑，确认无错后再全量训练 |
| 模型推理慢 | 后端启动时预加载模型；设置最大生成长度限制 |
| Qwen 模型下载慢 | 配置 HF 镜像或代理（已配置 Clash SOCKS5） |
