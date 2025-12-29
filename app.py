import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont # חשוב לייבא את ImageFont
from deep_translator import GoogleTranslator
import easyocr

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
    
    # טעינת הפונט שהעלית - וודא שהשם כאן זהה בדיוק לשם הקובץ ב-GitHub!
    try:
        # אם קראת לקובץ בשם אחר (למשל font.otf), שנה כאן
        font = ImageFont.truetype("font.ttf", 20) 
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x, y = int(top_left[0]), int(top_left[1])
            w, h = int(bottom_right[0] - x), int(bottom_right[1] - y)
            
            # ניקוי הבועה (צביעה בלבן)
            draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill="white")
            
            try:
                translated = translator.translate(text)
                # תיקון היפוך לעברית (חשוב!)
                display_text = translated[::-1] 
                # כתיבת הטקסט עם הפונט החדש
                draw.text((x + w//2, y + h//2), display_text, fill="black", font=font, anchor="mm")
            except:
                pass

    return pil_img

st.title("🎨 מתרגם קומיקס")
file = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("הבינה המלאכותית קוראת ומתרגמת..."):
            result = process_comic(file.read())
            st.image(result, use_container_width=True)
