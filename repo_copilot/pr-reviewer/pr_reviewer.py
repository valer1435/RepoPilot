import logging
import string
import sys

import requests
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from flask import request, Flask

from utils import (
    generate_jwt,
    get_installation_access_token,
    get_diff_url,
    parse_diff_to_line_numbers, get_branch_files, get_pr_head_branch
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Open code helper")

GREETING = """
👋 Hi, I'm @open-code-helper, an LLM-powered GitHub app
powered by [NVIDIA AI Foundation Models and Endpoints](https://catalog.ngc.nvidia.com/ai-foundation-models)
that gives you actionable feedback on your writing.

Simply create a new comment in this PR that says:

@open-code-helper run

and I will start my analysis. I only look at what you changed
in this PR.
"""

load_dotenv()

# If the app was installed, retrieve the installation access token through the App's
# private key and app ID, by generating an intermediary JWT token.


PROMPT = """
You are an expert in programming. 
You given a code file. Please analyse it on missed or bad formatted docstrings and type hints. Insert or improve google styled docstrings and typehints where possible.
Please, return only changed code
Please, format you answer as markdown.
Here is the code:
"""


def mentor(
        content,
        model,
        prompt=PROMPT
):
    answer = []
    for i in content:
        subanswer = model.get_answer(f'{prompt}```{content[i]}```')
        if not subanswer:
            subanswer = DeepSeekLLM().get_answer(f'{prompt}```{content[i]}```')
        a = f"### File {i}: \n{subanswer}"
        answer.append(a)

    return '\n\n\n'.join(answer)


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "I'm Working"


@app.route('/webhook/', methods=['POST'])
def handle_webhook():
    data = request.json

    installation = data.get("installation")
    if installation and installation.get("id"):
        installation_id = installation.get("id")
        logger.info(f"Installation ID: {installation_id}")

        JWT_TOKEN = generate_jwt()

        installation_access_token = get_installation_access_token(
            JWT_TOKEN, installation_id
        )
        headers = {
            "Authorization": f"token {installation_access_token}",
            "User-Agent": "open-code-helper",
            "Accept": "application/vnd.github.VERSION.diff",
        }
    else:
        raise ValueError("No app installation found.")
    # If PR exists and is opened
    if "pull_request" in data.keys() and (
            data["action"] in ["opened", "reopened"]
    ):  # use "synchronize" for tracking new commits
        pr = data.get("pull_request")

        # Greet the user and show instructions.
        requests.post(
            f"{pr['issue_url']}/comments",
            json={"body": GREETING},
            headers=headers,
        )
        return JSONResponse(content={}, status_code=200)

    # Check if the event is a new or modified issue comment
    if "issue" in data.keys() and data.get("action") in ["created", "edited"]:
        issue = data["issue"]
        # Check if the issue is a pull request
        if "/pull/" in issue["html_url"]:
            pr = issue.get("pull_request")

            # Get the comment body
            comment = data.get("comment")
            comment_body = comment.get("body")
            # Remove all whitespace characters except for regular spaces
            comment_body = comment_body.translate(
                str.maketrans("", "", string.whitespace.replace(" ", ""))
            )

            # Skip if the bot talks about itself
            author_handle = comment["user"]["login"]

            # Check if the bot is mentioned in the comment
            if (
                    author_handle != "open-code-helper[bot]"
                    and "@open-code-helper run" in comment_body
            ):
                url = get_diff_url(pr)
                diff_response = requests.get(url, headers=headers)
                diff = diff_response.text

                files_with_lines = parse_diff_to_line_numbers(diff)
                # Get head branch of the PR
                headers["Accept"] = "application/vnd.github.full+json"
                head_branch = get_pr_head_branch(pr, headers)
                #
                # # Get files from head branch
                head_branch_files = get_branch_files(pr, head_branch, headers, files_with_lines.keys())
                # # Enrich diff data with context from the head branch.
                # context_files = get_context_from_files(head_branch_files, files_with_lines)
                # Get suggestions from Open code helper
                content = mentor(head_branch_files, NvidiaLLM())
                # Let's comment on the PR
                requests.post(
                    f"{comment['issue_url']}/comments",
                    json={
                        "body": f":rocket: Open code helper finished "
                                + "analysing your PR! :rocket:\n\n"
                                + "Take a look at your results:\n"
                                + f"{content}\n\n"
                                + "This bot is powered by "
                                + "[NVIDIA AI Foundation Models and Endpoints](https://catalog.ngc.nvidia.com/ai-foundation-models).\n"
                    },
                    headers=headers
                )


if __name__ == '__main__':
    app.run(host='10.32.32.6', port=5050, debug=True)
