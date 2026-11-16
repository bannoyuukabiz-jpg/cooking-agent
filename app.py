import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

# --- 北欧ナチュラル＆スマホライク風デザインのCSS適用（プルダウンや履歴の背景も白に統一） ---
st.markdown("""
<style>
    /* 全体の背景と文字色 */
    .stApp {
        background-color: #FAF8F5 !important;
        color: #2C3E2D !important;
    }
    
    /* 見出しの色 */
    h1, h2, h3 {
        color: #4A5D43 !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* ラベルや文字をくっきりと見やすく */
    label, .stTextInput label, .stTextArea label, p, span {
        color: #2C3E2D !important;
        font-weight: 500;
    }
    
    /* ボタンを角丸で可愛い北欧風カラーにする */
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
    
    /* 入力欄・テキストエリア・プルダウン・情報表示の背景をすべて白に統一 */
    .stTextInput input, textarea, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div, .stInfo {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
        border-radius: 12px !important;
        border: 1px solid #D8CEC3 !important;
    }
    
    /* プルダウンの選択肢ポップアップの背景も明るく */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
    }
    
    /* エクスパンダー（履歴などの折りたたみ）の背景を白に統一 */
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

# --- セッション状態の初期化 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"category": "野菜", "name": "トマト", "quantity": "3個"},
        {"category": "肉", "name": "豚肉スライス", "quantity": "200g"},
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

# --- パスワード認証画面 ---
if not st.session_state.authenticated:
    st.title("🔒 ログイン")
    st.write("お二人専用のキッチンアプリです。下のボタンを押して入室してください。")
    if st.button("🐮 うしのクッキングに入室する"):
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- メインアプリ画面 ---
st.title("🐮 うしのクッキング")
st.write("今日はなに食べよう？🐮")

# --- スマホライクなアイコン付きメニュー選択（LINEのタブ風） ---
menu_options = {
    "🛒 なにがあるかな？": "🛒 なにがあるかな？",
    "⚙️ キッチン用品": "⚙️ キッチン用品",
    "🍲 なに食べよう？": "🍲 なに食べよう？",
    "📜 履歴": "📜 履歴",
    "⭐ お気に入り": "⭐ お気に入り"
}

# 横並びのボタン風カラムでスマホのタブバーのように配置
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
    if st.button("⭐\nお茶", key="tab_5"): # 省略してコンパクトに
        st.session_state.current_menu = "⭐ お気に入り"

st.markdown(f"**現在地： {st.session_state.current_menu}**")
st.divider()

menu = st.session_state.current_menu

# --- 1. なにがあるかな？ ---
if menu == "🛒 なにがあるかな？":
    st.header("🛒 なにがあるかな？")
    st.write("冷蔵庫にある食材を登録しましょう！")
    
    food_name_input = st.text_input("食材名（例：キャベツ、豚肉、牛乳など）")
    food_qty_input = st.text_input("数量（例：1玉、200g ※未入力でもOK）")
    
    def guess_category(name):
        name_lower = name.lower()
        if any(w in name_lower for w in ["トマト", "キャベツ", "レタス", "玉ねぎ", "人参", "きゅうり", "じゃがいも", "野菜", "ネギ"]):
            return "野菜"
        elif any(w in name_lower for w in ["豚", "鶏", "牛", "肉", "ベーコン", "ソーセージ", "ひき肉"]):
            return "肉"
        elif any(w in name_lower for w in ["鮭", "鯖", "えび", "魚", "アジ", "シーフード"]):
            return "魚介"
        elif any(w in name_lower for w in ["牛乳", "チーズ", "バター", "卵", "ヨーグルト"]):
            return "乳製品・卵"
        elif any(w in name_lower for w in ["醤油", "味噌", "砂糖", "塩", "油", "マヨネーズ", "ケチャップ", "ソース"]):
            return "調味料"
        else:
            return "その他"

    if st.button("✨ 食材を追加する"):
        if food_name_input:
            auto_cat = guess_category(food_name_input)
            st.session_state.inventory.append({
                "category": auto_cat,
                "name": food_name_input,
                "quantity": food_qty_input.strip()
            })
            st.success(f"「{food_name_input}」を登録しました！（自動分類：{auto_cat}）")
            st.rerun()
        else:
            st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    
    if st.session_state.inventory:
        for i, item in enumerate(st.session_state.inventory):
            with st.container():
                col_c, col_n, col_q = st.columns([2, 3, 2])
                with col_c:
                    new_cat = st.text_input("カテゴリ", value=item['category'], key=f"cat_{i}")
                with col_n:
                    new_name = st.text_input("食材名", value=item['name'], key=f"name_{i}")
                with col_q:
                    new_q = st.text_input("数量", value=item['quantity'], key=f"qty_{i}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 更新", key=f"update_inv_{i}"):
                        st.session_state.inventory[i] = {
                            "category": new_cat,
                            "name": new_name,
                            "quantity": new_q
                        }
                        st.success("更新しました！")
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 削除", key=f"del_inv_{i}"):
                        st.session_state.inventory.pop(i)
                        st.rerun()
                st.markdown("---")
    else:
        st.info("食材が登録されていません。")

# --- 2. キッチン用品 ---
elif menu == "⚙️ キッチン用品":
    st.header("⚙️ キッチン用品")
    st.write("おうちにある家電や調理器具を登録できます。")
    
    tool_input = st.text_input("キッチン用品名（例：ヘルシオ、バルミューダトースター、圧力鍋など）", value="ヘルシオ")
    
    def search_tool_feature(name):
        name_lower = name.lower()
        if "ヘルシオ" in name_lower:
            return "過熱水蒸気やウォーターオーブン機能で、油を使わないノンフライ調理やジューシーな焼き物・蒸し物が得意です。"
        elif "バルミューダ" in name_lower or "トースター" in name_lower:
            return "スチームテクノロジーと温度制御により、外はサクッと、中はもちもちの最高のトーストや焼き上がりが実現できます。"
        elif "圧力鍋" in name_lower:
            return "高温高圧で調理するため、固い根菜や塊肉も短時間でトロトロに柔らかく仕上がります。"
        elif "ホットクック" in name_lower:
            return "水なし・自動調理が得意で、かき混ぜながら食材の旨みを引き出した無水調理ができます。"
        else:
            return "毎日の調理を便利にしてくれる頼もしい調理器具です。"

    default_feature = search_tool_feature(tool_input)
    tool_feature_input = st.text_area("特徴・得意なこと（自動入力されますが編集もできます）", value=default_feature)
    
    if st.button("💾 キッチン用品を登録する"):
        if tool_input:
            st.session_state.tools.append({
                "name": tool_input,
                "feature": tool_feature_input
            })
            st.success("キッチン用品を登録しました！")
            st.rerun()
        else:
            st.warning("キッチン用品名を入力してください。")
            
    st.divider()
    st.subheader("おうちにあるキッチン用品")
    if st.session_
