import os
import logging
import tempfile
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, run_async

from config import TOKEN, MUSIC_LIBRARY_PATH
from database import init_db, get_song_by_id, get_fingerprints
from audio_fingerprint import generate_fingerprint, compare_fingerprints, visualize_audio

# تنظیم لاگ‌های برنامه
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# مقداردهی اولیه دیتابیس
init_db()

# چک کردن پوشه کتابخانه موسیقی
if not os.path.exists(MUSIC_LIBRARY_PATH):
    os.makedirs(MUSIC_LIBRARY_PATH)
    logger.info(f"پوشه کتابخانه موسیقی در مسیر {MUSIC_LIBRARY_PATH} ایجاد شد")

def start(update: Update, context: CallbackContext) -> None:
    """ارسال پیام خوش‌آمدگویی"""
    update.message.reply_text(
        "سلام! به ربات یافتن موزیک خوش آمدید! 🎵\n\n"
        "فایل صوتی دمو یا ریمیکس خود را برای من ارسال کنید تا آهنگ اصلی را پیدا کنم.\n\n"
        "از دستورات زیر می‌توانید استفاده کنید:\n"
        "/help - راهنمای استفاده از ربات\n"
        "/about - درباره ربات"
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """ارسال پیام راهنما"""
    update.message.reply_text(
        "🎵 *راهنمای استفاده از ربات یافتن موزیک* 🎵\n\n"
        "این ربات به شما کمک می‌کند تا نسخه کامل آهنگ‌های ریمیکس شده را پیدا کنید.\n\n"
        "*نحوه استفاده:*\n"
        "1. یک فایل صوتی (دمو یا ریمیکس) ارسال کنید\n"
        "2. ربات آهنگ را تجزیه و تحلیل کرده و سعی می‌کند آهنگ اصلی را پیدا کند\n"
        "3. اگر آهنگ در دیتابیس وجود داشته باشد، برای شما ارسال می‌شود\n\n"
        "*دستورات:*\n"
        "/start - شروع مجدد ربات\n"
        "/help - نمایش این راهنما\n"
        "/about - اطلاعات درباره ربات\n\n"
        "*نکته:* کیفیت تشخیص به کیفیت دمو ارسالی شما بستگی دارد. هرچه کیفیت بهتر باشد، احتمال تشخیص دقیق‌تر بیشتر است.",
        parse_mode=ParseMode.MARKDOWN
    )

def about_command(update: Update, context: CallbackContext) -> None:
    """ارسال اطلاعات درباره ربات"""
    update.message.reply_text(
        "🎵 *درباره ربات یافتن موزیک* 🎵\n\n"
        "این ربات با استفاده از تکنیک‌های پردازش سیگنال دیجیتال و یادگیری ماشین، آهنگ‌های ریمیکس شده را تشخیص می‌دهد.\n\n"
        "فناوری‌های استفاده شده:\n"
        "- استخراج ویژگی‌های صوتی با Librosa\n"
        "- الگوریتم‌های تشخیص اثر انگشت صوتی\n"
        "- پایگاه داده برای ذخیره‌سازی اطلاعات آهنگ‌ها\n\n"
        "نسخه: 1.0.0\n"
        "توسعه‌دهنده: برنامه‌نویس هوش مصنوعی",
        parse_mode=ParseMode.MARKDOWN
    )

@run_async
def process_audio(update: Update, context: CallbackContext) -> None:
    """پردازش فایل صوتی دریافتی و جستجو برای آهنگ مشابه"""
    # چک کردن فرمت فایل دریافتی
    audio_file = None
    file_extension = None
    
    if update.message.audio:
        # فایل صوتی از تلگرام (MP3 معمولاً)
        audio_file = update.message.audio
        file_extension = '.mp3'
    elif update.message.voice:
        # پیام صوتی از تلگرام
        audio_file = update.message.voice
        file_extension = '.ogg'
    elif update.message.document:
        # سند صوتی (فرمت‌های مختلف)
        document = update.message.document
        mime_type = document.mime_type
        if mime_type and 'audio' in mime_type:
            audio_file = document
            file_extension = os.path.splitext(document.file_name)[1] if document.file_name else '.audio'
    
    if not audio_file:
        update.message.reply_text("لطفاً یک فایل صوتی ارسال کنید.")
        return
    
    # دریافت و ذخیره فایل ارسالی
    status_message = update.message.reply_text("در حال دریافت فایل صوتی... ⏳")
    
    file = context.bot.get_file(audio_file.file_id)
    
    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
        temp_path = temp_file.name
    
    file.download(custom_path=temp_path)
    
    status_message.edit_text("در حال پردازش فایل صوتی و استخراج ویژگی‌ها... 🔍")
    
    # استخراج اثر انگشت صوتی
    demo_fingerprint = generate_fingerprint(temp_path)
    
    if demo_fingerprint is None:
        os.unlink(temp_path)  # پاک کردن فایل موقت
        status_message.edit_text("خطا در پردازش فایل صوتی. لطفاً فایل دیگری ارسال کنید.")
        return
    
    # دریافت همه اثر انگشت‌های دیتابیس
    db_fingerprints = get_fingerprints()
    
    if not db_fingerprints:
        os.unlink(temp_path)  # پاک کردن فایل موقت
        status_message.edit_text("هیچ آهنگی در دیتابیس وجود ندارد. لطفاً ابتدا کتابخانه موسیقی را پر کنید.")
        return
    
    # مقایسه اثر انگشت صوتی با دیتابیس
    status_message.edit_text("در حال جستجو در کتابخانه موسیقی... 🔎")
    results = compare_fingerprints(demo_fingerprint, db_fingerprints)
    
    # پاک کردن فایل موقت
    os.unlink(temp_path)
    
    if not results:
        status_message.edit_text("متأسفانه آهنگ مشابهی در کتابخانه پیدا نشد. 😔")
        return
    
    # ارسال نتایج به کاربر
    status_message.edit_text("آهنگ(های) مشابه پیدا شد! در حال ارسال... 🎵")
    
    for i, result in enumerate(results[:3]):  # حداکثر 3 نتیجه اول
        song = get_song_by_id(result['id'])
        similarity_percent = round(result['similarity'] * 100, 2)
        
        info_message = f"🎵 *آهنگ پیدا شده ({i+1}/{min(3, len(results))})* 🎵\n\n" \
                      f"*عنوان:* {song.title}\n" \
                      f"*خواننده:* {song.artist}\n" \
                      f"*درصد شباهت:* {similarity_percent}%"
        
        # ارسال فایل آهنگ
        with open(song.file_path, 'rb') as audio:
            context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio,
                caption=info_message,
                parse_mode=ParseMode.MARKDOWN,
                title=song.title,
                performer=song.artist
            )

def main() -> None:
    """راه‌اندازی ربات"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # تعریف هندلرها
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    
    # هندلر برای فایل‌های صوتی
    dispatcher.add_handler(MessageHandler(
        Filters.audio | Filters.voice | Filters.document.category("audio"),
        process_audio
    ))
    
    # شروع ربات
    updater.start_polling()
    logger.info("ربات شروع به کار کرد")
    updater.idle()

if __name__ == '__main__':
    main() 