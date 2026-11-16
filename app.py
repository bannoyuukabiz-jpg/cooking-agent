import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(page_title="うしのクッキング", page_icon="🐮", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #FAF8F5 !important; color: #2C3E2D !important; }
    h1, h2, h3 { color: #4A5D43 !important; font-family: 'Helvetica Neue', Arial, sans-serif; }
    label, .stTextInput label, .stTextArea label, p, span { color: #2C3E2D !important; font-weight: 500; }
    .stButton > button {
        background-color: #E29578 !important; color: white !important;
        border-radius: 20px !important; border: none !important;
        padding: 0.5rem 1.5rem !important; font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.3s ease;
    }
    .stButton > button:hover { background-color: #D37A5C !important; color: white !important; }
    .stTextInput input, textarea, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div, .stInfo {
        background-color: #FFFFFF !important; color: #2C3E2D !important;
        border-radius: 12px !important; border: 1px solid #D8CEC3 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] { background-color: #FFFFFF !important; color: #2C3E2D !important; }
    .streamlit-expanderHeader { background-color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #D8CEC3 !important; color: #2C3E2D !important; }
    div.streamlit-expanderContent { background-color: #FFFFFF !important; border: 1px solid #D8CEC3 !important; border-top: none !important; border-bottom-left-radius: 12px !important; border-bottom-right-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "inventory" not in st.session_state:
    st.session_state.inventory = [{"category": "野菜", "name": "トマト", "quantity": "3個"}, {"category": "肉", "name": "豚肉スライス", "quantity": "200g"}]
if "tools" not in st.session_state:
    st.session_state.tools = [{"name": "ヘルシオ オーブンレンジ", "feature": "過熱水蒸気でノンフライ調理や蒸し焼きが得意"}]
if "history" not in st.session_state: st.session_state.history = []
if "favorites" not in st.session_state:
    st.session_state.favorites = ["トマトと豚肉のヘルシオジューシー炒め", "キャベツの温野菜サラダ（ヘルシオ使用）"]

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
if "current_menu" not in st.session_state: st.session_state.current_menu = "🛒 なにがあるかな？"

with col_t1:
    if st.button("🛒\n在庫", key="tab_1"): st.session_state.current_menu = "🛒 なにがあるかな？"
with col_t2:
    if st.button("⚙️\nキッチン", key="tab_2"): st.session_state.current_menu = "⚙️ キッチン用品"
with col_t3:
    if st.button("🍲\n献立", key="tab_3"): st.session_state.current_menu = "🍲 なに食べよう？"
with col_t4:
    if st.button("📜\n履歴", key="tab_4"): st.session_state.current_menu = "📜 履歴"
with col_t5:
    if st.button("⭐\nお気に入り", key="tab_5"): st.session_state.current_menu = "⭐ お気に入り"

st.divider()

menu = st.session_state.current_menu

if menu == "🛒 なにがあるかな？":
    st.header("🛒 なにがあるかな？")
    st.write("冷蔵庫にある食材を登録しましょう！")
    food_name_input = st.text_input("食材名（例：キャベツ、豚肉など）")
    food_qty_input = st.text_input("数量（例：1玉、200g ※未入力でもOK）")
    
    def guess_category(name):
        n = name.lower()
        if any(w in n for w in ["トマト", "キャベツ", "レタス", "玉ねぎ", "人参", "きゅうり", "野菜"]): return "野菜"
        elif any(w in n for w in ["豚", "鶏", "牛", "肉", "ベーコン"]): return "肉"
        elif any(w in n for w in ["鮭", "鯖", "えび", "魚"]): return "魚介"
        elif any(w in n for w in ["牛乳", "チーズ", "バター", "卵"]): return "乳製品・卵"
        elif any(w in n for w in ["醤油", "味噌", "砂糖", "塩", "油"]): return "調味料"
        return "その他"

    if st.button("✨ 食材を追加する"):
        if food_name_input:
            cat = guess_category(food_name_input)
            st.session_state.inventory.append({"category": cat, "name": food_name_input, "quantity": food_qty_input.strip()})
            st.success(f"「{food_name_input}」を追加しました！（{cat}）")
            st.rerun()
        else: st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    if st.session_state.inventory:
        for i, item in enumerate(st.session_
