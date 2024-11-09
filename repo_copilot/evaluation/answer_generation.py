import json
from dataclasses import dataclass
from typing import List

from tqdm import tqdm

prompt = ("You helpful AI assistant developed to help users operate with framework."
          "Please make your answer detailed, provide code examples if you can provide it."
          "  Query:\n{q}")


@dataclass
class DatasetEntry:
    query: str
    reference_answer: str
    t: str
    model_answer: str = None
    model_contexts: List[str] = None


class EvaluationManager:
    def __init__(self, rag_pipeline):
        self.rag_pipeline = rag_pipeline

    def evaluate(self, dataset_path):
        print(f'Loading dataset')
        dataset = self._load_dataset(dataset_path)
        print(f'Evaluation is started, len={len(dataset)}')
        for d in tqdm(dataset):
            d.model_answer, d.model_contexts = self._evaluate(d)

        return dataset

    def _load_dataset(self, dataset_path):
        dataset = []
        with open(dataset_path) as f:
            loaded = json.load(f)
            for sample in loaded:
                dataset.append(DatasetEntry(query=sample['q'],
                                            reference_answer=sample['a'],
                                            t=sample['type']))
        return dataset

    def _evaluate(self, entry):
        return self.rag_pipeline.query(prompt.format(q=entry.query))

    def save(self, dataset, path=None):
        json_like_res = []
        for sample in dataset:
            json_like_res.append({'q': sample.query,
                                  'r_a': sample.reference_answer,
                                  'm_a': sample.model_answer,
                                  'm_c': sample.model_contexts,
                                  't': sample.t})
        if path:
            json.dump(json_like_res, open(path, 'w+'))
        return json_like_res
