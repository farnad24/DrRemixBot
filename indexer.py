import os
import argparse
import glob
from tqdm import tqdm
import traceback

from config import MUSIC_LIBRARY_PATH
from database import init_db, add_song, clear_database, get_all_songs
from audio_fingerprint import generate_fingerprint

def get_audio_files(directory, extensions=['.mp3', '.m4a', '.wav', '.flac', '.ogg']):
    """دریافت همه فایل‌های صوتی در یک پوشه و زیرپوشه‌های آن
    
    Args:
        directory: مسیر پوشه
        extensions: پسوندهای فایل‌های صوتی
        
    Returns:
        لیستی از مسیرهای فایل‌های صوتی
    """
    audio_files = []
    for ext in extensions:
        pattern = os.path.join(directory, f"**/*{ext}")
        audio_files.extend(glob.glob(pattern, recursive=True))
    
    return audio_files

def extract_metadata(file_path):
    """استخراج متادیتا از نام فایل
    
    Args:
        file_path: مسیر فایل آهنگ
        
    Returns:
        عنوان و نام هنرمند
    """
    # گرفتن نام فایل بدون پسوند
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # تلاش برای جدا کردن نام هنرمند و عنوان آهنگ
    if ' - ' in name_without_ext:
        artist, title = name_without_ext.split(' - ', 1)
    else:
        # اگر فرمت استاندارد نباشد، کل نام را به عنوان عنوان استفاده می‌کنیم
        artist = "نامشخص"
        title = name_without_ext
    
    return title.strip(), artist.strip()

def index_music_library(directory=MUSIC_LIBRARY_PATH, clear=False):
    """ایندکس کردن کتابخانه موسیقی
    
    Args:
        directory: مسیر پوشه کتابخانه
        clear: آیا دیتابیس قبلی پاک شود؟
    """
    print(f"شروع ایندکس‌گذاری موسیقی از پوشه: {directory}")
    
    # مقداردهی اولیه دیتابیس
    init_db()
    
    # پاک کردن دیتابیس قبلی در صورت درخواست
    if clear:
        clear_database()
        print("دیتابیس قبلی پاک شد")
    
    # دریافت فایل‌های صوتی
    audio_files = get_audio_files(directory)
    print(f"{len(audio_files)} فایل صوتی پیدا شد")
    
    # تعداد فایل‌های اضافه شده و خطادار
    added_count = 0
    error_count = 0
    
    # پردازش هر فایل
    for file_path in tqdm(audio_files, desc="پردازش فایل‌ها"):
        try:
            # استخراج متادیتا
            title, artist = extract_metadata(file_path)
            
            # تولید اثر انگشت صوتی
            fingerprint = generate_fingerprint(file_path)
            
            if fingerprint is not None:
                # افزودن به دیتابیس
                add_song(title, artist, file_path, fingerprint)
                added_count += 1
            else:
                print(f"خطا در استخراج اثر انگشت برای فایل: {file_path}")
                error_count += 1
                
        except Exception as e:
            print(f"خطا در پردازش فایل {file_path}: {str(e)}")
            traceback.print_exc()
            error_count += 1
    
    # نمایش نتایج
    print(f"\nایندکس‌گذاری به پایان رسید:")
    print(f"- {added_count} فایل با موفقیت اضافه شد")
    print(f"- {error_count} فایل با خطا مواجه شد")
    
    # نمایش تعداد کل آهنگ‌ها در دیتابیس
    songs = get_all_songs()
    print(f"تعداد کل آهنگ‌ها در دیتابیس: {len(songs)}")

if __name__ == "__main__":
    # تنظیم پارسر آرگومان‌ها
    parser = argparse.ArgumentParser(description='ایندکس‌کننده کتابخانه موسیقی برای ربات تلگرام')
    parser.add_argument('--dir', type=str, default=MUSIC_LIBRARY_PATH, 
                        help='مسیر پوشه کتابخانه موسیقی')
    parser.add_argument('--clear', action='store_true', 
                        help='پاک کردن دیتابیس قبلی')
    
    args = parser.parse_args()
    
    # شروع ایندکس‌گذاری
    index_music_library(args.dir, args.clear) 