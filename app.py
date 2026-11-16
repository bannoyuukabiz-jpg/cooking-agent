import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(
    page_title="うしのクッキング",
    page_icon="🐮",
    layout="centered"
)

# 北欧ナチュラル（サーモンピンク × くすみブルー × 明るい白）CSS
st.markdown("""
<style>
    /* 全体の背景 */
    .stApp {
        background-color: #FAF8F5 !important;
        color: #2C3E2D !important;
    }
    
    /* 見出し（くすみブルーをアクセントに） */
    h1, h2, h3 {
        color: #3B7A9E !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* すべてのテキスト・ラベルをはっきりした濃い色に固定 */
    label, p, span, div, .stMarkdown {
        color: #2C3E2D !important;
    }

    /* ボタン（ポットのサーモンピンク） */
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

    /* 入力欄・テキストエリア・プルダウンを真っ白に強制固定 */
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
    
    /* プルダウンの選択肢リスト */
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

    /* アコーディオン（st.expander）のヘッダーと中身を白く明るく固定 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2D9CE !important;
        border-radius: 14px !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        background-color: #FDF4F2 !important; /* ほんのりサーモンピンクのヘッダー */
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

    /* st.info（お知らせ枠）の背景を優しいくすみブルー系に固定 */
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
    st.session_state.current_menu = "🍙 なにがあるかな？"

with col_t1:
    if st.button("🍙\n食材", key="tab_1"):
        st.session_state.current_menu = "🍙 なにがあるかな？"
with col_t2:
    if st.button("🍳\nキッチン", key="tab_2"):
        st.session_state.current_menu = "🍳 キッチン用品"
with col_t3:
    if st.button("🍲\n献立", key="tab_3"):
        st.session_state.current_menu = "🍲 なに食べよう？"
with col_t4:
    if st.button("📜\n履歴", key="tab_4"):
        st.session_state.current_menu = "📜 履歴"
with col_t5:
    if st.button("⭐\nお気に入り", key="tab_5"):
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

if menu == "🍙 なにがあるかな？":
    st.header("🍙 なにがあるかな？")
    st.write("冷蔵庫にある食材を登録しましょう！")
    
    c_key = st.session_state.form_counter
    food_name_input = st.text_input("食材名", placeholder="例：キャベツ、豚肉、牛乳など", key=f"fname_{c_key}")
    food_qty_input = st.text_input("数量", placeholder="例：1玉、200g ※未入力でもOK", key=f"fqty_{c_key}")
    
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
            return "8. ❔️その他"

    # 初期状態はカテゴリを空欄（未選択）にする
    default_idx = None
    if food_name_input:
        guessed = guess_category(food_name_input)
        if guessed in categories:
            default_idx = categories.index(guessed)

    food_cat_input = st.selectbox(
        "カテゴリ",
        categories,
        index=default_idx,
        placeholder="カテゴリを選択",
        key=f"fcat_{c_key}"
    )

    if st.button("✨ 食材を追加する"):
        if food_name_input:
            selected_cat = food_cat_input if food_cat_input else "8. ❔️その他"
            st.session_state.inventory.append({
                "category": selected_cat,
                "name": food_name_input,
                "quantity": food_qty_input.strip()
            })
            st.toast("登録しました！", icon="✨")
            st.session_state.form_counter += 1
            st.rerun()
        else:
            st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    
    if st.session_state.inventory:
        for idx, cat_name in enumerate(categories):
            cat_items = [(i, item) for i, item in enumerate(st.session_state.inventory) if item['category'] == cat_name]
            
            with st.expander(f"{cat_name} ({len(cat_items)}件)", expanded=True):
                if cat_items:
                    for i, item in cat_items:
                        col_n, col_q, col_b = st.columns([3, 2, 1])
                        with col_n:
                            new_name = st.text_input("食材名", value=item['name'], key=f"name_{i}", label_visibility="collapsed")
                        with col_q:
                            new_q = st.text_input("数量", value=item['quantity'], key=f"qty_{i}", label_visibility="collapsed")
                        with col_b:
                            if st.button("🗑️ 削除", key=f"del_inv_{i}"):
                                st.session_state.inventory.pop(i)
                                st.rerun()
                        
                        if new_name != item['name'] or new_q != item['quantity']:
                            st.session_state.inventory[i]["name"] = new_name
                            st.session_state.inventory[i]["quantity"] = new_q
                else:
                    st.info("登録されている食材はありません。")
            
            if idx < len(categories) - 1:
                st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #E2D9CE;'>", unsafe_allow_html=True)
    else:
        st.info("食材が登録されていません。")

elif menu == "🍳 キッチン用品":
    st.header("🍳 キッチン用品")
    st.write("おうちにある家電や調理器具を登録できます。")
    
    tool_input = st.text_input("キッチン用品名（例：ヘルシオ、バルミューダトースター、圧力鍋など）", value="ヘルシオ")
    
    def search_tool_feature(name):
        n = name.lower()
        if "ヘルシオ" in n:
            return "過熱水蒸気やウォーターオーブン機能で、油を使わないノンフライ調理やジューシーな焼き物・蒸し物が得意です。"
        elif "バルミューダ" in n or "トースター" in n:
            return "スチームテクノロジーと温度制御により、外はサクッと、中はもちもちの最高のトーストや焼き上がりが実現できます。"
        elif "圧力鍋" in n:
            return "高温高圧で調理するため、固い根菜や塊肉も短時間でトロトロに柔らかく仕上がります。"
        elif "ホットクック" in n:
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
    if st.session_state.tools:
        for i, tool in enumerate(st.session_state.tools):
            with st.container():
                st.markdown(f"**🍳 {tool['name']}**")
                st.markdown(f"{tool['feature']}")
                if st.button("🗑️ 削除", key=f"del_tool_{i}"):
                    st.session_state.tools.pop(i)
                    st.rerun()
                st.markdown("---")
    else:
        st.info("キッチン用品が登録されていません。")

elif menu == "🍲 なに食べよう？":
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
                    
                    prompt = (
                        "あなたは家庭の優秀な料理アシスタントです。\n"
                        "以下の冷蔵庫の在庫食材と、利用できるキッチン用品を使って、おすすめの献立（主菜・副菜など）を1つ提案してください。\n\n"
                        "【冷蔵庫の在庫】\n" + (inv_text if inv_text else "特になし") + "\n\n"
                        "【キッチン用品】\n" + (tools_text if tools_text else "特になし") + "\n\n"
                        "【本日のリクエスト】\n" + cooking_style + "\n\n"
                        "出力には、料理名、材料、簡単な作り方の手順、およびそのキッチン用品を活用するポイントを含めてください。"
                    )
                    
                    response = model.generate_content(prompt)
                    result_text = response.text
                else:
                    result_text = (
                        "**メニュー名：トマトと豚肉のジューシー炒め**\n"
                        "- **使った食材：** トマト, 豚肉スライス\n"
                        "- **キッチン用品：** ヘルシオ\n"
                        "- **作り方：**\n"
                        "  1. 豚肉と切ったトマトを耐熱容器に入れます。\n"
                        "  2. ヘルシオの「まかせて調理」にセットします。\n"
                        "  3. ジューシーに仕上がり完成です！"
                    )
                
                timestamp = datetime.now().strftime("%m/%d %H:%M")
                st.session_state.history.insert(0, {"time": timestamp, "style": cooking_style, "content": result_text})
                
                st.markdown("### 💡 提案された献立")
                st.markdown(result_text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

elif menu == "📜 履歴":
    st.header("📜 履歴")
    st.write("過去に生成した献立の記録です。")
    if st.session_state.history:
        for idx, h in enumerate(st.session_state.history):
            with st.expander(f"🕒 {h['time']} - リクエスト: {h['style']}"):
                st.markdown(h['content'])
    else:
        st.info("まだ生成された履歴はありません。「なに食べよう？」から献立を作ってみてね！")

elif menu == "⭐ お気に入り":
    st.header("⭐ お気に入りのレシピ")
    st.write("保存したお気に入りの料理を見返せます。")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"- 🍳 **{fav}**")
    else:
        st.info("お気に入りはまだ登録されていません。")
