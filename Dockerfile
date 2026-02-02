# Python 3.11 yoki 3.12 ishlatamiz (aiogram 3.1.1 uchun yetarli)
FROM python:3.11-slim

# Kerakli tizim paketlarini o'rnatamiz (build uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Ish papkasi
WORKDIR /app

# Fayllarni copy qilamiz
COPY . /app

# Dependencies o'rnatamiz (requirements.txt dan)
RUN pip install --no-cache-dir -r requirements.txt

# Botni ishga tushirish
CMD ["python", "bot.py"]
