import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_title="Comic Translator Pro")

@st.cache_resource
def load_reader():
    # טעינת המודל לאנגלית
    return easyocr.Reader(['en'])

def reverse_hebrew_logic(text):
    # הופך כל מילה בנפרד ואז את סדר המילים כדי שהמשפט יהיה קריא
    words = text.split()
    reversed_words = [word[::-1] for word in words]
    return " ".join(reversed_words[::-1])

def process_comic(image_bytes):
    reader = load_reader()
    translator = GoogleTranslator(source='en', target='iw')
    
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = reader.readtext(img)
    
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype("font.ttf", 16)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w, h = bottom_right[0] - x, bottom_right[1] - y
            
            # ניקוי הבועה עם מלבן לבן נקי
            draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill="white")
            
            try:
                translated = translator.translate(text)
                
                # סידור המשפט לעברית תקנית
                display_text = reverse_hebrew_logic(translated)
                
                # חלוקה לשורות אם הטקסט ארוך מהבועה
                if len(display_text) > 15:
                    mid = len(display_text) // 2
                    split_idx = display_text.find(' ', mid - 5, mid + 5)
                    if split_idx != -1:
                        display_text = display_text[:split_idx] + "\n" + display_text[split_idx+1:]

                # כתיבה במרכז הבועה
                draw.multiline_text((x + w/2, y + h/2), display_text, 
                                  fill="black", font=font, anchor="mm", 
                                  align="center", spacing=4)
            except:
                pass
    return pil_img

st.title("🎨 מתרגם הקומיקס שלי - מוכן!")
file = st.file_uploader("העלה דף קומיקס", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("יוצר תוצאה מושלמת..."):
            file.seek(0)
            res = process_comic(file.read())
            st.image(res, use_container_width=True)
