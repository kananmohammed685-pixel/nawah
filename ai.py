"""
ai.py
-----
هنا نرسل صورة التمرة للذكاء الاصطناعي (Claude) ونستقبل النوع.

ملاحظة: نتصل بالخدمة مباشرة عبر طلب HTTP عادي (مكتبة urllib الجاهزة في بايثون)
بدل مكتبة anthropic، حتى لا نعتمد على ملفات مجمّعة قد يمنعها ويندوز.

النقطة المهمة: نجبر النموذج يختار فقط من قائمة الأنواع الموجودة في قاعدة البيانات
(عن طريق enum). هذا يمنع إنه "يخترع" نوع ثاني غير موجود،
وإذا ما كان متأكد يرجّع "غير معروف" بدل ما يعطي إجابة خاطئة.
"""
import base64
import json
import os
import random
import urllib.error
import urllib.request

MODEL = "claude-sonnet-5-5"
API_URL = "https://api.anthropic.com/v1/messages"
UNKNOWN = "غير معروف"


def identify_date(image_bytes: bytes, media_type: str, variety_names: list[str]) -> dict:
    """
    تستقبل الصورة + قائمة الأنواع المتاحة، وترجع:
    {"variety": "سكري", "confidence": 0.85}
    """
    # المفتاح يُقرأ من متغير البيئة ANTHROPIC_API_KEY
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    # الوضع التجريبي: إذا ما فيه مفتاح وكان DEMO_MODE=1 نرجّع نوعاً عشوائياً (محاكاة فقط!)
    # الواجهة تعرض شارة "تجريبي" ليعرف أي شخص أن النتيجة ليست تحليلاً حقيقياً.
    if not api_key and os.getenv("DEMO_MODE") == "1":
        return {"variety": random.choice(variety_names),
                "confidence": round(random.uniform(0.7, 0.95), 2), "demo": True}

    if not api_key or not api_key.isascii():
        raise RuntimeError("مفتاح ANTHROPIC_API_KEY غير موجود أو غير صحيح. ضعي المفتاح الحقيقي (يبدأ بـ sk-ant-).")

    options = variety_names + [UNKNOWN]

    # "أداة" وهمية نستخدمها فقط عشان نحصل على إجابة منظمة (JSON) بقيم محددة
    tool = {
        "name": "report_date_variety",
        "description": "سجّل نوع التمرة الظاهرة في الصورة.",
        "input_schema": {
            "type": "object",
            "properties": {
                "variety": {"type": "string", "enum": options},
                "confidence": {"type": "number", "description": "نسبة الثقة من 0 إلى 1"},
            },
            "required": ["variety", "confidence"],
        },
    }

    body = {
        "model": MODEL,
        "max_tokens": 300,
        "tools": [tool],
        "tool_choice": {"type": "tool", "name": "report_date_variety"},
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64.b64encode(image_bytes).decode(),
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "حدد نوع التمرة في الصورة من القائمة فقط. "
                        "إذا الصورة ليست لتمرة أو لست متأكداً، اختر 'غير معروف'."
                    ),
                },
            ],
        }],
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
    except urllib.error.HTTPError as e:
        details = e.read().decode("utf-8", "ignore")[:200]
        raise RuntimeError(f"رفضت الخدمة الطلب (رمز {e.code}): {details}")

    # نبحث عن نتيجة الأداة في رد النموذج
    for block in data.get("content", []):
        if block.get("type") == "tool_use":
            return block["input"]
    return {"variety": UNKNOWN, "confidence": 0.0}
