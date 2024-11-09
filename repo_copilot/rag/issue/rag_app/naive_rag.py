import os

import yaml
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai_like import OpenAILike

from repo_copilot.rag.issue.rag_app.data_loader import DataLoader
from repo_copilot.rag.issue.rag_app.retrieval.retriever import Retriever


class NaiveRAGApp:
    def __init__(self, config_path):
        with open(config_path) as fh:
            self.config = yaml.load(fh, Loader=yaml.FullLoader)
        token_variable = self.config['LLMCaller']['token_variable']
        self.model = OpenAILike(is_chat_model=True, api_key=os.environ[token_variable],
                                **self.config['LLMCaller']['llm'])
        self.prompt = "Answer of question regarding on provided context:\n{context}\nQuery:\n{query}"
        self.data_loader = DataLoader(self.config)
        self.retriever = Retriever(self.config, self.model)
        if self.data_loader.enabled:
            print("Start loading data")
            self.add_site()

    def add_links(self, links, collection_name):
        self.data_loader.load_html(links, collection_name)

    def add_site(self):
        self.data_loader.load_site()

    def add_code_base(self):
        self.data_loader.load_code()

    def query(self, question, citations=False):
        try:
            chunks = self.retriever.retrieve(question)
            string_prompt = self.prompt.format(context='\n'.join([i.text for i in chunks]), query=question)
            response = self.model.complete(string_prompt)
        except ValueError as e:
            print(e)
            return "Sorry, I'm unable answer your question with information I have.", []
        if citations:
            return response.text, response.source_nodes
        else:
            return response.text, []
