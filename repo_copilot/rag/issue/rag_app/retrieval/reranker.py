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
        min_score = min(scores)
        max_score = max(scores)
        normalized_scores = [(score - min_score) / (max_score - min_score) for score in scores]
        for i in range(len(chunks)):
            chunks[i].score = normalized_scores[i]
        return sorted(chunks, key=lambda x: -x.score)[:self.top_k]
