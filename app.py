import streamlit as st
from io import BytesIO
import fitz  # PyMuPDF
from openai import OpenAI

# کلید API
metis_api_key = "tpsg-qq0H6FxAHnGmFSDu8e9PPFRvC0NsnNS"
if not metis_api_key:
    st.error("API Key یافت نشد. لطفاً آن را در secrets.toml تنظیم کنید.")

# استایل برای نمایش راست‌چین
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

# آپلود فایل
uploaded_file = st.file_uploader("فایل PDF خود را آپلود کنید:", type="pdf")
bt = st.button('📌 شروع ترجمه')

if uploaded_file and bt:
    pdfdocument = fitz.open(stream=uploaded_file.read(), filetype='pdf')
    translated_pages = []  # ذخیره ترجمه‌ها برای دانلود

    for page_num in range(len(pdfdocument)):  # پردازش هر صفحه جداگانه
        page = pdfdocument[page_num]
        text = page.get_text('text')

        if text.strip():  # اگر صفحه‌ای متن داشت، آن را پردازش کن
            client = OpenAI(api_key=metis_api_key, base_url="https://api.metisai.ir/openai/v1")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "متن را به فارسی روان ترجمه کن"},
                    {"role": "user", "content": text}
                ],
                max_tokens=4000
            )

            if response and hasattr(response, "choices") and response.choices:
                translated_text = response.choices[0].message.content
                translated_pages.append(f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}")
            else:
                translated_text = "⚠ خطا در دریافت ترجمه."

            # نمایش ترجمه هر صفحه جداگانه
            st.subheader(f"📜 صفحه {page_num + 1}")
            st.text_area(f"🔍 متن اصلی (صفحه {page_num + 1})", text, height=150, key=f"original_{page_num}")
            st.text_area(f"✅ ترجمه (صفحه {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
            st.divider()  # ایجاد فاصله بین صفحات

    # **دانلود کل ترجمه به عنوان یک فایل**
    if translated_pages:
        final_translation = "\n\n".join(translated_pages)
        st.download_button(
            label="📥 دانلود ترجمه کامل",
            data=BytesIO(final_translation.encode("utf-8")),
            file_name="translated.pdf",
            mime="text/plain"
        )
