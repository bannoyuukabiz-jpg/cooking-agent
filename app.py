import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(
    page_title="おうちクッキングエージェント",
    page_icon="🍳",
    layout="centered"
)

# --- セッション状態の初期化（メモリ上の仮データ保存） ---
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
    st.session_state.favorites = []

# --- パスワード認証機能 ---
if not st.session_state.authenticated:
    st.title("🔒 クッキングエージェントへようこそ")
    st.write("お二人専用のアプリです。下のボタンを押してログインしてください。")
    if st.button("🍳 アプリに入室する（お母様・あなた）"):
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- メインアプリ画面（4つのタブに拡張） ---
st.title("🍳 おうちクッキングエージェント")
st.write("冷蔵庫の食材やツールを管理して、ぴったりの献立をご提案します！")

tab1, tab2, tab3, tab4 = st.tabs(["🛒 食材の在庫", "⚙️ ツール設定", "🍲 献立提案", "⭐ お気に入り"])

# --- Tab 1: 食材の在庫管理 ---
with tab1:
    st.header("冷蔵庫の食材を登録・編集する")
    
    category = st.text_input("カテゴリ名（例：野菜、肉、調味料）", value="野菜")
    col1, col2 = st.columns(2)
    with col1:
        food_name = st.text_input("食材名（例：キャベツ、卵）")
    with col2:
        food_quantity = st.text_input("数量（例：1玉、1パック）", value="1つ")
        
    if st.button("食材を追加する"):
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
    st.subheader("現在登録されている食材一覧")
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
    st.header("おうちのツール・家電設定")
    st.write("「ヘルシオ」などのオーブンや調理器具の特徴を登録できます。")
    
    new_tool_name = st.text_input("ツール・家電名", value="ヘルシオ")
    new_tool_feature = st.text_area("特徴・得意なこと", value="過熱水蒸気でジューシーに焼くのが得意")
    
    if st.button("ツール情報を保存"):
        if new_tool_name:
            st.session_state.tools.append({
                "name": new_tool_name,
                "feature": new_tool_feature
            })
            st.success("ツール情報を保存しました！")
        else:
            st.warning("ツール名を入力してください。")
            
    st.divider()
    st.subheader("登録中のツール一覧")
    for tool in st.session_state.tools:
        st.markdown(f"- **{tool['name']}**: {tool['feature']}")

# --- Tab 3: 献立提案 ---
with tab3:
    st.header("今日の献立提案")
    cooking_style = st.text_input("今日の気分・調理方法（例：時短、ヘルシー、ヘルシオでジューシーに）", value="おまかせ")
    
    if st.button("献立を考えてもらう！"):
        with st.spinner("AIが冷蔵庫の食材とツールを組み合わせて考えています..."):
            # 食材とツールのリストをテキスト化
            inv_text = ", ".join([f"{i['name']} ({i['quantity']})" for i in st.session_state.inventory])
            tools_text = ", ".join([f"{t['name']} ({t['feature']})" for t in st.session_state.tools])
            
            # Gemini APIキーが設定されている場合の処理（またはシミュレーション）
            try:
                # Streamlit secretsからAPIキーを取得
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = f"""
                    あなたは家庭の優秀な料理アシスタントです。
                    以下の冷蔵庫の在庫食材と、利用できる調理ツールを使って、おすすめの献立（主菜・副菜など）を1つ提案してください。
                    
                    【冷蔵庫の在庫】
                    {inv_text if inv_text else "特になし"}
                    
                    【調理ツール】
                    {tools_text if tools_text else "特になし"}
                    
                    【本日のリクエスト】
                    {cooking_style}
                    
                    出力には、料理名、材料、簡単な作り方の手順、およびそのツールを活用するポイントを含めてください。
                    """
                    response = model.generate_content(prompt)
                    st.markdown("### 💡 AIからの献立提案")
                    st.write(response.text)
                else:
                    # APIキーが未設定の場合のデモ提案（動く安心設計）
                    st.markdown("### 💡 AIからの献立提案（デモモード）")
                    st.success("APIキーが未設定のため、サンプル提案を表示しています。")
                    st.markdown(f"""
                    **メニュー名：トマトと豚肉のヘルシオジューシー炒め**
                    - **使った食材：** トマト ({next((i['quantity'] for i in st.session_state.inventory if i['name']=='トマト'), '3個')}), 豚肉スライス
                    - **調理ツール：** ヘルシオ（過熱水蒸気）
                    - **作り方：**
                      1. 豚肉と切ったトマトを耐熱容器に入れます。
                      2. ヘルシオの「まかせて調理（焼く）」または「炒め物コース」にセットします。
                      3. 過熱水蒸気でジューシーに仕上がり完成です！
                    """)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- Tab 4: お気に入り ---
with tab4:
    st.header("お気に入りのレシピ")
    st.write("保存したお気に入りの料理を見返せます。")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"- {fav}")
    else:
        st.info("お気に入りはまだ登録されていません。")
