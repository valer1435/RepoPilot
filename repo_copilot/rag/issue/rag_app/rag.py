import os

import yaml
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai_like import OpenAILike

from repo_copilot.rag.issue.rag_app.data_loader import DataLoader
from repo_copilot.rag.issue.rag_app.retrieval.retriever import Retriever


class RAGApp:
    def __init__(self, config_path):
        with open(config_path) as fh:
            self.config = yaml.load(fh, Loader=yaml.FullLoader)
        token_variable = self.config['LLMCaller']['token_variable']
        self.model = OpenAILike(is_chat_model=True, api_key=os.environ[token_variable],
                                **self.config['LLMCaller']['llm'])
        self.data_loader = DataLoader(self.config)
        self.retriever = Retriever(self.config, self.model)
        if self.data_loader.enabled:
            print("Start loading data")
            self.add_site()
            self.add_code_base()

    def add_links(self, links, collection_name):
        self.data_loader.load_html(links, collection_name)

    def add_site(self):
        self.data_loader.load_site()

    def add_code_base(self):
        self.data_loader.load_code()

    async def aquery(self, question, citations=False):
        try:
            agent = ReActAgent.from_tools(self.retriever.query_tools,
                                          context='You helpful AI assistant developed to help users operate with '
                                                  'framework. Use set of tools to provide comprehensive answer.  '
                                                  'Support final answers by examples if any is provided by tools. '
                                                  'Please use both Documentation first to '
                                                  'answer the user question. If you still can not answer after '
                                                  'using Documentation tool, use codeBase tool.'
                                                  'If CodeBase also does not have useful information -'
                                                  ' just write that you are unable to answer. At each step '
                                                  'ensure that you used both tools!',
                                          llm=self.model,
                                          max_iterations=5,
                                          verbose=True)
            response = await agent.achat(question)
        except ValueError as e:
            return "Sorry, I'm unable answer your question with information I have.", []
        if citations:
            return response.response, response.source_nodes
        else:
            return response.response, []

    def query(self, question, citations=False):
        try:
            agent = ReActAgent.from_tools(self.retriever.query_tools,
                                          context='You helpful AI assistant developed to help users operate with '
                                                  'framework. Use set of tools to provide comprehensive answer.  '
                                                  'Support final answers by examples if any is provided by tools. '
                                                  'Please use both Documentation first to '
                                                  'answer the user question. If you still can not answer after '
                                                  'using Documentation tool, use codeBase tool.'
                                                  'If CodeBase also does not have useful information -'
                                                  ' just write that you are unable to answer. At each step ensure that you '
                                                  'used both tools!',
                                          llm=self.model,
                                          max_iterations=7,
                                          verbose=True)
            response = agent.chat(question)
        except ValueError as e:
            print(e)
            return "Sorry, I'm unable answer your question with information I have.", []
        if citations:
            return response.response, response.source_nodes
        else:
            return response.response, []
