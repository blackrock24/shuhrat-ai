import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

st.set_page_config(page_title="Shuhrat AI", page_icon="💬", layout="centered")

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 480px !important;
    padding: 0.5rem 0.6rem 5rem 0.6rem !important;
    background-color: #EFEAE2;
    background-image: radial-gradient(#d5cec2 0.8px, transparent 0.8px);
    background-size: 16px 16px;
    border-radius: 16px;
    min-height: 92vh;
}
.wa-topbar {
    background-color: #FFFFFF;
    padding: 10px 14px;
    border-radius: 12px 12px 0 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 10px;
}
.wa-left { display: flex; align-items: center; gap: 10px; }
.wa-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white; font-weight: bold; display: flex;
    align-items: center; justify-content: center; font-size: 15px;
}
.wa-name { font-size: 16px; font-weight: 700; color: #111b21; margin: 0; }
.wa-sub { font-size: 11px; color: #00a884; margin: 0; }
.wa-icons { color: #54656f; font-size: 17px; letter-spacing: 8px; }
.wa-today { text-align: center; margin: 8px auto 12px auto; }
.wa-today span {
    background-color: #FFFFFF; color: #54656f;
    font-size: 12px; padding: 4px 12px; border-radius: 8px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.08);
}
.msg-row-user { display: flex; justify-content: flex-end; margin-bottom: 8px; }
.msg-row-bot { display: flex; justify-content: flex-start; margin-bottom: 8px; }
.bubble-user {
    background-color: #D9FDD3; color: #111b21;
    padding: 8px 12px 6px 12px; border-radius: 12px 0 12px 12px;
    max-width: 82%; font-size: 14.5px; line-height: 1.4;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
}
.bubble-bot {
    background-color: #FFFFFF; color: #111b21;
    padding: 8px 12px 6px 12px; border-radius: 0 12px 12px 12px;
    max-width: 85%; font-size: 14.5px; line-height: 1.4;
    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
}
.msg-meta { text-align: right; font-size: 10.5px; color: #667781; margin-top: 3px; }
.ticks { color: #53bdeb; font-weight: bold; }
</style>

<div class="wa-topbar">
    <div class="wa-left">
        <span style="color:#54656f;font-size:18px;">←</span>
        <div class="wa-avatar">007</div>
        <div>
            <p class="wa-name">Shuhrat AI</p>
            <p class="wa-sub">online</p>
        </div>
    </div>
    <div class="wa-icons">📹 📞 ⋮</div>
</div>
<div class="wa-today"><span>Today</span></div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("GEMINI_API_KEY topilmadi! .env faylini tekshiring.")
    st.stop()

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = (
    "Sen Shuhrat akaning shaxsiy, aqlli AI yordamchisi va professional tarjimonisan. "
    "O'zbek, ingliz va rus tillarida ravon javob berasan. Rasm, skrinshot yoki hujjat yuborilsa "
    "batafsil tahlil qil va tarjima qil. Ovozli xabar yuborilsa tushunib aniq javob ber."
)

def ask_gemini(contents):
    models_to_try = ["gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            )
            return response.text
        except Exception:
            time.sleep(1)
            continue
    return "Hozir Google serveri biroz band ekan, Shuhrat aka. 5 soniyadan keyin yana yuboring!"
if "messages" not in st.session_state:
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalomu alaykum, Shuhrat aka! 👋 Shaxsiy AI yordamchingiz tayyor. Matn yozing, rasm 📷 yoki ovozli xabar 🎤 yuboring!", "time": now}
    ]

for msg in st.session_state.messages:
    t = msg.get("time", datetime.now().strftime("%H:%M"))
    safe_text = msg["content"].replace("\n", "<br>")
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-row-user"><div class="bubble-user">{safe_text}<div class="msg-meta">{t} <span class="ticks">✓✓</span></div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-row-bot"><div class="bubble-bot">{safe_text}<div class="msg-meta">{t}</div></div></div>', unsafe_allow_html=True)

col_a, col_b = st.columns([3, 1])
with col_a:
    with st.expander("📎 Rasm 📷 / 🎤 Ovoz"):
        uploaded_file = st.file_uploader("Fayl tanlang", type=["png", "jpg", "jpeg", "webp", "pdf"], label_visibility="collapsed")
        audio_value = st.audio_input("Gapiring", label_visibility="collapsed")
with col_b:
    if st.button("Tozalash"):
        st.session_state.messages = []
        st.rerun()

prompt = st.chat_input("😊 Message...")

if prompt or audio_value or uploaded_file:
    now = datetime.now().strftime("%H:%M")
    user_display = prompt if prompt else ("🎤 Ovozli xabar" if audio_value else f"📷 {uploaded_file.name}")
    st.session_state.messages.append({"role": "user", "content": user_display, "time": now})

    contents = []
    if uploaded_file:
        contents.append(types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type))
    if audio_value:
        contents.append(types.Part.from_bytes(data=audio_value.getvalue(), mime_type="audio/wav"))
    contents.append(prompt if prompt else "Yuborilgan rasm yoki ovozli xabarni tushunib, o'zbek tilida javob ber.")

    with st.spinner("Yozmoqda..."):
        reply = ask_gemini(contents)

    st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now().strftime("%H:%M")})
    st.rerun()