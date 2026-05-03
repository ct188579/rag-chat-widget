from typing import List, Optional, Dict, Any
from langchain.schema import Document
from app.core.embeddings import Embeddings
import re
import uuid


class DocumentProcessor:
    def __init__(self):
        self.embeddings = Embeddings()

    async def process_text(
        self,
        text: str,
        title: str = "未命名文档",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        chunks = self._split_text(text)
        documents = []
        
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **(metadata or {})
                }
            )
            documents.append(doc)
        
        return documents

    async def process_file(
        self,
        file_content: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        title = filename.rsplit(".", 1)[0] if "." in filename else filename
        return await self.process_text(file_content, title, metadata)

    async def process_markdown(
        self,
        content: str,
        title: str = "未命名文档",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        sections = self._split_markdown(content)
        documents = []
        
        for i, section in enumerate(sections):
            if section.get("content", "").strip():
                doc = Document(
                    page_content=section["content"],
                    metadata={
                        "id": str(uuid.uuid4()),
                        "title": f"{title} - {section.get('heading', 'Section ' + str(i))}",
                        "heading": section.get("heading", ""),
                        "chunk_index": i,
                        "type": "markdown",
                        **(metadata or {})
                    }
                )
                documents.append(doc)
        
        return documents

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        if len(text) <= chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            
            if end < text_len:
                last_period = chunk.rfind("。")
                last_newline = chunk.rfind("\n")
                split_pos = max(last_period, last_newline)
                
                if split_pos > chunk_size // 2:
                    chunk = chunk[:split_pos + 1]
                    end = start + split_pos + 1
            
            chunks.append(chunk.strip())
            start = end - overlap if end < text_len else end
        
        return [c for c in chunks if c.strip()]

    def _split_markdown(self, content: str) -> List[Dict[str, str]]:
        sections = []
        current_section = {"heading": "", "content": ""}
        
        lines = content.split("\n")
        for line in lines:
            if re.match(r"^#{1,6}\s+", line):
                if current_section["content"]:
                    sections.append(current_section)
                heading = re.sub(r"^#{1,6}\s+", "", line).strip()
                current_section = {"heading": heading, "content": ""}
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"]:
            sections.append(current_section)
        
        if not sections:
            sections = [{"heading": "全文", "content": content}]
        
        return sections

    async def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        texts = [doc.page_content for doc in documents]
        return await self.embeddings.embed_batch(texts)