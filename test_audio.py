"""
اسکریپت تست برای بررسی عملکرد تشخیص آهنگ
"""

import os
import sys
import argparse
from database import init_db, get_fingerprints, get_song_by_id
from audio_fingerprint import generate_fingerprint, compare_fingerprints

def test_audio_recognition(test_file):
    """تست تشخیص فایل صوتی"""
    print(f"در حال تست فایل: {test_file}")
    
    # بررسی وجود فایل
    if not os.path.exists(test_file):
        print(f"خطا: فایل {test_file} وجود ندارد.")
        return
    
    # مقداردهی اولیه دیتابیس
    init_db()
    
    # استخراج اثر انگشت صوتی
    print("در حال استخراج ویژگی‌های صوتی...")
    test_fingerprint = generate_fingerprint(test_file)
    
    if test_fingerprint is None:
        print("خطا در پردازش فایل صوتی.")
        return
        
    # دریافت اثر انگشت‌های دیتابیس
    print("در حال دریافت اثر انگشت‌های دیتابیس...")
    db_fingerprints = get_fingerprints()
    
    if not db_fingerprints:
        print("هیچ آهنگی در دیتابیس وجود ندارد.")
        return
    
    print(f"تعداد {len(db_fingerprints)} آهنگ در دیتابیس یافت شد.")
    
    # مقایسه اثر انگشت‌های صوتی
    print("در حال مقایسه اثر انگشت‌ها...")
    results = compare_fingerprints(test_fingerprint, db_fingerprints, threshold=0.70)
    
    if not results:
        print("هیچ آهنگ مشابهی یافت نشد.")
        return
    
    # نمایش نتایج
    print(f"\n{len(results)} آهنگ مشابه یافت شد:")
    
    for i, result in enumerate(results[:5]):
        song = get_song_by_id(result['id'])
        similarity = result['similarity'] * 100
        
        print(f"{i+1}. عنوان: {song.title}")
        print(f"   خواننده: {song.artist}")
        print(f"   درصد شباهت: {similarity:.2f}%")
        print(f"   مسیر فایل: {song.file_path}")
        print("")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="تست تشخیص آهنگ")
    parser.add_argument("file", help="مسیر فایل صوتی برای تست")
    
    args = parser.parse_args()
    test_audio_recognition(args.file) 