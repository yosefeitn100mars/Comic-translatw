import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import requests
import os

# פונקציה שהופכת עברית ומסדרת שורות ידנית
def fix_hebrew_manual(text, max_chars=15):
    if not text: return ""
    # הפיכה בסיסית של כל המשפט
    words = text.split()
    # סידור מילים מימין לשמאל והפיכת אותיות בכל מילה
    fixed_words = [w[::-1] for w in words]
    # חיבור חזרה לשורות
    lines = []
    current_line = []
    current_count = 0
    
    for word in fixed_words:
        if current_count + len(word) > max_chars:
            lines.append(" ".join(current_line[::-1]))
            current_line = [word]
            current_count = len(word)
        else:
            current_line.append(word)
            current_count += len(word) + 1
    lines.append(" ".join(current_line[::-1]))
    return "\n".join(lines)

@st.cache_resource
def get_font():
    font_p = "Assistant-Bold.ttf"
    if not os.path.exists(font_p):
        url = "https://github.com/google/fonts/raw/main/ofl/assistant/Assistant%5Bwght%5D.ttf"
        r = requests.get(url)
        with open(font_p, "wb") as f: f.write(r.content)
    return font_p

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

def process():
    st.title("מתרגם קומיקס - גרסת הניצחון")
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    font_p = get_font()

    up = st.file_uploader("תעלה תמונה", type=['jpg','png','jpeg'])
    if up and st.button("תרגם"):
        img = Image.open(up).convert("RGB")
        draw = ImageDraw.Draw(img)
        cv_img = np.array(img)
        results = reader.readtext(cv_img)

        for (bbox, text, prob) in results:
            if prob > 0.2:
                (tl, tr, br, bl) = bbox
                x_min, y_min = int(tl[0]), int(tl[1])
                x_max, y_max = int(br[0]), int(br[1])
                
                # מחיקה
                draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")
                
                try:
                    # תרגום
                    trans = translator.translate(text)
                    # הפיכה ידנית (בלי ספריות חיצוניות)
                    final_text = fix_hebrew_manual(trans, max_chars=int((x_max-x_min)/10) + 5)
                    
                    font_size = max(12, int((y_max-y_min) / (final_text.count('\n')+1.5)))
                    font = ImageFont.truetype(font_p, font_size)
                    
                    # ציור
                    draw.text(((x_min+x_max)/2, (y_min+y_max)/2), final_text, 
                              fill="black", font=font, anchor="mm", align="center")
                except: continue
        st.image(img)

process()
