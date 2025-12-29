import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import io

# הגדרות דף
st.set_page_config(page_title="Comic Translator AI", layout="wide")

def process_comic(image_bytes):
    # טעינת התמונה
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. זיהוי בועות
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 2. מציאת קווי מתאר
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # מנוע התרגום החדש
    translator = GoogleTranslator(source='en', target='iw')
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            draw.rectangle([x, y, x+w, y+h], fill="white")
            
            # תרגום טקסט לדוגמה (עד שנוסיף OCR מלא)
            try:
                translated_text = translator.translate("Hello") 
                draw.text((x, y + h/2), translated_text, fill="black")
            except:
                pass

    return pil_img

# ממשק המשתמש
st.title("🎨 מתרגם הקומיקס שלי")

uploaded_file = st.file_uploader("העלה עמוד קומיקס", type=["jpg", "jpeg", "png"])

if uploaded_file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מעבד..."):
            result_img = process_comic(uploaded_file.read())
            st.image(result_img, use_container_width=True)
