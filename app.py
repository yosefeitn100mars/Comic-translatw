import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import textwrap
from bidi.algorithm import get_display
import arabic_reshaper
import requests
import os

st.set_page_config(page_title="Comic Translator Final")

# --- פונקציה להורדת פונט עברי איכותי ---
@st.cache_resource
def get_hebrew_font():
    font_path = "Rubik-Bold.ttf"
    if not os.path.exists(font_path):
        # הורדה ישירה מ-Google Fonts (קישור יציב)
        url = "https://github.com/google/fonts/raw/main/ofl/rubik/Rubik%5Bwght%5D.ttf"
        response = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    return font_path

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_hebrew_layout(text, width=15):
    # שבירת שורות לפי רוחב הבועה
    wrapped = textwrap.fill(text, width=width)
    # תיקון כיווניות (RTL) לכל שורה
    reshaped_lines = [get_display(arabic_reshaper.reshape(line)) for line in wrapped.split('\n')]
    return '\n'.join(reshaped_lines)

def process_image(file):
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    font_p = get_hebrew_font()
    
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
            
            # מחיקה לבנה אטומה
            draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")
            
            try:
                # תרגום
                translated = translator.translate(text)
                
                # חישוב רוחב הבועה להתאמת הטקסט
                box_width = x_max - x_min
                chars_per_line = max(8, int(box_width / 8))
                
                # עיבוד עברית
                final_text = fix_hebrew_layout(translated, width=chars_per_line)
                
                # התאמת גודל פונט
                num_lines = final_text.count('\n') + 1
                font_size = max(10, int((y_max - y_min) / (num_lines * 1.2)))
                font = ImageFont.truetype(font_p, font_size)
                
                # ציור הטקסט במרכז הבועה
                cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
                draw.text((cx, cy), final_text, fill="black", font=font, anchor="mm", align="center")
            except:
                continue
                
    return pil_img

st.title("מתרגם קומיקס - גרסת הברזל")
uploaded = st.file_uploader("תעלה דף קומיקס", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם"):
        with st.spinner("מוריד פונט ומעבד..."):
            uploaded.seek(0)
            res = process_image(uploaded)
            st.image(res, use_container_width=True)

                    
