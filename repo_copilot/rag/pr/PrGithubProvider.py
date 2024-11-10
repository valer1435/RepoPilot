from typing import Optional

from pr_agent.git_providers import GithubProvider


class PrGithubProvider(GithubProvider):
    def __init__(self, pr_url: Optional[str] = None, config_path: Optional[str] = ""):
        super().__init__(pr_url)
        self.config_path = config_path

    def get_repo_settings(self):
        try:
            with open(self.config_path, mode='rb') as f:
                return f.read()
        except Exception:
            return ""
