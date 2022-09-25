# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9.14-slim-buster

EXPOSE 9000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . .

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app 

WORKDIR /app
RUN python -m pip install -e .

USER root

WORKDIR /app/careers

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uvicorn", "--port", "9000", "--host", "0.0.0.0",  "app:app"]
