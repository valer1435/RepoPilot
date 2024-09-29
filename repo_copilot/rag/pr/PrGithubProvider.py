from typing import Optional

from pr_agent.git_providers import GithubProvider
from pr_agent.git_providers.git_provider import IncrementalPR


class PrGithubProvider(GithubProvider):
    def __init__(self, pr_url: Optional[str] = None, incremental=IncrementalPR(False), config_path: Optional[str] = ""):
        super().__init__(pr_url, incremental=incremental)
        self.config_path = config_path

    def get_repo_settings(self):
        try:
            with open(self.config_path, mode='rb') as f:
                return f.read()
        except Exception:
            return ""
