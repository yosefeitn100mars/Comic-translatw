import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import os

st.set_page_config(page_title="Translator")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_text(text):
    # היפוך פשוט ומהיר לעברית
    return text[::-1]

def process():
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    
    # נתיבים סטנדרטיים לפונטים בשרתי Streamlit/Linux
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    
    font_path = None
    for f in possible_fonts:
        if os.path.exists(f):
            font_path = f
            break

    uploaded_file = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file and st.button("Translate"):
        img = Image.open(uploaded_file).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # המרה ל-OpenCV בשביל ה-OCR
        cv_img = np.array(img)
        results = reader.readtext(cv_img)

        for (bbox, text, prob) in results:
            if prob > 0.2:
                # מציאת מיקום
                (tl, tr, br, bl) = bbox
                x_min, y_min = int(tl[0]), int(tl[1])
                x_max, y_max = int(br[0]), int(br[1])
                
                # מחיקה לבנה אטומה - שלא יישאר זכר לאנגלית
                draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")
                
                try:
                    # תרגום
                    translated = translator.translate(text)
                    # היפוך אותיות (בלי לסבך עם מילים)
                    display_text = fix_text(translated)
                    
                    # קביעת פונט - אם לא מצאנו נתיב, נשתמש בברירת מחדל של PIL
                    if font_path:
                        font = ImageFont.truetype(font_path, max(12, int((y_max-y_min)*0.8)))
                    else:
                        font = ImageFont.load_default()
                    
                    # כתיבה
                    draw.text(((x_min+x_max)/2, (y_min+y_max)/2), display_text, fill="black", font=font, anchor="mm")
                except:
                    continue
        
        st.image(img)

st.title("Comic Fix")
process()
