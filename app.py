import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import os
import requests

st.set_page_config(page_title="Comic Master Pro")

@st.cache_resource
def load_assets():
    # הורדת פונט איכותי (Rubik) - הפעם מקישור יציב של גוגל
    font_path = "Rubik-Bold.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/rubik/Rubik%5Bwght%5D.ttf"
        try:
            r = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except:
            font_path = None
    return easyocr.Reader(['en']), font_path

def fix_he(text):
    # הופך את הטקסט כדי שיוצג נכון מימין לשמאל
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

def process_comic(file):
    reader, font_path = load_assets()
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
            
            # מחיקה לבנה נקייה
            draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")
            
            try:
                # תרגום ועיבוד
                trans = translator.translate(text)
                final_text = fix_he(trans)
                
                # התאמת גודל פונט
                h = y_max - y_min
                size = max(12, int(h * 0.7))
                
                if font_path:
                    font = ImageFont.truetype(font_path, size)
                else:
                    font = ImageFont.load_default()
                
                # כתיבה במרכז הבועה
                cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
                draw.text((cx, cy), final_text, fill="black", font=font, anchor="mm")
            except:
                continue
                
    return pil_img

st.title("מתרגם קומיקס - הגרסה המלוטשת")
f = st.file_uploader("תעלה קומיקס", type=['jpg','png','jpeg'])

if f:
    if st.button("תרגם עכשיו"):
        with st.spinner("יוצר גרסה עברית..."):
            f.seek(0)
            result = process_comic(f)
            st.image(result, use_container_width=True)
