import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pillow_hebrew import prepare_text
from deep_translator import GoogleTranslator
import easyocr
import requests
import os

# פונקציה להורדת פונט עברי - בלי זה יהיו ריבועים
def get_font(size):
    font_path = "Assistant-Bold.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/assistant/Assistant%5Bwght%5D.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)
    return ImageFont.truetype(font_path, size)

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def process_image(file):
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    results = reader.readtext(img)

    for (bbox, text, prob) in results:
        if prob > 0.15:
            tl, tr, br, bl = bbox
            x_min, y_min = int(min(tl[0], bl[0])), int(min(tl[1], tr[1]))
            x_max, y_max = int(max(br[0], tr[0])), int(max(br[1], bl[1]))
            
            # מחיקה לבנה חלקה
            draw.rectangle([x_min-3, y_min-3, x_max+3, y_max+3], fill="white")
            
            try:
                # תרגום
                translated = translator.translate(text)
                
                # הקסם: הכנת הטקסט לעברית (מטפל בהיפוך ובסידור)
                final_text = prepare_text(translated)
                
                # גודל פונט יחסי לבועה
                h = y_max - y_min
                font = get_font(max(12, int(h * 0.6)))
                
                # כתיבה במרכז הבועה
                cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
                draw.text((cx, cy), final_text, fill="black", font=font, anchor="mm", align="center")
            except:
                continue
                
    return pil_img

st.title("מתרגם קומיקס - הניסיון שיעבוד")
uploaded = st.file_uploader("תעלה את התמונה", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם"):
        with st.spinner("מנקה את הריבועים וכותב עברית..."):
            uploaded.seek(0)
            res = process_image(uploaded)
            st.image(res, use_container_width=True)

                    
