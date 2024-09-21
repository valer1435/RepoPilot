from functools import partial

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.algo.ai_handlers.litellm_ai_handler import LiteLLMAIHandler
from pr_agent.config_loader import get_settings
from pr_agent.git_providers.git_provider import get_main_pr_language
from pr_agent.log import get_logger

from repo_copilot.rag.issue.github_issue_provider import IssueGithubProvider
from repo_copilot.rag.issue.rag_app.rag import RAGApp


class IssueQuestions:
    def __init__(self, issue_url: str, rag_engine: RAGApp, ai_handler: partial[BaseAiHandler,] = LiteLLMAIHandler):
        self.issue_url = issue_url
        self.git_provider = IssueGithubProvider(issue_url)  # Only github is available
        self.main_pr_language = get_main_pr_language(
            self.git_provider.get_languages(), None)
        self.ai_handler = ai_handler()
        self.ai_handler.main_pr_language = self.main_pr_language
        self.rag_engine = rag_engine

    def parse_args(self, args):
        if args and len(args) > 0:
            question_str = " ".join(args)
        else:
            question_str = ""
        return question_str

    async def run(self):
        get_logger().info(f'Answering a Issue question {self.issue_url} ')
        relevant_configs = {'pr_questions': dict(get_settings().pr_questions),
                            'config': dict(get_settings().config)}
        get_logger().debug("Relevant configs", artifacts=relevant_configs)

        response, citations = await self.rag_engine.query(self.git_provider.get_issue_as_prompt(), citations=True)
        if get_settings().config.publish_output:
            self.git_provider.publish_comment(response, citations)


