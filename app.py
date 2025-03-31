import streamlit as st
from io import BytesIO
import fitz # PyMuPDF
from openai import OpenAI
from hugginface_hub import InferenceClient
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500&family=Noto+Sans+Arabic:wght@500&display=swap'):
html{direction: rtl}
.st-emotion-cache-1fttcpj , .st-emotion-cache-nwtri{disply:none;}
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

uploaded-file = st.file-uploader(" فایل PDF خودتون رو آپلود کنید", type="pdf")
bt = st.button('Translate')
if uploaded-file and bt:
    pdfdocument = fitz and bt:
    pdfdocument = fitz.open(stream= uploaded_file.read() , filetype='pdf')
    for page_num in range(len(pdfdocument)):
        page = pdfdocument[page-num]
        text = (page.get_text('text')
client = OpenAI(api_key = metis_api_key, base_url="https://api.metisai.ir/openai/v1")
            model = "gpt-4o",
        )
        msg = [
         {
                'role' : 'system',
                'content': 'translate all texts into fluent persian'
         },
         {
                 'role' : 'user'
                 'content': text
         }
        ]
        completion = client.chat.completions.create(
            messages=msg,
        )



  st.markdown(completion.choices[0].massages.content)
translated_text = completion.choices[0].message.content
st.download_button("دانلود ترجمه", translated_text, file_name="translated.txt")
