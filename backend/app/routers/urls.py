from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.database import WebContent, ContentCollection, CollectionURL, ProcessingTask
from app.models.schemas import (
    URLAddRequest,
    URLBatchImportRequest,
    URLResponse,
    URLDetailResponse,
    TaskStatusResponse
)
from app.services.web_extractor import WebExtractor
from app.services.rag import rag_service

router = APIRouter()
extractor = WebExtractor()


async def process_batch(urls: List[str], task_id: str, db: Session):
    """后台处理批量导入任务"""
    task = db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()
    if not task:
        return

    task.status = "running"
    db.commit()

    result = await extractor.extract_batch(urls)

    for r in result["results"]:
        if r["success"]:
            existing = db.query(WebContent).filter(WebContent.url == r["url"]).first()
            if existing:
                continue

            data = r["data"]
            content = WebContent(
                url=data.url,
                title=data.title,
                author=data.author,
                publish_date=data.date,
                site_name=data.site_name,
                content=data.content,
                text_content=data.text_content,
                excerpt=data.excerpt,
                content_hash=data.content_hash,
                word_count=data.word_count,
                is_processed=False,
                last_fetched_at=datetime.utcnow()
            )
            db.add(content)
            task.processed_count += 1
        else:
            task.failed_count += 1
        db.commit()

    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()


@router.post("/add", response_model=URLResponse)
async def add_url(
    request: URLAddRequest,
    db: Session = Depends(get_db)
):
    """添加单个 URL"""
    # 检查是否已存在
    existing = db.query(WebContent).filter(WebContent.url == request.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL 已存在")

    try:
        extracted = await extractor.extract_content(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"提取失败：{str(e)}")

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
        is_processed=False,
        last_fetched_at=datetime.utcnow()
    )
    db.add(content)
    db.commit()
    db.refresh(content)

    # 关联集合
    if request.collection_id:
        collection_url = CollectionURL(
            collection_id=request.collection_id,
            content_id=content.id
        )
        db.add(collection_url)
        db.commit()

    return URLResponse(
        id=content.id,
        url=content.url,
        title=content.title,
        site_name=content.site_name,
        is_processed=content.is_processed,
        created_at=content.created_at
    )


@router.post("/add/batch")
async def add_url_batch(
    request: URLBatchImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """批量导入 URL"""
    # URL 去重
    if request.dedupe:
        existing_urls = db.query(WebContent.url).filter(
            WebContent.url.in_(request.urls)
        ).all()
        existing_set = {url[0] for url in existing_urls}
        urls_to_add = [url for url in request.urls if url not in existing_set]
    else:
        urls_to_add = request.urls

    if not urls_to_add:
        return {"message": "所有 URL 已存在", "task_id": None}

    # 创建任务记录
    task_id = f"batch_{datetime.utcnow().timestamp()}"
    task = ProcessingTask(
        task_id=task_id,
        task_type="batch_import",
        status="pending",
        total_count=len(urls_to_add)
    )
    db.add(task)
    db.commit()

    background_tasks.add_task(process_batch, urls_to_add, task_id, db)

    return {
        "task_id": task_id,
        "message": f"批量导入任务已启动，共 {len(urls_to_add)} 个 URL",
        "skipped": len(request.urls) - len(urls_to_add)
    }


@router.get("/list", response_model=List[URLResponse])
async def list_urls(
    skip: int = Query(default=0, ge=0, description="跳过记录数"),
    limit: int = Query(default=50, ge=1, le=200, description="返回记录数"),
    collection_id: Optional[int] = Query(None, ge=1, description="集合 ID"),
    is_processed: Optional[bool] = Query(None, description="处理状态筛选"),
    db: Session = Depends(get_db)
):
    """获取 URL 列表"""
    query = db.query(WebContent)

    if collection_id:
        query = query.join(CollectionURL).filter(
            CollectionURL.collection_id == collection_id
        )

    if is_processed is not None:
        query = query.filter(WebContent.is_processed == is_processed)

    contents = query.order_by(
        WebContent.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [
        URLResponse(
            id=c.id,
            url=c.url,
            title=c.title,
            site_name=c.site_name,
            is_processed=c.is_processed,
            created_at=c.created_at
        ) for c in contents
    ]


@router.get("/{url_id}", response_model=URLDetailResponse)
async def get_url(url_id: int, db: Session = Depends(get_db)):
    """获取 URL 详情"""
    content = db.query(WebContent).filter(WebContent.id == url_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="URL 不存在")

    return URLDetailResponse(
        id=content.id,
        url=content.url,
        title=content.title,
        author=content.author,
        publish_date=content.publish_date,
        site_name=content.site_name,
        content=content.content,
        excerpt=content.excerpt,
        content_hash=content.content_hash,
        word_count=content.word_count,
        is_processed=content.is_processed,
        process_error=content.process_error,
        retry_count=content.retry_count,
        created_at=content.created_at,
        updated_at=content.updated_at,
        last_fetched_at=content.last_fetched_at
    )


@router.delete("/{url_id}")
async def delete_url(url_id: int, db: Session = Depends(get_db)):
    """删除 URL"""
    content = db.query(WebContent).filter(WebContent.id == url_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="URL 不存在")

    # 从向量库删除
    try:
        await rag_service.delete_content(content.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"从向量库删除失败：{str(e)}")

    # 删除关联记录
    db.query(CollectionURL).filter(CollectionURL.content_id == url_id).delete()
    db.delete(content)
    db.commit()

    return {"message": "删除成功"}


@router.post("/validate")
async def validate_urls(urls: List[str]):
    """验证 URL 可访问性"""
    results = []
    for url in urls:
        status = await extractor.check_url_status(url)
        results.append({"url": url, **status})
    return results


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """获取任务状态"""
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
