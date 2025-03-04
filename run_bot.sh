#!/bin/bash

# اسکریپت راه‌اندازی ربات تلگرام موزیک‌یاب

# تنظیم مسیر پروژه
PROJECT_DIR=$(dirname "$(readlink -f "$0")")
cd "$PROJECT_DIR" || exit 1

# فعال‌سازی محیط مجازی
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "محیط مجازی پیدا نشد. در حال ایجاد محیط مجازی..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# بررسی وجود فایل .env
if [ ! -f .env ]; then
    echo "فایل .env پیدا نشد. لطفاً آن را از روی .env.example ایجاد کنید."
    exit 1
fi

# بررسی وجود پوشه کتابخانه موسیقی
MUSIC_FOLDER=$(grep "MUSIC_LIBRARY_PATH" .env | cut -d '=' -f2 | tr -d ' ')
if [ -z "$MUSIC_FOLDER" ]; then
    MUSIC_FOLDER="./music_folder"
fi

if [ ! -d "$MUSIC_FOLDER" ]; then
    echo "پوشه موسیقی در مسیر $MUSIC_FOLDER پیدا نشد. در حال ایجاد پوشه..."
    mkdir -p "$MUSIC_FOLDER"
fi

# اجرای ربات
echo "در حال راه‌اندازی ربات..."
python bot.py 