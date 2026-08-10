"""
Seed data generator - creates comprehensive synthetic AI training dataset.

When HuggingFace datasets are not accessible (network restrictions),
this script generates structured educational content that mirrors the
structure of FineWeb-Edu, QVAC Genesis, and StudyChat datasets.

Usage:
    python -m backend.data_pipeline.seed_data
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DIR


# ============================================================
# Knowledge Base (simulating FineWeb-Edu + QVAC Genesis + StudyChat)
# ============================================================

KNOWLEDGE_ITEMS = [
    # ---- FineWeb-Edu style: AI/ML educational content ----
    {
        "id": "fwe-001", "source": "fineweb-edu", "topic": "Machine Learning",
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves. The process of machine learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples we provide. The primary aim is to allow computers to learn automatically without human intervention or assistance and adjust actions accordingly.",
        "difficulty": "beginner", "tags": ["ml", "ai", "fundamentals"]
    },
    {
        "id": "fwe-002", "source": "fineweb-edu", "topic": "Machine Learning",
        "title": "Supervised vs Unsupervised Learning",
        "content": "Supervised learning is the machine learning task of learning a function that maps an input to an output based on example input-output pairs. It infers a function from labeled training data consisting of a set of training examples. In supervised learning, each example is a pair consisting of an input object and a desired output value. Unsupervised learning is a type of algorithm that learns patterns from untagged data. The hope is that through mimicry, the machine is forced to build a compact internal representation of its world. Contrast with supervised learning where the model is trained on labeled data.",
        "difficulty": "beginner", "tags": ["ml", "supervised", "unsupervised"]
    },
    {
        "id": "fwe-003", "source": "fineweb-edu", "topic": "Deep Learning",
        "title": "Neural Networks Fundamentals",
        "content": "A neural network is a series of algorithms that endeavors to recognize underlying relationships in a set of data through a process that mimics the way the human brain operates. Neural networks are systems of interconnected nodes called neurons that process information using connectionist approaches. Each neuron receives input signals, processes them using an activation function, and passes the output to the next layer. Common activation functions include ReLU, Sigmoid, and Tanh. Deep learning uses multiple layers of these neurons to progressively extract higher-level features from raw input.",
        "difficulty": "intermediate", "tags": ["deep-learning", "neural-networks", "ai"]
    },
    {
        "id": "fwe-004", "source": "fineweb-edu", "topic": "Deep Learning",
        "title": "Convolutional Neural Networks (CNN)",
        "content": "A Convolutional Neural Network (CNN) is a deep learning architecture that takes an input image, assigns importance to various aspects/objects in the image, and is able to differentiate one from the other. The pre-processing required in a CNN is much lower compared to other classification algorithms. While in primitive methods filters are hand-engineered, with enough training, CNNs have the ability to learn these filters/characteristics. The architecture of a CNN consists of convolutional layers, pooling layers, and fully connected layers.",
        "difficulty": "intermediate", "tags": ["cnn", "computer-vision", "deep-learning"]
    },
    {
        "id": "fwe-005", "source": "fineweb-edu", "topic": "Deep Learning",
        "title": "Recurrent Neural Networks and LSTMs",
        "content": "Recurrent Neural Networks (RNNs) are a class of neural networks that are powerful for modeling sequence data such as time series or natural language. Unlike traditional feedforward neural networks, RNNs have internal memory that allows them to remember important things about the input they received. Long Short-Term Memory networks (LSTMs) are a special kind of RNN capable of learning long-term dependencies. They were introduced to solve the vanishing gradient problem in traditional RNNs. LSTMs have a cell state and three gates (input, forget, output) that regulate information flow.",
        "difficulty": "intermediate", "tags": ["rnn", "lstm", "sequence-modeling"]
    },
    {
        "id": "fwe-006", "source": "fineweb-edu", "topic": "Deep Learning",
        "title": "Transformer Architecture Explained",
        "content": "The Transformer model introduced in the paper 'Attention Is All You Need' revolutionized NLP by using a self-attention mechanism instead of recurrence. The Transformer architecture consists of an encoder and decoder, each composed of multiple layers of multi-head attention and feed-forward networks. The key innovation is the self-attention mechanism, which computes attention scores between all pairs of positions in the input sequence. This allows the model to capture long-range dependencies much more effectively than RNNs. Positional encodings are added to give the model information about token positions.",
        "difficulty": "advanced", "tags": ["transformer", "attention", "nlp"]
    },
    {
        "id": "fwe-007", "source": "fineweb-edu", "topic": "Large Language Models",
        "title": "How Large Language Models Work",
        "content": "Large Language Models (LLMs) are neural networks trained on massive amounts of text data to understand and generate human-like text. The training process involves predicting the next word in a sequence given the previous words. Modern LLMs use the Transformer architecture with billions of parameters. Key concepts include pre-training on large corpora followed by fine-tuning for specific tasks. LLMs like GPT-4, Claude, and LLaMA have demonstrated remarkable abilities in translation, summarization, question answering, and code generation. The scale of these models enables emergent abilities not present in smaller models.",
        "difficulty": "intermediate", "tags": ["llm", "gpt", "pretraining"]
    },
    {
        "id": "fwe-008", "source": "fineweb-edu", "topic": "Large Language Models",
        "title": "Prompt Engineering Techniques",
        "content": "Prompt engineering is the practice of designing and optimizing prompts to effectively interact with large language models. Key techniques include: few-shot prompting (providing examples in the prompt), chain-of-thought prompting (encouraging step-by-step reasoning), zero-shot prompting (direct task description), and system prompts (setting model behavior). Temperature controls randomness, while top-p sampling controls diversity. Advanced methods include prompt chaining, where complex tasks are broken into sequential prompts, and retrieval-augmented generation (RAG) which combines prompts with external knowledge retrieval.",
        "difficulty": "intermediate", "tags": ["prompt-engineering", "llm", "rag"]
    },
    {
        "id": "fwe-009", "source": "fineweb-edu", "topic": "Large Language Models",
        "title": "Fine-tuning LLMs for Custom Tasks",
        "content": "Fine-tuning adapts a pre-trained language model to a specific task or domain by continuing training on task-specific data. Parameter-Efficient Fine-Tuning (PEFT) methods like LoRA (Low-Rank Adaptation) freeze most model parameters and train only small adapter modules. Full fine-tuning updates all parameters, which is computationally expensive but can achieve higher performance. Instruction tuning fine-tunes models on diverse instruction-following examples to improve generalization. Reinforcement Learning from Human Feedback (RLHF) is used to align model outputs with human preferences.",
        "difficulty": "advanced", "tags": ["fine-tuning", "lora", "peft", "rlhf"]
    },
    {
        "id": "fwe-010", "source": "fineweb-edu", "topic": "Natural Language Processing",
        "title": "Text Preprocessing for NLP",
        "content": "Text preprocessing is a crucial step in NLP pipelines. Common techniques include: tokenization (splitting text into tokens), stop word removal (removing common words like 'the', 'and'), stemming (reducing words to root form, e.g., 'running' to 'run'), lemmatization (reducing words to dictionary form, e.g., 'better' to 'good'), and lowercasing. Advanced preprocessing includes handling special characters, URLs, and emojis. The choice of preprocessing depends on the task: for example, sentiment analysis might preserve punctuation while topic modeling might remove it.",
        "difficulty": "beginner", "tags": ["nlp", "preprocessing", "text"]
    },
    {
        "id": "fwe-011", "source": "fineweb-edu", "topic": "Data Science",
        "title": "Exploratory Data Analysis (EDA)",
        "content": "Exploratory Data Analysis (EDA) is an approach to analyzing data sets to summarize their main characteristics, often using visual methods. Key steps include: understanding data dimensions and types, checking for missing values, analyzing distributions of variables, identifying outliers, and exploring relationships between variables. Common visualization tools include histograms, box plots, scatter plots, and correlation matrices. EDA helps uncover patterns, spot anomalies, test hypotheses, and check assumptions before building machine learning models.",
        "difficulty": "beginner", "tags": ["data-science", "eda", "visualization"]
    },
    {
        "id": "fwe-012", "source": "fineweb-edu", "topic": "Data Science",
        "title": "Feature Engineering for ML",
        "content": "Feature engineering is the process of transforming raw data into features that better represent the underlying problem to predictive models. Common techniques include: handling missing values, encoding categorical variables (one-hot encoding, label encoding), feature scaling (standardization, normalization), creating interaction features, binning continuous variables, and extracting date/time features. Domain knowledge is crucial for effective feature engineering. Well-engineered features can significantly improve model performance even with simple algorithms.",
        "difficulty": "intermediate", "tags": ["feature-engineering", "ml", "data-science"]
    },
    {
        "id": "fwe-013", "source": "fineweb-edu", "topic": "Python",
        "title": "Python for Data Science: NumPy and Pandas",
        "content": "NumPy provides support for large, multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays. Pandas provides data structures like DataFrame and Series for data manipulation and analysis. Key operations include: data selection, filtering, grouping, merging, pivoting, and applying functions. NumPy arrays are more memory-efficient than Python lists and support vectorized operations. Pandas integrates well with other libraries like scikit-learn and matplotlib for complete data science workflows.",
        "difficulty": "beginner", "tags": ["python", "numpy", "pandas"]
    },
    {
        "id": "fwe-014", "source": "fineweb-edu", "topic": "Python",
        "title": "PyTorch vs TensorFlow: A Comparison",
        "content": "PyTorch and TensorFlow are the two most popular deep learning frameworks. PyTorch, developed by Meta, offers a more Pythonic, dynamic computation graph that makes debugging easier and is preferred in research. TensorFlow, developed by Google, provides production-ready deployment tools like TensorFlow Serving and TensorFlow Lite. Key differences: PyTorch uses eager execution by default while TensorFlow traditionally used static graphs (though it now supports eager mode via TensorFlow 2.x). Both frameworks support GPU acceleration, distributed training, and have extensive model zoos.",
        "difficulty": "intermediate", "tags": ["pytorch", "tensorflow", "deep-learning"]
    },
    {
        "id": "fwe-015", "source": "fineweb-edu", "topic": "Machine Learning",
        "title": "Model Evaluation and Validation",
        "content": "Model evaluation is essential to assess how well a machine learning model generalizes to unseen data. Common techniques include: train-test split, cross-validation (k-fold, stratified), and bootstrap sampling. Key metrics depend on the task: accuracy, precision, recall, F1-score for classification; MSE, MAE, R-squared for regression; AUC-ROC for binary classification. Overfitting occurs when a model performs well on training data but poorly on test data. Regularization techniques (L1, L2, dropout) and early stopping help prevent overfitting.",
        "difficulty": "intermediate", "tags": ["ml", "evaluation", "cross-validation"]
    },
    {
        "id": "fwe-016", "source": "fineweb-edu", "topic": "Reinforcement Learning",
        "title": "Reinforcement Learning Fundamentals",
        "content": "Reinforcement Learning (RL) is a type of machine learning where an agent learns to make decisions by interacting with an environment. The agent receives rewards or penalties for its actions and learns to maximize cumulative reward. Key concepts include: states, actions, rewards, policy, value function, and Q-function. The exploration-exploitation dilemma is central to RL: the agent must balance trying new actions (exploration) with using known rewarding actions (exploitation). Algorithms include Q-learning, Deep Q-Networks (DQN), Policy Gradients, and Actor-Critic methods.",
        "difficulty": "advanced", "tags": ["reinforcement-learning", "rl", "agent"]
    },
    # ---- QVAC Genesis style: problem-solving Q&A pairs ----
    {
        "id": "qvac-001", "source": "qvac-genesis", "topic": "Machine Learning",
        "title": "What is the Bias-Variance Tradeoff?",
        "content": "Question: Explain the bias-variance tradeoff in machine learning. Solution: The bias-variance tradeoff is a fundamental concept in ML that describes the tradeoff between a model's ability to accurately capture patterns (low bias) and its sensitivity to training data (low variance). High bias models (underfitting) make strong assumptions about data and may miss relevant patterns. High variance models (overfitting) are too sensitive to training data and fail to generalize. The optimal model balances both. Bias decreases with model complexity while variance increases. The goal is to find the complexity level that minimizes total error.",
        "difficulty": "intermediate", "tags": ["bias-variance", "ml-theory"]
    },
    {
        "id": "qvac-002", "source": "qvac-genesis", "topic": "Machine Learning",
        "title": "Explain Gradient Descent",
        "content": "Question: How does gradient descent work for optimizing ML models? Solution: Gradient descent is an iterative optimization algorithm used to minimize a loss function by updating model parameters in the opposite direction of the gradient. The learning rate determines step size. Batch gradient descent uses the entire dataset per iteration, stochastic gradient descent (SGD) uses one sample, and mini-batch gradient descent uses a subset. Momentum helps accelerate convergence by adding a fraction of the previous update. Adaptive methods like Adam and RMSprop adjust learning rates per parameter.",
        "difficulty": "intermediate", "tags": ["gradient-descent", "optimization"]
    },
    {
        "id": "qvac-003", "source": "qvac-genesis", "topic": "Deep Learning",
        "title": "Why Use Dropout Regularization?",
        "content": "Question: How does dropout help prevent overfitting in neural networks? Solution: Dropout is a regularization technique that randomly drops units (neurons) from the neural network during training. Each neuron is kept with probability p (typically 0.5) and dropped with probability 1-p. This prevents co-adaptation of neurons, forcing the network to learn more robust features. Dropout effectively trains an ensemble of sub-networks. During inference, all neurons are used but their outputs are scaled by p. Dropout is particularly effective for large neural networks and can be combined with other regularization methods like L1/L2.",
        "difficulty": "intermediate", "tags": ["dropout", "regularization", "deep-learning"]
    },
    {
        "id": "qvac-004", "source": "qvac-genesis", "topic": "Large Language Models",
        "title": "What is RAG (Retrieval-Augmented Generation)?",
        "content": "Question: Explain how Retrieval-Augmented Generation works and its benefits. Solution: RAG combines information retrieval with text generation. When a query is received, the system first retrieves relevant documents from a knowledge base using vector similarity search. These documents are then added to the prompt context for the LLM, which generates a response grounded in the retrieved information. Benefits include: reduced hallucinations (model can cite sources), access to up-to-date information without retraining, cost-effective domain adaptation, and improved transparency. Challenges include retrieval quality, context window limits, and latency.",
        "difficulty": "intermediate", "tags": ["rag", "llm", "retrieval"]
    },
    {
        "id": "qvac-005", "source": "qvac-genesis", "topic": "Data Science",
        "title": "Explain the Central Limit Theorem",
        "content": "Question: What is the Central Limit Theorem and why is it important in statistics? Solution: The Central Limit Theorem (CLT) states that the sampling distribution of the mean of any independent, random variable will be approximately normally distributed, regardless of the underlying population distribution, provided the sample size is sufficiently large (typically n >= 30). This is fundamental to statistical inference because it allows us to make probabilistic statements about population parameters using sample statistics, and it justifies the use of normal distribution in confidence intervals and hypothesis testing.",
        "difficulty": "intermediate", "tags": ["statistics", "clt", "probability"]
    },
    {
        "id": "qvac-006", "source": "qvac-genesis", "topic": "Machine Learning",
        "title": "Difference Between L1 and L2 Regularization",
        "content": "Question: Compare L1 and L2 regularization in machine learning. Solution: L1 regularization (Lasso) adds the absolute value of coefficients as a penalty term to the loss function, while L2 regularization (Ridge) adds the squared magnitude. L1 tends to produce sparse solutions with many coefficients set to zero, making it useful for feature selection. L2 tends to distribute penalty across all coefficients, reducing them proportionally. L1 has a non-differentiable point at zero, solved using subgradient methods. L2 is differentiable everywhere. Elastic Net combines both L1 and L2 penalties.",
        "difficulty": "intermediate", "tags": ["regularization", "l1", "l2", "ml"]
    },
    {
        "id": "qvac-007", "source": "qvac-genesis", "topic": "Computer Vision",
        "title": "How Does Object Detection Work?",
        "content": "Question: Explain the key approaches to object detection in computer vision. Solution: Object detection approaches fall into two categories: two-stage detectors and one-stage detectors. Two-stage detectors (e.g., Faster R-CNN) first generate region proposals and then classify each region. They are more accurate but slower. One-stage detectors (e.g., YOLO, SSD) directly predict bounding boxes and class probabilities in a single pass, prioritizing speed. YOLO divides the image into grids and predicts boxes per grid cell. Modern approaches like DETR use Transformers for end-to-end detection without hand-crafted components.",
        "difficulty": "advanced", "tags": ["object-detection", "computer-vision", "yolo"]
    },
    {
        "id": "qvac-008", "source": "qvac-genesis", "topic": "Python",
        "title": "Explain Python Decorators",
        "content": "Question: How do Python decorators work and when should you use them? Solution: Python decorators are functions that take another function and extend its behavior without explicitly modifying it. They use the @ syntax and are commonly used for logging, access control, memoization, and timing. A decorator is a callable that returns a callable, typically wrapping the original function. Decorators can also accept arguments (using nested functions). The functools.wraps decorator should be used to preserve metadata of the original function. Decorators are a powerful example of Python's functional programming capabilities.",
        "difficulty": "intermediate", "tags": ["python", "decorators", "programming"]
    },
    # ---- StudyChat style: tutoring conversations ----
    {
        "id": "sc-001", "source": "studychat", "topic": "Machine Learning",
        "title": "Tutoring Session: Understanding Decision Trees",
        "content": "Student: I don't understand how decision trees split data. Teacher: A decision tree splits data by asking sequential questions about features. For example, to classify iris flowers, it might ask 'Is petal length > 2.5cm?' If yes, go left; if no, go right. The split is chosen to maximize information gain, which measures how much the split reduces uncertainty (entropy) about the target variable. Student: How does it choose which feature to split on? Teacher: It calculates the information gain for each possible split and picks the best one. Gini impurity and entropy are common splitting criteria.",
        "difficulty": "beginner", "tags": ["decision-trees", "tutoring", "ml"]
    },
    {
        "id": "sc-002", "source": "studychat", "topic": "Python",
        "title": "Tutoring Session: Debugging Python Code",
        "content": "Student: My code gives a KeyError when accessing a dictionary. Why? Teacher: KeyError occurs when you try to access a key that doesn't exist in the dictionary. Instead of direct access like dict[key], use dict.get(key, default) which returns a default value if the key is missing. Or check with 'key in dict' before accessing. Student: Should I use try-except instead? Teacher: Both approaches work. try-except is better when you expect the key might be missing occasionally. The 'in' check is better for simple lookups where you need to handle the missing case differently.",
        "difficulty": "beginner", "tags": ["python", "debugging", "tutoring"]
    },
    {
        "id": "sc-003", "source": "studychat", "topic": "Deep Learning",
        "title": "Tutoring Session: Vanishing Gradient Problem",
        "content": "Student: My deep network isn't learning. The loss doesn't decrease. Teacher: This might be the vanishing gradient problem. In deep networks, gradients become very small as they are backpropagated through many layers, making early layers learn very slowly. Solutions include: using ReLU instead of sigmoid/tanh activation, batch normalization, residual connections (skip connections), and careful weight initialization like Xavier/Glorot initialization. Student: Should I use more layers? Teacher: Not necessarily. You might need fewer layers with better initialization and normalization.",
        "difficulty": "intermediate", "tags": ["vanishing-gradient", "deep-learning", "tutoring"]
    },
    {
        "id": "sc-004", "source": "studychat", "topic": "Large Language Models",
        "title": "Tutoring Session: Understanding Tokenization",
        "content": "Student: What does 'token' mean in LLMs? Teacher: A token is a piece of text that the model processes. For example, 'unbelievable' might be split into 'un', 'believ', 'able'. Byte-Pair Encoding (BPE) is a common tokenization method that iteratively merges the most frequent character pairs. Student: Why not just use words? Teacher: Word-level tokenization would give a huge vocabulary (millions of words) and can't handle unknown words. Subword tokenization balances vocabulary size and coverage. Most LLMs use 32K-100K tokens in their vocabulary.",
        "difficulty": "beginner", "tags": ["tokenization", "llm", "tutoring"]
    },
    {
        "id": "sc-005", "source": "studychat", "topic": "Machine Learning",
        "title": "Tutoring Session: Confusion Matrix",
        "content": "Student: Can you explain the confusion matrix? Teacher: A confusion matrix shows the performance of a classification model. It has four cells: True Positives (correctly predicted positives), True Negatives (correctly predicted negatives), False Positives (predicted positive but actually negative), and False Negatives (predicted negative but actually positive). From these, we calculate metrics like accuracy, precision (TP/(TP+FP)), recall (TP/(TP+FN)), and F1-score (harmonic mean of precision and recall). Student: Which metric should I use? Teacher: For imbalanced datasets, use precision and recall rather than accuracy.",
        "difficulty": "beginner", "tags": ["confusion-matrix", "classification", "tutoring"]
    },
    {
        "id": "sc-006", "source": "studychat", "topic": "Data Science",
        "title": "Tutoring Session: Handling Missing Data",
        "content": "Student: What should I do with missing values in my dataset? Teacher: There are several approaches: remove rows with missing values (if they're few), use mean/median/mode imputation, or use more advanced methods like KNN imputation or regression imputation. The best approach depends on the nature and pattern of missing data. Student: How do I know if the missing data is random? Teacher: There are three types: MCAR (Missing Completely At Random), MAR (Missing At Random), and MNAR (Missing Not At Random). Statistical tests like Little's MCAR test can help determine the type.",
        "difficulty": "intermediate", "tags": ["missing-data", "data-science", "tutoring"]
    },
    {
        "id": "sc-007", "source": "studychat", "topic": "Python",
        "title": "Tutoring Session: List Comprehensions",
        "content": "Student: I keep writing long for loops. How can I make my code more Pythonic? Teacher: Use list comprehensions! Instead of: squares = []; for x in range(10): squares.append(x**2), write: squares = [x**2 for x in range(10)]. You can also add conditions: [x**2 for x in range(10) if x % 2 == 0]. For dictionaries, use dict comprehensions: {x: x**2 for x in range(5)}. Student: What about nested loops? Teacher: You can nest them, but keep it readable. More than two levels probably deserves a regular loop.",
        "difficulty": "beginner", "tags": ["python", "list-comprehensions", "tutoring"]
    },
    {
        "id": "sc-008", "source": "studychat", "topic": "Machine Learning",
        "title": "Tutoring Session: Cross-validation",
        "content": "Student: What is k-fold cross-validation and why use it? Teacher: K-fold cross-validation splits your data into k equal folds. The model trains on k-1 folds and tests on the remaining fold, repeating this k times so each fold is used for testing once. The final performance is the average across all k iterations. This gives a more robust estimate of model performance than a single train-test split, especially with limited data. Common choices are k=5 or k=10. Student: Any downsides? Teacher: It's computationally expensive, especially with large datasets.",
        "difficulty": "intermediate", "tags": ["cross-validation", "ml", "tutoring"]
    },
    {
        "id": "sc-009", "source": "studychat", "topic": "Deep Learning",
        "title": "Tutoring Session: Learning Rate Tuning",
        "content": "Student: How do I choose the right learning rate? Teacher: The learning rate is one of the most important hyperparameters. Too high: the loss oscillates or diverges. Too low: training takes too long or gets stuck. A good starting point is 0.001 for Adam optimizer. Use learning rate schedulers: step decay reduces the rate by a factor every few epochs, cosine annealing follows a cosine curve, and ReduceLROnPlateau reduces the rate when loss plateaus. Learning rate finders (like cyclical LR) can help find the optimal range.",
        "difficulty": "intermediate", "tags": ["learning-rate", "deep-learning", "tutoring"]
    },
    {
        "id": "sc-010", "source": "studychat", "topic": "Large Language Models",
        "title": "Tutoring Session: Context Window and Attention",
        "content": "Student: Why do LLMs have a context window limit? Teacher: The attention mechanism in Transformers has O(n) memory and compute cost relative to sequence length n. This means longer sequences require exponentially more memory. Context windows are typically 4K-128K tokens depending on the model. Student: How do models handle longer documents? Teacher: Techniques include: sliding window attention (only attends to nearby tokens), sparse attention patterns, and hierarchical approaches that summarize chunks. RAG also helps by retrieving only relevant text rather than processing everything.",
        "difficulty": "advanced", "tags": ["context-window", "attention", "llm", "tutoring"]
    },
]


# ============================================================
# Assessment Questions (generated from knowledge items)
# ============================================================

ASSESSMENT_QUESTIONS = [
    {
        "id": "q-001", "question": "机器学习的主要目标是什么？",
        "options": ["让计算机无需显式编程即可从数据中学习", "取代所有人类决策", "制造更快的处理器", "存储大量数据"],
        "correct_answer": 0, "explanation": "机器学习使系统能够从数据中学习并从经验中改进，无需为每种场景显式编程。",
        "topic": "Machine Learning", "difficulty": "beginner"
    },
    {
        "id": "q-002", "question": "监督学习与无监督学习的关键区别是什么？",
        "options": ["监督学习使用有标签数据，无监督学习使用无标签数据", "监督学习比无监督学习更快", "无监督学习需要更多数据", "监督学习不使用算法"],
        "correct_answer": 0, "explanation": "监督学习使用有标签的输入输出对进行训练，而无监督学习在无标签数据中发现模式。",
        "topic": "Machine Learning", "difficulty": "beginner"
    },
    {
        "id": "q-003", "question": "深度学习中的梯度消失问题是什么？",
        "options": ["早期层的梯度变得非常小，导致学习缓慢", "梯度变得过大", "损失函数消失", "模型内存不足"],
        "correct_answer": 0, "explanation": "在深层网络中，梯度在通过多层反向传播时可能呈指数级缩小，使早期层学习非常缓慢。",
        "topic": "Deep Learning", "difficulty": "intermediate"
    },
    {
        "id": "q-004", "question": "Transformer 架构的关键创新是什么？",
        "options": ["自注意力机制", "循环连接", "卷积层", "长短期记忆网络（LSTM）"],
        "correct_answer": 0, "explanation": "Transformer 引入了自注意力机制，计算输入中所有位置对之间的注意力分数，取代了循环结构。",
        "topic": "Deep Learning", "difficulty": "intermediate"
    },
    {
        "id": "q-005", "question": "在 LLM 系统中，RAG 代表什么？",
        "options": ["检索增强生成（Retrieval-Augmented Generation）", "随机访问生成（Random Access Generation）", "循环注意力图（Recurrent Attention Graph）", "快速自动评分（Rapid Automated Grading）"],
        "correct_answer": 0, "explanation": "RAG 将信息检索与文本生成相结合，检索相关文档以支撑 LLM 的回答。",
        "topic": "Large Language Models", "difficulty": "intermediate"
    },
    {
        "id": "q-006", "question": "神经网络中 dropout 的作用是什么？",
        "options": ["通过随机丢弃神经元来防止过拟合", "提高模型速度", "减少内存使用", "改善数据加载"],
        "correct_answer": 0, "explanation": "dropout 在训练时随机丢弃部分单元，防止神经元之间过度依赖，迫使网络学习更鲁棒的特征。",
        "topic": "Deep Learning", "difficulty": "intermediate"
    },
    {
        "id": "q-007", "question": "中心极限定理（CLT）说明了什么？",
        "options": ["当样本量足够大时，样本均值近似服从正态分布", "所有数据都服从正态分布", "均值等于中位数", "方差恒为常数"],
        "correct_answer": 0, "explanation": "CLT 指出，无论总体分布如何，随着样本量增大，均值的抽样分布趋近于正态分布。",
        "topic": "Data Science", "difficulty": "intermediate"
    },
    {
        "id": "q-008", "question": "L1 与 L2 正则化的区别是什么？",
        "options": ["L1 产生稀疏解，L2 将惩罚分摊到所有系数上", "L1 用于回归，L2 用于分类", "L1 比 L2 更快", "L1 使用平方惩罚，L2 使用绝对值惩罚"],
        "correct_answer": 0, "explanation": "L1（Lasso）添加绝对值惩罚，产生稀疏解，适合特征选择；L2（Ridge）添加平方惩罚，将惩罚分摊到所有系数上。",
        "topic": "Machine Learning", "difficulty": "intermediate"
    },
    {
        "id": "q-009", "question": "使用 LoRA 进行微调的一个关键好处是什么？",
        "options": ["只训练小型适配模块，节省计算资源", "提高数据质量", "永久减小模型体积", "无需训练数据"],
        "correct_answer": 0, "explanation": "LoRA（低秩适配）冻结大部分模型参数，只训练小型适配模块，使微调计算高效。",
        "topic": "Large Language Models", "difficulty": "advanced"
    },
    {
        "id": "q-010", "question": "在数据科学中，EDA 代表什么？",
        "options": ["探索性数据分析（Exploratory Data Analysis）", "增强数据算法（Enhanced Data Algorithm）", "指数数据聚合（Exponential Data Aggregation）", "外部数据访问（External Data Access）"],
        "correct_answer": 0, "explanation": "EDA 是分析数据集以概括其主要特征的过程，常借助可视化方法发现模式与异常。",
        "topic": "Data Science", "difficulty": "beginner"
    },
    {
        "id": "q-011", "question": "在研究中，PyTorch 相比 TensorFlow 的主要优势是什么？",
        "options": ["更符合 Python 习惯的动态计算图，便于调试", "训练速度更快", "部署工具更好", "社区更大"],
        "correct_answer": 0, "explanation": "PyTorch 的动态计算图使调试更容易，对研究者更直观，尽管如今两个框架已相当接近。",
        "topic": "Python", "difficulty": "intermediate"
    },
    {
        "id": "q-012", "question": "强化学习中的探索-利用困境是什么？",
        "options": ["在尝试新动作与利用已知高回报动作之间权衡", "在快慢算法之间选择", "决定收集多少数据", "在模型复杂度与性能之间权衡"],
        "correct_answer": 0, "explanation": "智能体必须平衡探索新动作以发现更好回报，与利用已知高回报动作获取即时收益。",
        "topic": "Reinforcement Learning", "difficulty": "advanced"
    },
    {
        "id": "q-013", "question": "k 折交叉验证的目的是什么？",
        "options": ["获得更稳健的模型性能估计", "减少训练时间", "提高模型准确率", "消除对测试集的需求"],
        "correct_answer": 0, "explanation": "k 折交叉验证在多个数据划分上训练和测试，比单次训练测试划分提供更稳健的性能估计。",
        "topic": "Machine Learning", "difficulty": "intermediate"
    },
    {
        "id": "q-014", "question": "什么是 Python 装饰器？",
        "options": ["扩展另一个函数行为的函数", "一种特殊类型的变量", "内置数据结构", "调试工具"],
        "correct_answer": 0, "explanation": "Python 装饰器是接收函数并扩展其行为而无需显式修改它的函数，使用 @ 语法。",
        "topic": "Python", "difficulty": "intermediate"
    },
    {
        "id": "q-015", "question": "在深度学习中，CNN 代表什么？",
        "options": ["卷积神经网络（Convolutional Neural Network）", "复杂神经网络（Complex Neural Network）", "连续神经网络（Continuous Neural Network）", "级联神经网络（Cascading Neural Network）"],
        "correct_answer": 0, "explanation": "CNN 是为处理图像等结构化网格数据而设计的深度学习架构，使用卷积层提取特征。",
        "topic": "Deep Learning", "difficulty": "beginner"
    },
    {
        "id": "q-016", "question": "YOLO 目标检测的关键优势是什么？",
        "options": ["无需区域提议即可进行快速单次检测", "比任何其他方法准确率都高", "无需训练即可工作", "只检测人脸"],
        "correct_answer": 0, "explanation": "YOLO 是单阶段检测器，在单次前向传播中预测边界框和类别概率，速度优先于两阶段方法。",
        "topic": "Computer Vision", "difficulty": "advanced"
    },
    {
        "id": "q-017", "question": "在 Python 中什么会导致 KeyError？",
        "options": ["访问字典中不存在的键", "使用错误的变量类型", "代码中的语法错误", "内存不足"],
        "correct_answer": 0, "explanation": "当试图访问字典中不存在的键时会发生 KeyError。可使用 dict.get() 或 in 关键字避免。",
        "topic": "Python", "difficulty": "beginner"
    },
    {
        "id": "q-018", "question": "混淆矩阵用于什么？",
        "options": ["评估分类模型性能", "可视化数据分布", "训练神经网络", "清洗数据"],
        "correct_answer": 0, "explanation": "混淆矩阵通过真正例、真负例、假正例、假负例展示分类模型的性能。",
        "topic": "Machine Learning", "difficulty": "beginner"
    },
    {
        "id": "q-019", "question": "在 LLM 中，字节对编码（BPE）的作用是什么？",
        "options": ["高效的子词分词，平衡词表大小", "压缩模型权重", "加密训练数据", "优化 GPU 内存"],
        "correct_answer": 0, "explanation": "BPE 是一种子词分词方法，迭代合并高频字符对，在词表大小与覆盖度之间取得平衡。",
        "topic": "Large Language Models", "difficulty": "intermediate"
    },
    {
        "id": "q-020", "question": "什么是偏差-方差权衡？",
        "options": ["模型欠拟合与过拟合之间的平衡", "速度与准确率之间的权衡", "训练集与测试集大小之间的平衡", "模型大小与数据大小之间的权衡"],
        "correct_answer": 0, "explanation": "偏差-方差权衡描述机器学习模型中欠拟合（高偏差）与过拟合（高方差）之间的平衡。",
        "topic": "Machine Learning", "difficulty": "intermediate"
    },
]


# ============================================================
# Courses (generated from knowledge items)
# ============================================================

COURSES = [
    {
        "id": "course-0", "title": "AI Training: Machine Learning",
        "description": "Comprehensive study of Machine Learning based on curated educational datasets. Covers supervised and unsupervised learning, model evaluation, and practical algorithms.",
        "topic": "Machine Learning", "difficulty": "beginner", "estimated_hours": 16, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-0-1", "title": "Introduction to Machine Learning", "content_summary": "Foundational concepts, types of ML, and the ML workflow.", "duration_minutes": 45},
            {"id": "ch-0-2", "title": "Supervised Learning Algorithms", "content_summary": "Linear regression, decision trees, SVM, and ensemble methods.", "duration_minutes": 60},
            {"id": "ch-0-3", "title": "Unsupervised Learning", "content_summary": "Clustering, dimensionality reduction, and anomaly detection.", "duration_minutes": 60},
            {"id": "ch-0-4", "title": "Model Evaluation and Validation", "content_summary": "Cross-validation, metrics, bias-variance tradeoff.", "duration_minutes": 45},
        ]
    },
    {
        "id": "course-1", "title": "AI Training: Deep Learning",
        "description": "Deep dive into neural networks, CNNs, RNNs, and Transformers with hands-on implementation.",
        "topic": "Deep Learning", "difficulty": "intermediate", "estimated_hours": 20, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-1-1", "title": "Neural Network Fundamentals", "content_summary": "Perceptrons, activation functions, backpropagation.", "duration_minutes": 60},
            {"id": "ch-1-2", "title": "Convolutional Neural Networks", "content_summary": "CNN architecture, pooling, and image classification.", "duration_minutes": 60},
            {"id": "ch-1-3", "title": "Recurrent Networks and LSTMs", "content_summary": "Sequence modeling, RNN variants, and applications.", "duration_minutes": 60},
            {"id": "ch-1-4", "title": "Transformer Architecture", "content_summary": "Self-attention, multi-head attention, and applications.", "duration_minutes": 75},
        ]
    },
    {
        "id": "course-2", "title": "AI Training: Large Language Models",
        "description": "From Transformer basics to advanced LLM techniques including fine-tuning, RAG, and prompt engineering.",
        "topic": "Large Language Models", "difficulty": "intermediate", "estimated_hours": 18, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-2-1", "title": "Introduction to LLMs", "content_summary": "What are LLMs, how they work, and key models.", "duration_minutes": 45},
            {"id": "ch-2-2", "title": "Prompt Engineering", "content_summary": "Techniques for effective prompt design and optimization.", "duration_minutes": 60},
            {"id": "ch-2-3", "title": "Fine-tuning with LoRA", "content_summary": "Parameter-efficient fine-tuning techniques.", "duration_minutes": 60},
            {"id": "ch-2-4", "title": "RAG and Knowledge Integration", "content_summary": "Retrieval-Augmented Generation and vector databases.", "duration_minutes": 60},
        ]
    },
    {
        "id": "course-3", "title": "AI Training: Natural Language Processing",
        "description": "Complete NLP pipeline from text preprocessing to advanced sequence modeling.",
        "topic": "Natural Language Processing", "difficulty": "intermediate", "estimated_hours": 14, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-3-1", "title": "Text Preprocessing", "content_summary": "Tokenization, normalization, and feature extraction.", "duration_minutes": 45},
            {"id": "ch-3-2", "title": "Word Embeddings", "content_summary": "Word2Vec, GloVe, and contextual embeddings.", "duration_minutes": 60},
            {"id": "ch-3-3", "title": "Sequence Models for NLP", "content_summary": "RNN, LSTM, and Transformer-based NLP models.", "duration_minutes": 60},
        ]
    },
    {
        "id": "course-4", "title": "AI Training: Data Science",
        "description": "Foundational data science skills including EDA, statistics, feature engineering, and visualization.",
        "topic": "Data Science", "difficulty": "beginner", "estimated_hours": 12, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-4-1", "title": "Introduction to Data Science", "content_summary": "Data science workflow and tools.", "duration_minutes": 45},
            {"id": "ch-4-2", "title": "Exploratory Data Analysis", "content_summary": "Statistical analysis, visualization, and pattern discovery.", "duration_minutes": 60},
            {"id": "ch-4-3", "title": "Feature Engineering", "content_summary": "Feature creation, selection, and transformation techniques.", "duration_minutes": 60},
        ]
    },
    {
        "id": "course-5", "title": "AI Training: Python Programming",
        "description": "Python for AI/ML development including NumPy, Pandas, PyTorch, and TensorFlow.",
        "topic": "Python", "difficulty": "beginner", "estimated_hours": 10, "source": "studychat",
        "chapters": [
            {"id": "ch-5-1", "title": "Python Fundamentals", "content_summary": "Data types, control flow, functions, and comprehensions.", "duration_minutes": 45},
            {"id": "ch-5-2", "title": "NumPy and Pandas", "content_summary": "Array operations, data manipulation, and analysis.", "duration_minutes": 60},
            {"id": "ch-5-3", "title": "PyTorch vs TensorFlow", "content_summary": "Framework comparison, basic model building.", "duration_minutes": 60},
        ]
    },
    {
        "id": "course-6", "title": "AI Training: Computer Vision",
        "description": "Computer vision fundamentals from CNNs to object detection and image segmentation.",
        "topic": "Computer Vision", "difficulty": "advanced", "estimated_hours": 16, "source": "qvac-genesis",
        "chapters": [
            {"id": "ch-6-1", "title": "Image Processing Basics", "content_summary": "Filters, edge detection, and feature extraction.", "duration_minutes": 45},
            {"id": "ch-6-2", "title": "Object Detection", "content_summary": "YOLO, Faster R-CNN, and DETR architectures.", "duration_minutes": 60},
            {"id": "ch-6-3", "title": "Image Segmentation", "content_summary": "Semantic and instance segmentation techniques.", "duration_minutes": 60},
        ]
    },
    {
        "id": "course-7", "title": "AI Training: Reinforcement Learning",
        "description": "RL fundamentals from Q-learning to deep RL and policy gradient methods.",
        "topic": "Reinforcement Learning", "difficulty": "advanced", "estimated_hours": 14, "source": "fineweb-edu",
        "chapters": [
            {"id": "ch-7-1", "title": "RL Fundamentals", "content_summary": "Markov decision processes, rewards, and policies.", "duration_minutes": 45},
            {"id": "ch-7-2", "title": "Q-Learning and DQN", "content_summary": "Value-based methods and deep Q-networks.", "duration_minutes": 60},
            {"id": "ch-7-3", "title": "Policy Gradients", "content_summary": "Policy-based methods and Actor-Critic architectures.", "duration_minutes": 60},
        ]
    },
]


# ============================================================
# Projects
# ============================================================

PROJECTS = [
    {"id": "project-0", "title": "Project: Image Classification with CNN", "description": "Build a CNN classifier for the CIFAR-10 dataset using PyTorch. Implement data augmentation, batch normalization, and dropout.", "tech_stack": ["Python", "PyTorch", "torchvision"], "difficulty": "intermediate", "estimated_hours": 12, "topics_covered": ["Deep Learning", "CNN", "computer-vision"], "source": "fineweb-edu"},
    {"id": "project-1", "title": "Project: Sentiment Analysis with BERT", "description": "Fine-tune a BERT model for sentiment classification on movie reviews. Implement tokenization, training loop, and evaluation.", "tech_stack": ["Python", "PyTorch", "Transformers"], "difficulty": "intermediate", "estimated_hours": 10, "topics_covered": ["NLP", "fine-tuning", "classification"], "source": "fineweb-edu"},
    {"id": "project-2", "title": "Project: RAG-based Q&A System", "description": "Build a retrieval-augmented generation system using LangChain, ChromaDB, and an LLM API. Implement document chunking, embedding, and query pipeline.", "tech_stack": ["Python", "LangChain", "ChromaDB", "OpenAI API"], "difficulty": "advanced", "estimated_hours": 16, "topics_covered": ["LLM", "RAG", "retrieval"], "source": "studychat"},
    {"id": "project-3", "title": "Project: Customer Churn Prediction", "description": "Build an ML pipeline to predict customer churn. Includes EDA, feature engineering, model selection, and deployment as a FastAPI endpoint.", "tech_stack": ["Python", "scikit-learn", "pandas", "FastAPI"], "difficulty": "intermediate", "estimated_hours": 12, "topics_covered": ["Machine Learning", "classification", "deployment"], "source": "qvac-genesis"},
    {"id": "project-4", "title": "Project: Real-time Object Detection", "description": "Implement YOLOv8 for real-time object detection on video streams. Optimize inference speed and deploy with Docker.", "tech_stack": ["Python", "YOLOv8", "OpenCV", "Docker"], "difficulty": "advanced", "estimated_hours": 14, "topics_covered": ["Computer Vision", "object-detection", "deployment"], "source": "fineweb-edu"},
    {"id": "project-5", "title": "Project: LLM Fine-tuning Pipeline", "description": "Fine-tune a LLaMA model using LoRA for a custom instruction-following dataset. Implement training, evaluation, and inference.", "tech_stack": ["Python", "PyTorch", "Transformers", "PEFT"], "difficulty": "advanced", "estimated_hours": 20, "topics_covered": ["LLM", "fine-tuning", "lora"], "source": "fineweb-edu"},
    {"id": "project-6", "title": "Project: Time Series Forecasting", "description": "Build LSTM-based time series forecasting for stock prices or weather data. Include data preprocessing, model training, and visualization.", "tech_stack": ["Python", "PyTorch", "pandas", "matplotlib"], "difficulty": "intermediate", "estimated_hours": 10, "topics_covered": ["Deep Learning", "LSTM", "time-series"], "source": "qvac-genesis"},
    {"id": "project-7", "title": "Project: Recommendation System", "description": "Build a collaborative filtering recommendation system using matrix factorization and neural approaches.", "tech_stack": ["Python", "scikit-learn", "PyTorch", "pandas"], "difficulty": "intermediate", "estimated_hours": 12, "topics_covered": ["Machine Learning", "recommendation", "collaborative-filtering"], "source": "fineweb-edu"},
    {"id": "project-8", "title": "Project: AI Chatbot with LangChain", "description": "Build a conversational AI chatbot with memory, tools, and multi-turn conversation support using LangChain.", "tech_stack": ["Python", "LangChain", "FastAPI", "OpenAI API"], "difficulty": "intermediate", "estimated_hours": 14, "topics_covered": ["LLM", "chatbot", "langchain"], "source": "studychat"},
    {"id": "project-9", "title": "Project: Data Pipeline and ETL", "description": "Build an automated ETL pipeline that extracts, transforms, and loads data for ML training. Includes data validation and monitoring.", "tech_stack": ["Python", "pandas", "SQL", "Airflow"], "difficulty": "intermediate", "estimated_hours": 10, "topics_covered": ["Data Science", "ETL", "pipeline"], "source": "qvac-genesis"},
]


# ============================================================
# Learning Paths
# ============================================================

LEARNING_PATHS = [
    {
        "id": "path-0", "direction": "AI Engineer", "title": "Learning Path: AI Engineer",
        "nodes": [
            {"id": "path-0-0", "title": "Python Programming Fundamentals", "type": "course", "items": ["course-5"]},
            {"id": "path-0-1", "title": "Introduction to Machine Learning", "type": "course", "items": ["course-0"]},
            {"id": "path-0-2", "title": "Deep Learning with PyTorch", "type": "course", "items": ["course-1"]},
            {"id": "path-0-3", "title": "Large Language Models", "type": "course", "items": ["course-2"]},
            {"id": "path-0-4", "title": "Hands-on ML Project", "type": "project", "items": ["project-0"]},
            {"id": "path-0-5", "title": "RAG-based Q&A System", "type": "project", "items": ["project-2"]},
        ],
        "total_weeks": 12
    },
    {
        "id": "path-1", "direction": "ML Engineer", "title": "Learning Path: ML Engineer",
        "nodes": [
            {"id": "path-1-0", "title": "Python for Data Science", "type": "course", "items": ["course-5"]},
            {"id": "path-1-1", "title": "Data Science Fundamentals", "type": "course", "items": ["course-4"]},
            {"id": "path-1-2", "title": "Machine Learning", "type": "course", "items": ["course-0"]},
            {"id": "path-1-3", "title": "Deep Learning", "type": "course", "items": ["course-1"]},
            {"id": "path-1-4", "title": "Customer Churn Prediction", "type": "project", "items": ["project-3"]},
            {"id": "path-1-5", "title": "Recommendation System", "type": "project", "items": ["project-7"]},
        ],
        "total_weeks": 12
    },
    {
        "id": "path-2", "direction": "Data Scientist", "title": "Learning Path: Data Scientist",
        "nodes": [
            {"id": "path-2-0", "title": "Python for Data Science", "type": "course", "items": ["course-5"]},
            {"id": "path-2-1", "title": "Data Science Fundamentals", "type": "course", "items": ["course-4"]},
            {"id": "path-2-2", "title": "Machine Learning", "type": "course", "items": ["course-0"]},
            {"id": "path-2-3", "title": "Data Pipeline and ETL", "type": "project", "items": ["project-9"]},
            {"id": "path-2-4", "title": "Customer Churn Prediction", "type": "project", "items": ["project-3"]},
        ],
        "total_weeks": 10
    },
    {
        "id": "path-3", "direction": "Backend AI Developer", "title": "Learning Path: Backend AI Developer",
        "nodes": [
            {"id": "path-3-0", "title": "Python Programming", "type": "course", "items": ["course-5"]},
            {"id": "path-3-1", "title": "Machine Learning", "type": "course", "items": ["course-0"]},
            {"id": "path-3-2", "title": "Large Language Models", "type": "course", "items": ["course-2"]},
            {"id": "path-3-3", "title": "AI Chatbot with LangChain", "type": "project", "items": ["project-8"]},
            {"id": "path-3-4", "title": "RAG-based Q&A System", "type": "project", "items": ["project-2"]},
        ],
        "total_weeks": 10
    },
]


def run():
    """Generate all seed data files."""
    print("=" * 60)
    print("Generating synthetic AI training dataset (seed data)")
    print("=" * 60)

    # Knowledge base
    kb_path = PROCESSED_DIR / "knowledge_base.json"
    KNOWLEDGE_ITEMS.sort(key=lambda x: (x["source"], x["id"]))
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_ITEMS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Knowledge base: {len(KNOWLEDGE_ITEMS)} items → {kb_path}")

    # Assessment questions
    q_path = PROCESSED_DIR / "assessment_questions.json"
    with open(q_path, "w", encoding="utf-8") as f:
        json.dump(ASSESSMENT_QUESTIONS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Assessment questions: {len(ASSESSMENT_QUESTIONS)} → {q_path}")

    # Courses
    c_path = PROCESSED_DIR / "courses.json"
    with open(c_path, "w", encoding="utf-8") as f:
        json.dump(COURSES, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Courses: {len(COURSES)} → {c_path}")

    # Projects
    p_path = PROCESSED_DIR / "projects.json"
    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(PROJECTS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Projects: {len(PROJECTS)} → {p_path}")

    # Learning paths
    lp_path = PROCESSED_DIR / "learning_paths.json"
    with open(lp_path, "w", encoding="utf-8") as f:
        json.dump(LEARNING_PATHS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Learning paths: {len(LEARNING_PATHS)} → {lp_path}")

    print("\n Seed data generation complete!")
    print(f"  Total: {len(KNOWLEDGE_ITEMS)} knowledge items, {len(ASSESSMENT_QUESTIONS)} questions, {len(COURSES)} courses, {len(PROJECTS)} projects, {len(LEARNING_PATHS)} paths")


if __name__ == "__main__":
    run()