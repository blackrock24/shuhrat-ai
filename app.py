import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
SUPA_URL = os.getenv("SUPABASE_URL", "").strip()
SUPA_KEY = os.getenv("SUPABASE_KEY", "").strip()
FAMILY_PIN = os.getenv("FAMILY_PIN", "0077").strip()

st.set_page_config(page_title="Shuhrat Family AI", page_icon="💬", layout="centered")

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
    background-color: #FFFFFF; padding: 10px 14px; border-radius: 12px 12px 0 0;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #e0e0e0; margin-bottom: 10px;
}
.wa-left { display: flex; align-items: center; gap: 10px; }
.wa-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white; font-weight: bold; display: flex;
    align-items: center; justify-content: center; font-size: 14px;
}
.wa-name { font-size: 16px; font-weight: 700; color: #111b21; margin: 0; }
.wa-sub { font-size: 11px; color: #00a884; margin: 0; }
.call-btn {
    text-decoration: none; background-color: #E7FCE3; color: #008069;
    padding: 6px 10px; border-radius: 20px; font-size: 13px; font-weight: 600;
    border: 1px solid #25D366; margin-left: 6px;
}
.msg-row-me { display: flex; justify-content: flex-end; margin-bottom: 8px; }
.msg-row-other { display: flex; justify-content: flex-start; margin-bottom: 8px; }
.bubble-me {
    background-color: #D9FDD3; color: #111b21;
    padding: 7px 12px 5px 12px; border-radius: 12px 0 12px 12px;
    max-width: 82%; font-size: 14.5px; box-shadow: 0 1px 1px rgba(0,0,0,0.1);
}
.bubble-other {
    background-color: #FFFFFF; color: #111b21;
    padding: 7px 12px 5px 12px; border-radius: 0 12px 12px 12px;
    max-width: 85%; font-size: 14.5px; box-shadow: 0 1px 1px rgba(0,0,0,0.1);
}
.sender-tag { font-size: 11.5px; font-weight: 700; color: #008069; margin-bottom: 2px; }
.msg-meta { text-align: right; font-size: 10px; color: #667781; margin-top: 2px; }
.ticks { color: #53bdeb; font-weight: bold; }
</style>
<div class="wa-topbar">
    <div class="wa-left">
        <div class="wa-avatar">007</div>
        <div>
            <p class="wa-name">Shuhrat Family • AI</p>
            <p class="wa-sub">● Jonli • Oila va AI 🤖</p>
        </div>
    </div>
    <div>
        <a class="call-btn" href="https://jit.si" target="_blank">📞 Audio</a>
        <a class="call-btn" href="https://jit.si" target="_blank">📹 Video</a>
    </div>
</div>
""", unsafe_allow_html=True)

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if not st.session_state.auth_user:
    st.info("🔒 Oila a'zolari uchun yopiq guruh. Kirish uchun PIN-kodni kiriting:")
    who = st.selectbox("Kim kiryapti?", ["Shuhrat aka", "Kelin oyi", "Asadbek"])
    pin = st.text_input("Oila PIN-kodi (4 raqam):", type="password")
    if st.button("Kirish ✅"):
        if pin == FAMILY_PIN:
            st.session_state.auth_user = who
            st.rerun()
        else:
            st.error("PIN-kod noto'g'ri!")
    st.stop()

client = genai.Client(api_key=API_KEY)
supabase = create_client(SUPA_URL, SUPA_KEY)

SYSTEM_PROMPT = (
    "Sen Shuhrat akaning oilaviy guruhidagi aqlli AI yordamchi va tarjimonisan. "
    "Guruhda Shuhrat aka, Kelin oyi va Asadbek bor. Qisqa, samimiy va aniq javob ber."
)

def ask_gemini(contents):
models = ["gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
    for m in models:
        try:
            r = client.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            )
            return r.text
        except Exception:
            time.sleep(1)
    return "Server biroz band, birozdan keyin urinib ko'ring."

st.caption(f"👤 Siz: {st.session_state.auth_user} • Jonli suhbat uchun tepada 📞 Audio yoki 📹 Video ni bosing • AI uchun @ai yozing")

@st.fragment(run_every="3s")
def live_chat_messages():
    rows = supabase.table("family_messages").select("*").order("id", desc=False).limit(60).execute().data
    if not rows:
        st.markdown('<div class="msg-row-other"><div class="bubble-other"><div class="sender-tag">Shuhrat AI 🤖</div>Assalomu alaykum! Oilaviy guruh tayyor. Yangi xabarlar avtomatik 3 soniyada chiqadi!</div></div>', unsafe_allow_html=True)
    for r in rows:
        t = r["created_at"][11:16] if r.get("created_at") else ""
        safe = r["content"].replace("\n", "<br>")
        if r["sender"] == st.session_state.auth_user:
            st.markdown(f'<div class="msg-row-me"><div class="bubble-me">{safe}<div class="msg-meta">{t} <span class="ticks">✓✓</span></div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-row-other"><div class="bubble-other"><div class="sender-tag">{r["sender"]}</div>{safe}<div class="msg-meta">{t}</div></div></div>', unsafe_allow_html=True)

live_chat_messages()

with st.expander("📎 Rasm 📷 / 🎤 Ovoz yuborish"):
    uploaded_file = st.file_uploader("Rasm", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
    audio_value = st.audio_input("Ovoz", label_visibility="collapsed")

prompt = st.chat_input("😊 Xabar yozing (AI uchun @ai qo'shing)...")

if prompt or audio_value or uploaded_file:
    msg_text = prompt if prompt else ("🎤 Ovozli xabar yuborildi" if audio_value else f"📷 Rasm yuborildi: {uploaded_file.name}")
    supabase.table("family_messages").insert({"sender": st.session_state.auth_user, "content": msg_text}).execute()

    if (prompt and "@ai" in prompt.lower()) or audio_value or uploaded_file:
        contents = []
        if uploaded_file:
            contents.append(types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type))
        if audio_value:
            contents.append(types.Part.from_bytes(data=audio_value.getvalue(), mime_type="audio/wav"))
        contents.append(f"{st.session_state.auth_user} yozdi: {prompt if prompt else 'Rasm yoki ovozni tushunib javob ber.'}")
        ai_reply = ask_gemini(contents)
        supabase.table("family_messages").insert({"sender": "Shuhrat AI 🤖", "content": ai_reply}).execute()

    st.rerun()
