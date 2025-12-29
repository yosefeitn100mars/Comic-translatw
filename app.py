import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

# הגדרה נכונה כדי שלא יקרוס
st.set_page_config(page_title="Comic Translator Fix")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_hebrew_display(text):
    # הופך את סדר האותיות והמילים כדי שייקרא נכון מימין לשמאל
    words = text.split()
    reversed_words = [w[::-1] for w in words]
    return " ".join(reversed_words[::-1])

def process_comic(file):
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    
    # המרת קובץ לתמונה
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # ניסיון טעינת הפונט שהעלית - אם נכשל, משתמש בברירת מחדל
    try:
        # גודל 14 הוא גודל "בטוח" שלא יחרוג מהבועה
        font = ImageFont.truetype("font.ttf", 14)
    except:
        font = ImageFont.load_default()

    results = reader.readtext(img)

    for (bbox, text, prob) in results:
        if prob > 0.2:
            # זיהוי מיקום הטקסט
            (tl, tr, br, bl) = bbox
            x_min, y_min = int(tl[0]), int(tl[1])
            x_max, y_max = int(br[0]), int(br[1])
            
            # --- התיקון הקריטי ---
            # 1. מחיקה לבנה רחבה מאוד (מכסה את כל האנגלית בלבן אטום)
            draw.rectangle([x_min-5, y_min-5, x_max+5, y_max+5], fill="white", outline="white")
            
            try:
                # 2. תרגום וסידור טקסט
                translated = translator.translate(text)
                clean_text = fix_hebrew_display(translated)
                
                # 3. כתיבה במרכז השטח הלבן
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                draw.text((center_x, center_y), clean_text, fill="black", font=font, anchor="mm")
            except:
                continue
                
    return pil_img

st.title("מתרגם קומיקס - גרסת הברזל")
uploaded = st.file_uploader("העלה דף קומיקס", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנקה ומתרגם..."):
            uploaded.seek(0)
            final_img = process_comic(uploaded)
            st.image(final_img, use_container_width=True)
