import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import requests
import os

st.set_page_config(page_title="Comic Translator Final")

# פונקציה להורדת פונט - עם קישור מתוקן ויציב
def get_font(size):
    font_name = "Rubik-Bold.ttf"
    if not os.path.exists(font_name):
        try:
            # קישור מתוקן וישיר לפונט מגוגל
            url = "https://github.com/google/fonts/raw/main/ofl/rubik/Rubik-Bold.ttf"
            r = requests.get(url, timeout=5)
            with open(font_name, 'wb') as f:
                f.write(r.content)
            return ImageFont.truetype(font_name, size)
        except:
            # אם ההורדה נכשלת, מחזיר פונט ברירת מחדל כדי שנראה לפחות משהו
            return ImageFont.load_default()
    return ImageFont.truetype(font_name, size)

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_hebrew(text):
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

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
            # גבולות הבועה
            tl, tr, br, bl = bbox
            x_min = int(min(tl[0], bl[0]))
            y_min = int(min(tl[1], tr[1]))
            x_max = int(max(br[0], tr[0]))
            y_max = int(max(br[1], bl[1]))
            
            # ציור מלבן לבן (כבר עובד מצוין)
            pad = 5
            draw.rectangle([x_min-pad, y_min-pad, x_max+pad, y_max+pad], fill="white", outline="white")
            
            try:
                # תרגום
                translated = translator.translate(text)
                final_text = fix_hebrew(translated)
                
                # חישוב גודל פונט
                box_height = y_max - y_min
                font_size = int(box_height * 0.55)
                font_size = max(14, min(font_size, 30))
                
                # קבלת הפונט (המתוקן)
                font = get_font(font_size)
                
                # כתיבה
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                draw.text((center_x, center_y), final_text, fill="black", font=font, anchor="mm")
            except Exception as e:
                print(f"Error drawing text: {e}")
                continue
                
    return pil_img

st.title("מתרגם קומיקס - הפינאלה")
uploaded = st.file_uploader("תעלה את התמונה", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם"):
        with st.spinner("מבצע קסמים אחרונים..."):
            uploaded.seek(0)
            res = process_image(uploaded)
            st.image(res, use_container_width=True)
