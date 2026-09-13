"""
text_processor.py — 文本预处理与特征提取模块
功能：NLTK 分词/去停用词 → TF-IDF 向量化 → 文本特征向量
"""
import os
import re
import pickle
import numpy as np

import config


class TextProcessor:
    """
    文本预处理与特征提取器

    流程：
    1. NLTK 分词 + 去停用词 + 词形还原
    2. TF-IDF 向量化
    3. 输出固定维度特征向量
    """

    def __init__(self, max_features=config.TFIDF_MAX_FEATURES):
        self.max_features = max_features
        self.vectorizer = None       # TfidfVectorizer 实例
        self.stopwords = None
        self.lemmatizer = None
        self._nltk_ready = False
        self._init_nltk()

    def _init_nltk(self):
        """初始化 NLTK 资源"""
        try:
            import nltk
            # 确保所需资源已下载
            for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
                try:
                    nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else
                                   f"corpora/{resource}" if resource in ("stopwords", "wordnet") else
                                   f"tokenizers/{resource}")
                except LookupError:
                    nltk.download(resource, quiet=True)

            from nltk.corpus import stopwords
            from nltk.stem import WordNetLemmatizer
            self.stopwords = set(stopwords.words("english"))
            self.lemmatizer = WordNetLemmatizer()
            self._nltk_ready = True
        except ImportError:
            print("[NLP] nltk 未安装，请执行: pip install nltk")
        except Exception as e:
            print(f"[NLP] NLTK 初始化失败: {e}")

    def preprocess_text(self, text):
        """
        NLTK 文本预处理：小写 → 去标点 → 分词 → 去停用词 → 词形还原

        Args:
            text: 原始文本字符串

        Returns:
            str: 预处理后的空格分隔词串
        """
        if not text or not self._nltk_ready:
            return text.lower() if text else ""

        text = text.lower()
        text = re.sub(r"[^a-z\s]", " ", text)  # 去除非字母字符

        try:
            from nltk.tokenize import word_tokenize
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()

        # 去停用词 + 词形还原
        tokens = [
            self.lemmatizer.lemmatize(t)
            for t in tokens
            if t not in self.stopwords and len(t) > 1
        ]

        return " ".join(tokens) if tokens else "empty"

    def fit_vectorizer(self, texts):
        """
        在文本语料上拟合 TF-IDF 向量化器

        Args:
            texts: list[str] 原始文本列表
        """
        from sklearn.feature_extraction.text import TfidfVectorizer

        processed = [self.preprocess_text(t) for t in texts]
        # 过滤空文本
        valid_texts = [t for t in processed if t and t != "empty"]
        if not valid_texts:
            valid_texts = ["empty"]

        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            sublinear_tf=True,       # 1+log(tf)
            norm="l2",
        )
        self.vectorizer.fit(valid_texts)
        print(f"[NLP] TF-IDF 向量化器已拟合，词汇量: {len(self.vectorizer.vocabulary_)}")

    def transform(self, text):
        """
        将单条文本转为 TF-IDF 特征向量

        Args:
            text: 原始文本

        Returns:
            np.ndarray: (max_features,) 或 None
        """
        if self.vectorizer is None:
            return np.zeros(self.max_features, dtype=np.float32)

        processed = self.preprocess_text(text)
        if not processed or processed == "empty":
            return np.zeros(self.max_features, dtype=np.float32)

        vec = self.vectorizer.transform([processed]).toarray().flatten()
        # 填充到固定维度
        if len(vec) < self.max_features:
            vec = np.pad(vec, (0, self.max_features - len(vec)))
        return vec.astype(np.float32)

    def transform_batch(self, texts):
        """
        批量转换为 TF-IDF 特征矩阵

        Returns:
            np.ndarray: (batch_size, max_features)
        """
        features = []
        for text in texts:
            feat = self.transform(text)
            if feat is None:
                feat = np.zeros(self.max_features, dtype=np.float32)
            features.append(feat)
        return np.stack(features, axis=0)

    def save(self, path):
        """保存向量化器"""
        with open(path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load(self, path):
        """加载向量化器"""
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.vectorizer = pickle.load(f)
            return True
        return False
