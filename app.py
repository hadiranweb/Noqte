import streamlit as st
import requests
import json
from io import BytesIO
import fitz  # PyMuPDF
import time
import os
from dotenv import load_dotenv
import subprocess
import sys

# Load environment variables
load_dotenv()

# Auto-install required libraries
required_libraries = ["streamlit", "requests", "pymupdf", "python-dotenv"]
for library in required_libraries:
    subprocess.check_call([sys.executable, "-m", "pip", "install", library])

# Get API key from environment variables
api_key = os.getenv("METIS_API_KEY")
base_url = "https://api.x.ai/v1/chat/completions"  # Adjusted to match cURL endpoint

if not api_key:
    st.error("API key not found. Please set it in environment variables as 'METIS_API_KEY'.")
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

# File uploader for PDF
uploaded_file = st.file_uploader("Upload your PDF file:", type="pdf")
bt = st.button("📌 Start Translation")

def translate_page(text):
    """Translate text using API, matching the cURL template structure"""
    url = base_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Matches -H "Authorization: Bearer ..."
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "Translate the text into fluent Persian"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "model": "grok-2-latest",  # Matches the cURL model
        "stream": False,           # Matches "stream": false
        "temperature": 0           # Matches "temperature": 0
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "⚠ Error retrieving translation.")
    except requests.exceptions.RequestException as e:
        translated_text = f"⚠ Server connection error: {str(e)}"
    return translated_text

if uploaded_file and bt:
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = len(pdf_document)
    translated_pages = []

    # Progress bar and status
    progress_bar = st.progress(0)
    status_text = st.empty()

    for page_num in range(total_pages):
        status_text.text(f"Processing page {page_num + 1} of {total_pages}...")
        page = pdf_document[page_num]
        text = page.get_text("text").strip()

        if text:  # Process only pages with text
            translated_text = translate_page(text)
            translated_pages.append(f"📄 **Page {page_num + 1}:**\n\n{translated_text}")

            # Display original and translated text
            st.subheader(f"📜 Page {page_num + 1}")
            st.text_area(f"🔍 Original Text (Page {page_num + 1})", text, height=150, key=f"original_{page_num}")
            st.text_area(f"✅ Translation (Page {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
            st.divider()

            # Update progress bar
            progress_bar.progress((page_num + 1) / total_pages)
            time.sleep(2)  # Delay to avoid API overload

    status_text.text("Translation completed!")

    # Download full translation
    if translated_pages:
        final_translation = "\n\n".join(translated_pages)
        st.download_button(
            label="📥 Download Full Translation",
            data=BytesIO(final_translation.encode("utf-8")),
            file_name="translated.txt",
            mime="text/plain"
        )

    pdf_document.close()  # Free memory
