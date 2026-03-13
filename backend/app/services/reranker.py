"""BGE-Reranker 重排序服务"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import os

from app.core.logger import get_logger

logger = get_logger("reranker")


@dataclass
class RerankResult:
    """重排序结果"""
    doc_id: str
    url: str
    title: str
    content: str
    score: float
    metadata: Dict


class BGEReranker:
    """BGE-Reranker 重排序服务"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._initialized = False

    def _load_model(self):
        """加载 Reranker 模型"""
        if self._initialized:
            return

        try:
            from sentence_transformers import CrossEncoder

            logger.info(f"正在加载 Reranker 模型：{self.model_name}")
            self.model = CrossEncoder(self.model_name, device='cpu')
            self._initialized = True
            logger.info(f"Reranker 模型加载完成")

        except ImportError as e:
            logger.error(f"缺少依赖：{e}，请安装 sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"加载 Reranker 模型失败：{e}")
            # 如果模型加载失败（如模型不存在），降级为不使用 reranker
            self._initialized = False

    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[RerankResult]:
        """
        对文档列表进行重排序

        Args:
            query: 查询文本
            documents: 文档列表，每个文档包含 doc_id, url, title, content, metadata
            top_k: 返回的顶部文档数量

        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []

        # 尝试加载模型
        if not self._initialized:
            self._load_model()

        # 如果模型加载失败，直接返回原始文档（按输入顺序）
        if not self._initialized or self.model is None:
            logger.warning("Reranker 模型不可用，返回原始排序")
            return [
                RerankResult(
                    doc_id=doc['doc_id'],
                    url=doc['url'],
                    title=doc['title'],
                    content=doc['content'],
                    score=1.0 / (i + 1),  # 简单分数
                    metadata=doc.get('metadata', {})
                )
                for i, doc in enumerate(documents)
            ][:top_k]

        try:
            # 构建句子对
            sentence_pairs = []
            for doc in documents:
                # 组合查询和文档内容
                pair = [query, f"{doc['title']} {doc['content']}"]
                sentence_pairs.append(pair)

            # 批量预测相关性分数
            scores = self.model.predict(sentence_pairs, convert_to_tensor=False)

            # 构建结果
            results = []
            for i, doc in enumerate(documents):
                results.append({
                    'doc_id': doc['doc_id'],
                    'url': doc['url'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'score': float(scores[i]),
                    'metadata': doc.get('metadata', {})
                })

            # 按分数降序排序
            results.sort(key=lambda x: x['score'], reverse=True)

            # 返回 top-k
            return [
                RerankResult(
                    doc_id=r['doc_id'],
                    url=r['url'],
                    title=r['title'],
                    content=r['content'],
                    score=r['score'],
                    metadata=r['metadata']
                )
                for r in results[:top_k]
            ]

        except Exception as e:
            logger.error(f"Reranker 重排序失败：{e}")
            # 降级：返回原始文档
            return [
                RerankResult(
                    doc_id=doc['doc_id'],
                    url=doc['url'],
                    title=doc['title'],
                    content=doc['content'],
                    score=1.0 / (i + 1),
                    metadata=doc.get('metadata', {})
                )
                for i, doc in enumerate(documents)
            ][:top_k]


# 单例
reranker = BGEReranker()
