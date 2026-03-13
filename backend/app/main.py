from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logger import logger
from app.routers import urls, knowledge, chat
from app.core.database import engine, Base
import time


app = FastAPI(
    title="Web RAG Knowledge Base System",
    description="基于通用网页内容提取的知识库系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(f"请求开始：{request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"请求完成：{request.method} {request.url.path} - "
        f"状态：{response.status_code} - 耗时：{process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

app.include_router(urls.router, prefix="/api/urls", tags=["URLs"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {
        "message": "Web RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/api/settings")
async def get_settings():
    return {
        "openai_api_key": settings.OPENAI_API_KEY[:8] + "..." if settings.OPENAI_API_KEY else "",
        "openai_model": settings.OPENAI_MODEL,
        "dashscope_api_key": settings.DASHSCOPE_API_KEY[:8] + "..." if settings.DASHSCOPE_API_KEY else "",
        "dashscope_model": settings.DASHSCOPE_MODEL,
        "llm_provider": settings.LLM_PROVIDER,
    }


@app.post("/api/settings")
async def update_settings(request: Request):
    try:
        body = await request.json()
        logger.info(f"收到设置更新请求：{body.keys()}")
        return {
            "message": "设置已更新",
            "updated_keys": list(body.keys())
        }
    except Exception as e:
        logger.error(f"更新设置失败：{e}")
        return JSONResponse(
            status_code=400,
            content={"message": "更新失败", "error": str(e)}
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常：{request.method} {request.url.path} - {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )
