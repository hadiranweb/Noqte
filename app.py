import streamlit as st
import requests
import json
from io import BytesIO
import fitz  # PyMuPDF
import time

# کلید API
api_key = "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"
base_url = "https://openrouter.ai/api/v1/chat/completions"

if not api_key:
    st.error("API Key یافت نشد. لطفاً آن را تنظیم کنید.")

# استایل راست‌چین برای نمایش در Streamlit
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

st.title('📄 مترجم PDF (صفحه به صفحه)')

# آپلود فایل PDF
uploaded_file = st.file_uploader("فایل PDF خود را آپلود کنید:", type="pdf")
bt = st.button('📌 شروع ترجمه')

if uploaded_file and bt:
    pdfdocument = fitz.open(stream=uploaded_file.read(), filetype='pdf')
    translated_pages = []  # ذخیره ترجمه‌ها برای دانلود

    for page_num in range(len(pdfdocument)):  # پردازش هر صفحه جداگانه
        page = pdfdocument[page_num]
        text = page.get_text('text')

        if text.strip():  # اگر صفحه‌ای متن داشت، آن را پردازش کن
            payload = {
                "model": "deepseek/deepseek-v3-base:free",
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

            response = requests.post(base_url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "⚠ خطا در دریافت ترجمه.")
            else:
                translated_text = "⚠ خطا در ارتباط با سرور."

            translated_pages.append(f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}")

            # نمایش ترجمه هر صفحه جداگانه
            st.subheader(f"📜 صفحه {page_num + 1}")
            st.text_area(f"🔍 متن اصلی (صفحه {page_num + 1})", text, height=150, key=f"original_{page_num}")
            st.text_area(f"✅ ترجمه (صفحه {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
            st.divider()  # ایجاد فاصله بین صفحات
            time.sleep(2)  # تاخیر 2 ثانیه‌ای برای جلوگیری از ارسال درخواست‌های زیاد

    # دانلود کل ترجمه به عنوان یک فایل
    if translated_pages:
        final_translation = "\n\n".join(translated_pages)
        st.download_button(
            label="📥 دانلود ترجمه کامل",
            data=BytesIO(final_translation.encode("utf-8")),
            file_name="translated.txt",
            mime="text/plain"
        )
