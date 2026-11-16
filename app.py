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
        padding: 0.4rem 1rem !important; font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: all 0.3s ease;
        width: 100%;
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
    st.session_state.inventory = [
        {"category": "🥑野菜・果物", "name": "トマト", "quantity": "3個"}, 
        {"category": "🍖肉類・畜産物", "name": "豚肉スライス", "quantity": "200g"}
    ]
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

t1, t2, t3, t4, t5 = st.columns(5)
if "current_menu" not in st.session_state: st.session_state.current_menu = "🛒 食材"

with t1:
    if st.button("🥕\n食材", key="b1"):
        st.session_state.current_menu = "🛒 食材"
        st.rerun()
with t2:
    if st.button("⚙️\nキッチン", key="b2"):
        st.session_state.current_menu = "⚙️ キッチン用品"
        st.rerun()
with t3:
    if st.button("🍲\n献立", key="b3"):
        st.session_state.current_menu = "🍲 なに食べよう？"
        st.rerun()
with t4:
    if st.button("📜\n履歴", key="b4"):
        st.session_state.current_menu = "📜 履歴"
        st.rerun()
with t5:
    if st.button("⭐\nお気に入り", key="b5"):
        st.session_state.current_menu = "⭐ お気に入り"
        st.rerun()

st.divider()
m = st.session_state.current_menu

# --- 1. 食材タブ ---
if m == "🛒 食材":
    st.header("🛒 食材")
    st.write("冷蔵庫にある食材を登録しましょう！")
    fn = st.text_input("食材名（例：米、キャベツ、豚肉など）")
    fq = st.text_input("数量（例：1袋、200g ※未入力でもOK）")
    
    # 指定された7つのカテゴリへの自動振り分けロジック
    def guess_cat(name):
        n = name.lower()
        if any(w in n for w in ["米", "小麦粉", "パン", "パスタ", "うどん", "そば", "シリアル", "麺"]): return "🌾穀物・麺類・パン"
        elif any(w in n for w in ["トマト", "キャベツ", "レタス", "玉ねぎ", "人参", "きゅうり", "じゃがいも", "果物", "バナナ", "りんご", "みかん", "野菜"]): return "🥑野菜・果物"
        elif any(w in n for w in ["豚", "鶏", "牛", "肉", "ハム", "ソーセージ", "卵", "たまご"]): return "🍖肉類・畜産物"
        elif any(w in n for w in ["鮭", "鯖", "えび", "魚", "あじ", "まぐろ", "カニ", "かまぼこ", "海苔", "わかめ"]): return "🐟️水産物・海藻"
        elif any(w in n for w in ["牛乳", "チーズ", "ヨーグルト", "豆腐", "納豆", "油揚げ", "豆乳"]): return "🥛乳製品・大豆製品"
        elif any(w in n for w in ["醤油", "味噌", "砂糖", "塩", "酢", "マヨネーズ", "油", "ケチャップ", "ソース"]): return "🧂調味料・油"
        elif any(w in n for w in ["お菓子", "チョコレート", "スナック", "和菓子", "洋菓子", "アイス", "クッキー", "ケーキ"]): return "🍰お菓子・スイーツ"
        return "🥑野菜・果物" # デフォルト

    if st.button("✨ 食材を追加する"):
        if fn:
            cat = guess_cat(fn)
            st.session_state.inventory.append({"category": cat, "name": fn, "quantity": fq.strip()})
            st.success(f"「{fn}」を【{cat}】に追加しました！"); st.rerun()
        else: st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    
    if st.session_state.inventory:
        # 定義された7つのカテゴリの順番
        all_categories = [
            "🌾穀物・麺類・パン",
            "🥑野菜・果物",
            "🍖肉類・畜産物",
            "🐟️水産物・海藻",
            "🥛乳製品・大豆製品",
            "🧂調味料・油",
            "🍰お菓子・スイーツ"
        ]
        
        # 実際に登録されているカテゴリをフィルタリング（順番維持）
        existing_cats = [c for c in all_categories if any(item['category'] == c for item in st.session_state.inventory)]
        # 定義外のカテゴリがあれば最後に追加
        other_cats = list(set(item['category'] for item in st.session_state.inventory if item['category'] not in all_categories))
        display_cats = existing_cats + other_cats
        
        for idx, cat in enumerate(display_cats):
            # カテゴリごとにプルダウン（expander）で開閉できるようにする
            with st.expander(f"📁 {cat}", expanded=True):
                for original_i, item in enumerate(st.session_state.inventory):
                    if item['category'] == cat:
                        with st.container():
                            col_c, col_n, col_q, col_btn = st.columns([2.5, 3, 2, 1.5])
                            with col_c: nc = st.text_input("カテゴリ", value=item['category'], key=f"c_{original_i}")
                            with col_n: nn = st.text_input("食材名", value=item['name'], key=f"n_{original_i}")
                            with col_q: nq = st.text_input("数量", value=item['quantity'], key=f"q_{original_i}")
                            
                            with col_btn:
                                st.write("") # 位置調整
                                if st.button("💾 更新", key=f"up_{original_i}"):
                                    st.session_state.inventory[original_i] = {"category": nc, "name": nn, "quantity": nq}
                                    st.success("更新しました！"); st.rerun()
                                if st.button("🗑️ 削除", key=f"dl_{original_i}"):
                                    st.session_state.inventory.pop(original_i); st.rerun()
                        # カテゴリ内には区切り線を入れない仕様
            
            # カテゴリの間には薄い区切り線を入れる（最後のカテゴリ以外）
            if idx < len(display_cats) - 1:
                st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #E5DDD5;'>", unsafe_allow_html=True)
    else: 
        st.info("食材が登録されていません。")

# --- 2. キッチン用品タブ ---
elif m == "⚙️ キッチン用品":
    st.header("⚙️ キッチン用品")
    ti = st.text_input("キッチン用品名", value="ヘルシオ")
    
    def
