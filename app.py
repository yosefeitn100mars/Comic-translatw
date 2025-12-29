import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_title="Comic Translator Pro")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_hebrew(text):
    # סידור משפט מימין לשמאל
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

def process_image(file):
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    
    # טעינת התמונה
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
            w, h = x_max - x_min, y_max - y_min

            # 1. מחיקה חזקה - מלבן לבן אטום עם שוליים
            draw.rectangle([x_min-3, y_min-3, x_max+3, y_max+3], fill="white")
            
            try:
                translated = translator.translate(text)
                display_text = fix_hebrew(translated)
                
                # 2. התאמת גודל פונט אוטומטית לבועה
                font_size = max(10, min(16, int(h * 0.8))) 
                try:
                    font = ImageFont.truetype("font.ttf", font_size)
                except:
                    font = ImageFont.load_default()

                # 3. כתיבה במרכז המדויק
                draw.text((x_min + w/2, y_min + h/2), display_text, 
                          fill="black", font=font, anchor="mm")
            except:
                continue
                
    return pil_img

st.title("מתרגם קומיקס - שלב סופי")
uploaded = st.file_uploader("העלה תמונה", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנקה ומסדר..."):
            uploaded.seek(0)
            res = process_image(uploaded)
            st.image(res, use_container_width=True)
