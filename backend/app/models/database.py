from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class WebContent(Base):
    """网页内容表"""
    __tablename__ = 'web_contents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), unique=True, index=True, nullable=False, comment="网页 URL")
    title = Column(String(1000), nullable=True, comment="网页标题")
    author = Column(String(200), nullable=True, comment="作者")
    publish_date = Column(DateTime, nullable=True, comment="发布日期")
    site_name = Column(String(200), nullable=True, comment="网站名称")

    content = Column(Text, nullable=True, comment="Markdown 格式内容")
    text_content = Column(Text, nullable=True, comment="纯文本内容")
    excerpt = Column(Text, nullable=True, comment="摘要")
    raw_html = Column(Text, nullable=True, comment="原始 HTML")

    content_hash = Column(String(64), index=True, nullable=True, comment="内容哈希")
    word_count = Column(Integer, nullable=True, comment="字数")

    is_processed = Column(Boolean, default=False, index=True, comment="是否已处理")
    process_error = Column(Text, nullable=True, comment="处理错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")

    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )
    last_fetched_at = Column(DateTime, nullable=True, index=True, comment="最后获取时间")

    # 关系
    collection_urls = relationship("CollectionURL", back_populates="content", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_url_prefix', 'url', mysql_length=255),
        Index('idx_site_name', 'site_name'),
        Index('idx_is_processed_created', 'is_processed', 'created_at'),
    )

    def __repr__(self):
        return f"<WebContent(id={self.id}, url='{self.url[:50]}...')>"


class ContentCollection(Base):
    """内容集合表"""
    __tablename__ = 'content_collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True, comment="集合名称")
    description = Column(Text, nullable=True, comment="集合描述")

    is_active = Column(Boolean, default=True, index=True, comment="是否启用")
    auto_update = Column(Boolean, default=False, comment="是否自动更新")
    update_interval = Column(Integer, default=7, comment="更新间隔（天）")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关系
    urls = relationship("CollectionURL", back_populates="collection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ContentCollection(id={self.id}, name='{self.name}')>"


class CollectionURL(Base):
    """集合 -URL 关联表"""
    __tablename__ = 'collection_urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(
        Integer,
        ForeignKey('content_collections.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="集合 ID"
    )
    content_id = Column(
        Integer,
        ForeignKey('web_contents.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="内容 ID"
    )

    added_at = Column(DateTime, default=datetime.utcnow, comment="添加时间')

    # 关系
    collection = relationship("ContentCollection", back_populates="urls")
    content = relationship("WebContent", back_populates="collection_urls")

    # 唯一约束
    __table_args__ = (
        Index('idx_collection_content', 'collection_id', 'content_id', unique=True),
    )

    def __repr__(self):
        return f"<CollectionURL(collection_id={self.collection_id}, content_id={self.content_id})>"


class ProcessingTask(Base):
    """处理任务表"""
    __tablename__ = 'processing_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False, comment="任务 ID")

    task_type = Column(String(20), nullable=False, index=True, comment="任务类型")

    status = Column(String(20), nullable=False, index=True, default="pending", comment="任务状态")
    progress = Column(Integer, default=0, comment="进度百分比")

    total_count = Column(Integer, default=0, comment="总数')
    processed_count = Column(Integer, default=0, comment="已处理数")
    failed_count = Column(Integer, default=0, comment="失败数')

    error_message = Column(Text, nullable=True, comment="错误信息")

    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间")
    completed_at = Column(DateTime, nullable=True, index=True, comment="完成时间')

    def __repr__(self):
        return f"<ProcessingTask(task_id='{self.task_id}', status='{self.status}')>"


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = 'chat_histories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=True, comment="会话 ID")
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI 回答")
    sources = Column(Text, nullable=True, comment="参考来源（JSON 格式）")
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间')

    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
    )

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session_id='{self.session_id}')>"
