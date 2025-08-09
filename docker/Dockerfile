# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VENV_PATH="/opt/poetry/virtualenvs"
ENV POETRY_NO_INTERACTION=1

# Install system dependencies, install Poetry, then clean up in a single layer
# 1. Set environment variables for Poetry for a predictable installation
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV_CREATE=false

# 2. Add Poetry's bin directory to the PATH. This is essential.
ENV PATH="$POETRY_HOME/bin:$PATH"

# 3. Install system dependencies and Poetry itself
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libgomp1 && \
    curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

# Add poetry to path
#ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry add "uvicorn[standard]"
RUN poetry add fastapi
RUN poetry install --no-root --no-dev

# Copy the application source code
#COPY src ./src
#COPY data ./data
COPY . .

# Set the working directory to the app folder
WORKDIR /app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
