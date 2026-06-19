"""
完整 RAG 系统（纯 Python 版）
==============================
BM25 关键词检索 + AI 问答
零外部依赖，无需下载任何模型，断网也能用
"""

import os
import re
import math
from collections import Counter
from src.utils import ask_llm


class BM25:
    """BM25 关键词检索算法（纯 Python 实现）"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_count = 0
        self.avg_doc_len = 0
        self.idf = {}
        self.doc_freq = Counter()

    def _tokenize(self, text):
        """简单中文分词（按字和词切分）"""
        # 按非中文字符切分，保留中文
        tokens = re.findall(r'[\w]+', text.lower())
        # 中文单字
        chinese_chars = re.findall(r'[一-鿿]', text.lower())
        return tokens + chinese_chars

    def fit(self, documents):
        """构建索引"""
        self.documents = documents
        self.doc_count = len(documents)
        total_length = 0

        # 统计词频和文档频率
        doc_token_lists = []
        for doc in documents:
            tokens = self._tokenize(doc)
            doc_token_lists.append(tokens)
            total_length += len(tokens)
            # 文档频率：包含该词的文档数
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freq[token] += 1

        self.avg_doc_len = total_length / max(self.doc_count, 1)

        # 计算 IDF
        for token, freq in self.doc_freq.items():
            self.idf[token] = math.log(
                (self.doc_count - freq + 0.5) / (freq + 0.5) + 1.0
            )

        self.doc_token_lists = doc_token_lists
        print(f"📚 BM25 索引就绪：{self.doc_count} 个文档，{len(self.idf)} 个词条")

    def search(self, query, top_k=5):
        """搜索最相关的文档"""
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        scores = []

        for i, tokens in enumerate(self.doc_token_lists):
            doc_len = len(tokens)
            token_count = Counter(tokens)
            score = 0.0

            for token in query_tokens:
                if token in self.idf:
                    tf = token_count.get(token, 0)
                    idf = self.idf[token]
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                    score += idf * numerator / denominator

            scores.append((i, score))

        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)
        results = [self.documents[i] for i, s in scores[:top_k] if s > 0]

        return results if results else self.documents[:top_k]


class RAG:
    """检索增强生成系统（纯 Python，零下载）"""

    def __init__(self):
        self.bm25 = BM25()
        self.documents = []
        self.sources = []

    def chunk_text(self, text, chunk_size=300):
        """把长文本切分成小块"""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) < chunk_size:
                current += para + "\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n"

        if current:
            chunks.append(current.strip())

        # 合并太小的块
        merged = []
        temp = ""
        for c in chunks:
            if len(temp) + len(c) < chunk_size * 0.5:
                temp += c + "\n"
            else:
                if temp:
                    merged.append(temp.strip())
                temp = c + "\n"
        if temp:
            merged.append(temp.strip())

        if not merged:
            merged = [text.strip()]

        return merged

    def add_file(self, filepath):
        """把一个文件加入知识库"""
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在：{filepath}")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = self.chunk_text(text)
        self.add_chunks(chunks, source=os.path.basename(filepath))
        print(f"✅ 已添加：{filepath}")

    def add_chunks(self, chunks, source="unknown"):
        """把文本块加入索引"""
        self.documents.extend(chunks)
        self.sources.extend([source] * len(chunks))
        self.bm25.fit(self.documents)
        print(f"📦 知识库现有 {len(self.documents)} 个文档块")

    def search(self, query, top_k=5):
        """搜索最相关的文档块"""
        return self.bm25.search(query, top_k)

    def query(self, question, top_k=5):
        """检索 + 生成回答"""
        if not self.documents:
            return "知识库为空，请先添加文档。"

        docs = self.search(question, top_k)
        if not docs:
            return "未找到相关信息。"

        context = "\n\n".join([f"[片段{i+1}] {d}" for i, d in enumerate(docs)])

        prompt = (
            f"基于以下参考资料回答问题。\n\n"
            f"参考资料：\n{context}\n\n"
            f"问题：{question}\n\n"
            f"要求：\n"
            f"1. 只基于参考资料回答\n"
            f"2. 如果资料中没有相关信息，说'资料中未提及'\n"
            f"3. 引用相关片段编号"
        )
        return ask_llm(
            [{"role": "user", "content": prompt}],
            system="你是一个知识库问答助手，严格基于提供的资料回答。",
            temp=0.3,
            max_tokens=1000
        )

    def add_folder(self, folder_path):
        """批量添加文件夹中的所有 .txt 文件"""
        if not os.path.exists(folder_path):
            print(f"❌ 文件夹不存在：{folder_path}")
            return
        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        if not files:
            print(f"⚠️ 文件夹中没有 .txt 文件")
            return
        print(f"📂 找到 {len(files)} 个文件")
        for f in files:
            self.add_file(os.path.join(folder_path, f))

    def info(self):
        """查看知识库状态"""
        print(f"\n📊 知识库状态")
        print(f"{'=' * 30}")
        print(f"文档块数量：{len(self.documents)}")
        print(f"索引方式：BM25 关键词检索（纯 Python）")
        return len(self.documents)


def demo():
    """演示"""
    rag = RAG()
    # 先用 knowledge_base.txt
    rag.add_file("data/knowledge_base.txt")

    print(f"\n{'=' * 50}")
    print("💬 测试问答")
    print(f"{'=' * 50}")

    questions = [
        "AI 文案代写怎么定价？",
        "AI 工具开发能赚多少钱？",
        "今天天气怎么样？",  # 故意不在库里
    ]
    for q in questions:
        print(f"\n❓ {q}")
        answer = rag.query(q)
        print(f"💡 {answer}")
        print("-" * 40)


if __name__ == "__main__":
    demo()
