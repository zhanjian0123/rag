from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== 请求模型 ====================

class URLAddRequest(BaseModel):
    """添加 URL 请求"""
    url: str = Field(..., min_length=1, max_length=2048, description="网页 URL")
    collection_id: Optional[int] = Field(None, ge=1, description="集合 ID")
    metadata: Optional[dict] = Field(None, description="元数据")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "url": "https://example.com/article",
            "collection_id": 1,
            "metadata": {"source": "manual"}
        }
    })


class URLBatchImportRequest(BaseModel):
    """批量导入 URL 请求"""
    urls: List[str] = Field(..., min_length=1, max_length=100, description="URL 列表")
    collection_id: Optional[int] = Field(None, ge=1, description="集合 ID")
    dedupe: bool = Field(True, description="是否去重")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "urls": [
                "https://example.com/article1",
                "https://example.com/article2"
            ],
            "collection_id": 1,
            "dedupe": True
        }
    })


class ChatRequest(BaseModel):
    """聊天请求"""
    question: str = Field(..., min_length=1, max_length=5000, description="问题")
    collection_id: Optional[int] = Field(None, ge=1, description="集合 ID")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "question": "什么是机器学习？",
            "top_k": 5
        }
    })


class BuildKnowledgeRequest(BaseModel):
    """构建知识库请求"""
    urls: Optional[List[str]] = Field(None, description="URL 列表")
    collection_name: Optional[str] = Field(None, min_length=1, max_length=100, description="集合名称")
    collection_id: Optional[int] = Field(None, ge=1, description="集合 ID")
    background: bool = Field(True, description="是否后台执行")


class CreateCollectionRequest(BaseModel):
    """创建集合请求"""
    name: str = Field(..., min_length=1, max_length=100, description="集合名称")
    description: str = Field("", max_length=500, description="集合描述")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "技术文档",
            "description": "收集技术相关的文档"
        }
    })


class UpdateSettingsRequest(BaseModel):
    """更新设置请求"""
    openai_api_key: Optional[str] = Field(None, description="OpenAI API 密钥")
    openai_model: Optional[str] = Field(None, description="OpenAI 模型")
    dashscope_api_key: Optional[str] = Field(None, description="DashScope API 密钥")
    dashscope_model: Optional[str] = Field(None, description="DashScope 模型")
    llm_provider: Optional[str] = Field(None, description="LLM 提供商")


# ==================== 响应模型 ====================

class URLResponse(BaseModel):
    """URL 响应"""
    id: int
    url: str
    title: Optional[str]
    site_name: Optional[str]
    is_processed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class URLDetailResponse(BaseModel):
    """URL 详情响应"""
    id: int
    url: str
    title: Optional[str]
    author: Optional[str]
    publish_date: Optional[datetime]
    site_name: Optional[str]
    content: Optional[str]
    excerpt: Optional[str]
    content_hash: Optional[str]
    word_count: Optional[int]
    is_processed: bool
    process_error: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    last_fetched_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SourceInfo(BaseModel):
    """来源信息"""
    url: str
    title: str
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    sources: List[SourceInfo]


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: int
    total: int
    processed: int
    failed: int
    message: str


class CollectionResponse(BaseModel):
    """集合响应"""
    id: int
    name: str
    description: Optional[str]
    url_count: int
    is_active: bool
    created_at: datetime


class StatsResponse(BaseModel):
    """统计信息响应"""
    total_urls: int
    processed_urls: int
    vector_documents: int
    bm25_documents: int = 0


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """错误响应"""
    message: str
    detail: Optional[str] = None
