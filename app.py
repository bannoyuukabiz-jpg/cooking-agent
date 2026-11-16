import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

# 北欧ナチュラル風デザインのCSS
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
    .stButton > button {
        background-color: #F4A498 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: bold !important;
        box-shadow: 0 3px 6px rgba(244, 164, 152, 0.3);
        transition: all 0.2s ease;
    }
    .stButton > button p, .stButton > button span {
        color: #FFFFFF !important;
    }
    .stButton > button:hover {
        background-color: #E58B7D !important;
    }
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
    div[data-testid="stExpander"] summary:hover {
        background-color: #FCE8E4 !important;
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
    st.session_state.favorites = [
        "トマトと豚肉のヘルシオジューシー炒め",
        "キャベツの温野菜サラダ（ヘルシオ使用）"
    ]

if not st.session_state.authenticated:
    st.title("🔒 ログイン")
    st.write("お二人専用のキッチンアプリです。下のボタンを押して入室してください。")
    if st.button("🐮 うしのクッキングに入室する"):
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

st.title("🐮 うしのクッキング")
st.write("今日はなに食べよう？🐮")

col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)

if "current_menu" not in st.session_state:
    st.session_state.current_menu = "🛒 なにがあるかな？"

with col_t1:
    if st.button("🛒\n食材", key="tab_1"):
        st.session_state.current_menu = "🛒 なにがあるかな？"
with col_t2:
    if st.button("⚙️\n用品", key="tab_2"):
        st.session_state.current_menu = "⚙️ キッチン用品"
with col_t3:
    if st.button("🍲\n献立", key="tab_3"):
        st.session_state.current_menu = "🍲 なに食べよう？"
with col_t4:
    if st.button("📜\n履歴", key="tab_4"):
        st.session_state.current_menu = "📜 履歴"
with col_t5:
    if st.button("⭐\nお気に", key="tab_5"):
        st.session_state.current_menu = "⭐ お気に入り"

st.markdown(f"**現在地： {st.session_state.current_menu}**")
st.divider()

menu = st.session_state.current_menu

categories = [
    "1. 🌾穀物・麺類・パン",
    "2. 🥑野菜・果物",
    "3. 🍖肉類・畜産物",
    "4. 🐟️水産物・海藻",
    "5. 🥛乳製品・大豆製品",
    "6. 🧂調味料・油",
    "7. 🍰お菓子・スイーツ",
    "8. ❔️その他"
]

if menu == "🛒 なにがあるかな？":
    st.header("🛒 なにがあるかな？")
    st.write("冷蔵庫にある食材を登録しましょう！")
    
    food_name_input = st.text_input("食材名（例：キャベツ、豚肉、牛乳など）")
    food_qty_input = st.text_input("数量（例：1玉、200g ※未入力でもOK）")
    
    # カテゴリのセレクトボックス（デフォルト未入力風に「選択してください」または自動判定、今回は「❔️その他」を含むリストから自動選択、または手動選択）
    def guess_category(name):
        n = name.lower()
        if any(w in n for w in ["米", "小麦粉", "パン", "パスタ", "うどん", "そば", "シリアル"]):
            return "1. 🌾穀物・麺類・パン"
        elif any(w in n for w in ["トマト", "キャベ
