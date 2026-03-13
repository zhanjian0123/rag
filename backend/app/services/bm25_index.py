"""BM25 稀疏检索索引服务"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
import os
import pickle
from rank_bm25 import BM25Okapi
from app.core.logger import get_logger

logger = get_logger("bm25_index")


@dataclass
class Document:
    """文档数据结构"""
    doc_id: str
    url: str
    title: str
    content: str
    metadata: Dict


class BM25Index:
    """BM25 索引服务"""

    def __init__(self, persist_directory: str = "./bm25_index"):
        self.persist_directory = persist_directory
        self.bm25: Optional[BM25Okapi] = None
        self.documents: Dict[str, Document] = {}
        self.doc_ids: List[str] = []
        self._tokenized_corpus: List[List[str]] = []

        # 确保持久化目录存在
        os.makedirs(self.persist_directory, exist_ok=True)

        # 加载现有索引
        self._load_index()

    def _tokenize(self, text: str) -> List[str]:
        """文本分词 - 中文使用字符级分词，英文使用空格分词"""
        # 简单的中文分词：按字符分割
        tokens = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                tokens.append(char)
            else:
                tokens.append(char)

        # 对于英文单词，合并连续的字幕
        result = []
        current_word = []
        for token in tokens:
            if token.isalnum() and not ('\u4e00' <= token <= '\u9fff'):
                current_word.append(token)
            else:
                if current_word:
                    result.append(''.join(current_word))
                    current_word = []
                if '\u4e00' <= token <= '\u9fff':
                    result.append(token)

        if current_word:
            result.append(''.join(current_word))

        return [t for t in result if t.strip()]

    def _load_index(self):
        """加载索引"""
        index_file = os.path.join(self.persist_directory, "bm25_index.pkl")
        docs_file = os.path.join(self.persist_directory, "documents.json")

        if os.path.exists(index_file) and os.path.exists(docs_file):
            try:
                with open(index_file, 'rb') as f:
                    data = pickle.load(f)
                    self._tokenized_corpus = data.get('tokenized_corpus', [])
                    self.doc_ids = data.get('doc_ids', [])

                with open(docs_file, 'r', encoding='utf-8') as f:
                    docs_data = json.load(f)
                    self.documents = {
                        k: Document(**v) if isinstance(v, dict) else v
                        for k, v in docs_data.items()
                    }

                if self._tokenized_corpus:
                    self.bm25 = BM25Okapi(self._tokenized_corpus)
                    logger.info(f"成功加载 BM25 索引，共 {len(self.documents)} 个文档")
            except Exception as e:
                logger.error(f"加载 BM25 索引失败：{e}")
                self._reset_index()

    def _save_index(self):
        """保存索引"""
        try:
            index_file = os.path.join(self.persist_directory, "bm25_index.pkl")
            docs_file = os.path.join(self.persist_directory, "documents.json")

            with open(index_file, 'wb') as f:
                pickle.dump({
                    'tokenized_corpus': self._tokenized_corpus,
                    'doc_ids': self.doc_ids
                }, f)

            # 序列化文档
            docs_data = {
                k: {
                    'doc_id': v.doc_id,
                    'url': v.url,
                    'title': v.title,
                    'content': v.content,
                    'metadata': v.metadata
                }
                for k, v in self.documents.items()
            }
            with open(docs_file, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, ensure_ascii=False)

            logger.info(f"已保存 BM25 索引，共 {len(self.documents)} 个文档")
        except Exception as e:
            logger.error(f"保存 BM25 索引失败：{e}")

    def _reset_index(self):
        """重置索引"""
        self.bm25 = None
        self.documents = {}
        self.doc_ids = []
        self._tokenized_corpus = []

    def add_document(self, doc_id: str, url: str, title: str, content: str,
                     metadata: Optional[Dict] = None) -> bool:
        """添加文档到索引"""
        try:
            # 如果文档已存在，先删除
            if doc_id in self.documents:
                self.remove_document(doc_id)

            # 创建文档对象
            doc = Document(
                doc_id=doc_id,
                url=url,
                title=title,
                content=content,
                metadata=metadata or {}
            )

            # 分词
            # 组合标题和内容进行索引，标题权重更高（通过重复）
            text_to_tokenize = f"{title} {title} {content}"
            tokens = self._tokenize(text_to_tokenize)

            # 添加文档
            self.documents[doc_id] = doc
            self.doc_ids.append(doc_id)
            self._tokenized_corpus.append(tokens)

            # 重新构建 BM25 索引
            self.bm25 = BM25Okapi(self._tokenized_corpus)

            logger.debug(f"添加文档到 BM25 索引：{doc_id}")
            return True

        except Exception as e:
            logger.error(f"添加文档到 BM25 索引失败：{e}")
            return False

    def add_batch(self, documents: List[Tuple[str, str, str, str, Optional[Dict]]]) -> int:
        """批量添加文档"""
        added_count = 0
        for doc_id, url, title, content, metadata in documents:
            if self.add_document(doc_id, url, title, content, metadata):
                added_count += 1

        # 批量保存
        self._save_index()
        return added_count

    def remove_document(self, doc_id: str) -> bool:
        """从索引中删除文档"""
        try:
            if doc_id not in self.documents:
                return False

            # 找到索引位置
            idx = self.doc_ids.index(doc_id)

            # 删除
            del self.documents[doc_id]
            self.doc_ids.pop(idx)
            self._tokenized_corpus.pop(idx)

            # 重新构建 BM25 索引
            if self._tokenized_corpus:
                self.bm25 = BM25Okapi(self._tokenized_corpus)
            else:
                self.bm25 = None

            logger.debug(f"从 BM25 索引删除文档：{doc_id}")
            return True

        except Exception as e:
            logger.error(f"删除 BM25 索引文档失败：{e}")
            return False

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Dict]]:
        """搜索相关文档"""
        if not self.bm25 or not self._tokenized_corpus:
            return []

        try:
            # 分词查询
            query_tokens = self._tokenize(query)

            if not query_tokens:
                return []

            # BM25 搜索
            scores = self.bm25.get_scores(query_tokens)

            # 获取 top-k
            results = []
            for i, score in enumerate(scores):
                if score > 0:  # 只返回有分数的结果
                    doc_id = self.doc_ids[i]
                    doc = self.documents.get(doc_id)
                    if doc:
                        results.append((
                            doc_id,
                            float(score),
                            {
                                'url': doc.url,
                                'title': doc.title,
                                'content': doc.content[:500],  # 限制内容长度
                                **doc.metadata
                            }
                        ))

            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)

            return results[:top_k]

        except Exception as e:
            logger.error(f"BM25 搜索失败：{e}")
            return []

    def get_document_count(self) -> int:
        """获取文档数量"""
        return len(self.documents)

    def clear(self):
        """清空索引"""
        self._reset_index()
        self._save_index()


# 单例
bm25_index = BM25Index()
