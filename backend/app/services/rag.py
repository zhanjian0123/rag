from typing import List, Optional, Dict, Tuple, Set
from dataclasses import dataclass, field
import hashlib
import asyncio
from functools import lru_cache
from collections import OrderedDict

from app.core.config import settings
from app.core.logger import get_logger
from app.services.web_extractor import ExtractedContent
from app.services.bm25_index import bm25_index
from app.services.reranker import reranker, RerankResult

logger = get_logger("rag")


@dataclass
class SourceInfo:
    """来源信息"""
    url: str
    title: str
    excerpt: str
    score: float


@dataclass
class SearchResult:
    """检索结果"""
    doc_id: str
    url: str
    title: str
    content: str
    score: float
    metadata: Dict
    source: str = "dense"  # "dense", "sparse", or "reranked"


class RAGService:
    """RAG 服务 - 双路混合检索 + Reranker 重排序"""

    def __init__(self):
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self._client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_or_create_collection(
            name="web_contents",
            metadata={"hnsw:space": "cosine"}
        )
        self._embedding_cache: OrderedDict[str, List[float]] = OrderedDict()
        self._use_reranker = settings.USE_RERANKER

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入"""
        # 检查缓存
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self._embedding_cache:
            # LRU 缓存：移动到末尾表示最近使用
            self._embedding_cache.move_to_end(cache_key)
            return self._embedding_cache[cache_key]

        embedding = self._compute_embedding(text)
        self._embedding_cache[cache_key] = embedding

        # 限制缓存大小
        if len(self._embedding_cache) > 1000:
            # 删除最旧的 500 个
            keys_to_remove = list(self._embedding_cache.keys())[:500]
            for key in keys_to_remove:
                del self._embedding_cache[key]

        return embedding

    def _compute_embedding(self, text: str) -> List[float]:
        """计算文本嵌入"""
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding 失败：{e}")
                raise ValueError(f"OpenAI embedding 失败：{e}")

        elif settings.LLM_PROVIDER == "dashscope" and settings.DASHSCOPE_API_KEY:
            try:
                import dashscope
                from dashscope import TextEmbedding
                dashscope.api_key = settings.DASHSCOPE_API_KEY
                response = TextEmbedding.call(
                    model=settings.DASHSCOPE_EMBEDDING_MODEL,
                    input=text
                )
                if response.output and 'embeddings' in response.output:
                    return response.output['embeddings'][0]['embedding']
                raise ValueError(f"DashScope 响应格式错误：{response}")
            except Exception as e:
                logger.error(f"DashScope embedding 失败：{e}")
                raise ValueError(f"DashScope embedding 失败：{e}")
        else:
            raise ValueError("未配置 LLM Provider，请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY")

    def _generate_id(self, url: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(url.encode()).hexdigest()

    async def add_content(self, content: ExtractedContent) -> str:
        """添加内容到向量库和 BM25 索引"""
        logger.info(f"添加内容到知识库：{content.url}")

        content_id = self._generate_id(content.url)
        text_content = content.text_content or ""

        if not text_content:
            logger.warning(f"内容为空，跳过：{content.url}")
            return content_id

        try:
            # 1. 添加到向量库 (Dense)
            embedding = self._get_embedding(text_content[:8000])
            self._collection.upsert(
                ids=[content_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{
                    "url": content.url,
                    "title": content.title or "",
                    "excerpt": content.excerpt or "",
                    "site_name": content.site_name or ""
                }]
            )

            # 2. 添加到 BM25 索引 (Sparse)
            bm25_index.add_document(
                doc_id=content_id,
                url=content.url,
                title=content.title or "",
                content=text_content[:8000],
                metadata={
                    "excerpt": content.excerpt or "",
                    "site_name": content.site_name or ""
                }
            )

            logger.info(f"成功添加到知识库 (Dense + Sparse)：{content.url}")
            return content_id

        except Exception as e:
            logger.error(f"添加到知识库失败 {content.url}: {e}")
            raise

    async def add_batch(self, contents: List[ExtractedContent]) -> Dict[str, int]:
        """批量添加内容到知识库"""
        # 向量库批量添加
        dense_ids = []
        dense_embeddings = []
        dense_documents = []
        dense_metadatas = []

        # BM25 批量添加
        sparse_docs = []

        for content in contents:
            content_id = self._generate_id(content.url)
            text_content = content.text_content or ""

            if not text_content:
                continue

            try:
                embedding = self._get_embedding(text_content[:8000])
                dense_ids.append(content_id)
                dense_embeddings.append(embedding)
                dense_documents.append(text_content)
                dense_metadatas.append({
                    "url": content.url,
                    "title": content.title or "",
                    "excerpt": content.excerpt or "",
                    "site_name": content.site_name or ""
                })

                sparse_docs.append((
                    content_id,
                    content.url,
                    content.title or "",
                    text_content[:8000],
                    {
                        "excerpt": content.excerpt or "",
                        "site_name": content.site_name or ""
                    }
                ))
            except Exception as e:
                logger.error(f"批量添加失败 {content.url}: {e}")

        added_count = 0
        if dense_ids:
            self._collection.upsert(
                ids=dense_ids,
                embeddings=dense_embeddings,
                documents=dense_documents,
                metadatas=dense_metadatas
            )
            added_count = len(dense_ids)

        # BM25 批量添加
        if sparse_docs:
            bm25_index.add_batch(sparse_docs)

        return {"added": added_count}

    def _merge_results(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult]
    ) -> List[Dict]:
        """
        合并双路检索结果
        使用倒数排名融合 (Reciprocal Rank Fusion, RRF)
        """
        # 构建 doc_id 到结果的映射
        doc_map: Dict[str, Dict] = {}

        # 处理 Dense 结果
        for rank, result in enumerate(dense_results, 1):
            doc_map[result.doc_id] = {
                'doc_id': result.doc_id,
                'url': result.url,
                'title': result.title,
                'content': result.content,
                'dense_score': result.score,
                'sparse_score': 0.0,
                'metadata': result.metadata
            }

        # 处理 Sparse 结果，合并
        for rank, result in enumerate(sparse_results, 1):
            if result.doc_id in doc_map:
                # 已存在，累加分数
                doc_map[result.doc_id]['sparse_score'] = result.score
            else:
                # 新文档
                doc_map[result.doc_id] = {
                    'doc_id': result.doc_id,
                    'url': result.url,
                    'title': result.title,
                    'content': result.content,
                    'dense_score': 0.0,
                    'sparse_score': result.score,
                    'metadata': result.metadata
                }

        # 使用 RRF 计算融合分数
        k = 60  # RRF 常数
        for doc_id, doc in doc_map.items():
            # 找到在 dense 结果中的排名
            dense_rank = next(
                (i for i, r in enumerate(dense_results, 1) if r.doc_id == doc_id),
                len(dense_results) + 1
            )
            # 找到在 sparse 结果中的排名
            sparse_rank = next(
                (i for i, r in enumerate(sparse_results, 1) if r.doc_id == doc_id),
                len(sparse_results) + 1
            )

            # RRF 分数
            doc['rrf_score'] = (1 / (k + dense_rank)) + (1 / (k + sparse_rank))

        # 按 RRF 分数排序
        merged = list(doc_map.values())
        merged.sort(key=lambda x: x['rrf_score'], reverse=True)

        return merged

    async def search(self, query: str, top_k: int = 5) -> List[SourceInfo]:
        """
        双路混合检索：
        1. Dense 检索 (向量相似度)
        2. Sparse 检索 (BM25 关键词匹配)
        3. RRF 融合
        4. Reranker 重排序 (可选)
        """
        logger.info(f"双路检索：{query[:50]}...")

        # 1. Dense 检索
        dense_results = await self._dense_search(query, settings.DENSE_TOP_K)
        logger.info(f"Dense 检索结果：{len(dense_results)} 条")

        # 2. Sparse 检索 (BM25)
        sparse_results = self._sparse_search(query, settings.SPARSE_TOP_K)
        logger.info(f"Sparse 检索结果：{len(sparse_results)} 条")

        # 3. 合并结果 (RRF)
        merged_results = self._merge_results(dense_results, sparse_results)
        logger.info(f"RRF 融合后：{len(merged_results)} 条")

        # 4. Reranker 重排序
        if self._use_reranker and merged_results:
            rerank_results = await self._rerank_results(query, merged_results, top_k)
            return self._convert_to_source_info(rerank_results)
        else:
            # 不使用 Reranker，直接返回 RRF 排名前 top_k
            final_results = merged_results[:top_k]
            return self._convert_to_source_info(final_results)

    async def _dense_search(self, query: str, top_k: int) -> List[SearchResult]:
        """向量检索"""
        try:
            query_embedding = self._get_embedding(query)

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            search_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distances = results.get("distances", [[]])[0]
                    score = 1 - distances[i] if i < len(distances) else 0

                    search_results.append(SearchResult(
                        doc_id=metadata.get("id", self._generate_id(metadata.get("url", ""))),
                        url=metadata.get("url", ""),
                        title=metadata.get("title", "") or "",
                        content=doc,
                        score=round(score, 4),
                        metadata=metadata,
                        source="dense"
                    ))

            return search_results

        except Exception as e:
            logger.error(f"Dense 检索失败：{e}")
            return []

    def _sparse_search(self, query: str, top_k: int) -> List[SearchResult]:
        """BM25 关键词检索"""
        try:
            results = bm25_index.search(query, top_k)

            search_results = []
            for doc_id, score, metadata in results:
                search_results.append(SearchResult(
                    doc_id=doc_id,
                    url=metadata.get('url', ''),
                    title=metadata.get('title', ''),
                    content=metadata.get('content', ''),
                    score=round(score, 4),
                    metadata=metadata,
                    source="sparse"
                ))

            return search_results

        except Exception as e:
            logger.error(f"Sparse 检索失败：{e}")
            return []

    async def _rerank_results(
        self,
        query: str,
        documents: List[Dict],
        top_k: int
    ) -> List[RerankResult]:
        """使用 Reranker 重排序"""
        try:
            rerank_results = reranker.rerank(query, documents, top_k)
            logger.info(f"Reranker 重排序完成，返回 {len(rerank_results)} 条")
            return rerank_results
        except Exception as e:
            logger.error(f"Reranker 重排序失败：{e}")
            # 降级：返回原始排名
            return documents[:top_k]

    def _convert_to_source_info(self, results: List) -> List[SourceInfo]:
        """将检索结果转换为 SourceInfo"""
        source_infos = []
        for result in results:
            if isinstance(result, RerankResult):
                source_infos.append(SourceInfo(
                    url=result.url,
                    title=result.title,
                    excerpt=(result.metadata.get('excerpt', '') or result.content)[:200],
                    score=round(result.score, 4)
                ))
            elif isinstance(result, dict):
                source_infos.append(SourceInfo(
                    url=result.get('url', ''),
                    title=result.get('title', ''),
                    excerpt=result.get('excerpt', result.get('content', ''))[:200],
                    score=round(result.get('rrf_score', 0), 4)
                ))
            else:
                # SearchResult 类型
                source_infos.append(SourceInfo(
                    url=result.url,
                    title=result.title,
                    excerpt=(result.metadata.get('excerpt', '') or result.content)[:200],
                    score=round(result.score, 4)
                ))

        return source_infos

    async def ask(
        self,
        question: str,
        top_k: int = 5
    ) -> Tuple[str, List[SourceInfo]]:
        """智能问答"""
        logger.info(f"收到问答请求：{question[:50]}...")

        # 双路混合检索
        sources = await self.search(question, top_k)

        if not sources:
            logger.info("未找到相关知识内容")
            return "抱歉，我没有找到相关的知识内容来回答这个问题。", []

        logger.info(f"找到 {len(sources)} 个相关来源")

        # 构建上下文
        context = "\n\n".join([
            f"[来源 {i+1}] {s.title}\n{s.excerpt}"
            for i, s in enumerate(sources)
        ])

        prompt = f"""请根据以下参考资料回答用户的问题。要求：
