import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_config_title="Comic Fix Pro")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['en'])

def fix_text_direction(text):
    # הופך את סדר המילים כדי שהמשפט יהיה קריא בעברית
    words = text.split()
    return " ".join([w[::-1] for w in words][::-1])

def process_image(img_file):
    reader = get_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    # קריאת התמונה
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # שימוש בפונט ברירת מחדל של המערכת כדי למנוע שגיאות טעינה
    try:
        font = ImageFont.load_default()
    except:
        font = None

    results = reader.readtext(img)

    for (bbox, text, prob) in results:
        if prob > 0.2:
            # הגדרת אזור הבועה
            (tl, tr, br, bl) = bbox
            x_min, y_min = int(tl[0]), int(tl[1])
            x_max, y_max = int(br[0]), int(br[1])
            
            # 1. מחיקה אטומה - מלבן לבן נקי מעל האנגלית
            draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white", outline="white")
            
            try:
                # 2. תרגום וסידור טקסט
                translated = translator.translate(text)
                final_text = fix_text_direction(translated)
                
                # 3. כתיבה
                draw.text(((x_min + x_max)/2, (y_min + y_max)/2), 
                          final_text, fill="black", font=font, anchor="mm")
            except:
                continue
                
    return pil_img

# ממשק משתמש פשוט ומהיר
st.title("מתרגם קומיקס - גרסת הגיבוי")
uploaded_file = st.file_uploader("תעלה תמונה", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מוחק אנגלית וכותב עברית..."):
            result_img = process_image(uploaded_file)
            st.image(result_img, use_container_width=True)
