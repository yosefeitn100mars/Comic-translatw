import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
from deep_translator import GoogleTranslator
import easyocr
import io

st.set_page_config(page_title="Comic Translator AI")

# טעינת מנוע הקריאה (זה יקרה רק פעם אחת)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

def process_comic(image_bytes):
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    # המרת התמונה לעיבוד
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # זיהוי טקסט באנגלית בתמונה
    results = reader.readtext(img)
    
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    for (bbox, text, prob) in results:
        if prob > 0.3: # אם הוא בטוח שזה טקסט
            # קואורדינטות הבועה
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x, y = int(top_left[0]), int(top_left[1])
            w, h = int(bottom_right[0] - x), int(bottom_right[1] - y)
            
            # 1. מחיקת הטקסט המקורי (צביעה בלבן)
            draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill="white")
            
            # 2. תרגום הטקסט שנמצא
            try:
                translated = translator.translate(text)
                # כתיבת התרגום (בצורה פשוטה בינתיים)
                draw.text((x, y), translated, fill="black")
            except:
                pass

    return pil_img

st.title("🎨 מתרגם קומיקס חכם")

file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if file:
    img_data = file.read()
    st.image(img_data, caption="מקור", use_container_width=True)
    
    if st.button("תרגם עכשיו"):
        with st.spinner("הבינה המלאכותית קוראת את הקומיקס... זה לוקח דקה..."):
            result = process_comic(img_data)
            st.image(result, caption="התוצאה המתורגמת", use_container_width=True)
