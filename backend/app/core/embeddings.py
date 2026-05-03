from typing import List, Optional
import numpy as np
import httpx
from app.config import settings


class EmbeddingsProvider:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def embed(self, text: str) -> List[float]:
        if self.provider == "openai":
            return await self._embed_openai(text)
        elif self.provider == "local":
            return await self._embed_local(text)
        else:
            return await self._embed_openai(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "openai":
            return await self._embed_batch_openai(texts)
        elif self.provider == "local":
            return await self._embed_batch_local(texts)
        else:
            return await self._embed_batch_openai(texts)

    async def _embed_openai(self, text: str) -> List[float]:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return self._fallback_embedding(text)

        client = AsyncOpenAI(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL or None,
            http_client=httpx.AsyncClient(http2=False)
        )

        response = await client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def _embed_batch_openai(self, texts: List[str]) -> List[List[float]]:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return [self._fallback_embedding(t) for t in texts]

        client = AsyncOpenAI(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL or None,
            http_client=httpx.AsyncClient(http2=False)
        )

        response = await client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def _embed_local(self, text: str) -> List[float]:
        return self._fallback_embedding(text)

    async def _embed_batch_local(self, texts: List[str]) -> List[List[float]]:
        return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> List[float]:
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.dimension).tolist()


class Embeddings:
    def __init__(self):
        self.provider = EmbeddingsProvider()

    async def embed(self, text: str) -> List[float]:
        return await self.provider.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return await self.provider.embed_batch(texts)