import streamlit as st
import google.generativeai as genai
from agent import TOOLS, run_agent

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="✨",
    layout="centered"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4285F4 0%, #34A853 50%, #FBBC05 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    .tool-badge {
        background: #1e2130;
        border: 1px solid #334;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        color: #aab;
        display: inline-block;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown('<h1 class="main-title">✨ Gemini AI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by Gemini 2.0 Flash · Dilengkapi AI Agent Tools</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<span class="tool-badge">🕐 Jam & Tanggal</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="tool-badge">🔢 Kalkulator</span>', unsafe_allow_html=True)
with col3:
    st.markdown('<span class="tool-badge">🌤️ Info Cuaca</span>', unsafe_allow_html=True)

st.divider()

# ─── Inisialisasi Session State ───────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # Untuk ditampilkan di UI

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None  # Objek chat Gemini

# ─── Sidebar: Pengaturan ─────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Pengaturan")

    system_prompt = st.text_area(
        "System Prompt",
        value="""Kamu adalah asisten AI yang ramah dan helpful bernama Gemini.
Kamu bisa berbicara dalam Bahasa Indonesia maupun Inggris.
Gunakan tools yang tersedia ketika diperlukan untuk memberikan informasi yang akurat.
Selalu berikan respons yang jelas, terstruktur, dan mudah dipahami.""",
        height=150
    )

    st.divider()

    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.chat_session = None
        st.rerun()

    st.divider()
    st.caption("💡 Tips: Coba tanya 'jam berapa sekarang?' atau 'hitung 25 * 48' atau 'cuaca Jakarta'")

# ─── Inisialisasi Model & Chat Session ───────────────────────────────────────

def get_chat_session(system_prompt: str):
    """Membuat atau mengambil chat session yang sudah ada."""
    if st.session_state.chat_session is None:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt,
            tools=[TOOLS]
        )
        st.session_state.chat_session = model.start_chat(
            enable_automatic_function_calling=False
        )
    return st.session_state.chat_session

# ─── Tampilkan Riwayat Chat ───────────────────────────────────────────────────

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Input & Proses Pesan ─────────────────────────────────────────────────────

if prompt := st.chat_input("Ketik pesan kamu di sini..."):

    # Tampilkan pesan user
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Proses dengan AI Agent
    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir..."):
            try:
                chat_session = get_chat_session(system_prompt)
                response_text = run_agent(
                    model=None,
                    chat_session=chat_session,
                    user_message=prompt
                )
                st.markdown(response_text)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_text
                })

            except Exception as e:
                if "API_KEY" in str(e) or "credentials" in str(e).lower():
                    st.error("❌ API Key tidak valid. Periksa `.streamlit/secrets.toml`")
                else:
                    st.error(f"❌ Error: {str(e)}")