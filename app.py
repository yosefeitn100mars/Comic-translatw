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
    
    # טעינת הפונט - גודל 13 כדי שיהיה קטן ובטוח
    try:
        font = ImageFont.truetype("font.ttf", 13)
    except:
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        if prob > 0.2:
            # זיהוי מיקום וגודל
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y
            
            # 1. מחיקה חזקה - אנחנו יוצרים מלבן לבן קצת יותר גדול מהטקסט
            draw.rectangle([x-4, y-4, x+w+4, y+h+4], fill="white")
            
            try:
                # 2. תרגום
                translated = translator.translate(text)
                
                # 3. טיפול בטקסט ארוך - חלוקה לשורות
                words = translated.split()
                if len(words) > 3:
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])[::-1]
                    line2 = " ".join(words[mid:])[::-1]
                    display_text = line1 + "\n" + line2
                else:
                    display_text = translated[::-1]
                
                # 4. ציור במרכז
                draw.multiline_text((x + w/2, y + h/2), display_text, 
                                  fill="black", font=font, anchor="mm", 
                                  align="center", spacing=2)
            except:
                pass
    return pil_img

st.title("מתרגם קומיקס")
file = st.file_uploader("העלה דף קומיקס", type=["jpg", "png", "jpeg"])

if file:
    if st.button("תרגם עכשיו"):
        with st.spinner("מנקה אנגלית וכותב עברית..."):
            file.seek(0)
            res = process_comic(file.read())
            st.image(res, use_container_width=True)
