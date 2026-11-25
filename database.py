"""
database.py
-----------
إعداد الاتصال بقاعدة البيانات (SQLite).
SQLite = ملف واحد (nawah.db) ما يحتاج تثبيت أي برنامج.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./nawah.db"

# engine = "المحرك" اللي يتصل بالقاعدة
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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
