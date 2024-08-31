from typing import Optional

from pr_agent.git_providers import GithubProvider
from pr_agent.git_providers.git_provider import IncrementalPR


class PrGithubProvider(GithubProvider):
    def __init__(self, pr_url: Optional[str] = None, incremental=IncrementalPR(False), config_path: Optional[str] = ""):
        super().__init__(pr_url, incremental=IncrementalPR(False))
        self.config_path = config_path

    def get_repo_settings(self):
        try:

            # more logical to take 'pr_agent.toml' from the default branch
            contents = self.repo_obj.get_contents(self.config_path).decoded_content
            return contents
        except Exception:
            return ""
