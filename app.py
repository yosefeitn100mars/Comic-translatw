import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import textwrap

st.set_page_config(page_title="Comic Translator Pro")

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
    
    try:
        font_path = "font.otf" 
        # פונט בסיסי לחישובים
        base_font = ImageFont.truetype(font_path, 16)
    except:
        base_font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x, y = int(top_left[0]), int(top_left[1])
            w, h = int(bottom_right[0] - x), int(bottom_right[1] - y)
            
            # ניקוי הבועה
            draw.rectangle([x, y, x+w, y+h], fill="white")
            
            try:
                translated = translator.translate(text)
                
                # שבירת שורות אוטומטית לפי רוחב הבועה
                # נחשב כמה תווים נכנסים ברוחב (בערך)
                chars_per_line = max(1, w // 8) 
                lines = textwrap.wrap(translated, width=chars_per_line)
                
                # היפוך כל שורה בנפרד וחיבורן מחדש עם ירידת שורה
                display_text = "\n".join([line[::-1] for line in lines])
                
                # התאמת גודל הפונט לכמות הטקסט
                current_font_size = 18
                if len(lines) > 2: current_font_size = 14
                font = ImageFont.truetype(font_path, current_font_size)
                
                # ציור הטקסט במרכז הבועה
                draw.multiline_text((x + w//2, y + h//2), display_text, fill="black", 
                                  font=font, anchor="mm", align="center")
            except:
                pass

    return pil_img

st.title("🎨 מתרגם קומיקס מקצועי")
file = st.file_uploader("העלה עמוד קומיקס", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנתח טקסט ומסדר שורות..."):
            res = process_comic(file.read())
            st.image(res, use_container_width=True)
