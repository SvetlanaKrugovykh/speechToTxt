@echo off
set fileName=%1

docker run -it --rm --name whisper-container -v D:\01_PythonProjects\01_SpeechToText\assets\audio:/app/assets/audio -e PYTHONPATH=/app whisper-app python /app/src/whisper_server.py /app/assets/audio/%fileName%
