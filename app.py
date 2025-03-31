import streamlit as st
from io import BytesIO
import fitz # PyMuPDF
import openai

# کلید API خود را اینجا وارد کنید
metis_api_key = 'YOUR_API_KEY'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500&family=Noto+Sans+Arabic:wght@500&display=swap'):
html{direction: rtl}
.st-emotion-cache-1fttcpj , .st-emotion-cache-nwtri{display:none;}
.st-emotion-cache-5rimss p{text-align:right;font-family: 'DM sans', sans-serif;
font-family: 'Noto Sans Arabic', sans-serif;"
}
pre-{text_align:left;}
h1,h2,h3,h4,h5,h6{font-family: 'Noto Sana Arabic', sans-sarif;}
span,p,a,button,ol,li {text-align:right;font-family: 'DM Sans', sans-serif;
font-family: 'Noto Sans Arabic', sans-sarif;
}
</style>
""", unsafe_allow_html=True)

st.title('pdf مترجم')

uploaded_file = st.file_uploader(" فایل PDF خودتون رو آپلود کنید", type="pdf")
bt = st.button('Translate')

if uploaded_file and bt:
    pdfdocument = fitz.open(stream=uploaded_file.read(), filetype='pdf')
    for page_num in range(len(pdfdocument)):
        page = pdfdocument[page_num]
        text = page.get_text('text')
        
        # ایجاد درخواست به OpenAI API
        client = openai.OpenAI(api_key=metis_api_key, base_url="https://api.metisai.ir/openai/v1")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "translate all texts into fluent persian"},
                {"role": "user", "content": text}
            ],
            max_tokens=15000  # تنظیم تعداد توکن‌های مورد نیاز
        )

        translated_text = response['choices'][0]['message']['content']
        st.markdown(translated_text)
        st.download_button("دانلود ترجمه", translated_text, file_name="translated.txt")
