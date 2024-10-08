import os

import yaml
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai_like import OpenAILike

from repo_copilot.rag.issue.rag_app.data_loader import DataLoader
from repo_copilot.rag.issue.rag_app.preprocessor import Preprocessor
from retrieval.retriever import Retriever


class RAGApp:
    def __init__(self, config_path):
        with open(config_path) as fh:
            self.config = yaml.load(fh, Loader=yaml.FullLoader)
        token_variable = self.config['LLMCaller']['token_variable']
        self.model = OpenAILike(is_chat_model=True, api_key=os.environ[token_variable],
                                **self.config['LLMCaller']['llm'])
        self.data_loader = DataLoader(self.config)
        self.preprocessor = Preprocessor(self.config['Preprocessor'])
        self.retriever = Retriever(self.config, self.model)

    def add_links(self, links, collection_name):
        self.data_loader.load_html(links, collection_name)

    def add_site(self, url, collection_name):
        self.data_loader.load_site(url, collection_name)

    def add_code_base(self, owner, repo, branch, extensions, folders, collection_name):
        self.data_loader.load_code(owner, repo, branch, extensions, folders, collection_name)

    async def query(self, question, citations=False):
        processed_query = self.preprocessor.preprocess(question)
        agent = ReActAgent.from_tools(self.retriever.query_tools,
                                      llm=self.model,
                                      max_iterations=15,
                                      verbose=True)
        response = await agent.achat(processed_query)
        if citations:
            return response.response, response.source_nodes
        else:
            return response.response, []
