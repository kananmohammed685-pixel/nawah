"""
main.py
-------
التطبيق الرئيسي: كل مسارات الـ API (Endpoints) هنا.
للتشغيل:  uvicorn main:app --reload
"""
import os
import uuid
import secrets

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal, ON_VERCEL
from models import Variety, Company, Suggestion, Analysis
from seed import seed_if_empty
import ai

# ---------- الإعدادات ----------
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")   # غيّريها!
UPLOAD_DIR = "/tmp/uploads" if ON_VERCEL else "uploads"   # على Vercel الكتابة في /tmp فقط
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5 ميجابايت

def upgrade_old_tables():
    """لو كان عندك ملف nawah.db قديم (قبل إضافة الدولة والتقييم)، نعيد إنشاء جدولي الشركات والاقتراحات."""
    tables = inspect(engine).get_table_names()
    if "companies" in tables:
        cols = [c["name"] for c in inspect(engine).get_columns("companies")]
        if "country" not in cols:
            print("تحديث جدول الشركات القديم إلى الشكل الجديد...")
            Company.__table__.drop(engine)
            Suggestion.__table__.drop(engine, checkfirst=True)


os.makedirs(UPLOAD_DIR, exist_ok=True)
upgrade_old_tables()
Base.metadata.create_all(engine)          # ينشئ الجداول إذا مو موجودة
with SessionLocal() as _db:
    seed_if_empty(_db)                    # يعبّي البيانات الأولية

app = FastAPI(title="Nawah - نواة")


# ---------- الصفحات ----------
@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/admin")
def admin_page():
    return FileResponse("static/admin.html")


