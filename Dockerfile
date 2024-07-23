# Use a lightweight base image with Python 3.11
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir numpy==2.0.0 openai-whisper pydub
RUN pip install --no-cache-dir flask

ENV FLASK_APP=src.app:create_app
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000
# Define the PYTHONPATH environment variable to include /app
ENV PYTHONPATH="/app"

# Run the whisper_server.py script
# CMD ["python", "src/whisper_server.py"]
CMD ["flask", "run"]