from abc import ABC, abstractmethod
from typing import Any

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding


class EmbeddingModel(ABC):
    @abstractmethod
    def embed(self, text: str) -> Any:
        pass


class EmbeddingModelFactory:
    @staticmethod
    def get_embedding_model(model_type: str, **config):
        if model_type == "openai":
            return OpenAIEmbedding(**config)
        elif model_type == "huggingface":
            return HuggingFaceEmbedding(**config)
        else:
            raise ValueError("Invalid model type")
