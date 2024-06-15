from embedchain import App


class RAGApp:
    def __init__(self, model_name, repo_description):
        self.app = App.from_config(config={
            "llm": {
                "provider": "openai",
                "config": {
                    "number_documents": 5,
                    "model": model_name,
                    "temperature": 0.0,
                    "max_tokens": 2048,
                    "top_p": 1,
                    "stream": False,
                    "prompt": f"You are an AI programming assistant, and you only answer questions "
                              f" related to {repo_description}.\n"
                              "Instruction:\n"
                              "Use only provided information for answer:\n"
                              "$context\n"
                              "Question:\n"
                              "$query\n"
                              "If provided information does not contains information for answer - "
                              "just say that you don't know the answer "
                              "and ask user to look futher into documentation or source files."
                              "If question is about giving an example, try to give step-to-step guide."
                              "Answer: "}
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "WhereIsAI/UAE-Large-V1"
                }
            },
            'chunker': {
                'chunk_size': 5000
            }

        })

    def add(self, data, data_type='web_page'):
        self.app.add(data, data_type=data_type)

    def query(self, question, citations=False):
        return self.app.query(question, citations=citations)

    def reset(self):
        self.app.reset()
