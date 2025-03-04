import os
import numpy as np
import librosa
import soundfile as sf
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

from config import SAMPLE_RATE, DURATION, HOP_LENGTH, N_FFT, N_MELS

def load_audio(file_path, sr=SAMPLE_RATE, duration=DURATION):
    """بارگذاری فایل صوتی و تبدیل به آرایه یک‌بعدی
    
    Args:
        file_path: مسیر فایل صوتی
        sr: نرخ نمونه‌برداری
        duration: مدت زمان مورد نظر (ثانیه)
        
    Returns:
        آرایه یک‌بعدی از داده‌های صوتی و نرخ نمونه‌برداری واقعی
    """
    try:
        # بارگذاری فایل صوتی با librosa
        signal, sr = librosa.load(file_path, sr=sr, duration=duration, mono=True)
        return signal, sr
    except Exception as e:
        print(f"خطا در بارگذاری فایل '{file_path}': {str(e)}")
        return None, None

def extract_features(signal, sr=SAMPLE_RATE, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS):
    """استخراج ویژگی‌های صوتی از سیگنال با ویژگی‌های بیشتر و پایدارتر
    
    Args:
        signal: آرایه یک‌بعدی سیگنال صوتی
        sr: نرخ نمونه‌برداری
        n_fft: اندازه FFT
        hop_length: طول پرش
        n_mels: تعداد فیلترهای mel
        
    Returns:
        ویژگی‌های استخراج شده به شکل یک بردار
    """
    if signal is None:
        return None
    
    # پیش‌پردازش: نرمال‌سازی سیگنال
    signal = librosa.util.normalize(signal)
    
    # کاهش نویز با فیلتر مدین
    signal = librosa.decompose.nn_filter(signal, aggregate=np.median, metric='cosine')
    
    # استخراج MFCC (Mel-Frequency Cepstral Coefficients) - افزایش تعداد ضرایب
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=20, n_fft=n_fft, hop_length=hop_length)
    # افزودن مشتق اول و دوم MFCC برای اطلاعات بیشتر
    mfccs_delta = librosa.feature.delta(mfccs)
    mfccs_delta2 = librosa.feature.delta(mfccs, order=2)
    
    # استخراج کروماگرام (Chromagram) با کیفیت بالاتر
    chroma = librosa.feature.chroma_cqt(y=signal, sr=sr, hop_length=hop_length)
    
    # استخراج spectral contrast
    contrast = librosa.feature.spectral_contrast(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # استخراج Mel spectrogram با وضوح بالاتر
    mel_spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # ویژگی‌های جدید: Zero Crossing Rate برای تشخیص بهتر ریتم
    zcr = librosa.feature.zero_crossing_rate(signal)
    
    # ویژگی‌های جدید: Spectral Rolloff برای تشخیص بهتر طیف فرکانسی
    rolloff = librosa.feature.spectral_rolloff(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # ویژگی‌های جدید: Spectral Bandwidth برای تشخیص غنای طیفی
    bandwidth = librosa.feature.spectral_bandwidth(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # ویژگی‌های جدید: Tempogram برای تشخیص بهتر ریتم
    tempo = librosa.feature.tempogram(y=signal, sr=sr, hop_length=hop_length)
    
    # استفاده از میانگین و انحراف معیار به جای فقط میانگین
    mfccs_mean = np.mean(mfccs, axis=1)
    mfccs_std = np.std(mfccs, axis=1)
    mfccs_delta_mean = np.mean(mfccs_delta, axis=1)
    mfccs_delta_std = np.std(mfccs_delta, axis=1)
    mfccs_delta2_mean = np.mean(mfccs_delta2, axis=1)
    mfccs_delta2_std = np.std(mfccs_delta2, axis=1)
    
    chroma_mean = np.mean(chroma, axis=1)
    chroma_std = np.std(chroma, axis=1)
    
    contrast_mean = np.mean(contrast, axis=1)
    contrast_std = np.std(contrast, axis=1)
    
    mel_mean = np.mean(mel_spec_db, axis=1)
    mel_std = np.std(mel_spec_db, axis=1)
    
    zcr_mean = np.mean(zcr, axis=1)
    zcr_std = np.std(zcr, axis=1)
    
    rolloff_mean = np.mean(rolloff, axis=1)
    rolloff_std = np.std(rolloff, axis=1)
    
    bandwidth_mean = np.mean(bandwidth, axis=1)
    bandwidth_std = np.std(bandwidth, axis=1)
    
    tempo_mean = np.mean(tempo, axis=1)
    tempo_std = np.std(tempo, axis=1)
    
    # ادغام همه ویژگی‌ها
    features = np.concatenate([
        mfccs_mean, mfccs_std, 
        mfccs_delta_mean, mfccs_delta_std,
        mfccs_delta2_mean, mfccs_delta2_std,
        chroma_mean, chroma_std,
        contrast_mean, contrast_std,
        mel_mean, mel_std,
        zcr_mean, zcr_std,
        rolloff_mean, rolloff_std,
        bandwidth_mean, bandwidth_std,
        tempo_mean, tempo_std
    ])
    
    return features

def generate_fingerprint(file_path):
    """تولید اثر انگشت صوتی برای یک فایل
    
    Args:
        file_path: مسیر فایل صوتی
        
    Returns:
        اثر انگشت صوتی (بردار ویژگی‌ها)
    """
    signal, sr = load_audio(file_path)
    if signal is None:
        return None
    
    features = extract_features(signal, sr)
    return features

def compare_fingerprints(demo_fingerprint, db_fingerprints, threshold=0.65):
    """مقایسه اثر انگشت صوتی دمو با اثر انگشت‌های موجود در دیتابیس با روش‌های پیشرفته‌تر
    
    Args:
        demo_fingerprint: اثر انگشت صوتی دمو
        db_fingerprints: لیست دیکشنری‌هایی که شامل اثر انگشت‌های صوتی دیتابیس و اطلاعات آنهاست
        threshold: آستانه شباهت (بین 0 تا 1) - کاهش یافته برای افزایش حساسیت
        
    Returns:
        لیست آهنگ‌های پیدا شده به همراه امتیاز شباهت
    """
    results = []
    
    # نرمال‌سازی اثر انگشت دمو برای مقایسه بهتر
    demo_fingerprint_norm = demo_fingerprint / np.linalg.norm(demo_fingerprint)
    
    for item in db_fingerprints:
        db_fingerprint = item['fingerprint']
        
        # نرمال‌سازی اثر انگشت دیتابیس
        db_fingerprint_norm = db_fingerprint / np.linalg.norm(db_fingerprint)
        
        # محاسبه شباهت کسینوسی با دقت بالاتر
        similarity = cosine_similarity([demo_fingerprint_norm], [db_fingerprint_norm])[0][0]
        
        # محاسبه فاصله اقلیدسی نرمال‌شده (معکوس فاصله برای تبدیل به شباهت)
        euclidean_dist = np.linalg.norm(demo_fingerprint_norm - db_fingerprint_norm)
        euclidean_similarity = 1 / (1 + euclidean_dist)  # تبدیل به شباهت بین 0 و 1
        
        # ترکیب دو معیار برای دقت بیشتر با وزن‌دهی
        combined_similarity = 0.7 * similarity + 0.3 * euclidean_similarity
        
        if combined_similarity >= threshold:
            results.append({
                'id': item['id'],
                'title': item['title'],
                'artist': item['artist'],
                'similarity': combined_similarity
            })
    
    # مرتب‌سازی نتایج بر اساس شباهت
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    return results

def visualize_audio(file_path, output_path=None):
    """رسم نمودار برای یک فایل صوتی
    
    Args:
        file_path: مسیر فایل صوتی
        output_path: مسیر ذخیره تصویر خروجی (اختیاری)
    """
    signal, sr = load_audio(file_path)
    if signal is None:
        return
    
    plt.figure(figsize=(15, 10))
    
    # رسم موج صوتی
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(signal, sr=sr)
    plt.title('Waveform')
    
    # رسم spectogram
    plt.subplot(3, 1, 2)
    spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH)
    spec_db = librosa.power_to_db(spec, ref=np.max)
    img = librosa.display.specshow(spec_db, sr=sr, hop_length=HOP_LENGTH, x_axis='time', y_axis='mel')
    plt.colorbar(img, format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    
    # رسم MFCC
    plt.subplot(3, 1, 3)
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13, n_fft=N_FFT, hop_length=HOP_LENGTH)
    img = librosa.display.specshow(mfccs, sr=sr, hop_length=HOP_LENGTH, x_axis='time')
    plt.colorbar(img)
    plt.title('MFCC')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show() 