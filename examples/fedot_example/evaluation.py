from dotenv import load_dotenv

from naive_rag import NaiveRAGApp
from repo_copilot.evaluation.answer_generation import EvaluationManager
from repo_copilot.rag.issue.rag_app.rag import RAGApp

load_dotenv()
rag_pipeline = RAGApp('config.yml')
naive_rag = NaiveRAGApp('config.yml')

evaluator = EvaluationManager(rag_pipeline)

res = evaluator.evaluate('../../data/labeled_questions.json')

evaluator.save(res, 'res1.json')
