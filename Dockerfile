# The Dockerfile is the recipe for building the TAKE IT app "image".
# An image is a frozen, ready-to-run package: an operating system, Python,
# our add-on packages, and our code, all bundled together.

# Start from an official image that already has Python 3.12 on a small Linux.
# It is published for both normal PCs (amd64) and Raspberry Pi (arm64).
FROM python:3.12-slim

# Don't write Python scratch files (.pyc), and print log messages right away.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Inside the container, our code lives in a folder called /app.
WORKDIR /app

# Copy in just the shopping list first, then install everything on it.
# (Doing this before copying the code makes rebuilds much faster.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy in the rest of our code.
COPY . .

# The app listens on port 8000 inside the container.
EXPOSE 8000
