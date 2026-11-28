"""
models.py
---------
جدولا قاعدة البيانات (Database Models).
تنحفظ كلها في ملف nawah.db (قاعدة SQL من نوع SQLite) ويمكن فتحه من Anaconda.
كل كلاس = جدول، وكل سطر داخله = عمود.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey

from database import Base


class Variety(Base):
    """جدول أنواع التمور + قيمها الغذائية (مصدر المعلومات الأساسي)."""
    __tablename__ = "varieties"

    id = Column(Integer, primary_key=True)
    name_ar = Column(String, unique=True, nullable=False)   # الاسم بالعربي: سكري
    name_en = Column(String)                                 # الاسم بالإنجليزي: Sukkari
    calories_per_100g = Column(Float)                        # السعرات لكل 100 جرام
    sugar_per_100g = Column(Float)                           # السكر (جرام) لكل 100 جرام
    calories_per_date = Column(Float)                        # السعرات للتمرة الواحدة تقريباً
    description = Column(Text)                               # وصف مختصر للنوع


class Analysis(Base):
    """سجل كل تحليل صورة: النتيجة + هل أكّد المستخدم صحتها (بيانات تدريب لاحقاً)."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    image_path = Column(String)                                 # مكان حفظ الصورة
    ai_variety = Column(String)                                 # النوع اللي توقعه الذكاء الاصطناعي
    ai_confidence = Column(Float)                               # نسبة الثقة (0 إلى 1)
    variety_id = Column(Integer, ForeignKey("varieties.id"), nullable=True)
    user_confirmed = Column(Boolean, nullable=True)             # صح / خطأ / لم يُجب بعد (None)
    corrected_variety = Column(String, nullable=True)           # النوع الصحيح لو المستخدم صحّح
    created_at = Column(DateTime, default=datetime.utcnow)
