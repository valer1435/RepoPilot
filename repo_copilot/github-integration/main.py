import asyncio
import os
from datetime import datetime
from functools import partial
from typing import Optional

import aiohttp
import pr_agent.git_providers
import yaml
from aiohttp import ClientTimeout
from pr_agent.agent.pr_agent import PRAgent
from pr_agent.config_loader import get_settings
from pr_agent.log import LoggingFormat, get_logger, setup_logger

from pr.PrGithubProvider import PrGithubProvider
from repo_copilot.rag.issue.github_issue_provider import IssueGithubProvider
from repo_copilot.rag.issue.issue_agent import IssueAgent
from repo_copilot.rag.issue.rag_app.rag import RAGApp

setup_logger(fmt=LoggingFormat.JSON, level="DEBUG")


class RepoPilot:
    NOTIFICATION_URL = "https://api.github.com/repos/{owner}/{repo}/notifications"

    def __init__(self, issue_config_path: str, pr_config_path: Optional[str] = None):
        pr_agent.git_providers._GIT_PROVIDERS['custom_github'] = partial(PrGithubProvider, config_path=pr_config_path)
        self.handled_ids = set()
        self.pr_config_path = pr_config_path
        self._setup_pr_agent()
        self.rag_app = self._setup_rag(issue_config_path)
        self.issue_agent = IssueAgent(self.rag_app)
        self.user_id = self._get_issue_provider().get_user_id()
        self.user_tag = "@" + self.user_id
        self.pr_agent = PRAgent()

        with open(issue_config_path) as fh:
            config = yaml.load(fh, Loader=yaml.FullLoader)
        self.working_repo_owner = config['RepoSettings']['owner']
        self.working_repo_name = config['RepoSettings']['name']
        self.last_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

    def _get_issue_provider(self):
        return IssueGithubProvider()

    def _get_pr_provider(self):
        return PrGithubProvider(config_path=self.pr_config_path)

    def _setup_pr_agent(self):
        provider = "custom_github"  # Override provider
        user_token = os.environ["GITHUB_TOKEN"]  # GitHub user token
        # Setting the configurations
        get_settings().set("CONFIG.git_provider", provider)

        get_settings().set("github.user_token", user_token)
        get_settings().set("CONFIG.PUBLISH_OUTPUT_PROGRESS", False)

    def _setup_rag(self, config_path):
        return RAGApp(config_path)

    def add_docs_site(self):
        self.rag_app.add_site()

    def add_docs_pages(self, links, collection_name):
        self.rag_app.add_links(links, collection_name)

    def add_codebase(self):
        self.rag_app.add_code_base()

    async def _parse_comment(self, provider, notification, session, headers):
        latest_comment = notification['subject']['latest_comment_url']
        async with session.get(latest_comment, headers=headers) as comment_response:
            if comment_response.status == 200:
                comment = await comment_response.json()
                comment_id = comment['id']
                if 'user' in comment and 'login' in comment['user']:
                    if comment['user']['login'] == self.user_id:
                        return None, None, None
                comment_body = comment['body'] if 'body' in comment else ''
                commenter_github_user = comment['user']['login'] \
                    if 'user' in comment else ''
                get_logger().info(
                    f"Commenter: {commenter_github_user}\nComment: {comment_body}")
                if not comment_body or self.user_tag not in comment_body:
                    if notification['subject']['type'] == 'Issue' and len(provider.issue_comments) == 0 and comment[
                        'state'] == 'open':
                        return comment_id, "__init__", commenter_github_user
                    else:
                        return None, None, None
                comment_id = comment['id']
                return comment_id, comment_body, commenter_github_user
            return None, None, None

    async def handle_pr(self, notification, session, headers):
        pr_url = notification['subject']['url']
        provider = self._get_pr_provider()
        provider.set_pr(pr_url)
        comment_id, comment_body, commenter_github_user = await self._parse_comment(provider, notification, session,
                                                                                    headers)
        if not comment_body:
            return False
        rest_of_comment = comment_body.split(self.user_tag)[1].strip()

        success = await self.pr_agent.handle_request(pr_url, rest_of_comment,
                                                     notify=lambda: provider.add_eyes_reaction(
                                                         comment_id))  # noqa E501
        if not success:
            provider.set_pr(pr_url)
        return True

    async def handle_issue(self, notification, session, headers):
        issue_url = notification['subject']['url']
        provider = self._get_issue_provider()
        provider.set_issue(issue_url)
        comment_id, comment_body, commenter_github_user = await self._parse_comment(provider, notification, session,
                                                                                    headers)
        if not comment_body:
            return False
        if comment_body == '__init__':
            content = f"""👋 Welcome to the Issue Discussion!

Hello there! I'm here to assist you with any questions. 

Please feel free to share your thoughts, and I'll do my best to provide you with the information or support you need. Let's work together to resolve any issues and make things better!

Looking forward to your input! 🌟. To ask me just tag {self.user_tag}"""
            provider.publish_comment(content)
            return True

        success = await self.issue_agent.handle_request(issue_url,
                                                        notify=lambda: provider.add_eyes_reaction(
                                                            comment_id))  # noqa E501
        return success

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

        timeout = 60 * 60 * 24
        session = aiohttp.ClientSession(timeout=ClientTimeout(total=timeout,
                                                              connect=timeout,
                                                              sock_read=timeout,
                                                              sock_connect=timeout
                                                              ))
        while True:

            await asyncio.sleep(5)
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {token}"
            }
            params = {
                "since": self.last_time
            }

            response = await session.get(self.NOTIFICATION_URL.format(owner=self.working_repo_owner,
                                                                      repo=self.working_repo_name),
                                         headers=headers,
                                         params=params)
            if response.status == 200:
                notifications = await response.json()
                if not notifications:
                    print('No notifications')
                    continue
                for notification in notifications:
                    if notification['repository']['owner']['login'] != self.working_repo_owner or \
                            notification['repository']['name'] != self.working_repo_name:
                        continue
                    if 'reason' in notification and notification['reason'] in ['mention', 'subscribed']:
                        if 'subject' in notification:
                            if notification['subject']['type'] == 'PullRequest':
                                if self.pr_config_path:
                                    await self.handle_pr(notification, session, headers)
                                self.last_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
                            elif notification['subject']['type'] == 'Issue':
                                await self.handle_issue(notification, session, headers)
                                self.last_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

            elif response.status != 304:
                print(f"Failed to fetch notifications. Status code: {response.status}")
            else:
                print('')
