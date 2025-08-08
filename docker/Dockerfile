# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VENV_PATH="/opt/poetry/virtualenvs"
ENV POETRY_NO_INTERACTION=1

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the application source code
COPY src ./src
COPY data ./data
COPY docker ./docker

# Set the working directory to the app folder
WORKDIR /app/docker

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
