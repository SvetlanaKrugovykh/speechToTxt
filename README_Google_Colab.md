# 🚀 Google Colab Integration for Faster-Whisper

Этот модуль добавляет поддержку Google Colab для **БЕСПЛАТНОГО** GPU-ускоренного распознавания речи.

## 📋 Что добавлено в проект:

### 1. `colab_batch_processor.py` 
- **Отдельный модуль** для Google Colab (не влияет на основной проект)
- GPU-ускоренная обработка
- Автоматическое определение устройства (GPU/CPU)
- Batch processing для множества файлов

### 2. `Google_Colab_Faster_Whisper.ipynb`
- **Готовый Jupyter notebook** для Google Colab
- Пошаговые инструкции
- Автоматическая установка зависимостей
- Простой интерфейс для загрузки и скачивания

## 🚀 Как использовать Google Colab:

### Простыми словами:
1. **Открываете** [colab.research.google.com](https://colab.research.google.com) в браузере
2. **Загружаете** файл `Google_Colab_Faster_Whisper.ipynb`
3. **Запускаете** все ячейки по порядку
4. **Получаете** результаты в 10-20 раз быстрее!

### Подробные шаги:

#### 1. Подготовка файлов
```
📁 Ваши файлы → Google Drive → папка "audio_files"
```

#### 2. Открытие Colab
- Идите на [colab.research.google.com](https://colab.research.google.com)
- Нажмите "Upload" и выберите `Google_Colab_Faster_Whisper.ipynb`

#### 3. Включение GPU
- Runtime → Change runtime type → Hardware accelerator → GPU

#### 4. Запуск обработки
- Нажмите "Runtime" → "Run all"
- Следуйте инструкциям в notebook

## ⚡ Сравнение производительности:

| Метод | Устройство | Время на файл | Все 48 файлов |
|-------|-----------|---------------|---------------|
| **Ваш компьютер** | CPU | 30-60 сек | 2-3 часа |
| **Google Colab** | GPU (Tesla T4) | 3-10 сек | 5-15 минут |

## 🎯 Преимущества Google Colab:

### ✅ Плюсы:
- **Бесплатно** 12 часов GPU в день
- **Быстрее** в 10-20 раз
- **Больше RAM** (12GB vs локальные ограничения)
- **Не нужно ничего устанавливать**
- **Тот же код** и качество

### ⚠️ Ограничения:
- Нужен интернет
- Файлы надо загружать в Google Drive
- Сессия живет 12 часов
- После 12 часов GPU переключается на CPU

## 📂 Структура файлов:

```
📁 Ваш проект/
├── 📄 colab_batch_processor.py          # Модуль для Colab
├── 📓 Google_Colab_Faster_Whisper.ipynb # Notebook для Colab
├── 📄 README_Google_Colab.md            # Эта инструкция
└── 📁 (остальные файлы не затронуты)    # Основной проект работает как прежде
```

## 🔧 Настройки качества:

В notebook можете изменить:

```python
# Для скорости
model = WhisperModel("small", device="cuda", compute_type="float16")

# Для качества  
model = WhisperModel("medium", device="cuda", compute_type="float16")

# Для максимального качества
model = WhisperModel("large", device="cuda", compute_type="float16")
```

## 📝 Пример использования:

1. **Загрузите** аудио файлы в Google Drive
2. **Откройте** `Google_Colab_Faster_Whisper.ipynb` в Colab
3. **Измените** путь к файлам:
   ```python
   source_dir = "/content/drive/MyDrive/ваша_папка_с_аудио"
   ```
4. **Запустите** все ячейки
5. **Скачайте** ZIP файл с результатами

## 🆘 Если что-то не работает:

### Проблема: "No GPU available"
**Решение:** Runtime → Change runtime type → Hardware accelerator → GPU

### Проблема: "Source directory not found"
**Решение:** Проверьте путь к папке в Google Drive

### Проблема: "Session disconnected"
**Решение:** Нормально, просто перезапустите последнюю ячейку

## 🎯 Когда использовать Colab:

- **Много файлов** (10+ файлов)
- **Нужна скорость** (срочный проект)
- **Слабый компьютер** (не хватает RAM)
- **Эксперименты** с разными моделями

## 💡 Советы:

1. **Сначала протестируйте** на 3-5 файлах
2. **Сохраняйте** результаты в Google Drive
3. **Используйте** GPU в рабочее время (быстрее загрузка)
4. **Не закрывайте** вкладку во время обработки

---

**Ваш основной проект остается нетронутым!** Colab модули - это дополнительная опция для ускорения. 🚀
