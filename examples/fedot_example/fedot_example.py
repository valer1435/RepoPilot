from dotenv import load_dotenv

from main import RepoPilot

load_dotenv()


class FedotDataSet:
    def __init__(self):
        self.owner = 'aimclub'
        self.repo = 'FEDOT'
        self.branch = 'master'
        self.extensions = ['.py']
        self.folders = ['fedot']


#bot = RepoPilot(issue_config_path='config.yml', pr_config_path='pr_agent.toml')
# local llm
bot = RepoPilot(issue_config_path='config_local/config.yml', pr_config_path='pr_agent.toml')
fedot = FedotDataSet()

# bot.add_docs_site('https://fedot.readthedocs.io/en/latest/index.html', 'fedot')
# bot.add_codebase(fedot.owner, fedot.repo, fedot.branch, fedot.extensions, fedot.folders,  'fedot_code')

bot.pool()
