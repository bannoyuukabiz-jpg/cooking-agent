import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #FAF8F5 !important;
        color: #2C3E2D !important;
    }
    h1, h2, h3 {
        color: #4A5D43 !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    label, .stTextInput label, .stTextArea label, p, span {
        color: #2C3E2D !important;
        font-weight: 500;
    }
    .stButton > button {
        background-color: #E29578 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #D37A5C !important;
        color: white !important;
    }
    .stTextInput input, textarea, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div, .stInfo {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
        border-radius: 12px !important;
        border: 1px solid #D8CEC3 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
    }
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #D8CEC3 !important;
        color: #2C3E2D !important;
    }
    div.streamlit-expanderContent {
        background-color: #FFFFFF !important;
        border: 1px solid #D8CEC3 !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 入力フォームのリセット用キーの管理
if "form_counter" not in st.session_state:
    st.session_state.form_counter = 0

if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"category": "肉類・畜産物", "name": "豚肉スライス", "quantity": "200g"},
        {"category": "野菜・果物", "name": "トマト", "quantity": "3個"},
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
    if st.button("🛒\n在庫", key="tab_1"):
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
    if st.button("⭐\nお茶", key="tab_5"):
        st.session_state.current_menu = "⭐ お気に入り"

st.markdown(f"**現在地： {st.session_state.current_menu}**")
st.divider()

menu = st.session_state.current_menu

if menu == "🛒 なにがあるかな？":
    st.header("🛒 なにがあるかな？")
    st.write("冷蔵庫にある食材を登録しましょう！")
    
    # 食材名（自動反映・編集可能）
    food_name_input = st.text_input("食材名（例：キャベツ、豚肉、牛乳など）", key=f"food_name_{st.session_state.form_counter}")
    
    # 数量とカテゴリを2カラムにする
    col_q, col_c = st.columns(2)
    with col_q:
        food_qty_input = st.text_input("数量（例：1玉、200g ※未入力でもOK）", key=f"food_qty_{st.session_state.form_counter}")
    with col_c:
        categories_list = [
            "1. 🌾穀物・麺類・パン",
            "2. 🥑野菜・果物",
            "3. 🍖肉類・畜産物",
            "4. 🐟️水産物・海藻",
            "5. 🥛乳製品・大豆製品",
            "6. 🧂調味料・油",
            "7. 🍰お菓子・スイーツ"
        ]
        
        # 入力された食材名から自動でカテゴリを推測
        def guess_category(name):
            n = name.lower()
            if any(w in n for w in ["米", "小麦粉", "パン", "パスタ", "うどん", "そば", "シリアル"]):
                return "1. 🌾穀物・麺類・パン"
            elif any(w in n for w in ["トマト", "キャベツ", "レタス", "玉ねぎ", "人参", "きゅうり", "じゃがいも", "野菜", "ネギ", "りんご", "バナナ", "みかん"]):
                return "2. 🥑野菜・果物"
            elif any(w in n for w in ["豚", "鶏", "牛", "肉", "ベーコン", "ソーセージ", "ひき肉", "卵"]):
                return "3. 🍖肉類・畜産物"
            elif any(w in n for w in ["鮭", "鯖", "えび", "魚", "アジ", "シーフード", "かまぼこ", "海苔"]):
                return "4. 🐟️水産物・海藻"
            elif any(w in n for w in ["牛乳", "チーズ", "バター", "ヨーグルト", "豆腐", "納豆", "油揚げ"]):
                return "5. 🥛乳製品・大豆製品"
            elif any(w in n for w in ["醤油", "味噌", "砂糖", "塩", "酢", "油", "マヨネーズ", "ケチャップ", "ソース"]):
                return "6. 🧂調味料・油"
            elif any(w in n for w in ["チョコ", "スナック", "アイス", "お菓子", "クッキー", "ケーキ"]):
                return "7. 🍰お菓子・スイーツ"
            else:
                return "2. 🥑野菜・果物"

        guessed_cat = guess_category(food_name_input) if food_name_input else categories_list[1]
        try:
            default_index = categories_list.index(guessed_cat)
        except ValueError:
            default_index = 1
            
        food_cat_input = st.selectbox("カテゴリ", categories_list, index=default_index, key=f"food_cat_{st.session_state.form_counter}")

    if st.button("✨ 食材を追加する"):
        if food_name_input:
            st.session_state.inventory.append({
                "category": food_cat_input,
                "name": food_name_input,
                "quantity": food_qty_input.strip()
            })
            # トーストを表示してフォームをクリア（カウンターを進める）
            st.toast("登録しました！")
            st.session_state.form_counter += 1
            st.rerun()
        else:
            st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    
    if st.session_state.inventory:
        for idx, cat_name in enumerate(categories_list):
            cat_items = [(i, item) for i, item in enumerate(st.session_state.inventory) if item['category'] == cat_name]
            
            with st.expander(f"{cat_name} ({len(cat_items)}件)", expanded=True):
                if cat_items:
                    for i, item in cat_items:
                        col_n, col_q_edit = st.columns([3, 2])
                        with col_n:
                            new_name = st.text_input("食材名", value=item['name'], key=f"name_{i}")
                        with col_q_edit:
                            new_q = st.text_input("数量", value=item['quantity'], key=f"qty_{i}")
                        
                        # 編集・削除ボタン（縦積み・「更新」を「編集」に変更）
                        if st.button("💾 編集", key=f"update_inv_{i}"):
                            st.session_state.inventory[i] = {
                                "category": item['category'], # カテゴリは維持
                                "name": new_name,
                                "quantity": new_q
                            }
                            st.success("更新しました！")
                            st.rerun()
