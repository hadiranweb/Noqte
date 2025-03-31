import streamlit as st
from io import BytesIO
import fitz  # PyMuPDF
import openai
import toml
# دریافت کلید API از secrets
metis_api_key = "qq0H6FxAHnGmFSDu8e9PPFRvC0NsnNS"
if not metis_api_key:
    st.error("API Key یافت نشد. لطفاً آن را در secrets.toml تنظیم کنید.")
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

st.title('pdf مترجم')

uploaded_file = st.file_uploader("فایل PDF خودتون رو آپلود کنید", type="pdf")
bt = st.button('Translate')

if uploaded_file and bt:
    pdfdocument = fitz.open(stream=uploaded_file.read(), filetype='pdf')
    for page_num in range(len(pdfdocument)):
        page = pdfdocument[page_num]
        text = page.get_text('text')

        client = openai.OpenAI(api_key=metis_api_key, base_url="https://api.metisai.ir/openai/v1")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "translate all texts into fluent persian"},
                {"role": "user", "content": text}
            ],
            max_tokens=1000  # تنظیم تعداد توکن‌های مورد نیاز
        )

        if response and hasattr(response, "choices") and response.choices:
            translated_text = response.choices[0].message.content
        else:
            translated_text = "خطایی در دریافت ترجمه رخ داده است."

        st.markdown(translated_text)

        st.download_button(
            label="دانلود ترجمه",
            data=BytesIO(translated_text.encode("utf-8")),
            file_name="translated.txt",
            mime="text/plain"
        )
