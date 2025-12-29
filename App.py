import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
import io

# הגדרות דף
st.set_page_config(page_title="Comic Translator AI", layout="wide")

def process_comic(image_bytes):
    # טעינת התמונה
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. זיהוי בועות (זיהוי צבע לבן)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 2. מציאת קווי מתאר של הבועות
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    translator = Translator()
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # כאן אנחנו מדמים זיהוי טקסט בתוך הבועות שמצאנו
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500: # סינון רעשים קטנים
            x, y, w, h = cv2.boundingRect(cnt)
            
            # ניקוי הבועה (צביעה בלבן)
            draw.rectangle([x, y, x+w, y+h], fill="white")
            
            # דוגמה לתרגום (במציאות כאן נכנס ה-OCR)
            text_hebrew = "תרגום לדוגמה" 
            
            # כתיבת הטקסט בעברית (יישור לימין)
            # הערה: יש צורך בקובץ פונט עברי במחשב כדי שזה יעבוד
            try:
                font = ImageFont.truetype("arial.ttf", 20)
                draw.text((x + w - 10, y + h/2), text_hebrew, fill="black", font=font, anchor="rm")
            except:
                draw.text((x, y), text_hebrew, fill="black")

    return pil_img

# ממשק המשתמש
st.title("🎨 מתרגם קומיקס אוטומטי - מאנגלית לעברית")
st.markdown("העלה עמוד קומיקס וקבל אותו מתורגם עם בועות נקיות")

uploaded_file = st.file_uploader("בחר תמונה (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("מקור")
        st.image(uploaded_file, use_container_width=True)
        
    with col2:
        st.header("תרגום (עיבוד)")
        if st.button("התחל תרגום"):
            with st.spinner("מנתח בועות ומתרגם..."):
                result_img = process_comic(uploaded_file.read())
                st.image(result_img, use_container_width=True)
                
                # כפתור הורדה
                buf = io.BytesIO()
                result_img.save(buf, format="PNG")
                st.download_button("הורד תוצאה", buf.getvalue(), "translated_comic.png")

st.info("כשתפעיל את זה במחשב, נצטרך רק להתקין את הספריות streamlit, opencv-python, pillow ו-googletrans.")
