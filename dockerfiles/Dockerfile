# Use python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (like curl)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy configuration files
COPY pyproject.toml poetry.lock* ./

# Config poetry to not create venv
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --only main

# Install Gunicorn production server
RUN pip install gunicorn

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 5000

# Run the app
# -w 2: Two worker processes (good for Pi)
# -b 0.0.0.0:5000: Open to the network
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "run:app"]