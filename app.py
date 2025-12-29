import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

# הגדרות בסיסיות למניעת קריסה
st.set_page_config(page_title="Comic Translator")

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
    
    # טעינת הפונט החדש (Assistant) - הגדרנו גודל קטן למניעת ריבועים
    try:
        font = ImageFont.truetype("font.ttf", 14)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y
            
            # 1. מחיקת האנגלית - מלבן לבן נקי עם שוליים
            draw.rectangle([x-3, y-3, x+w+3, y+h+3], fill="white")
            
            try:
                # 2. תרגום
                translated = translator.translate(text)
                
                # 3. הכנת הטקסט - רק היפוך בסיסי לעברית
                display_text = translated[::-1]
                
                # 4. כתיבה במרכז הבועה
                draw.text((x + w/2, y + h/2), display_text, fill="black", font=font, anchor="mm")
            except:
                pass
    return pil_img

# ממשק משתמש פשוט מאוד
st.title("מתרגם קומיקס")

file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מתרגם..."):
            file.seek(0)
            res = process_comic(file.read())
            st.image(res, use_container_width=True)
