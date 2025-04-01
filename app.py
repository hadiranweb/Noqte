import streamlit as st
import requests
import json
from io import BytesIO
import fitz  # PyMuPDF
import os

# API configuration
api_key = os.getenv("METIS_API_KEY")
base_url = "https://api.metisai.ir/api/v1/wrapper/openai_chat_completion/chat/completions"

# Debug: Check API key
st.write("API Key in use:", api_key)
if not api_key or api_key.strip() == "":
    st.error("کلید API خالی یا نامعتبر است.")
    st.stop()

# RTL styling for UI
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

st.title("📄 PDF Translator (Page by Page)")
uploaded_file = st.file_uploader("Upload your PDF file:", type="pdf")
bt = st.button("📌 Start Translation")

def translate_page(text):
    url = base_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key  # بدون Bearer
    }
    data = {
        "messages": [
            {"role": "system", "content": "Translate the text into fluent Persian"},
            {"role": "user", "content": text}
        ],
        "model": "gpt-3.5-turbo-0125",  # مطابق cURL
        "stream": False,
        "temperature": 0
    }
    st.write("Request data:", data)  # دیباگ
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        st.write("Response:", result)  # دیباگ
        translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "⚠ Error retrieving translation.")
    except requests.exceptions.RequestException as e:
        translated_text = f"⚠ خطای سرور: {str(e)} - کد وضعیت: {e.response.status_code if e.response else 'پاسخی دریافت نشد'}"
        if e.response:
            st.write("جزئیات پاسخ سرور:", e.response.text)
        else:
            st.write("هیچ پاسخی از سرور دریافت نشد.")
    return translated_text

if uploaded_file and bt:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_document:
        total_pages = len(pdf_document)
        translated_pages = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for page_num in range(total_pages):
            status_text.text(f"در حال پردازش صفحه {page_num + 1} از {total_pages}...")
            page = pdf_document[page_num]
            text = page.get_text("text").strip()
            if not text:
                translated_text = "⚠ این صفحه خالی است."
            else:
                translated_text = translate_page(text)
            translated_pages.append(f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}")
            
            with st.expander(f"📜 صفحه {page_num + 1}"):
                st.text_area(f"🔍 متن اصلی (صفحه {page_num + 1})", text, height=150, key=f"original_{page_num}")
                st.text_area(f"✅ ترجمه (صفحه {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
            
            progress_bar.progress((page_num + 1) / total_pages)

        status_text.text("ترجمه تکمیل شد!")
        if translated_pages:
            final_translation = "\n\n".join(translated_pages)
            st.download_button(
                label="📥 دانلود ترجمه کامل",
                data=BytesIO(final_translation.encode("utf-8")),
                file_name="translated.txt",
                mime="text/plain"
            )
