import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor de Voz 🎤🌍", layout="centered", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
        body {
            background-color: #f7f9fb;
        }
        h1, h2, h3, h4 {
            text-align: center;
            color: #222831;
            font-family: 'Poppins', sans-serif;
        }
        .stButton>button {
            background-color: #00adb5;
            color: white;
            border: none;
            padding: 0.8em 1.5em;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #007b83;
            transform: scale(1.05);
        }
        .stSelectbox label, .stTextInput label, .stCheckbox label {
            color: #393e46;
            font-weight: 600;
        }
        .result-box {
            background-color: #e3fdfd;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #00adb5;
        }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.title("🎧 Traductor de Voz Inteligente")
st.markdown("""
Habla y deja que la IA traduzca tu voz a otro idioma 🌍.  
Presiona el botón de **Escuchar**, di tu frase, y luego elige cómo y a qué idioma quieres traducirla.
""")

# --- IMAGEN PRINCIPAL ---
try:
    image = Image.open('ebbacd691475f0a6f7d43d7be15472aa.jpg')
    st.image(image, width=280)
except:
    st.warning("No se pudo cargar la imagen de encabezado.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("ℹ️ Instrucciones")
    st.write("""
    1️⃣ Presiona **Escuchar 🎤** y di la frase que deseas traducir.  
    2️⃣ Selecciona los idiomas de entrada y salida.  
    3️⃣ Elige el acento del audio final.  
    4️⃣ Presiona **Convertir** y escucha tu traducción 🔊.
    """)

# --- BOTÓN DE ESCUCHAR ---
st.subheader("Presiona el botón y habla lo que deseas traducir:")

stt_button = Button(label="🎙️ Escuchar", width=300, height=60)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# --- PROCESAMIENTO DE VOZ ---
if result and "GET_TEXT" in result:
    st.markdown("### 🗣️ Texto Detectado:")
    st.markdown(f"<div class='result-box'>{result.get('GET_TEXT')}</div>", unsafe_allow_html=True)

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    st.markdown("### 🌐 Configuración de Idiomas")
    in_lang = st.selectbox("Selecciona el idioma de entrada:", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Selecciona el idioma de salida:", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))

    lang_codes = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }
    input_language = lang_codes[in_lang]
    output_language = lang_codes[out_lang]

    st.markdown("### 🎧 Acento del audio")
    english_accent = st.selectbox("Selecciona el acento:", (
        "Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"
    ))

    accent_tlds = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    tld = accent_tlds[english_accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        file_name = text[:20] if text else "audio"
        tts.save(f"temp/{file_name}.mp3")
        return file_name, trans_text

    display_output_text = st.checkbox("📖 Mostrar texto traducido")

    if st.button("🔊 Convertir"):
        with st.spinner("Generando audio..."):
            result_name, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result_name}.mp3", "rb")
            st.markdown("### 🎶 Tu audio está listo:")
            st.audio(audio_file.read(), format="audio/mp3")

            if display_output_text:
                st.markdown("### ✏️ Traducción generada:")
                st.markdown(f"<div class='result-box'>{output_text}</div>", unsafe_allow_html=True)

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        now = time.time()
        for f in mp3_files:
            if os.stat(f).st_mtime < now - (n * 86400):
                os.remove(f)

    remove_files(7)

    


