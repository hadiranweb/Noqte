import streamlit as st
import requests
import json
from io import BytesIO
import fitz  # PyMuPDF
import time
import os

# دریافت کلید API از متغیر محیطی برای امنیت بیشتر
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1/chat/completions"

if not api_key:
    st.error("کلید API یافت نشد. لطفاً آن را در متغیرهای محیطی با نام 'OPENROUTER_API_KEY' تنظیم کنید.")
    st.stop()

# استایل راست‌چین برای رابط کاربری
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@500&family=Noto+Sans+Arabic:wght@500&display=swap');
html { direction: rtl; }
.st-emotion-cache-1fttcpj , .st-emotion-cache-nwtri { display: none; }
.st-emotion-cache-5rimss p { text-align: right; font-family: 'DM Sans', sans-serif, 'Noto Sans Arabic', sans-serif; }
pre { text-align: left; }
h1, h2, h3, h4, h5, h6 { font-family: 'Noto Sans Arabic', sans-serif; }
span, p, a, button, ol, li { text-align: right; font-family: 'DM Sans', sans-serif, 'Noto Sans Arabic', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("📄 مترجم PDF (صفحه به صفحه)")

# آپلود فایل PDF
uploaded_file = st.file_uploader("فایل PDF خود را آپلود کنید:", type="pdf")
bt = st.button("📌 شروع ترجمه")

def extract_text_from_page(page):
    """استخراج متن از یک صفحه PDF"""
    return page.get_text("text").strip()

def translate_text(text, api_key, base_url):
    """ارسال درخواست ترجمه به API و مدیریت خطاها"""
    payload = {
        "model": "mistral/ministral-8b",
        "messages": [
            {"role": "system", "content": "متن را به فارسی روان ترجمه کن"},
            {"role": "user", "content": text}
        ],
        "max_tokens": 8000
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(base_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # بررسی وضعیت پاسخ
        result = response.json()
        translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "⚠ خطا در دریافت ترجمه.")
    except requests.exceptions.RequestException as e:
        translated_text = f"⚠ خطا در ارتباط با سرور: {str(e)}"
    return translated_text

if uploaded_file and bt:
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = len(pdf_document)
    translated_pages = []

    # نمایش نوار پیشرفت و وضعیت
    progress_bar = st.progress(0)
    status_text = st.empty()

    for page_num in range(total_pages):
        status_text.text(f"در حال پردازش صفحه {page_num + 1} از {total_pages}...")
        page = pdf_document[page_num]
        text = extract_text_from_page(page)

        if text:  # فقط صفحاتی که متن دارند پردازش شوند
            translated_text = translate_text(text, api_key, base_url)
            translated_pages.append(f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}")

            # نمایش متن اصلی و ترجمه
            st.subheader(f"📜 صفحه {page_num + 1}")
            st.text_area(f"🔍 متن اصلی (صفحه {page_num + 1})", text, height=150, key=f"original_{page_num}")
            st.text_area(f"✅ ترجمه (صفحه {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
            st.divider()

            # به‌روزرسانی نوار پیشرفت
            progress_bar.progress((page_num + 1) / total_pages)
            time.sleep(2)  # تاخیر برای جلوگیری از فشار به API

    status_text.text("ترجمه تکمیل شد!")

    # امکان دانلود ترجمه کامل
    if translated_pages:
        final_translation = "\n\n".join(translated_pages)
        st.download_button(
            label="📥 دانلود ترجمه کامل",
            data=BytesIO(final_translation.encode("utf-8")),
            file_name="translated.txt",
            mime="text/plain"
        )

    pdf_document.close()  # آزادسازی حافظ