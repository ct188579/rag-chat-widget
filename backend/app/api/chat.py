from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List

from app.services.rag_engine import RAGEngine
from app.core.vector_store import VectorStore
from app.core.llm import LLMManager
from app.models.schemas import ChatRequest, ChatResponse, RAGSource

router = APIRouter()


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_llm_manager(request: Request) -> LLMManager:
    return request.app.state.llm_manager


@router.post("/chat", response_model=ChatResponse)
async def chat(
        body: ChatRequest,
        vector_store: VectorStore = Depends(get_vector_store),
        llm: LLMManager = Depends(get_llm_manager)
):
    print(f"DEBUG: received body = {body}")
    try:
        rag_engine = RAGEngine(vector_store, llm)

        sources = []
        if body.enable_rag:
            sources = await rag_engine.retrieve(
                body.message,
                top_k=body.rag_config.top_k if body.rag_config else 5,
                namespace=body.rag_config.namespace if body.rag_config else None
            )
            context = rag_engine.format_context(sources)
        else:
            context = None

        answer = await rag_engine.ainvoke(body.message, context)

        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=body.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request_data: ChatRequest):
    """SSE流式聊天接口（备用）"""

    async def event_generator():
        # 实现SSE流式输出
        pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )