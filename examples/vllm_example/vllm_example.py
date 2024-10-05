from dotenv import load_dotenv

from main import RepoPilot

load_dotenv()

bot = RepoPilot(issue_config_path='config.yml', pr_config_path='pr_agent.toml')
bot.add_docs_site()
#bot.add_codebase()

bot.pool()
