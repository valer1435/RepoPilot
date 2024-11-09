from llama_index.core import VectorStoreIndex, SelectorPromptTemplate, PromptTemplate
from llama_index.core.prompts import PromptType
from llama_index.core.prompts.default_prompt_selectors import default_text_qa_conditionals
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient

from repo_copilot.rag.issue.rag_app.retrieval.embedding.embedding_factory import EmbeddingModelFactory

RETRIEVER_TEXT_QA_PROMPT_TMPL = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "give the detailed answer on the user query."
    "Query: {query_str}\n"
    "Answer: "
)
RETRIEVER_TEXT_QA_PROMPT = PromptTemplate(
    RETRIEVER_TEXT_QA_PROMPT_TMPL, prompt_type=PromptType.QUESTION_ANSWER
)

RETRIEVER_TEXT_QA_PROMPT_SEL = SelectorPromptTemplate(
    default_template=RETRIEVER_TEXT_QA_PROMPT,
    conditionals=default_text_qa_conditionals,
)

class Retriever:
    def __init__(self, config, model):
        self.top_k = config['Retriever']['top_k']
        self.sparse_top_k = config['Retriever']['sparse_top_k']
        self.embedding = EmbeddingModelFactory.get_embedding_model(config['Embedding']['provider'],
                                                                   **config['Embedding']['config'])

        self.host = config['VectorStore']['host']
        self.port = config['VectorStore']['port']

        client = QdrantClient(host=self.host, port=self.port)
        aclient = AsyncQdrantClient(host=self.host, port=self.port)

        self.query_tools = []
        for store in config['VectorStore']['collections']:
            vs = (QdrantVectorStore(
                store['name'],
                client=client,
                aclient=aclient,
                enable_hybrid=True,
                batch_size=20))
            query_engine = VectorStoreIndex.from_vector_store(
                vector_store=vs,
                embed_model=self.embedding
            ).as_query_engine(similarity_top_k=self.top_k,
                              sparse_top_k=self.sparse_top_k,
                              text_qa_template=RETRIEVER_TEXT_QA_PROMPT_SEL,
                              llm=model,
                              embed_model=self.embedding)
            self.query_tools.append(QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=store['agent_name'],
                    description=(
                        store["description"]
                    ),
                )
            ))

    def retrieve(self, query):
        chunks = self.query_tools[0].query_engine.retrieve(query)
        return chunks
