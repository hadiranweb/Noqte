import streamlit as st
from io import BytesIO
import fitz  # PyMuPDF
from openai import OpenAI
import os
from dotenv import load_dotenv
import concurrent.futures

with open("static/style.css", "r") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_dotenv()

# تنظیمات API
metis_api_key = os.getenv("METIS_API_KEY")
base_url = "https://api.metisai.ir/openai/v1"

st.write("API Key in use:", metis_api_key)

def translate(text):
    if not metis_api_key or metis_api_key.strip() == "":
        st.error("کلید API خالی یا نامعتبر است.")
        return "خطای کلید API"
    
    try:
        client = OpenAI(api_key=metis_api_key, base_url=base_url)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Translate the text into fluent Persian"},
                {"role": "user", "content": text}
            ],
            max_tokens=1000
        )
        translated_text = response.choices[0].message.content
    except Exception as e:
        translated_text = f"⚠ خطای سرور: {str(e)}"
        st.error(f"خطا در ارتباط با API: {str(e)}")
    
    return translated_text

def process_page(page_num, page):
    text = page.get_text("text").strip()
    if not text:
        return page_num, "⚠ این صفحه خالی است."
    else:
        translated_text = translate(text)
        return page_num, translated_text

st.title("بدون محدودیت ترجمه کن (صفحه‌به‌صفحه)")
uploaded_file = st.file_uploader("by hadiranweb:", type="pdf")
bt = st.button("آتش;)")

if uploaded_file and bt:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_document:
        total_pages = len(pdf_document)
        translated_pages = [None] * total_pages  # لیست برای ذخیره نتایج به ترتیب
        progress_bar = st.progress(0)
        status_text = st.empty()

        # اگر تعداد صفحات بیشتر از 20 باشد، به‌صورت دسته‌ای پردازش می‌کنیم
        if total_pages > 20:
            batch_size = 20
            for start in range(0, total_pages, batch_size):
                end = min(start + batch_size, total_pages)
                status_text.text(f"در حال پردازش دسته صفحات {start + 1} تا {end} از {total_pages}...")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
                    # ارسال درخواست‌ها به‌صورت موازی برای هر دسته
                    future_to_page = {
                        executor.submit(process_page, page_num, pdf_document[page_num]): page_num
                        for page_num in range(start, end)
                    }
                    
                    # جمع‌آوری نتایج
                    for future in concurrent.futures.as_completed(future_to_page):
                        page_num, translated_text = future.result()
                        translated_pages[page_num] = f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}"
                        
                        with st.expander(f"📜 صفحه {page_num + 1}"):
                            text = pdf_document[page_num].get_text("text").strip()
                            st.text_area(f"🔍 متن اصلی (صفحه {page_num + 1})", text, height=150, key=f"original_{page_num}")
                            st.text_area(f"✅ ترجمه (صفحه {page_num + 1})", translated_text, height=150, key=f"translated_{page_num}")
                
                progress_bar.progress(end / total_pages)
        else:
            # برای کمتر از 20 صفحه، به‌صورت تک‌تک پردازش می‌کنیم
            for page_num in range(total_pages):
                status_text.text(f"در حال پردازش صفحه {page_num + 1} از {total_pages}...")
                page = pdf_document[page_num]
                text = page.get_text("text").strip()
                if not text:
                    translated_text = "⚠ این صفحه خالی است."
                else:
                    translated_text = translate(text)
                translated_pages[page_num] = f"📄 **صفحه {page_num + 1}:**\n\n{translated_text}"
                
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
