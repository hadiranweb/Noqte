import streamlit as st
from huggingface_hub import InferenceClient
from io import BytesIO
import fitz  # PyMuPDF
import os

# API configuration
api_key = os.getenv("HF_API_KEY")
client = InferenceClient(
    provider="sambanova",
    api_key=api_key,
)

# Debug: Check API key
st.write("API Key in use:", api_key)
if not api_key or api_key.strip() == "":
    st.error("کلید API خالی یا نامعتبر است. لطفاً HF_API_KEY را در Secrets تنظیم کنید.")
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

st.title("📄 PDF Translator (Page by Page) by HadiranWeb")
uploaded_file = st.file_uploader("فایل پی‌دی‌اف خودتون رو آپلود کنید:", type="pdf")
bt = st.button("📌 شروع ترجمه دقیق")

def translate_page(text):
    try:
        st.write("Sending request with text:", text[:50] + "..." if len(text) > 50 else text)  # دیباگ
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            messages=[
                {"role": "system", "content": "Translate the text into fluent Persian"},
                {"role": "user", "content": text}
            ],
            max_tokens=1000,  # برای متن‌های طولانی‌تر
        )
        st.write("Response received.")  # دیباگ
        translated_text = completion.choices[0].message.content
    except Exception as e:
        translated_text = f"⚠ خطا در ترجمه: {str(e)}"
        st.write("خطا:", str(e))
    return translated_text

if uploaded_file and bt:
    try:
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
    except Exception as e:
        st.error(f"خطا در پردازش PDF: {str(e)}")
