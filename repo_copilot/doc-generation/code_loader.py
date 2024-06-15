import hashlib
import os

from embedchain.helpers.json_serializable import JSONSerializable
from langchain.schema import Document


class CodeLoader(JSONSerializable):
    def __init__(self, model, extensions=None, summaries=None):
        if summaries:
            self.summaries = summaries
        else:
            self.summaries = {}
        if not extensions:
            self.extensions = ['.py']
        else:
            self.extensions = extensions
        self.model = model
        self.summarize_prompt = "Please generate a comprehensive summary of a file with code from a repository. "
        "The summary should include detailed descriptions of all classes and functions present in the file. "
        "For each class and function, provide a clear explanation of their purpose, the types of arguments they "
        "accept, and the type of output they return. It is not necessary to include the actual code of the "
        "functions and methods, but the summary should effectively describe their functionality and usage. "
        "Ensure the summary is structured and easy to understand for someone reviewing the file's "
        "contents.\n"
        "Content:\n{}\n"
        "Source path of the file:\n{}"
        self.example_prompt = "You are given with a code example from code repository. Your tasks are:\n"
        "1) Try to understand the logic of this example. Which task is solved or which feature is described."
        "2) Divide code on logical blocks and understand logic of each block. "
        "3) Generate documentation page devoted to this example. It should consists from overall summary of example, "
        "step-by-step guide with code snippets (you should not loose any code). "
        "Ensure that user who will see this page will easily understand this example and will be able copy paste "
        "example and use it with it's own purposes."
        "Content of the example:\n"
        "{}\n\n"
        "Ensure you did not loose any codeline! Return only .rst formatted documentation page"

    def summary(self, document):
        path = document.metadata['source']
        content = document.page_content
        invoke_res = self.model.invoke(self.example_prompt.format(content, path)).content
        return invoke_res

    def generate_docs(self, contexts):
        context = '\n------------\n'.join(contexts)
        invoke_res = self.model.invoke(self.doc_prompt.format(context)).content
        return invoke_res

    def load_python_files(self, directory_path):
        """
        Recursively loads the content of all .py files in the specified directory and its subdirectories into LangChain documents.

        Args:
        directory_path (str): The path to the directory to start the search from.

        Returns:
        list: A list of Document objects containing the content of each .py file.
        """

        def traverse_directory(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_valid_file = any(item.endswith(e) for e in self.extensions)
                if os.path.isdir(item_path):
                    traverse_directory(item_path)
                elif is_valid_file:
                    with open(item_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        metadata = {"source": item_path}
                        if content:
                            self.summaries[item_path] = self.summary(Document(page_content=content, metadata=metadata))

        traverse_directory(directory_path)

    def load_data(self, url):
        """
        Create rst doc files from folders
        """
        content = self.summaries[url]
        doc_id = hashlib.sha256(content.encode()).hexdigest()
        return {
            "doc_id": doc_id,
            "data": [
                {
                    "content": content,
                    "meta_data": {'url': url},
                }
            ],
        }
