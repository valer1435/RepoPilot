import asyncio
import os

import aiohttp
from pr_agent.agent.pr_agent import PRAgent
from pr_agent.config_loader import get_settings
from pr_agent.log import LoggingFormat, get_logger, setup_logger

from pr.PrGithubProvider import PrGithubProvider
from repo_copilot.rag.issue.github_issue_provider import IssueGithubProvider
from repo_copilot.rag.issue.issue_agent import IssueAgent
from repo_copilot.rag.issue.rag_app.rag import RAGApp

setup_logger(fmt=LoggingFormat.JSON, level="DEBUG")


class RepoPilot:
    NOTIFICATION_URL = "https://api.github.com/notifications"

    def __init__(self, issue_config_path: str, pr_config_path: str):
        self._setup_pr_agent()
        self.rag_app = self._setup_rag(issue_config_path)
        self.handled_ids = set()
        self.last_modified = [None]
        self.pr_github_provider = PrGithubProvider(config_path=pr_config_path)
        self.issue_github_provider = IssueGithubProvider()
        self.user_id = self.pr_github_provider.get_user_id()
        self.user_tag = "@" + self.user_id
        self.pr_agent = PRAgent()
        self.issue_agent = IssueAgent(self.rag_app)
        get_settings().set("CONFIG.PUBLISH_OUTPUT_PROGRESS", False)

    def _setup_pr_agent(self):
        provider = "github"  # GitHub provider
        user_token = os.environ["GITHUB_TOKEN"]  # GitHub user token
        openai_key = os.environ['OPENAI_API_KEY']  # OpenAI key
        # openai_base = os.environ['OPENAI_API_BASE']
        # openai_model = 'openai/deepseek-chat'

        # Setting the configurations
        get_settings().set("CONFIG.git_provider", provider)
        get_settings().set("openai.key", openai_key)
        # get_settings().set("openai.api_base", openai_base)
        # get_settings().set("CONFIG.model", openai_model)
        get_settings().set("github.user_token", user_token)

    def _setup_rag(self, config_path):
        return RAGApp(config_path)

    def add_docs(self, docs_links: list[str]):
        self.rag_app.add_links(docs_links)

    async def _parse_comment(self, notification, session, headers):
        latest_comment = notification['subject']['latest_comment_url']
        async with session.get(latest_comment, headers=headers) as comment_response:
            if comment_response.status == 200:
                comment = await comment_response.json()
                if 'id' in comment:
                    if comment['id'] in self.handled_ids:
                        return None, None, None
                    else:
                        self.handled_ids.add(comment['id'])
                if 'user' in comment and 'login' in comment['user']:
                    if comment['user']['login'] == self.user_id:
                        return None, None, None
                comment_body = comment['body'] if 'body' in comment else ''
                commenter_github_user = comment['user']['login'] \
                    if 'user' in comment else ''
                get_logger().info(
                    f"Commenter: {commenter_github_user}\nComment: {comment_body}")
                if not comment_body or self.user_tag not in comment_body:
                    return None, None, None
                comment_id = comment['id']
                return comment_id, comment_body, commenter_github_user
            return None, None, None

    async def handle_pr(self, notification, session, headers):
        pr_url = notification['subject']['url']
        comment_id, comment_body, commenter_github_user = await self._parse_comment(notification, session, headers)
        if not comment_body:
            return False
        rest_of_comment = comment_body.split(self.user_tag)[1].strip()
        self.pr_github_provider.set_pr(pr_url)
        success = await self.pr_agent.handle_request(pr_url, rest_of_comment,
                                                     notify=lambda: self.pr_github_provider.add_eyes_reaction(
                                                         comment_id))  # noqa E501
        if not success:
            self.pr_github_provider.set_pr(pr_url)
        return True

    async def handle_issue(self, notification, session, headers):
        issue_url = notification['subject']['url']
        self.issue_github_provider.set_issue(issue_url)
        comment_id, comment_body, commenter_github_user = await self._parse_comment(notification, session, headers)
        if not comment_body:
            return False
        success = await self.issue_agent.handle_request(issue_url,
                                                        notify=lambda: self.issue_github_provider.add_eyes_reaction(
                                                            comment_id))  # noqa E501
        return True

    def pool(self):
        asyncio.run(self._polling_loop())

    async def _polling_loop(self):
        """
        Polls for notifications and handles them accordingly.
        """

        try:
            deployment_type = get_settings().github.deployment_type
            token = get_settings().github.user_token
        except AttributeError:
            deployment_type = 'none'
            token = None

        if deployment_type != 'user':
            raise ValueError("Deployment mode must be set to 'user' to get notifications")
        if not token:
            raise ValueError("User token must be set to get notifications")

        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    await asyncio.sleep(5)
                    headers = {
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": f"Bearer {token}"
                    }
                    params = {
                        "participating": "true"
                    }
                    if self.last_modified[0]:
                        headers["If-Modified-Since"] = self.last_modified[0]

                    async with session.get(self.NOTIFICATION_URL, headers=headers, params=params) as response:
                        if response.status == 200:
                            if 'Last-Modified' in response.headers:
                                self.last_modified[0] = response.headers['Last-Modified']
                            notifications = await response.json()
                            if not notifications:
                                continue
                            for notification in notifications:
                                self.handled_ids.add(notification['id'])
                                if 'reason' in notification and notification['reason'] == 'mention':
                                    if 'subject' in notification:
                                        if notification['subject']['type'] == 'PullRequest':
                                            await self.handle_pr(notification, session, headers)
                                        elif notification['subject']['type'] == 'Issue':
                                            await self.handle_issue(notification, session, headers)

                        elif response.status != 304:
                            print(f"Failed to fetch notifications. Status code: {response.status}")

                except Exception as e:
                    raise e
