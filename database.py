import os
import pickle
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_PATH, MUSIC_LIBRARY_PATH

# تنظیم دیتابیس
engine = create_engine(DATABASE_PATH)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Song(Base):
    """مدل دیتابیس برای آهنگ‌ها"""
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    file_path = Column(String)
    fingerprint = Column(LargeBinary)  # اثر انگشت صوتی به صورت باینری
    
    def __repr__(self):
        return f"<Song(title='{self.title}', artist='{self.artist}')>"

def init_db():
    """ایجاد دیتابیس و جداول"""
    Base.metadata.create_all(engine)
    print("دیتابیس با موفقیت ایجاد شد")

def add_song(title, artist, file_path, fingerprint):
    """افزودن آهنگ جدید به دیتابیس"""
    session = Session()
    
    # بررسی وجود آهنگ تکراری
    existing_song = session.query(Song).filter_by(title=title, artist=artist).first()
    if existing_song:
        print(f"آهنگ '{title}' از '{artist}' قبلاً در دیتابیس وجود دارد")
        session.close()
        return
    
    # ذخیره اثر انگشت به صورت باینری
    fingerprint_binary = pickle.dumps(fingerprint)
    
    # ایجاد رکورد جدید
    new_song = Song(title=title, artist=artist, file_path=file_path, fingerprint=fingerprint_binary)
    session.add(new_song)
    session.commit()
    print(f"آهنگ '{title}' از '{artist}' با موفقیت به دیتابیس اضافه شد")
    session.close()

def get_all_songs():
    """دریافت همه آهنگ‌های موجود در دیتابیس"""
    session = Session()
    songs = session.query(Song).all()
    session.close()
    return songs

def get_song_by_id(song_id):
    """دریافت آهنگ با شناسه مشخص"""
    session = Session()
    song = session.query(Song).filter_by(id=song_id).first()
    session.close()
    return song

def get_fingerprints():
    """دریافت همه اثر انگشت‌های صوتی برای مقایسه"""
    session = Session()
    songs = session.query(Song).all()
    fingerprints = []
    
    for song in songs:
        fingerprint = pickle.loads(song.fingerprint)
        fingerprints.append({
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'fingerprint': fingerprint
        })
    
    session.close()
    return fingerprints

def clear_database():
    """پاک کردن همه رکوردها از دیتابیس"""
    session = Session()
    session.query(Song).delete()
    session.commit()
    session.close()
    print("همه آهنگ‌ها از دیتابیس حذف شدند")

if __name__ == "__main__":
    # تست دیتابیس
    init_db()
    print("دیتابیس آماده است") 