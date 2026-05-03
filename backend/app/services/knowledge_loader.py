import os
import asyncio
from pathlib import Path
from app.core.vector_store import VectorStore
from app.services.document_processor import DocumentProcessor


SUPPORTED_EXTENSIONS = ['.txt', '.md', '.markdown']


class KnowledgeLoader:
    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "knowledge"
        )

    async def load_all(self, vector_store: VectorStore):
        if not os.path.exists(self.knowledge_dir):
            return
        
        processor = DocumentProcessor()
        
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(list(Path(self.knowledge_dir).rglob(f"*{ext}")))
        
        for file_path in files:
            try:
                text = file_path.read_text(encoding="utf-8")
                filename = file_path.stem
                
                if file_path.suffix in ['.md', '.markdown']:
                    documents = await processor.process_markdown(
                        content=text,
                        title=filename,
                        metadata={"source": str(file_path), "type": "knowledge"}
                    )
                else:
                    documents = await processor.process_text(
                        text=text,
                        title=filename,
                        metadata={"source": str(file_path), "type": "knowledge"}
                    )
                
                embeddings = await processor.embed_documents(documents)
                
                await vector_store.add_documents(
                    documents=documents,
                    embeddings=embeddings,
                    namespace="knowledge"
                )
                
                print(f"Loaded knowledge: {filename} ({len(documents)} chunks)")
                
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")


async def init_knowledge(vector_store: VectorStore):
    loader = KnowledgeLoader()
    await loader.load_all(vector_store)