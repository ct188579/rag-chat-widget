from typing import List, Tuple, Optional
import chromadb
import numpy as np
from langchain_core.documents.base import Document


class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        # 使用ChromaDB（开发环境）或Milvus（生产环境）
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def add_documents(
            self,
            documents: List[Document],
            embeddings: List[List[float]],
            namespace: Optional[str] = None
    ):
        """添加文档到向量库"""
        ids = [f"{namespace}_{i}" if namespace else str(i)
               for i in range(len(documents))]

        metadatas = []
        for doc in documents:
            meta = doc.metadata.copy()
            if namespace:
                meta["namespace"] = namespace
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[doc.page_content for doc in documents],
            metadatas=metadatas
        )

    async def similarity_search(
            self,
            embedding: List[float],
            top_k: int = 5,
            namespace: Optional[str] = None,
            score_threshold: float = 0.7
    ) -> List[Tuple[Document, float]]:
        """相似度搜索"""
        where = {"namespace": namespace} if namespace else None

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        documents = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            # Chroma返回的是距离，转换为相似度分数
            score = 1 - (distance / 2)  # cosine距离转相似度

            if score >= score_threshold:
                doc = Document(
                    page_content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i]
                )
                documents.append((doc, score))

        return documents

    async def delete_namespace(self, namespace: str):
        """删除命名空间下的所有文档"""
        self.collection.delete(where={"namespace": namespace})

    async def close(self):
        pass