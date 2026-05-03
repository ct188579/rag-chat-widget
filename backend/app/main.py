from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime

from app.api import chat, rag
from app.core.vector_store import VectorStore
from app.core.llm import LLMManager
from app.models.schemas import RAGSource


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.vector_store = VectorStore()
    app.state.llm_manager = LLMManager()
    
    from app.services.knowledge_loader import init_knowledge
    await init_knowledge(app.state.vector_store)
    
    yield
    await app.state.vector_store.close()


app = FastAPI(
    title="AI Chat Widget API",
    description="Backend API for AI Chat Widget with RAG support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_histories: Dict[str, List[dict]] = {}

    def connect(self, websocket: WebSocket, session_id: str):
        self.active_connections[session_id] = websocket
        self.session_histories[session_id] = []

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)
        self.session_histories.pop(session_id, None)

    def add_message(self, session_id: str, role: str, content: str):
        if session_id in self.session_histories:
            self.session_histories[session_id].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_history(self, session_id: str) -> List[dict]:
        return self.session_histories.get(session_id, [])


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    session_id = None
    try:
        session_id = await init_session(websocket)
        manager.connect(websocket, session_id)
        
        await send_message(websocket, {
            "type": "connected",
            "session_id": session_id,
            "message": "连接成功"
        })

        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=300.0
                )
                await handle_message(websocket, session_id, data)
            except asyncio.TimeoutError:
                await send_message(websocket, {
                    "type": "ping",
                    "message": "heartbeat"
                })
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if session_id:
            manager.disconnect(session_id)


async def init_session(websocket: WebSocket) -> Optional[str]:
    await websocket.accept()
    try:
        init_data = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=10.0
        )
        return init_data.get("session_id") or f"session_{datetime.utcnow().timestamp()}"
    except Exception:
        return f"session_{datetime.utcnow().timestamp()}"


async def handle_message(websocket: WebSocket, session_id: str, data: dict):
    msg_type = data.get("type", "chat")
    
    if msg_type == "pong":
        return
    
    if msg_type == "chat":
        await handle_chat(websocket, session_id, data)
    elif msg_type == "clear_history":
        manager.session_histories[session_id] = []
        await send_message(websocket, {
            "type": "history_cleared",
            "message": "历史记录已清空"
        })
    elif msg_type == "get_history":
        history = manager.get_history(session_id)
        await send_message(websocket, {
            "type": "history",
            "history": history
        })
    else:
        await send_message(websocket, {
            "type": "error",
            "message": f"未知消息类型: {msg_type}"
        })


async def handle_chat(websocket: WebSocket, session_id: str, data: dict):
    from app.services.rag_engine import RAGEngine
    
    message = data.get("message", "").strip()
    if not message:
        await send_message(websocket, {
            "type": "error",
            "message": "消息不能为空"
        })
        return
    
    enable_rag = data.get("enable_rag", True)
    top_k = data.get("top_k", 5)
    stream = data.get("stream", True)
    
    manager.add_message(session_id, "user", message)
    
    rag_engine = RAGEngine(
        vector_store=app.state.vector_store,
        llm_manager=app.state.llm_manager
    )
    
    sources: List[RAGSource] = []
    context = None
    
    if enable_rag:
        try:
            sources = await rag_engine.retrieve(message, top_k=top_k)
            if sources:
                context = rag_engine.format_context(sources)
                await send_message(websocket, {
                    "type": "sources",
                    "sources": [s.model_dump() for s in sources],
                    "count": len(sources)
                })
        except Exception as e:
            print(f"RAG检索失败: {e}")
    
    full_response = ""
    
    if stream:
        try:
            async for chunk in rag_engine.astream(message, context):
                full_response += chunk
                await send_message(websocket, {
                    "type": "chunk",
                    "content": chunk
                })
        except Exception as e:
            await send_message(websocket, {
                "type": "error",
                "message": f"生成回复失败: {str(e)}"
            })
            return
    else:
        try:
            full_response = await rag_engine.ainvoke(message, context)
            await send_message(websocket, {
                "type": "response",
                "content": full_response
            })
        except Exception as e:
            await send_message(websocket, {
                "type": "error",
                "message": f"生成回复失败: {str(e)}"
            })
            return
    
    if full_response:
        manager.add_message(session_id, "assistant", full_response)
    
    await send_message(websocket, {
        "type": "done",
        "message": "回复完成"
    })


async def send_message(websocket: WebSocket, data: dict):
    try:
        await websocket.send_json(data)
    except Exception as e:
        print(f"发送消息失败: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)