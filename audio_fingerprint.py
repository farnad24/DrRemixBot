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
    """استخراج ویژگی‌های صوتی از سیگنال
    
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
    
    # استخراج MFCC (Mel-Frequency Cepstral Coefficients)
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13, n_fft=n_fft, hop_length=hop_length)
    
    # استخراج کروماگرام (Chromagram)
    chroma = librosa.feature.chroma_stft(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # استخراج spectral contrast
    contrast = librosa.feature.spectral_contrast(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # استخراج Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # میانگین‌گیری روی محور زمان
    mfccs_mean = np.mean(mfccs, axis=1)
    chroma_mean = np.mean(chroma, axis=1)
    contrast_mean = np.mean(contrast, axis=1)
    mel_mean = np.mean(mel_spec_db, axis=1)
    
    # ادغام همه ویژگی‌ها
    features = np.concatenate([mfccs_mean, chroma_mean, contrast_mean, mel_mean])
    
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

def compare_fingerprints(demo_fingerprint, db_fingerprints, threshold=0.85):
    """مقایسه اثر انگشت صوتی دمو با اثر انگشت‌های موجود در دیتابیس
    
    Args:
        demo_fingerprint: اثر انگشت صوتی دمو
        db_fingerprints: لیست دیکشنری‌هایی که شامل اثر انگشت‌های صوتی دیتابیس و اطلاعات آنهاست
        threshold: آستانه شباهت (بین 0 تا 1)
        
    Returns:
        لیست آهنگ‌های پیدا شده به همراه امتیاز شباهت
    """
    results = []
    
    for item in db_fingerprints:
        db_fingerprint = item['fingerprint']
        
        # محاسبه شباهت کسینوسی
        similarity = cosine_similarity([demo_fingerprint], [db_fingerprint])[0][0]
        
        if similarity >= threshold:
            results.append({
                'id': item['id'],
                'title': item['title'],
                'artist': item['artist'],
                'similarity': similarity
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