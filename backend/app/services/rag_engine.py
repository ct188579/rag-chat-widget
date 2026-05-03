from typing import List, Optional, AsyncGenerator
from dataclasses import dataclass

from app.core.vector_store import VectorStore
from app.core.llm import LLMManager
from app.models.schemas import RAGSource


@dataclass
class RAGContext:
    sources: List[RAGSource]
    formatted_context: str


class RAGEngine:
    def __init__(self, vector_store: VectorStore, llm_manager: LLMManager):
        self.vector_store = vector_store
        self.llm = llm_manager

    async def retrieve(
            self,
            query: str,
            top_k: int = 5,
            namespace: Optional[str] = None,
            score_threshold: float = 0.7
    ) -> List[RAGSource]:
        """检索相关文档片段"""
        # 1. 向量化查询
        query_embedding = await self.llm.embed(query)

        # 2. 向量相似度搜索
        results = await self.vector_store.similarity_search(
            embedding=query_embedding,
            top_k=top_k,
            namespace=namespace,
            score_threshold=score_threshold
        )

        # 3. 组装结果
        sources = []
        for doc, score in results:
            sources.append(RAGSource(
                id=doc.metadata.get("id", ""),
                title=doc.metadata.get("title", "未知文档"),
                content=doc.page_content[:500],  # 截取前500字符
                score=score,
                url=doc.metadata.get("url"),
                page=doc.metadata.get("page")
            ))

        return sources

    def format_context(self, sources: List[RAGSource]) -> str:
        """将检索结果格式化为上下文"""
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"[文档 {i}] {source.title}\n"
                f"内容：{source.content}\n"
                f"来源：{source.url or '内部文档'}\n"
            )
        return "\n".join(context_parts)

    def build_prompt(self, query: str, context: Optional[str] = None) -> str:
        """构建带上下文的提示词"""
        if context:
            return f"""基于以下参考文档回答问题。如果文档中没有相关信息，请明确说明。

参考文档：
{context}

用户问题：{query}

请用中文回答，并在回答中引用相关文档编号（如[文档1]）。"""
        return query

    async def astream(
            self,
            query: str,
            context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回答"""
        prompt = self.build_prompt(query, context)

        async for chunk in self.llm.astream(prompt):
            yield chunk

    async def ainvoke(self, query: str, context: Optional[str] = None) -> str:
        """非流式生成回答"""
        prompt = self.build_prompt(query, context)
        return await self.llm.ainvoke(prompt)