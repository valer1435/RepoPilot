from functools import partial

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.algo.ai_handlers.litellm_ai_handler import LiteLLMAIHandler
from pr_agent.git_providers.utils import apply_repo_settings
from pr_agent.log import get_logger

from repo_copilot.rag.issue.issue_qa import IssueQuestions
from repo_copilot.rag.issue.rag_app.rag import RAGApp

command2class = {
    "any": IssueQuestions
}

commands = list(command2class.keys())


class IssueAgent:
    def __init__(self, rag_engine: RAGApp, ai_handler: partial[BaseAiHandler,] = LiteLLMAIHandler):
        self.ai_handler = ai_handler  # will be initialized in run_action
        self.forbidden_cli_args = ['enable_auto_approval']
        self.rag_engine = rag_engine

    async def handle_request(self, issue_url, notify=None) -> bool:
        # First, apply repo specific settings if exists
        apply_repo_settings(issue_url)
        if notify:
            notify()
        try:
            await IssueQuestions(issue_url, ai_handler=self.ai_handler, rag_engine=self.rag_engine).run()
        except Exception as e:
            get_logger().error(f"Error handling issue request: {e}")
            return False
        return True
