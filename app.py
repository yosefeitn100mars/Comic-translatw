import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import os
import requests

st.set_page_config(page_title="Comic Translator Final")

# פונקציה להורדת פונט אם הוא חסר - זה ימנע את הריבועים לנצח
def get_hebrew_font(size):
    font_path = "font.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/assistant/Assistant%5Bwght%5D.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)
    return ImageFont.truetype(font_path, size)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

def fix_hebrew(text):
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

def process_image(file):
    reader = load_reader()
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
            
            # מחיקה לבנה רחבה
            draw.rectangle([x_min-4, y_min-4, x_max+4, y_max+4], fill="white")
            
            try:
                translated = translator.translate(text)
                display_text = fix_hebrew(translated)
                
                # טעינת פונט בטוחה
                font = get_hebrew_font(size=max(12, int((y_max-y_min)*0.7)))
                
                draw.text(((x_min+x_max)/2, (y_min+y_max)/2), 
                          display_text, fill="black", font=font, anchor="mm")
            except:
                continue
    return pil_img

st.title("מתרגם קומיקס - גרסה ללא ריבועים")
file = st.file_uploader("העלה תמונה", type=['png', 'jpg', 'jpeg'])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מוריד פונט ומעבד..."):
            file.seek(0)
            res = process_image(file)
            st.image(res, use_container_width=True)
