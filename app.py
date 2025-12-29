import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
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
    
    # טעינת הפונט - מעודכן ל-font.ttf
    try:
        font_path = "font.ttf" 
        font = ImageFont.truetype(font_path, 18)
    except:
        # אם יש תקלה בטעינה, נשתמש בפונט ברירת מחדל
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            # מיקום הבועה
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y
            
            # 1. ניקוי הטקסט המקורי (מלבן לבן)
            draw.rectangle([x-2, y-2, x+w+2, y+h+2], fill="white")
