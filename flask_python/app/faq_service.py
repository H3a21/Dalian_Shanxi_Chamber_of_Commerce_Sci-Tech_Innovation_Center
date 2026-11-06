"""
FAQ 语义匹配引擎
优先使用 jieba 分词 + TF-IDF 余弦相似度进行中文问题匹配
如果依赖库未安装，回退到纯关键词匹配
"""
from datetime import datetime

# 可选依赖：jieba + scikit-learn（未安装时回退到关键词匹配）
_jieba_available = False
_sklearn_available = False
_numpy_available = False

try:
    import jieba
    _jieba_available = True
except ImportError:
    pass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _sklearn_available = True
except ImportError:
    pass

try:
    import numpy as np
    _numpy_available = True
except ImportError:
    pass


class FAQMatcher:
    """FAQ 匹配器（单例模式，内存缓存）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._faqs = []
            cls._instance._questions = []
            cls._instance._vectorizer = None
            cls._instance._matrix = None
            cls._instance._dirty = True
            cls._instance._last_loaded = None
        return cls._instance

    @staticmethod
    def mark_dirty():
        """外部调用：FAQ 有变更时标记缓存失效"""
        inst = FAQMatcher()
        inst._dirty = True

    def _load_faqs(self):
        """从 MongoDB 加载已发布的 FAQ"""
        from .mongo_models import FAQ
        try:
            docs = list(FAQ._collection.find({'status': 'published'}))
            self._faqs = docs
            self._questions = [d['question'] for d in docs]
            # 将 display_text 也加入匹配文本，使关键字/语义都能匹配到
            self._match_texts = []
            for d in docs:
                texts = [d.get('question', '')]
                dt = d.get('display_text', '')
                if dt:
                    texts.append(dt)
                self._match_texts.append(' '.join(texts))
            self._dirty = False
            self._last_loaded = datetime.now()

            if self._match_texts and _sklearn_available and _jieba_available and _numpy_available:
                self._vectorizer = TfidfVectorizer(
                    analyzer='word',
                    tokenizer=self._tokenize,
                    token_pattern=None
                )
                self._matrix = self._vectorizer.fit_transform(self._match_texts)
            else:
                self._vectorizer = None
                self._matrix = None
                if self._match_texts:
                    print(f"[FAQMatcher] 使用纯关键词匹配模式（jieba/scikit-learn 未安装），已加载 {len(self._match_texts)} 条 FAQ")
        except Exception as e:
            print(f"[FAQMatcher] 加载 FAQ 失败: {e}")
            self._faqs = []
            self._questions = []
            self._dirty = True

    def _tokenize(self, text):
        """jieba 分词（仅在 jieba 可用时被调用）"""
        if _jieba_available:
            return list(jieba.cut(text))
        return list(text)

    def _keyword_match(self, user_input):
        """快速关键词匹配：用户输入中的词是否直接出现在 FAQ 问题或 display_text 中"""
        user_lower = user_input.lower().strip()
        best_idx = -1
        best_len = 0
        # 优先精确匹配 question 字段（支持纯数字快捷方式如 "1"）
        for i, q in enumerate(self._questions):
            if user_lower == q.lower():
                return i, 1.0
        for i, txt in enumerate(self._match_texts):
            txt_lower = txt.lower()
            # 完全匹配
            if user_lower == txt_lower:
                return i, 1.0
            # 匹配文本完全包含在用户输入中
            if txt_lower in user_lower and len(txt_lower) > best_len:
                best_idx = i
                best_len = len(txt_lower)
            # 用户输入完全包含在匹配文本中
            if user_lower in txt_lower and len(user_lower) > best_len:
                best_idx = i
                best_len = len(user_lower)
        if best_idx >= 0 and best_len >= 2:
            return best_idx, 0.85
        return -1, 0

    def match(self, user_input, threshold=0.25):
        """
        匹配最佳 FAQ
        返回 (answer: str | None, score: float)
        """
        if self._dirty:
            self._load_faqs()

        if not self._match_texts:
            return None, 0

        # 1. 先尝试关键词快速匹配（不需要 sklearn）
        kw_idx, kw_score = self._keyword_match(user_input)
        if kw_score >= 0.85:
            return self._faqs[kw_idx]['answer'], kw_score

        # 2. TF-IDF 语义匹配（仅在 sklearn/jieba 可用时）
        if self._matrix is not None and self._vectorizer is not None:
            try:
                vec = self._vectorizer.transform([user_input])
                scores = cosine_similarity(vec, self._matrix)[0]
                best_idx = int(np.argmax(scores))
                best_score = float(scores[best_idx])
            except Exception as e:
                print(f"[FAQMatcher] TF-IDF 匹配失败，回退到关键词: {e}")
                if kw_idx >= 0:
                    return self._faqs[kw_idx]['answer'], kw_score
                return None, 0

            # 取两路匹配的最高分
            if best_score >= threshold:
                return self._faqs[best_idx]['answer'], best_score
            if kw_score > best_score and kw_score >= 0.2:
                return self._faqs[kw_idx]['answer'], kw_score

        # 3. 纯关键词模式：放宽阈值
        if kw_idx >= 0:
            return self._faqs[kw_idx]['answer'], kw_score

        return None, 0

    def get_all_questions(self):
        """获取所有已发布的匹配文本列表（供调试用）"""
        if self._dirty:
            self._load_faqs()
        return self._match_texts[:]
