import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

# 北欧ナチュラル風デザインのCSS（ボタンが消えないよう表示を確実に保証）
st.markdown("""
<style>
    .stApp {
        background-color: #FAF8F5 !important;
        color: #2C3E2D !important;
    }
    h1, h2, h3 {
        color: #3B7A9E !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    label, p, span, div, .stMarkdown {
        color: #2C3E2D !important;
    }
    /* ボタンのデザイン（必ず表示されるように設定） */
    div.stButton > button {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #E29578 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1) !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    div.stButton > button p, div.stButton > button span {
        color: #FFFFFF !important;
    }
    div.stButton > button:hover {
        background-color: #D37A5C !important;
    }
    /* 入力欄・セレクトボックスの背景を白に統一 */
    input, textarea, select,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
        border-radius: 12px !important;
        border: 1.5px solid #E2D9CE !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
    }
    li[role="option"]:hover {
        background-color: #FDF0ED !important;
    }
    /* アコーディオン（Expander） */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2D9CE !important;
        border-radius: 14px !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        background-color: #FDF4F2 !important;
        color: #2C3E2D !important;
        padding: 0.75rem 1rem !important;
    }
    div[data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important;
        padding: 1rem !important;
    }
    div[data-testid="stAlert"] {
        background-color: #EDF5F9 !important;
        border: 1px solid #B8D8E8 !important;
        border-radius: 12px !important;
        color: #2C3E2D !important;
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "form_counter" not in st.session_state:
    st.session_state.form_counter = 0

if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"category": "3. 🍖肉類・畜産物", "name": "豚肉スライス", "quantity": "200g"},
        {"category": "2. 🥑野菜・果物", "name": "トマト", "quantity": "3個"},
    ]

if "tools" not in st.session_state:
    st.session_state.tools = [
        {"name": "ヘルシオ オーブンレンジ", "feature": "過熱水蒸気でノンフライ調理や蒸し焼きが得意"}
    ]

if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st
