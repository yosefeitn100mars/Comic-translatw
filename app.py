import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import requests
import os

st.set_page_config(page_title="Comic Translator Debug")

# --- שלב 1: הורדת פונט חד פעמית ואמינה ---
@st.cache_resource
def get_font_path():
    font_path = "heebo_bold.ttf"
    # בודק אם הפונט קיים ואם הוא לא קובץ ריק (גדול מ-0)
    if not os.path.exists(font_path) or os.path.getsize(font_path) == 0:
        st.info("מוריד פונט עברית בפעם הראשונה...")
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/heebo/Heebo-Bold.ttf"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(font_path, 'wb') as f:
                    f.write(r.content)
                st.success("פונט ירד בהצלחה!")
            else:
                st.error(f"שגיאה בהורדת פונט: {r.status_code}")
                return None
        except Exception as e:
            st.error(f"נכשל בהורדת פונט: {e}")
            return None
    return font_path

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

def fix_hebrew(text):
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

def process_image(file):
    reader = load_ocr()
    translator = GoogleTranslator(source='en', target='iw')
    
    # טעינת הפונט מראש
    font_path = get_font_path()
    if font_path is None:
        st.error("עוצר: אין פונט עברית תקין במערכת.")
        return None

    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    results = reader.readtext(img)

    for (bbox, text, prob) in results:
        if prob > 0.15:
            tl, tr, br, bl = bbox
            x_min = int(min(tl[0], bl[0]))
            y_min = int(min(tl[1], tr[1]))
            x_max = int(max(br[0], tr[0]))
            y_max = int(max(br[1], bl[1]))
            
            # מחיקה
            pad = 5
            draw.rectangle([x_min-pad, y_min-pad, x_max+pad, y_max+pad], fill="white", outline="white")
            
            # --- שלב הכתיבה בלי החבאת שגיאות ---
            try:
                translated = translator.translate(text)
                final_text = fix_hebrew(translated)
                
                # חישוב גודל
                box_height = y_max - y_min
                font_size = int(box_height * 0.6)
                font_size = max(14, min(font_size, 40)) # מינימום 14
                
                font = ImageFont.truetype(font_path, font_size)
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                # כתיבה
                draw.text((center_x, center_y), final_text, fill="black", font=font, anchor="mm")
                
            except Exception as e:
                # אם יש שגיאה - נכתוב אותה ללוג בצד ימיו
                print(f"Error on text '{text}': {e}")
                # וננסה לכתוב "ERROR" באדום בתוך הבועה כדי שנראה שזה נכשל
                try:
                     draw.text((x_min, y_min), "Error", fill="red")
                except:
                    pass
                continue
                
    return pil_img

st.title("מתרגם קומיקס - דיבאג")
uploaded = st.file_uploader("תעלה תמונה", type=['png', 'jpg', 'jpeg'])

if uploaded:
    if st.button("תרגם"):
        with st.spinner("מעבד..."):
            uploaded.seek(0)
            res = process_image(uploaded)
            if res:
                st.image(res, use_container_width=True)
