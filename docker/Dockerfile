FROM python:3.10
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
COPY setup.py ./
COPY repo_copilot ./repo_copilot
RUN pip install -r requirements.txt
RUN pip install -e .
