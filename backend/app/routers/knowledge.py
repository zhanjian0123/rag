from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.database import WebContent, ContentCollection, CollectionURL, ProcessingTask
from app.models.schemas import (
    BuildKnowledgeRequest,
    TaskStatusResponse,
    CollectionResponse,
    StatsResponse,
    CreateCollectionRequest
)
from app.services.web_extractor import WebExtractor
from app.services.rag import rag_service

router = APIRouter()
extractor = WebExtractor()


async def process_build_task(urls: List[str], task_id: str, db: Session):
    """后台处理构建任务"""
    task = db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()
    if not task:
        return

    task.status = "running"
    db.commit()

    content = None

    for url in urls:
        try:
            extracted = await extractor.extract_content(url)

            content = db.query(WebContent).filter(WebContent.url == url).first()
            if content:
                content.title = extracted.title
                content.content = extracted.content
                content.text_content = extracted.text_content
                content.excerpt = extracted.excerpt
                content.content_hash = extracted.content_hash
                content.word_count = extracted.word_count
                content.last_fetched_at = datetime.utcnow()
            else:
                content = WebContent(
                    url=extracted.url,
                    title=extracted.title,
                    author=extracted.author,
                    publish_date=extracted.date,
                    site_name=extracted.site_name,
                    content=extracted.content,
                    text_content=extracted.text_content,
                    excerpt=extracted.excerpt,
                    content_hash=extracted.content_hash,
                    word_count=extracted.word_count,
                    last_fetched_at=datetime.utcnow()
                )
                db.add(content)

            db.commit()
            db.refresh(content)

            await rag_service.add_content(extracted)

            content.is_processed = True
            db.commit()

            task.processed_count += 1

        except Exception as e:
            task.failed_count += 1
            if content:
                content.process_error = str(e)
                content.retry_count += 1
                db.commit()

        task.progress = int((task.processed_count + task.failed_count) / task.total_count * 100)
        db.commit()

    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()


@router.post("/build")
async def build_knowledge(
    request: BuildKnowledgeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """构建知识库"""
    collection_id = request.collection_id
    collection_name = request.collection_name
    urls = request.urls

    # 创建或获取集合
    if collection_name:
        # 检查是否已存在
        existing = db.query(ContentCollection).filter(
            ContentCollection.name == collection_name
        ).first()
        if existing:
            collection_id = existing.id
        else:
            collection = ContentCollection(
                name=collection_name,
                description=""
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)
            collection_id = collection.id

    # 如果没有提供 URLs，从集合或未处理的记录中获取
    if not urls:
        if collection_id:
            contents = db.query(WebContent).join(CollectionURL).filter(
                CollectionURL.collection_id == collection_id
            ).all()
            urls = [c.url for c in contents]
        else:
            contents = db.query(WebContent).filter(
                WebContent.is_processed == False
            ).all()
            urls = [c.url for c in contents]

    if not urls:
        raise HTTPException(
            status_code=400,
            detail="没有需要处理的 URL，请先添加 URL 或指定集合"
        )

    # 创建任务记录
    task_id = f"build_{datetime.utcnow().timestamp()}"
    task = ProcessingTask(
        task_id=task_id,
        task_type="build",
        status="pending",
        total_count=len(urls)
    )
    db.add(task)
    db.commit()

    if request.background:
        background_tasks.add_task(process_build_task, urls, task_id, db)
        return {"task_id": task_id, "message": "知识库构建任务已启动", "status": "pending"}
    else:
        await process_build_task(urls, task_id, db)
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "知识库构建完成",
            "processed": task.processed_count,
            "failed": task.failed_count
        }


@router.get("/build/status/{task_id}", response_model=TaskStatusResponse)
async def get_build_status(task_id: str, db: Session = Depends(get_db)):
    """获取构建任务状态"""
    task = db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        total=task.total_count,
        processed=task.processed_count,
        failed=task.failed_count,
        message=f"已处理 {task.processed_count}/{task.total_count}"
    )


@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(db: Session = Depends(get_db)):
    """获取集合列表"""
    collections = db.query(ContentCollection).all()
    result = []
    for c in collections:
        url_count = db.query(CollectionURL).filter(
            CollectionURL.collection_id == c.id
        ).count()
        result.append(CollectionResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            url_count=url_count,
            is_active=c.is_active,
            created_at=c.created_at
        ))
    return result


@router.post("/collections")
async def create_collection(
    request: CreateCollectionRequest,
    db: Session = Depends(get_db)
):
    """创建集合"""
    # 检查名称是否已存在
    existing = db.query(ContentCollection).filter(
        ContentCollection.name == request.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="集合名称已存在")

    collection = ContentCollection(
        name=request.name,
        description=request.description
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)

    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        url_count=0,
        is_active=collection.is_active,
        created_at=collection.created_at
    )


@router.delete("/collections/{collection_id}")
async def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """删除集合"""
    collection = db.query(ContentCollection).filter(
        ContentCollection.id == collection_id
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="集合不存在")

    db.delete(collection)
    db.commit()

    return {"message": "删除成功"}


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""
    total_urls = db.query(WebContent).count()
    processed_urls = db.query(WebContent).filter(
        WebContent.is_processed == True
    ).count()

    rag_stats = await rag_service.get_stats()

    return StatsResponse(
        total_urls=total_urls,
        processed_urls=processed_urls,
        vector_documents=rag_stats.get("total_documents", 0),
        bm25_documents=rag_stats.get("bm25_documents", 0)
    )
