# docker build -t whisper-app .
# docker run -it --rm --name whisper-container -v D:\01_PythonProjects\01_SpeechToText\assets\audio:/app/assets/audio -e PYTHONPATH=/app whisper-app 


# docker run -it --rm --name whisper-container -v D:\01_PythonProjects\01_SpeechToText\assets\audio:/app/assets/audio -e PYTHONPATH=/app whisper-app python /app/src/whisper_server.py /app/assets/audio/greeting.mp3

# ./runner.cmd greeting.mp3
