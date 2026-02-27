import os
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
# In Docker: BACKEND_URL=http://backend:8000 (set in docker-compose)
# Locally:   falls back to localhost
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Titanic Chat Agent",
    page_icon="🚢",
    layout="centered",
)

# ─────────────────────────────────────────────
# Custom CSS — Premium dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e2e8f0;
}

/* Hide Streamlit default header */
header[data-testid="stHeader"] { display: none; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.20));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 18px;
    padding: 2rem 2.5rem 1.5rem;
    text-align: center;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(12px);
}
.hero h1 { font-size: 2.2rem; font-weight: 700; color: #e0e7ff; margin: 0 0 0.3rem; }
.hero p  { color: #a5b4fc; font-size: 0.95rem; margin: 0; }

/* ── Chat bubbles ── */
.bubble-user {
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: #fff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 82%;
    margin-left: auto;
    margin-bottom: 0.6rem;
    font-size: 0.92rem;
    box-shadow: 0 4px 18px rgba(99,102,241,0.4);
    animation: slideRight 0.25s ease;
}
.bubble-agent {
    background: rgba(30, 27, 60, 0.85);
    border: 1px solid rgba(99,102,241,0.3);
    color: #c7d2fe;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 82%;
    margin-right: auto;
    margin-bottom: 0.6rem;
    font-size: 0.92rem;
    backdrop-filter: blur(8px);
    animation: slideLeft 0.25s ease;
}
.bubble-error {
    background: rgba(127,29,29,0.4);
    border: 1px solid rgba(239,68,68,0.4);
    color: #fca5a5;
    padding: 0.75rem 1.1rem;
    border-radius: 12px;
    max-width: 82%;
    font-size: 0.88rem;
    margin-bottom: 0.6rem;
}
.label-user  { text-align: right; font-size: 0.72rem; color: #818cf8; margin-bottom: 2px; }
.label-agent { text-align: left;  font-size: 0.72rem; color: #6366f1; margin-bottom: 2px; }

/* ── Chart frame ── */
.chart-frame {
    background: rgba(15,12,41,0.7);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 14px;
    padding: 1rem;
    margin-top: 0.5rem;
    text-align: center;
}
.chart-badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 1.2rem;
    flex-wrap: wrap;
}
.stat-pill {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 30px;
    padding: 0.4rem 1rem;
    font-size: 0.78rem;
    color: #a5b4fc;
}

/* ── Divider ── */
.divider { border-top: 1px solid rgba(99,102,241,0.15); margin: 1rem 0; }

/* ── Suggestion chips ── */
.chip-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.chip {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 30px;
    padding: 0.3rem 0.85rem;
    font-size: 0.78rem;
    color: #c7d2fe;
    cursor: pointer;
}

/* ── Input area override ── */
.stTextArea textarea {
    background: rgba(15,12,41,0.9) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Animations ── */
@keyframes slideRight { from { opacity:0; transform: translateX(20px); } to { opacity:1; transform: translateX(0); } }
@keyframes slideLeft  { from { opacity:0; transform: translateX(-20px); } to { opacity:1; transform: translateX(0); } }

/* ── Scrollable chat area ── */
.chat-scroll { max-height: 55vh; overflow-y: auto; padding-right: 0.5rem; }
.chat-scroll::-webkit-scrollbar { width: 5px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # list of dicts: role, content, chart, chart_type
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "charts_generated" not in st.session_state:
    st.session_state.charts_generated = 0


# ─────────────────────────────────────────────
# Helper: call backend
# ─────────────────────────────────────────────
def query_agent(question: str) -> dict:
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": question},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The agent is taking too long — try a simpler question."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def decode_chart(b64_str: str) -> Image.Image | None:
    try:
        img_bytes = base64.b64decode(b64_str)
        return Image.open(BytesIO(img_bytes))
    except Exception:
        return None


def backend_healthy() -> bool:
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────
# Render hero
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🚢 Titanic Chat Agent</h1>
  <p>Ask natural language questions about the Titanic dataset — powered by <b>Groq × Llama 3.3-70b</b></p>
</div>
""", unsafe_allow_html=True)

# ── Status & stats ──
col_status, col_q, col_c = st.columns([2, 1.2, 1.2])
with col_status:
    if backend_healthy():
        st.success("🟢  Backend Online", icon=None)
    else:
        st.error("🔴  Backend Offline — start the FastAPI server on port 8000")

with col_q:
    st.markdown(f"""<div class="stat-pill">💬 Queries: <b>{st.session_state.total_queries}</b></div>""", unsafe_allow_html=True)
with col_c:
    st.markdown(f"""<div class="stat-pill">📊 Charts: <b>{st.session_state.charts_generated}</b></div>""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Suggestion chips
# ─────────────────────────────────────────────
SUGGESTIONS = [
    "What was the overall survival rate?",
    "Show a distribution of passenger ages",
    "Which class had the highest survival rate?",
    "Compare male vs female survival",
    "Plot fare distribution by class",
    "How many children (under 12) were aboard?",
]

st.markdown("**💡 Try asking:**")
chip_cols = st.columns(3)
selected_suggestion = None
for i, s in enumerate(SUGGESTIONS):
    with chip_cols[i % 3]:
        if st.button(s, key=f"chip_{i}", use_container_width=True):
            selected_suggestion = s

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chat history
# ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="label-user">You</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="label-agent">🤖 Titanic Agent</div>', unsafe_allow_html=True)
            if "error" in msg:
                st.markdown(f'<div class="bubble-error">⚠️ {msg["error"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-agent">{msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("chart"):
                    img = decode_chart(msg["chart"])
                    if img:
                        chart_type = msg.get("chart_type", "chart")
                        st.markdown(f"""
                        <div class="chart-frame">
                            <div class="chart-badge">📊 {chart_type}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.image(img, use_container_width=True)


# ─────────────────────────────────────────────
# Input area
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        label="Your question",
        placeholder="e.g. What percentage of female passengers survived?",
        label_visibility="collapsed",
        height=80,
    )
    col_send, col_clear = st.columns([5, 1])
    with col_send:
        send_btn = st.form_submit_button("✈️ Ask Agent", use_container_width=True, type="primary")
    with col_clear:
        clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

# Handle chip selection (pre-fill acts as a question)
final_question = None
if selected_suggestion:
    final_question = selected_suggestion
elif send_btn and user_input.strip():
    final_question = user_input.strip()

if clear_btn:
    st.session_state.messages = []
    st.session_state.total_queries = 0
    st.session_state.charts_generated = 0
    st.rerun()

# ─────────────────────────────────────────────
# Send to agent
# ─────────────────────────────────────────────
if final_question:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": final_question})
    st.session_state.total_queries += 1

    with st.spinner("🤖 Thinking..."):
        result = query_agent(final_question)

    if "error" in result:
        st.session_state.messages.append({"role": "agent", "error": result["error"]})
    else:
        agent_msg = {
            "role": "agent",
            "content": result.get("answer", "No answer returned."),
            "chart": result.get("chart"),
            "chart_type": result.get("chart_type"),
        }
        if result.get("chart"):
            st.session_state.charts_generated += 1
        st.session_state.messages.append(agent_msg)

    st.rerun()

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color: rgba(165,180,252,0.5); font-size:0.75rem;">
  Titanic Chat Agent • FastAPI + LangGraph + Groq • 
  <a href="http://localhost:8000/docs" target="_blank" style="color:#6366f1;">API Docs (Scalar)</a>
</div>
""", unsafe_allow_html=True)
