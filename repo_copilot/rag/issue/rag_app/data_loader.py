
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import  SentenceSplitter
from llama_index.readers.web import BeautifulSoupWebReader

from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import AsyncQdrantClient, QdrantClient

from embedding_factory import EmbeddingModelFactory


class DataLoader:
    def __init__(self, config):
        self.index = None
        client = QdrantClient(host="localhost", port=6333)
        aclient = AsyncQdrantClient(host="localhost", port=6333)

        # create our vector store with hybrid indexing enabled
        # batch_size controls how many nodes are encoded with sparse vectors at once
        self.vector_store = QdrantVectorStore(
            config['VectorStore']['name'],
            client=client,
            aclient=aclient,
            enable_hybrid=True,
            batch_size=20,
        )

        self.embedding = EmbeddingModelFactory.get_embedding_model(config['Embedding']['provider'],
                                                                   **config['Embedding']['config'])

        self.pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=1000, chunk_overlap=500),
                self.embedding
            ],
            vector_store=self.vector_store
        )

    def load_html(self, links):
        loader = BeautifulSoupWebReader()
        documents = loader.load_data(urls=links)
        print('Loading documents')
        # Ingest directly into a vector db
        self.pipeline.run(documents=documents)