# ---------- 1) تحليل صورة ----------
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """يستقبل الصورة، يرسلها للذكاء الاصطناعي، يحفظ النتيجة، ويرجّع معلومات التمرة."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "نوع الملف غير مدعوم. ارفعي صورة JPG أو PNG أو WEBP.")
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(400, "الصورة كبيرة جداً (الحد 5 ميجابايت).")

    # حفظ الصورة باسم عشوائي
    ext = file.content_type.split("/")[1]
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.{ext}")
    with open(path, "wb") as f:
        f.write(data)

    # الذكاء الاصطناعي يختار من الأنواع الموجودة في القاعدة فقط
    names = [v.name_ar for v in db.query(Variety).all()]
    try:
        result = ai.identify_date(data, file.content_type, names)
    except Exception as e:
        raise HTTPException(502, f"تعذر الاتصال بخدمة الذكاء الاصطناعي: {e}")

    variety = db.query(Variety).filter(Variety.name_ar == result["variety"]).first()

    analysis = Analysis(image_path=path, ai_variety=result["variety"],
                        ai_confidence=result["confidence"],
                        variety_id=variety.id if variety else None)
    db.add(analysis)
    db.commit()

    return {
        "analysis_id": analysis.id,
        "recognized": variety is not None,
        "confidence": result["confidence"],
        "demo": bool(result.get("demo")),      # True = نتيجة تجريبية وليست تحليلاً حقيقياً
        "variety": None if not variety else {
            "name_ar": variety.name_ar,
            "name_en": variety.name_en,
            "calories_per_100g": variety.calories_per_100g,
            "sugar_per_100g": variety.sugar_per_100g,
            "calories_per_date": variety.calories_per_date,
            "description": variety.description,
        },
    }


# ---------- 2) رأي المستخدم ----------
class Feedback(BaseModel):
    correct: bool
    corrected_variety: str | None = None   # النوع الصحيح لو التحليل خاطئ


@app.post("/api/analyses/{aid}/feedback")
def feedback(aid: int, body: Feedback, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, aid)
    if not analysis:
        raise HTTPException(404, "التحليل غير موجود")
    analysis.user_confirmed = body.correct
    analysis.corrected_variety = None if body.correct else body.corrected_variety
    db.commit()
    return {"ok": True}


# ---------- 3) القوائم ----------
@app.get("/api/varieties")
def varieties(db: Session = Depends(get_db)):
    return [{"id": v.id, "name_ar": v.name_ar, "name_en": v.name_en,
             "calories_per_100g": v.calories_per_100g,
             "sugar_per_100g": v.sugar_per_100g,
             "calories_per_date": v.calories_per_date,
             "description": v.description} for v in db.query(Variety).all()]


def split_varieties(text):
    """تحوّل النص 'مجدول،برحي' إلى قائمة ['مجدول', 'برحي'] (تقبل الفاصلة العربية والإنجليزية)."""
    parts = (text or "").replace("،", ",").split(",")
    return [p.strip() for p in parts if p.strip()]


@app.get("/api/companies")
def companies(db: Session = Depends(get_db)):
    """الشركات: المميزة أولاً، ثم الأعلى تقييماً، ثم حسب الترتيب في القاعدة."""
    rows = db.query(Company).order_by(Company.featured.desc(), Company.rating.desc(), Company.id).all()
    return [{"id": c.id, "name": c.name, "name_en": c.name_en, "description": c.description,
             "country": c.country, "city": c.city, "founded_year": c.founded_year,
             "varieties": split_varieties(c.varieties),
             "website": c.website, "phone": c.phone, "rating": c.rating,
             "featured": bool(c.featured)} for c in rows]


# ---------- 4) اقتراح شركة ----------
class SuggestIn(BaseModel):
    name: str
    country: str | None = None
    city: str | None = None
    website: str | None = None
    phone: str | None = None


@app.post("/api/suggest")
def suggest(body: SuggestIn, db: Session = Depends(get_db)):
    if not body.name.strip():
        raise HTTPException(400, "اسم الشركة مطلوب")
    db.add(Suggestion(name=body.name.strip(), country=body.country, city=body.city,
                      website=body.website, phone=body.phone))
    db.commit()
    return {"ok": True}


# ---------- 5) الإحصائيات والبيانات ----------
@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(Analysis).count()
    answered = db.query(Analysis).filter(Analysis.user_confirmed.isnot(None)).count()
    correct = db.query(Analysis).filter(Analysis.user_confirmed.is_(True)).count()
    return {
        "total_analyses": total,
        "answered": answered,
        "correct": correct,
        "accuracy": round(correct / answered, 3) if answered else None,
    }


@app.get("/api/dataset")
def dataset(db: Session = Depends(get_db)):
    """يصدّر الصور اللي أكّدها المستخدم مع التصنيف الصحيح (للتدريب لاحقاً)."""
    rows = db.query(Analysis).filter(Analysis.user_confirmed.isnot(None)).all()
    return [{"image": a.image_path,
             "label": a.ai_variety if a.user_confirmed else a.corrected_variety}
            for a in rows if (a.ai_variety if a.user_confirmed else a.corrected_variety)]


# ---------- 6) لوحة الإدارة (محمية بكلمة مرور) ----------
def check_admin(x_admin_password: str = Header(default="")):
    """تتحقق من كلمة المرور المرسلة في الـ Header."""
    if not secrets.compare_digest(x_admin_password, ADMIN_PASSWORD):
        raise HTTPException(401, "كلمة المرور خاطئة")


@app.get("/api/admin/suggestions", dependencies=[Depends(check_admin)])
def admin_list(db: Session = Depends(get_db)):
    rows = db.query(Suggestion).filter(Suggestion.status == "pending").all()
    return [{"id": s.id, "name": s.name, "country": s.country, "city": s.city,
             "website": s.website, "phone": s.phone} for s in rows]


@app.post("/api/admin/suggestions/{sid}/approve", dependencies=[Depends(check_admin)])
def admin_approve(sid: int, db: Session = Depends(get_db)):
    s = db.get(Suggestion, sid)
    if not s:
        raise HTTPException(404, "غير موجود")
    s.status = "approved"
    db.add(Company(name=s.name, country=s.country, city=s.city,
                   website=s.website, phone=s.phone))  # تنضاف تلقائياً للقائمة
    db.commit()
    return {"ok": True}


@app.post("/api/admin/suggestions/{sid}/reject", dependencies=[Depends(check_admin)])
def admin_reject(sid: int, db: Session = Depends(get_db)):
    s = db.get(Suggestion, sid)
    if not s:
        raise HTTPException(404, "غير موجود")
    s.status = "rejected"
    db.commit()
    return {"ok": True}


app.mount("/static", StaticFiles(directory="static"), name="static")
