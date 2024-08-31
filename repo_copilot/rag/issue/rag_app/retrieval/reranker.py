import numpy as np
from transformers import AutoModelForSequenceClassification


class Reranker:
    def __init__(self, config):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=config['model_config']['pretrained_model_name_or_path'],
            **config['model_config']['config'])
        self.model.to(config['model_config']['device'])
        self.model.eval()
        self.top_k = config['top_k']

    def rerank(self, query, chunks):
        # construct sentence pairs
        sentence_pairs = [[query, doc.node.text] for doc in chunks]
        scores = self.model.compute_score(sentence_pairs, max_length=1024)
        for i in range(len(chunks)):
            chunks[i].score = scores[i]
        return sorted(chunks, key=lambda x: -x.score)[:self.top_k]
