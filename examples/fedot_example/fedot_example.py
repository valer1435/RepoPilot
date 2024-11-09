from dotenv import load_dotenv
from repo_copilot.github_integration.main import RepoPilot

load_dotenv()
bot = RepoPilot(issue_config_path='config.yml', pr_config_path='pr_agent.toml')
bot.pool()
