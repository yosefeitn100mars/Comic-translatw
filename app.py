import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import re

st.set_page_config(page_title="Comic Translator Pro")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

def clean_hebrew_text(text):
    # פונקציה לניקוי תווים שגורמים לריבועים
    # משאירה רק אותיות עבריות, מספרים וסימני פיסוק בסיסיים
    cleaned = re.sub(r'[^א-ת0-9\s.,!?!\-]', '', text)
    return cleaned

def process_comic(image_bytes):
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = reader.readtext(img)
    
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    try:
        # טעינת הפונט שלך
        font = ImageFont.truetype("font.ttf", 17)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y
            
            # 1. מחיקת האנגלית - הגדלנו מעט את הריבוע הלבן כדי שלא יישאר זכר למקור
            draw.rectangle([x-5, y-5, x+w+5, y+h+5], fill="white")
            
            try:
                # 2. תרגום וניקוי
                translated = translator.translate(text)
                cleaned = clean_hebrew_text(translated)
                
                # 3. חלוקה לשורות אם הטקסט ארוך
                if len(cleaned) > 12:
                    words = cleaned.split()
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])[::-1]
                    line2 = " ".join(words[mid:])[::-1]
                    display_text = line1 + "\n" + line2
                else:
                    display_text = cleaned[::-1]
                
                # 4. כתיבה במרכז הבועה
                draw.multiline_text((x + w/2, y + h/2), display_text, 
                                  fill="black", font=font, anchor="mm", 
                                  align="center", spacing=4)
            except:
                pass
    return pil_img

st.title("מתרגם קומיקס - גרסה יציבה")
file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנקה ריבועים ומתרגם..."):
            file.seek(0)
            res = process_comic(file.read())
            st.image(res, use_container_width=True)
