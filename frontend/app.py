import streamlit as st
import os
import requests

# ---------------------------------------------------------------------------
# Page config & Custom CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ENISO Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp > header { background: transparent; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    section[data-testid="stSidebar"] .stMarkdown { color: #e0e0e0; }
    .category-btn {
        display: inline-block; padding: 6px 14px; margin: 3px; border-radius: 20px;
        background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3);
        font-size: 0.85rem; cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BACKEND_API_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.session_state.token = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------------------------------------------------------------------
# Authentication Functions
# ---------------------------------------------------------------------------
def login(username, password):
    try:
        response = requests.post(f"{BACKEND_API_URL}/api/auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            fetch_user_info()
            st.rerun()
        else:
            try:
                err_msg = response.json().get('detail', 'Unknown error')
            except:
                err_msg = response.text
            st.error(f"Login failed: {err_msg}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

def register(username, password):
    try:
        response = requests.post(f"{BACKEND_API_URL}/api/auth/register", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Registration successful! Logging in...")
            st.session_state.token = response.json()["access_token"]
            fetch_user_info()
            st.rerun()
        else:
            try:
                err_msg = response.json().get('detail', 'Unknown error')
            except:
                err_msg = response.text
            st.error(f"Registration failed: {err_msg}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

def fetch_user_info():
    if not st.session_state.token:
        return
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        response = requests.get(f"{BACKEND_API_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.session_state.username = data["username"]
            st.session_state.is_admin = data["is_admin"]
    except Exception as e:
        pass

def logout():
    st.session_state.token = None
    st.session_state.is_admin = False
    st.session_state.username = None
    st.session_state.messages = []
    st.rerun()

# ---------------------------------------------------------------------------
# App Logic
# ---------------------------------------------------------------------------
if not st.session_state.token:
    st.markdown("<h1 style='text-align: center;'>🎓 ENISO Assistant Login</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            l_username = st.text_input("Username")
            l_password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                login(l_username, l_password)
                
    with tab2:
        with st.form("register_form"):
            r_username = st.text_input("New Username")
            r_password = st.text_input("New Password", type="password")
            if st.form_submit_button("Register", use_container_width=True):
                register(r_username, r_password)
                
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.username}")
    if st.session_state.is_admin:
        st.markdown("<span style='color: #ef4444; font-weight: bold;'>Admin User</span>", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        
    st.markdown("---")
    
    if st.session_state.is_admin:
        st.markdown("### 📤 Upload Knowledge (Admin)")
        uploaded_files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
        if uploaded_files and st.button("Process Document(s)", use_container_width=True):
            with st.spinner("Processing & embedding document(s)..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    files_payload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                    response = requests.post(f"{BACKEND_API_URL}/api/upload", headers=headers, files=files_payload)
                    if response.status_code == 200:
                        st.success(f"Success! Embedded {response.json()['chunks_added']} chunks.")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
        st.markdown("---")
    
    st.markdown("### 🏷️ Quick Questions")
    quick_questions = {
        "📅 Emploi du Temps": "Quel est l'emploi du temps du groupe G1 ?",
        "📝 Examens": "Quelles sont les dates des examens DS ?",
        "🏢 Stages": "Comment faire un stage d'été ?",
        "🎓 PFE": "Quels sont les sujets PFE disponibles ?",
        "📋 Inscription": "Quelles sont les procédures d'inscription ?",
    }
    
    for label, question in quick_questions.items():
        if st.button(label, use_container_width=True):
            st.session_state["prefill_question"] = question
            
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown(
        "<small style='color: #666'>Powered by OpenRouter API<br>"
        "Model: Qwen 2.5 72B Instruct</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main Chat Interface
# ---------------------------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0;'>🎓 ENISO Assistant</h1>
    """,
    unsafe_allow_html=True,
)

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill_question", None)
user_input = st.chat_input("Ask about ENISO...")

if prefill and not user_input:
    user_input = prefill

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Generating response via OpenRouter..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(f"{BACKEND_API_URL}/api/chat", json={"message": user_input}, headers=headers)
                if response.status_code == 200:
                    full_response = response.json().get("response", "")
                    st.markdown(full_response)
                    st.session_state["messages"].append({"role": "assistant", "content": full_response})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
