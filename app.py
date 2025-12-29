import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import io

st.set_page_config(page_title="Comic Translator AI", layout="wide")

def process_comic(image_bytes):
    # טעינת התמונה
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # זיהוי בועות (שטחים לבנים)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 50, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    translator = GoogleTranslator(source='en', target='iw')

    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # 1. מחיקת הטקסט המקורי (צביעה בלבן)
            draw.rectangle([x, y, x+w, y+h], fill="white")
            
            # 2. כאן אנחנו שותלים תרגום (כרגע זה טקסט קבוע, בהמשך נחבר OCR)
            try:
                msg = "בום!" # דוגמה לתרגום
                draw.text((x + w//2, y + h//2), msg, fill="black", anchor="mm")
            except:
                pass

    return pil_img

st.title("🎨 מתרגם הקומיקס שלי")
uploaded_file = st.file_uploader("העלה עמוד קומיקס", type=["jpg", "jpeg", "png"])

if uploaded_file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנתח ומנקה בועות..."):
            result_img = process_comic(uploaded_file.read())
            st.image(result_img, use_container_width=True, caption="התוצאה (בועות מנוקות)")

