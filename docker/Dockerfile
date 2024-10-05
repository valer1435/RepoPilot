FROM python:3.10
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
COPY repo_copilot ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD []