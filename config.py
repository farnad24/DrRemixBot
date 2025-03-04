import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات ربات تلگرام
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # توکن از متغیرهای محیطی

# مسیرهای دیتابیس
DATABASE_PATH = os.getenv("DATABASE_PATH", "sqlite:///music_database.db")  # مسیر دیتابیس SQL
MUSIC_LIBRARY_PATH = os.getenv("MUSIC_LIBRARY_PATH", "./music_folder")  # مسیر پوشه کتابخانه موسیقی شما

# تنظیمات پردازش صوتی
SAMPLE_RATE = 22050  # فرکانس نمونه‌برداری
DURATION = 30  # مدت زمان پردازش (ثانیه)
HOP_LENGTH = 512  # طول پرش برای استخراج ویژگی‌ها
N_FFT = 2048  # اندازه FFT
N_MELS = 128  # تعداد فیلترهای mel

# تنظیمات پردازش صوتی بهبود یافته
SAMPLE_RATE = 44100  # افزایش فرکانس نمونه‌برداری برای کیفیت بهتر
DURATION = 45  # افزایش مدت زمان پردازش برای تطبیق بهتر
HOP_LENGTH = 256  # کاهش طول پرش برای وضوح بیشتر
N_FFT = 4096  # افزایش اندازه FFT برای وضوح طیفی بهتر
N_MELS = 256  # افزایش تعداد فیلترهای mel برای تفکیک بهتر

# تنظیمات تشخیص
SIMILARITY_THRESHOLD = 0.65  # آستانه شباهت
MAX_RESULTS = 5  # حداکثر تعداد نتایج 