from llama_index.core import VectorStoreIndex
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient

from embedding_factory import EmbeddingModelFactory


class Retriever:
    def __init__(self, config, model):
        self.top_k = config['Retriever']['top_k']
        self.sparse_top_k = config['Retriever']['sparse_top_k']
        self.embedding = EmbeddingModelFactory.get_embedding_model(config['Embedding']['provider'],
                                                                   **config['Embedding']['config'])

        client = QdrantClient(host="localhost", port=6333)
        aclient = AsyncQdrantClient(host="localhost", port=6333)
        self.vector_store = QdrantVectorStore(
            config['VectorStore']['name'],
            client=client,
            aclient=aclient,
            enable_hybrid=True,
            batch_size=20,
        )
        self.query_engine = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embedding
        ).as_query_engine(similarity_top_k=self.top_k,
                          sparse_top_k=self.sparse_top_k,
                          llm=model,
                          embed_model=self.embedding)

        self.query_tools = [
            QueryEngineTool(
                query_engine=self.query_engine,
                metadata=ToolMetadata(
                    name="Documentation",
                    description=(
                        "Used to provide general information, examples about framework"
                    ),
                )
            )
        ]