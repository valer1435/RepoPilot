import os

from llama_index.llms.openai_like import OpenAILike


class LLMCaller:
    def __init__(self, config):
        token_variable = config['token_variable']
        self.model = OpenAILike(is_chat_model=True, api_key=os.environ[token_variable], **config['llm'])
        self.task_prompt = config['task_prompt']

    def call_llm(self, query, chunks):
        return self.model.complete(
            self.task_prompt.format(context='\n'.join([chunk.text for chunk in chunks]), query=query)).text, chunks
