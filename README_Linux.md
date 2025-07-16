# 🐧 Linux Deployment Guide

## 🚀 Универсальный процессор для Linux

Создан `universal_processor.py` - автоматически определяет среду и оптимизирует настройки.

## 📋 Установка на Linux сервере:

### 1. Системные зависимости
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip ffmpeg

# CentOS/RHEL
sudo yum install python3 python3-pip ffmpeg

# Arch Linux
sudo pacman -S python python-pip ffmpeg
```

### 2. Python зависимости
```bash
# Основные пакеты
pip3 install faster-whisper torch

# Для аудио конвертации
pip3 install pydub

# Для GPU (если есть NVIDIA)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Проверка GPU (если есть)
```bash
# Проверка NVIDIA GPU
nvidia-smi

# Проверка в Python
python3 -c "import torch; print(torch.cuda.is_available())"
```

## 🔧 Запуск на Linux:

### 1. Командная строка
```bash
# Интерактивный режим
python3 universal_processor.py

# С параметрами
python3 universal_processor.py --source /path/to/audio --output /path/to/output --model small

# С разными моделями
python3 universal_processor.py -s /audio -o /output -m medium
```

### 2. Как systemd service
```bash
# Создать service файл
sudo nano /etc/systemd/system/whisper-processor.service

# Содержимое:
[Unit]
Description=Whisper Audio Processor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 universal_processor.py --source /audio --output /output
Restart=always

[Install]
WantedBy=multi-user.target

# Активировать
sudo systemctl enable whisper-processor
sudo systemctl start whisper-processor
```

### 3. Через cron для автоматизации
```bash
# Редактировать crontab
crontab -e

# Добавить задачу (каждый час)
0 * * * * cd /path/to/project && python3 universal_processor.py --source /audio --output /output
```

## 🐳 Docker контейнер:

```dockerfile
FROM python:3.9-slim

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Установить Python пакеты
RUN pip install faster-whisper torch pydub

# Копировать код
COPY universal_processor.py /app/
WORKDIR /app

# Запуск
CMD ["python3", "universal_processor.py"]
```

```bash
# Сборка
docker build -t whisper-processor .

# Запуск
docker run -v /path/to/audio:/audio -v /path/to/output:/output whisper-processor python3 universal_processor.py --source /audio --output /output
```

## 🔧 Конфигурация для production:

### 1. Создать config файл
```bash
# config.ini
[DEFAULT]
source_dir = /home/user/audio
output_dir = /home/user/output
model_size = small
device = auto
batch_size = 4
```

### 2. Логирование
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

### 3. Мониторинг
```bash
# Установить htop для мониторинга
sudo apt install htop

# Мониторинг GPU
watch nvidia-smi

# Мониторинг процессов
htop
```

## 📊 Производительность на Linux:

| Конфигурация | Время на файл | Рекомендация |
|-------------|---------------|--------------|
| CPU only | 30-60 сек | Для тестирования |
| GPU (GTX 1060) | 5-15 сек | Хорошо |
| GPU (RTX 3080) | 2-8 сек | Отлично |
| GPU (A100) | 1-3 сек | Максимум |

## 🛠️ Troubleshooting:

### CUDA проблемы:
```bash
# Проверить CUDA
nvcc --version

# Переустановить PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Проблемы с ffmpeg:
```bash
# Проверить ffmpeg
ffmpeg -version

# Переустановить
sudo apt remove ffmpeg
sudo apt install ffmpeg
```

### Проблемы с памятью:
```bash
# Мониторинг памяти
free -h
htop

# Увеличить swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔒 Безопасность:

```bash
# Создать отдельного пользователя
sudo useradd -m -s /bin/bash whisper
sudo -u whisper python3 universal_processor.py

# Ограничить доступ к файлам
chmod 600 /path/to/audio/*
chown whisper:whisper /path/to/audio/
```

## 🚀 Автоматизация:

```bash
#!/bin/bash
# process_audio.sh
cd /path/to/project
python3 universal_processor.py --source /incoming/audio --output /processed/text --model small

# Отправить результаты
rsync -av /processed/text/ user@server:/final/destination/
```

**Universal processor работает везде: Windows, Linux, macOS, Colab!** 🌍
