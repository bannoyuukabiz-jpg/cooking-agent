import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(
    page_title="おうちクッキングエージェント",
    page_icon="🍳",
    layout="centered"
)

# --- 北欧ナチュラル風デザインのCSS適用（すべての入力・カード部分を明るく統一） ---
st.markdown("""
<style>
    /* 全体の背景と文字色 */
    .stApp {
        background-color: #FAF8F5 !important; /* 温かみのあるオフホワイト */
        color: #2C3E2D !important; /* 濃いナチュラルグリーン */
    }
    
    /* 見出しの色や雰囲気 */
    h1, h2, h3 {
        color: #4A5D43 !important; /* 深みのあるくすみグリーン */
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* 入力欄の上のラベルやテキストの文字をくっきりと見やすくする */
    label, .stTextInput label, .stTextArea label, p, span {
        color: #2C3E2D !important;
        font-weight: 500;
    }
    
    /* ボタンを角丸で可愛い北欧風カラーにする */
    .stButton > button {
        background-color: #E29578 !important; /* サーモンピンク・テラコッタ系 */
        color: white !important;
        border-radius: 20px !important; /* 角を丸く */
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
    
    /* 入力欄・テキストエリア・情報表示エリアの背景を確実に白にする */
    .stTextInput input, textarea, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, .stInfo {
        background-color: #FFFFFF !important;
        color: #2C3E2D !important;
        border-radius: 12px !important;
        border: 1px solid #D8CEC3 !important;
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

if "favorites" not in st.session_state:
    st.session_state.favorites = [
        "トマトと豚肉のヘルシオジューシー炒め",
        "キャベツの温野菜サラダ（ヘルシオ使用）"
    ]

# --- パスワード認証画面 ---
if not st.session_state.authenticated:
    st.title("🔒 クッキングエージェントへようこそ")
    st.write("お二人専用のキッチンアプリです。下のボタンを押して入室してください。")
    if st.button("🍳 アプリに入室する（お母様・あなた）"):
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- メインアプリ画面（4つのタブ） ---
st.title("🍳 おうちクッキングエージェント")
st.write("🌿 冷蔵庫の食材やツールを管理して、ぴったりの献立をご提案します！")

tab1, tab2, tab3, tab4 = st.tabs(["🛒 食材の在庫", "⚙️ ツール設定", "🍲 献立提案", "⭐ お気に入り"])

# --- Tab 1: 食材の在庫管理 ---
with tab1:
    st.header("🛒 冷蔵庫の食材を登録・編集する")
    
    category = st.text_input("カテゴリ名（例：野菜、肉、調味料）", value="野菜")
    col1, col2 = st.columns(2)
    with col1:
        food_name = st.text_input("食材名（例：キャベツ、卵）")
    with col2:
        food_quantity = st.text_input("数量（例：1玉、1パック）", value="1つ")
        
    if st.button("✨ 食材を追加する"):
        if food_name:
            st.session_state.inventory.append({
                "category": category,
                "name": food_name,
                "quantity": food_quantity
            })
            st.success(f"「{category}」カテゴリに「{food_name} ({food_quantity})」を追加しました！")
        else:
            st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("📋 現在登録されている食材一覧")
    if st.session_state.inventory:
        for i, item in enumerate(st.session_state.inventory):
            c1, c2, c3 = st.columns([2, 3, 2])
            c1.write(f"📁 {item['category']}")
            c2.write(f"🥕 **{item['name']}** ({item['quantity']})")
            if c3.button("削除", key=f"del_inv_{i}"):
                st.session_state.inventory.pop(i)
                st.rerun()
    else:
        st.info("食材が登録されていません。上のフォームから追加してください。")

# --- Tab 2: ツール・家電設定 ---
with tab2:
    st.header("⚙️ おうちのツール・家電設定")
    st.write("「ヘルシオ」などのオーブンや調理器具の特徴を登録できます。")
    
    new_tool_name = st.text_input("ツール・家電名", value="ヘルシオ")
    new_tool_feature = st.text_area("特徴・得意なこと", value="過熱水蒸気でジューシーに焼くのが得意")
    
    if st.
