import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_title="Final Fix")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

def process_comic(image_bytes):
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = reader.readtext(img)
    
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # השם החדש כדי לעקוף את הזיכרון של המערכת
    try:
        font = ImageFont.truetype("my_new_font_v1.ttf", 15)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.15: # רגישות גבוהה יותר לזיהוי
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w, h = bottom_right[0] - x, bottom_right[1] - y
            
            # מחיקה רחבה מאוד של האנגלית
            draw.rectangle([x-5, y-5, x+w+5, y+h+5], fill="white")
            
            try:
                translated = translator.translate(text)
                # היפוך אותיות ידני לעברית
                display_text = translated[::-1]
                
                # כתיבה במרכז
                draw.text((x + w/2, y + h/2), display_text, fill="black", font=font, anchor="mm")
            except:
                pass
    return pil_img

st.title("מתרגם קומיקס - גרסה סופית")
file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        file.seek(0)
        res = process_comic(file.read())
        st.image(res, use_container_width=True)
