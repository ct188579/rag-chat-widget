from typing import List, Optional, AsyncGenerator
import json
from app.config import settings


class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

    async def chat(
        self,
        messages: List[dict],
        stream: bool = False
    ) -> tuple[str, Optional[AsyncGenerator[str, None]]]:
        if self.provider == "openai":
            return await self._chat_openai(messages, stream)
        elif self.provider == "anthropic":
            return await self._chat_anthropic(messages, stream)
        else:
            return await self._chat_openai(messages, stream)

    async def _chat_openai(
        self,
        messages: List[dict],
        stream: bool = False
    ) -> tuple[str, Optional[AsyncGenerator[str, None]]]:
        if not settings.LLM_API_KEY:
            return self._fallback_response(messages), None

        try:
            from openai import AsyncOpenAI
        except ImportError:
            return self._fallback_response(messages), None

        client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL or None
        )

        if stream:
            async def generator():
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return "", generator()
        else:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content or "", None

    async def _chat_anthropic(
        self,
        messages: List[dict],
        stream: bool = False
    ) -> tuple[str, Optional[AsyncGenerator[str, None]]]:
        return self._fallback_response(messages), None

    def _fallback_response(self, messages: List[dict]) -> str:
        last_message = messages[-1].get("content", "") if messages else ""
        return f"抱歉，我暂时无法处理您的请求。\n\n您说: {last_message}"


class LLMManager:
    def __init__(self):
        self.provider = LLMProvider()
        self.default_system_prompt = "你是一个友好的AI助手，请用中文回答用户的问题。"

    async def chat(
        self,
        prompt: str,
        history: Optional[List[dict]] = None,
        stream: bool = False
    ) -> tuple[str, Optional[AsyncGenerator[str, None]]]:
        messages = self._build_messages(prompt, history)
        return await self.provider.chat(messages, stream)

    async def ainvoke(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        result, _ = await self.provider.chat(messages, stream=False)
        return result

    async def astream(self, prompt: str) -> AsyncGenerator[str, None]:
        messages = [{"role": "user", "content": prompt}]
        _, generator = await self.provider.chat(messages, stream=True)
        if generator:
            async for chunk in generator:
                yield chunk
        else:
            result, _ = await self.provider.chat(messages, stream=False)
            for char in result:
                yield char

    def _build_messages(self, prompt: str, history: Optional[List[dict]] = None) -> List[dict]:
        messages = [{"role": "system", "content": self.default_system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return messages

    async def embed(self, text: str) -> List[float]:
        from app.core.embeddings import Embeddings
        embeddings = Embeddings()
        return await embeddings.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        from app.core.embeddings import Embeddings
        embeddings = Embeddings()
        return await embeddings.embed_batch(texts)