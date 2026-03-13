from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.database import ChatHistory
from app.models.schemas import ChatRequest, ChatResponse, SourceInfo

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """智能问答"""
    from app.services.rag import rag_service

    try:
        answer, sources = await rag_service.ask(
            request.question,
            top_k=request.top_k
        )

        # 保存聊天历史
        chat_history = ChatHistory(
            session_id=request.collection_id or "default",
            question=request.question,
            answer=answer,
            sources=str([s.model_dump() if hasattr(s, 'model_dump') else s.__dict__ for s in sources])
        )
        db.add(chat_history)
        db.commit()

        return ChatResponse(
            answer=answer,
            sources=[
                SourceInfo(
                    url=s.url,
                    title=s.title,
                    excerpt=s.excerpt,
                    score=s.score
                ) for s in sources
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"问答处理失败：{str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    session_id: Optional[str] = None,
    skip: int = Query(default=0, ge=0, description="跳过记录数"),
    limit: int = Query(default=20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取聊天历史"""
    query = db.query(ChatHistory)

    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)

    total = query.count()
    history = query.order_by(
        ChatHistory.created_at.desc()
    ).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "history": [
            {
                "id": h.id,
                "session_id": h.session_id,
                "question": h.question,
                "answer": h.answer,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in history
        ]
    }


@router.delete("/history/{history_id}")
async def delete_chat_history(history_id: int, db: Session = Depends(get_db)):
    """删除聊天历史"""
    history = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(history)
    db.commit()

    return {"message": "删除成功"}


@router.delete("/history")
async def clear_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """清空聊天历史"""
    query = db.query(ChatHistory)
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)

    deleted = query.delete()
    db.commit()

    return {"message": f"已删除 {deleted} 条记录"}
