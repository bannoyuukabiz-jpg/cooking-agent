import streamlit as st

# --- ページ設定 ---
st.set_page_config(page_title="クッキングエージェント", page_icon="🍳", layout="centered")

# --- パスワード認証機能 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 クッキングエージェントへようこそ")
    st.write("お二人専用のアプリです。下のボタンを押してログインしてください。")
    if st.button("🍳 アプリに入室する（お母様・あなた）"):
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- メインアプリ画面（3つのタブ） ---
st.title("🍳 おうちクッキングエージェント")
st.write("冷蔵庫の食材やツールを管理して、ぴったりの献立をご提案します！")

tab1, tab2, tab3 = st.tabs(["🛒 食材の在庫管理", "⚙️ ツール・家電設定", "🍲 献立を考えてもらう"])

with tab1:
    st.header("冷蔵庫の食材を登録・編集する")
    st.write("※カテゴリは下の入力欄に自由に入力できます（例：野菜、肉、調味料など）")
    
    category = st.text_input("カテゴリ名", value="野菜")
    
    col1, col2 = st.columns(2)
    with col1:
        food_name = st.text_input("食材名（例：トマト、豚肉）")
    with col2:
        food_quantity = st.text_input("数量（例：2個、200g）", value="1つ")
        
    if st.button("食材を追加する"):
        if food_name:
            st.success(f"「{category}」カテゴリに「{food_name} ({food_quantity})」を追加しました！")
        else:
            st.warning("食材名を入力してください。")

with tab2:
    st.header("おうちのツール・家電設定")
    tool_name = st.text_input("ツール・家電名（例：ヘルシオ オーブンレンジ）", value="ヘルシオ")
    tool_feature = st.text_area("特徴・得意なこと（例：過熱水蒸気でノンフライ調理や蒸し焼きが得意）", value="過熱水蒸気でジューシーに焼くのが得意")
    if st.button("ツール情報を保存"):
        st.success("ツール情報を保存しました！")

with tab3:
    st.header("今日の献立提案")
    cooking_style = st.text_input("今日の気分・調理方法（例：時短、ガッツリ、ヘルシーなど）", value="おまかせ")
    if st.button("献立を考えてもらう！"):
        st.info("（ここにGeminiがAI献立を出力する機能が入ります！）")
