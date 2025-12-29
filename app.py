import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr
import textwrap

st.set_page_config(page_title="Comic Translator Pro")

@st.cache_resource
def load_reader():
    # טעינת המודל לאנגלית
    return easyocr.Reader(['en'])

def process_comic(image_bytes):
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    # טעינת התמונה
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # זיהוי טקסט
    results = reader.readtext(img)
    
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # טעינת הפונט - וודא שהסיומת (otf/ttf) מתאימה לקובץ שלך!
    try:
        font_path = "font.ttf" 
        font = ImageFont.truetype(font_path, 18)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            # מיקום הבועה
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y
            
            # 1. מחיקת הטקסט המקורי (מלבן לבן)
            draw.rectangle([x, y, x + w, y + h], fill="white")
            
            try:
                # 2. תרגום
                translated = translator.translate(text)
                
                # 3. חלוקת שורות לפי רוחב הבועה
                # אם הבועה קטנה, נצמצם את כמות התווים בשורה
                width_in_chars = max(1, w // 10)
                wrapped_lines = textwrap.wrap(translated, width=width_in_chars)
                
                # 4. היפוך אותיות עבור עברית (בכל שורה בנפרד)
                display_text = "\n".join([line[::-1] for line in wrapped_lines])
                
                # 5. ציור הטקסט במרכז
                draw.multiline_text((x + w/2, y + h/2), display_text, 
                                  fill="black", font=font, anchor="mm", 
                                  align="center", spacing=4)
            except Exception as e:
                print(f"Translation error: {e}")

    return pil_img

st.title("🎨 מתרגם קומיקס מקצועי")
file = st.file_uploader("העלה עמוד קומיקס", type=["jpg", "png", "jpeg"])

if file:
    # הצגת המקור
    st.image(file, caption="תמונה מקורית", use_container_width=True)
    
    if st.button("תרגם עכשיו"):
        with st.spinner("הבינה המלאכותית מעבדת את הדף..."):
            # חשוב להחזיר את הסמן לתחילת הקובץ
            file.seek(0)
            res = process_comic(file.read())
            st.image(res, caption="התוצאה המתורגמת", use_container_width=True)
