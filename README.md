# RepoPilot
Open-source AI-powered tool for smart repository maintainance

## Features

1. Q&A service for documentation and code understanding with advanced RAG techniques
2. PR analysis is provided by [pr-agent](https://github.com/Codium-ai/pr-agent)
3. Documentation generatinon using [RepoAgent](https://github.com/OpenBMB/RepoAgent)

## Get started
0. **I strongly recommend to use [deepseek](https://www.deepseek.com/) model. Package was tested only with this model.**
1. Create new github account (or use exist)
2. Generate new personal [token](https://github.com/settings/tokens/new) 
3. Run qdrant: `docker run -p 6333:6333 qdrant/qdrant:v1.12.1`
### Option 1 (Preferable. Using pre-build docker image)
4. Create folder with following structure:
    ```
    my_project
    --.env  # file with environment envs
    --config.yml  # config file for Q&A RAG
    --pr_agent.toml  # config for pr-agent
    --start.py  # startup script
    ```
    You can find config and .env file examples in `examples` folder.
    
    ##### Note
    .env file structure as follows: 
    ```
    HUGGINGFACE_ACCESS_TOKEN=<<hf token>>
    OPENAI_BASE_URL=https://api.deepseek.com
    OPENAI_API_KEY=<<deepseek key>>
    DEEPSEEK_API_KEY=<<deepseek key>>
    GITHUB_TOKEN=<<github token>>
    ```
5. #### If GPU is available:
   Run `docker run --net=host --gpus all -it -v /path/to/folder/with/startup/script:/usr/local/app/example valer1435/repo_pilot bash`
   
   Then in the container run `cd /usr/local/app/example && python start.py`
6. #### If GPU is  NOT available:
   Run `docker run --net=host -it -v /path/to/folder/with/startup/script:/usr/local/app/example valer1435/repo_pilot bash`
   
   Then in the container run `cd /usr/local/app/example && python start.py`

### Option 2 (Build from source)
Run 
```bash
git clone https://github.com/valer1435/RepoPilot.git
cd RepoPilot
docker build -f docker/Dockerfile -t valer1435/repo_pilot:0.0.1 .
```

### Option 3 (no docker)
4. Install locally 
    ```bash
    git clone https://github.com/valer1435/RepoPilot.git
    cd RepoPilot
    pip3 install -r requirements.txt
    pip3 install -e .
    ```
5. Create folder with following structure:
    ```
    my_project
    --.env  # file with environment envs
    --config.yml  # config file for Q&A RAG
    --pr_agent.toml  # config for pr-agent
    --start.py  # startup script
    ```
    You can find config and .env file examples in `examples` folder.
    
    ##### Note
    .env file structure as follows: 
    ```
    HUGGINGFACE_ACCESS_TOKEN=<<hf token>>
    OPENAI_BASE_URL=https://api.deepseek.com
    OPENAI_API_KEY=<<deepseek key>>
    DEEPSEEK_API_KEY=<<deepseek key>>
    GITHUB_TOKEN=<<github token>>
    ```
6. Run `python start.py`

    

## Usage
Please follow format are presented in the `examples` folder.

### Pr reviewer
PR review capabilities have not been changed comparing with original framework.
For more information please refer to pr-agent [documentation](https://qodo-merge-docs.qodo.ai/).
To disable pr reviewer just set `pr_config_path=None` in `RepoPilot` in startup script.

### Issue automatic Q&A
You have to create .yml config file. Most things are common, but let's consider specific:

You have to setup 2 data sources (here example for vllm framework).
1. ```yml
     docs:
    collection_name: "vllm" # should be the same with qdrant collection
    site: "https://docs.vllm.ai/en/latest/" # site with docs
    extensions: ["/", '.html'] # extension of files to use
   ```
   Doc parser will recursively parse all pages of documentation, starting from single one. To do this algorithm parses all links to documentation pages on a single page. Then collects links from the second page and so on.
2. ```yml
   code:
    collection_name: "vllm_code" # should be the same with qdrant collection
    repo_owner: "vllm-project"  # repo owner (from github)
    repo_name: "vllm" # repo name (from github)
    branch: "main" # repo branch (from github)
    extensions: [".py"] # files to include
    folders: ["vllm"] # folders to include
   ```
## Documentation

You can follow AI-generated [documentation](https://valeriis-organization.gitbook.io/repopilot-docs) genereted by [RepoAgent](https://github.com/OpenBMB/RepoAgent). Please note that llm can hallucinate!
