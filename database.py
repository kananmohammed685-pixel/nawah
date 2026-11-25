"""
database.py
-----------
إعداد الاتصال بقاعدة البيانات (SQLite).
SQLite = ملف واحد (nawah.db) ما يحتاج تثبيت أي برنامج.

ملاحظتان للنشر على الإنترنت:
- على Vercel يُسمح بالكتابة في مجلد /tmp فقط، فنضع الملف هناك (يُمسح عند إعادة تشغيل الخادم).
- لو وضعتِ متغيراً اسمه DATABASE_URL (رابط قاعدة خارجية مثل Postgres) نستخدمه بدل SQLite
  فتبقى البيانات محفوظة دائماً.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

ON_VERCEL = bool(os.getenv("VERCEL"))      # Vercel يضيف هذا المتغير تلقائياً

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine_args = {}
else:
    DATABASE_URL = "sqlite:////tmp/nawah.db" if ON_VERCEL else "sqlite:///./nawah.db"
    engine_args = {"connect_args": {"check_same_thread": False}}

# engine = "المحرك" اللي يتصل بالقاعدة
engine = create_engine(DATABASE_URL, **engine_args)

# كل طلب (request) يفتح "جلسة" مع القاعدة ويسكرها بعد ما يخلص
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# كل الجداول ترث من هذا الكلاس
Base = declarative_base()


def get_db():
    """تعطي كل endpoint جلسة قاعدة بيانات وتسكرها تلقائياً بعد الانتهاء."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
