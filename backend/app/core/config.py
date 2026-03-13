from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "Web RAG Knowledge Base"
    DEBUG: bool = Field(default=False, description="调试模式")
    ENVIRONMENT: str = Field(default="production", description="运行环境")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./web_rag.db",
        description="数据库连接 URL"
    )

    # Chroma 向量库配置
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="./chroma_db",
        description="Chroma 持久化目录"
    )

    # OpenAI 配置
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API 密钥")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="OpenAI 模型")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="OpenAI 嵌入模型"
    )

    # DashScope 配置
    DASHSCOPE_API_KEY: str = Field(default="", description="阿里云 DashScope API 密钥")
    DASHSCOPE_MODEL: str = Field(default="qwen-turbo", description="DashScope 模型")
    DASHSCOPE_EMBEDDING_MODEL: str = Field(
        default="text-embedding-v2",
        description="DashScope 嵌入模型"
    )

    # LLM 提供商选择
    LLM_PROVIDER: str = Field(default="dashscope", description="LLM 提供商")

    # Reranker 配置
    USE_RERANKER: bool = Field(default=True, description="是否启用 Reranker 重排序")
    RERANKER_MODEL: str = Field(
        default="BAAI/bge-reranker-base",
        description="Reranker 模型名称"
    )
    RERANKER_TOP_K: int = Field(default=10, description="Reranker 重排序的候选数")

    # 检索配置
    DENSE_TOP_K: int = Field(default=15, description="向量检索返回数量")
    SPARSE_TOP_K: int = Field(default=15, description="BM25 检索返回数量")
    RERANK_TOP_K: int = Field(default=5, description="重排序后最终返回数量")
    # 混合检索权重配置
    VECTOR_WEIGHT: float = Field(default=0.7, description="向量检索权重")
    BM25_WEIGHT: float = Field(default=0.3, description="BM25 检索权重")

    # 切片策略配置
    CHUNK_STRATEGY: str = Field(default="hybrid", description="切片策略：sentence|paragraph|semantic|markdown|fixed|hybrid")
    CHUNK_SIZE: int = Field(default=500, description="切片大小（字符数）")
    CHUNK_OVERLAP: int = Field(default=100, description="切片重叠字符数")
    MD_CHUNK_BY_HEADER: bool = Field(default=True, description="Markdown 是否按标题层级切片")

    # 查询优化配置
    ENABLE_QUERY_REWRITE: bool = Field(default=True, description="是否启用查询重写")
    ENABLE_HYDE: bool = Field(default=False, description="是否启用 HyDE")
    ENABLE_QUERY_DECOMPOSE: bool = Field(default=False, description="是否启用子查询分解")

    # 网页提取配置
    TRAFILATURA_TIMEOUT: int = Field(default=30, description="网页提取超时时间 (秒)")
    TRAFILATURA_MAX_RETRIES: int = Field(default=3, description="最大重试次数")
    DEFAULT_USER_AGENT: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="默认 User-Agent"
    )

    # CORS 配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="允许的 CORS 源"
    )

    # API 限流配置
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="每分钟请求限制")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.DEBUG or self.ENVIRONMENT == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 单例配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例（依赖注入用）"""
    return settings
