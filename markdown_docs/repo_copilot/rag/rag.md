## ClassDef RAGApp
Doc is waiting to be generated...
### FunctionDef __init__(self, model_name, repo_description)
 **__init__**: The function of __init__ is to initialize the RAGApp instance with specific configurations for the language model, embedder, and chunker.

**parameters**: The parameters of this Function.
· model_name: A string specifying the name of the language model to be used.
· repo_description: A string describing the repository, which is used to customize the prompt for the language model.

**Code Description**: The description of this Function.
The `__init__` method initializes an instance of the `RAGApp` class by setting up the application with a configuration dictionary. This configuration includes settings for the language model (LLM), embedder, and chunker.

1. **Language Model (LLM) Configuration**:
   - **provider**: Set to "openai", indicating that the OpenAI API will be used.
   - **config**: A dictionary containing detailed configurations for the language model:
     - **number_documents**: Set to 5, specifying the number of documents to be processed.
     - **model**: Set to the value of `model_name`, which is passed as a parameter to the `__init__` method.
     - **temperature**: Set to 0.0, indicating a deterministic output from the model.
     - **max_tokens**: Set to 2048, limiting the maximum number of tokens in the output.
     - **top_p**: Set to 1, indicating that nucleus sampling is not used.
     - **stream**: Set to False, indicating that the response will not be streamed.
     - **prompt**: A formatted string that includes the `repo_description` and provides instructions for the AI assistant. This prompt guides the assistant to answer questions related to the repository, use only provided information, and handle unknown answers or example requests appropriately.

2. **Embedder Configuration**:
   - **provider**: Set to "huggingface", indicating that the Hugging Face model will be used for embedding.
   - **config**: A dictionary containing the model configuration:
     - **model**: Set to "WhereIsAI/UAE-Large-V1", specifying the embedding model to be used.

3. **Chunker Configuration**:
   - **chunk_size**: Set to 5000, specifying the size of the chunks for the chunker.

**Note**: Points to note about the use of the code
- Ensure that the `model_name` and `repo_description` parameters are correctly provided to match the intended use case.
- The prompt configuration is crucial as it defines the behavior of the AI assistant, especially in handling unknown information and providing examples.
***
### FunctionDef add(self, data, data_type)
 **add**: The function of add is to add data to the RAGApp.

**parameters**: The parameters of this Function.
· data: The data to be added to the RAGApp. This can be any type of data that the RAGApp supports.
· data_type: The type of data being added, with a default value of 'web_page'. This parameter specifies the type of data being added to help the RAGApp process it correctly.

**Code Description**: The `add` function is a method of the `RAGApp` class. It takes two parameters: `data` and `data_type`. The `data` parameter is the actual data that needs to be added to the RAGApp, and `data_type` is an optional parameter that specifies the type of data being added, defaulting to 'web_page' if not provided.

Inside the function, the `self.app.add` method is called with the same parameters. This indicates that the `add` method of the `RAGApp` class is a wrapper for the `add` method of another object, presumably an instance of a class that handles the actual addition of data. This design allows for abstraction and separation of concerns, where the `RAGApp` class can focus on higher-level operations, delegating the specific task of adding data to another class.

The function is called in the `fedot_example.py` script, although the specific context and usage details are not provided in the given information. This suggests that the `add` function is part of a larger system where data from various sources (like web pages) are integrated into the RAGApp for further processing or analysis.

**Note**: When using the `add` function, ensure that the `data` parameter is correctly formatted and that the `data_type` parameter accurately reflects the type of data being added. This is crucial for the RAGApp to process the data correctly. Additionally, since the function delegates the actual addition of data to another object, it's important to ensure that this underlying object is properly configured and capable of handling the data being added.
***
### FunctionDef query(self, question, citations)
Doc is waiting to be generated...
***
### FunctionDef reset(self)
Doc is waiting to be generated...
***