1. 只根据提供的参考资料回答，不要编造信息
2. 如果资料中没有相关信息，请如实说明
3. 回答要准确、简洁、有条理
4. 必要时可以引用来源

参考资料：
{context}

用户问题：{question}

请回答："""

        # 调用 LLM
        answer = await self._call_llm(prompt)

        return answer, sources

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM 生成回答"""
        system_prompt = "你是一个专业的知识库问答助手，根据给定的参考资料回答用户的问题。"

        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI LLM 调用失败：{e}")
                return f"抱歉，回答生成时遇到错误：{e}"

        elif settings.LLM_PROVIDER == "dashscope" and settings.DASHSCOPE_API_KEY:
            try:
                import dashscope
                from dashscope import Generation
                dashscope.api_key = settings.DASHSCOPE_API_KEY
                response = Generation.call(
                    model=settings.DASHSCOPE_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                if response.output and 'text' in response.output:
                    return response.output['text']
                return f"抱歉，回答生成时遇到错误：{response.message}"
            except Exception as e:
                logger.error(f"DashScope LLM 调用失败：{e}")
                return f"抱歉，回答生成时遇到错误：{e}"
        else:
            return "LLM Provider 未正确配置，请检查环境变量设置。"

    async def delete_content(self, url: str) -> bool:
        """从知识库删除内容"""
        content_id = self._generate_id(url)
        success = True

        try:
            # 从向量库删除
            self._collection.delete(ids=[content_id])
            logger.info(f"成功从向量库删除：{url}")
        except Exception as e:
            logger.error(f"从向量库删除失败 {url}: {e}")
            success = False

        try:
            # 从 BM25 索引删除
            bm25_index.remove_document(content_id)
            logger.info(f"成功从 BM25 索引删除：{url}")
        except Exception as e:
            logger.error(f"从 BM25 索引删除失败 {url}: {e}")
            # 不影响整体成功状态

        return success

    async def get_stats(self) -> dict:
        """获取统计信息"""
        try:
            return {
                "total_documents": self._collection.count(),
                "bm25_documents": bm25_index.get_document_count()
            }
        except Exception as e:
            logger.error(f"获取统计信息失败：{e}")
            return {"total_documents": 0, "bm25_documents": 0}


# 单例
rag_service = RAGService()
