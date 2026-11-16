import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

# --- 北欧ナチュラル＆スマホライク風デザインのCSS適用 ---
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
    
    /* 入力欄・テキストエリア・情報表示の背景を白に */
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

# --- メインアプリ画面（スマホライクなタブ構成） ---
st.title("🐮 うしのクッキング")
st.write("今日はなに食べよう？🐮")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 なにがあるかな？", "⚙️ キッチン用品", "🍲 なに食べよう？", "📜 履歴", "⭐ お気に入り"])

# --- Tab 1: なにがあるかな？（食材の在庫管理・自動カテゴリ・編集機能） ---
with tab1:
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

# --- Tab 2: キッチン用品（ツール設定・自動検索・編集・登録ボタン追加） ---
with tab2:
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
    
    # 登録ボタンを追加しました
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
    if st.session_state.tools:
        for i, tool in enumerate(st.session_state.tools):
            st.markdown(f"- **{tool['name']}**: {tool['feature']}")
    else:
        st.info("キッチン用品が登録されていません。")

# --- Tab 3: なに食べよう？（献立提案） ---
with tab3:
    st.header("🍲 なに食べよう？")
    
    style_option = st.selectbox(
        "今日の気分・調理方法を選んでね",
        ["おまかせ", "時短・簡単", "ヘルシー・さっぱり", "がっつりスタミナ", "ヘルシオでジューシーに", "自由に入力する"]
    )
    
    if style_option == "自由に入力する":
        cooking_style = st.text_input("ご自身の気分・リクエストを入力してください")
    else:
        cooking_style = style_option
        
    if st.button("✨ 献立を考えてもらう！"):
        with st.spinner("うしさんが冷蔵庫の食材とキッチン用品から考えています..."):
            inv_formatted = []
            for i in st.session_state.inventory:
                if i['quantity'].strip():
                    inv_formatted.append(f"{i['name']} ({i['quantity']})")
                else:
                    inv_formatted.append(f"{i['name']}")
            
            inv_text = ", ".join(inv_formatted)
            tools_text = ", ".join([f"{t['name']} ({t['feature']})" for t in st.session_state.tools])
            
            try:
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = f"""
                    あなたは家庭の優秀な料理アシスタントです。
                    以下の冷蔵庫の在庫食材と、利用できるキッチン用品を使って、おすすめの献立（主菜・副菜など）を1つ提案してください。
                    
                    【冷蔵庫の在庫】
                    {inv_text if inv_text else "特になし"}
                    
                    【キッチン用品】
                    {tools_text if tools_text else "特になし"}
                    
                    【本日のリクエスト】
                    {cooking_style}
                    
                    出力には
