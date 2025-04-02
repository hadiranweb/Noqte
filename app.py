import streamlit as st
from io import BytesIO
import fitz  # PyMuPDF
from openai import OpenAI
import requests
import json
import os
from dotenv import load_dotenv

with open("static/style.css", "r") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_dotenv()

api_key = os.getenv("METIS_API_KEY")
base_url = os.getenv("METIS_BASE_URL")
st.write("API Key in use:", api_key)

def translate(text):
    if not api_key or api_key.strip() == "":
        st.error("کلید API خالی یا نامعتبر است.")
        return "خطای کلید API"
    if not base_url:
        st.error("آدرس پایه API مشخص نشده")
        return "خطای آدرس API"

    url = f"{base_url}/api/v1/wrapper/openai_chat_completion/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Translate the text into fluent Persian"},
            {"role": "user", "content": text}
        ],
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "⚠ Error retrieving translation.")
    except requests.exceptions.RequestException as e:
        translated_text = f"⚠ خطای سرور: {str(e)} - کد وضعیت: {e.response.status_code if e.response else 'پاسخی دریافت نشد'}"
        if e.response:
            st.write("جزئیات پاسخ سرور:", e.response.text)
        else:
            st.write("هیچ پاسخی از سرور دریافت نشد.")
    return translated_text

st.title("📄 PDF Translator (Page by Page)")
uploaded_file = st.file_uploader("Upload your PDF file:", type="pdf")
bt = st.button("📌 Start Translation")

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
                translated_text = translate(text)
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
