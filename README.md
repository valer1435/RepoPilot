# RepoPilot
Open-source AI-powered tool for smart repository maintainance

## Features

1. Q&A service for documentation and code understanding with advanced RAG techniques
2. Documentation generatinon using [RepoAgent](https://github.com/OpenBMB/RepoAgent)
   

## Instalation

```bash
git clone https://github.com/valer1435/RepoPilot.git
cd RepoPilot
pip3 install -r requirements.txt
pip3 install -e .
```

## Usage 

Currently only RAG over documentation mode is supported

Use fedot_example as a reference
1. Create your own dataset (just pass links like [here](https://github.com/valer1435/RepoPilot/blob/main/examples/fedot_example/fedot_example.py#L6) )
2. run ```bash run.sh```
3. After downloading sources you will see browser page with chat (if GUI is used)

## Documentation

You can follow AI-generated [documentation](https://valeriis-organization.gitbook.io/repopilot-docs) genereted by [RepoAgent](https://github.com/OpenBMB/RepoAgent). Please note that llm can hallucinate!
