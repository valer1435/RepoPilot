from datetime import datetime
from typing import Optional, Tuple, List
from urllib.parse import urlparse

from github import AppAuthentication, Auth, Github
from pr_agent.config_loader import get_settings
from pr_agent.log import get_logger
from starlette_context import context


class IssueGithubProvider:
    def __init__(self, issue_url: Optional[str] = None):
        self.repo_obj = None
        try:
            self.installation_id = context.get("installation_id", None)
        except Exception:
            self.installation_id = None
        self.base_url = get_settings().get("GITHUB.BASE_URL", "https://api.github.com").rstrip("/")
        self.base_url_html = self.base_url.split("api/")[0].rstrip(
            "/") if "api/" in self.base_url else "https://github.com"
        self.github_client = self._get_github_client()
        self.repo = None

        self.github_user_id = None
        if issue_url and 'issue' in issue_url:
            self.set_issue(issue_url)

    def get_issue_url(self) -> str:
        return self.issue.html_url

    def set_issue(self, issue_url: str):
        self.repo, self.issue_num = self._parse_issue_url(issue_url)
        self.issue = self._get_issue()
        self.issue_comments = list(self.issue.get_comments())

    def publish_comment(self, content: str, citations: Optional[List] = None):
        if citations:
            citation_message = ["\n\n**Please follow links below:**"]
            for i, node in enumerate(citations, start=1):
                if i > 5:
                    break
                if 'URL' in node.metadata:
                    alias = node.text.strip('\n').split('\n', 1)[0]
                    citation_message.append(f"{i}. [{alias}]({node.metadata['URL']})")
                if 'url' in node.metadata:
                    citation_message.append(
                        f"{i}. [{node.metadata['file_name']}]({node.metadata['url']})")
            citation_message = '\n'.join(citation_message)
            content = content + citation_message
        response = self.issue.create_comment(content)
        return response

    def remove_initial_comment(self):
        try:
            for comment in getattr(self.pr, 'comments_list', []):
                if comment.is_temporary:
                    self.remove_comment(comment)
        except Exception as e:
            get_logger().exception(f"Failed to remove initial comment, error: {e}")

    def remove_comment(self, comment):
        try:
            comment.delete()
        except Exception as e:
            get_logger().exception(f"Failed to remove comment, error: {e}")

    def get_languages(self):
        languages = self._get_repo().get_languages()
        return languages

    def get_user_id(self):
        if not self.github_user_id:
            try:
                self.github_user_id = self.github_client.get_user().raw_data['login']
            except Exception as e:
                self.github_user_id = ""
                # logging.exception(f"Failed to get user id, error: {e}")
        return self.github_user_id

    def get_notifications(self, since: datetime):
        deployment_type = get_settings().get("GITHUB.DEPLOYMENT_TYPE", "user")

        if deployment_type != 'user':
            raise ValueError("Deployment mode must be set to 'user' to get notifications")

        notifications = self.github_client.get_user().get_notifications(since=since)
        return notifications

    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        if disable_eyes:
            return None
        try:
            headers, data_patch = self.issue._requester.requestJsonAndCheck(
                "POST", f"{self.base_url}/repos/{self.repo}/issues/comments/{issue_comment_id}/reactions",
                input={"content": "eyes"}
            )
            return data_patch.get("id", None)
        except Exception as e:
            get_logger().exception(f"Failed to add eyes reaction, error: {e}")
            return None

    def remove_reaction(self, issue_comment_id: int, reaction_id: str) -> bool:
        try:
            # self.pr.get_issue_comment(issue_comment_id).delete_reaction(reaction_id)
            headers, data_patch = self.issue._requester.requestJsonAndCheck(
                "DELETE",
                f"{self.base_url}/repos/{self.repo}/issues/comments/{issue_comment_id}/reactions/{reaction_id}"
            )
            return True
        except Exception as e:
            get_logger().exception(f"Failed to remove eyes reaction, error: {e}")
            return False

    @staticmethod
    def _parse_issue_url(issue_url: str) -> Tuple[str, int]:
        parsed_url = urlparse(issue_url)

        if 'github.com' not in parsed_url.netloc:
            raise ValueError("The provided URL is not a valid GitHub URL")

        path_parts = parsed_url.path.strip('/').split('/')
        if 'api.github.com' in parsed_url.netloc:
            if len(path_parts) < 5 or path_parts[3] != 'issues':
                raise ValueError("The provided URL does not appear to be a GitHub ISSUE URL")
            repo_name = '/'.join(path_parts[1:3])
            try:
                issue_number = int(path_parts[4])
            except ValueError as e:
                raise ValueError("Unable to convert issue number to integer") from e
            return repo_name, issue_number

        if len(path_parts) < 4 or path_parts[2] != 'issues':
            raise ValueError("The provided URL does not appear to be a GitHub PR issue")

        repo_name = '/'.join(path_parts[:2])
        try:
            issue_number = int(path_parts[3])
        except ValueError as e:
            raise ValueError("Unable to convert issue number to integer") from e

        return repo_name, issue_number

    def _get_github_client(self):
        deployment_type = get_settings().get("GITHUB.DEPLOYMENT_TYPE", "user")

        if deployment_type == 'app':
            try:
                private_key = get_settings().github.private_key
                app_id = get_settings().github.app_id
            except AttributeError as e:
                raise ValueError("GitHub app ID and private key are required when using GitHub app deployment") from e
            if not self.installation_id:
                raise ValueError("GitHub app installation ID is required when using GitHub app deployment")
            auth = AppAuthentication(app_id=app_id, private_key=private_key,
                                     installation_id=self.installation_id)
            return Github(app_auth=auth, base_url=self.base_url)

        if deployment_type == 'user':
            try:
                token = get_settings().github.user_token
            except AttributeError as e:
                raise ValueError(
                    "GitHub token is required when using user deployment. See: "
                    "https://github.com/Codium-ai/pr-agent#method-2-run-from-source") from e
            return Github(auth=Auth.Token(token), base_url=self.base_url)

    def _get_repo(self):
        if hasattr(self, 'repo_obj') and \
                hasattr(self.repo_obj, 'full_name') and \
                self.repo_obj.full_name == self.repo:
            return self.repo_obj
        else:
            self.repo_obj = self.github_client.get_repo(self.repo)
            return self.repo_obj

    def _get_issue(self):
        return self._get_repo().get_issue(self.issue_num)

    def get_issue_as_prompt(self):
        all_comments = ['There is a chat in github issue: ']
        if self.issue and self.issue.body:
            all_comments.append(f'Author: {self.issue.user.login}\nContent:\n{self.issue.body}')
        for i in self.issue_comments:
            if i and i.body:
                all_comments.append(f'Author: {i.user.login}\nContent:\n{i.body}')
        all_comments.append(
            'Please find the last relevant question and provide answer on it. Do not consider unrelevant messaages, but consider previous dialogue')
        return '\n\n'.join(all_comments)
