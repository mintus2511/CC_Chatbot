import streamlit as st
import json
import os

# Tạo thư mục nếu chưa có
os.makedirs("data", exist_ok=True)
THEME_FILE = os.path.join("data", "theme_prefs.json")

def apply_theme(user_id: str):
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, "r") as f:
            all_prefs = json.load(f)
    else:
        all_prefs = {}

    if user_id not in all_prefs:
        all_prefs[user_id] = {"dark_mode": False}

    is_dark = all_prefs[user_id]["dark_mode"]

    # === Sidebar: nút chuyển chế độ ===
    with st.sidebar:
        st.markdown("### 🌓 Giao diện")
        label = "🌞 Chế độ Sáng" if is_dark else "🌚 Chế độ Tối"

        st.markdown("""
            <style>
            div[data-testid="stSidebar"] button:hover {
                background-color: #FBAD22 !important;
                color: black !important;
                border: 1px solid white;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button(label):
            is_dark = not is_dark
            all_prefs[user_id]["dark_mode"] = is_dark
            with open(THEME_FILE, "w") as f:
                json.dump(all_prefs, f)
            st.rerun()

    # === CSS style ===
    if not is_dark:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Roboto:wght@400;500&display=swap');
            html, body, .stApp {
                font-family: 'Roboto', sans-serif !important;
                background-color: #ffffff !important;
                color: #222 !important;
            }
            .stApp h1, h2, h3 {
                font-family: 'Merriweather', serif !important;
                color: #111 !important;
            }
            section[data-testid="stSidebar"] {
                background-color: #ffffff !important;
            }
            section[data-testid="stSidebar"] * {
                color: #222 !important;
            }
            div[data-testid="stChatMessageContent"] {
                background-color: #f5f5f5 !important;
                color: #222 !important;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            .stMarkdown div, .stMarkdown section, .stMarkdown p {
                background-color: transparent !important;
                color: #222 !important;
            }
            button {
                background-color: #e1e1de !important;
                color: black !important;
                border: 1px solid #ccc !important;
            }
            button:hover {
                background-color: #FBAD22 !important;
                color: black !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Roboto:wght@400;500&display=swap');
            html, body, .stApp {
                font-family: 'Roboto', sans-serif !important;
                background-color: #121212 !important;
                color: white !important;
            }
            .stApp h1, h2, h3 {
                font-family: 'Merriweather', serif !important;
                color: white !important;
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #242B68 0%, #1b1f4a 100%) !important;
            }
            section[data-testid="stSidebar"] * {
                color: white !important;
            }
            div[data-testid="stChatMessageContent"] {
                background-color: #2a2a2a !important;
                color: white !important;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #444;
            }
            .stMarkdown div, .stMarkdown section, .stMarkdown p {
                background-color: transparent !important;
                color: white !important;
            }
            input, textarea, select {
                background-color: #2a2a2a !important;
                color: white !important;
                border: 1px solid #555 !important;
            }
            input::placeholder, textarea::placeholder {
                color: #ccc !important;
            }
            .stMultiSelect, .stSelectbox {
                background-color: #2a2a2a !important;
                color: white !important;
            }
            .stRadio label, .stSelectbox label, .stMultiSelect label {
                color: white !important;
            }
            button {
                background-color: #333 !important;
                color: white !important;
                border: 1px solid #555 !important;
            }
            button:hover {
                background-color: #FBAD22 !important;
                color: black !important;
            }
            </style>
        """, unsafe_allow_html=True)
