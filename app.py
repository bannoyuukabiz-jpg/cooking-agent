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

t1, t2, t3, t4, t5 = st.columns(5)
if "current_menu" not in st.session_state: st.session_state.current_menu = "🛒 なにがあるかな？"

with t1:
    if st.button("🛒\n在庫", key="b1"):
        st.session_state.current_menu = "🛒 なにがあるかな？"
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

if m == "🛒 なにがあるかな？":
    st.header("🛒 なにがあるかな？")
    fn = st.text_input("食材名（例：キャベツ等）")
    fq = st.text_input("数量（例：1玉 ※未入力でもOK）")
    
    def guess_cat(name):
        n = name.lower()
        if any(w in n for w in ["トマト", "キャベツ", "レタス", "玉ねぎ", "人参", "野菜"]): return "野菜"
        elif any(w in n for w in ["豚", "鶏", "牛", "肉", "ベーコン"]): return "肉"
        elif any(w in n for w in ["鮭", "鯖", "えび", "魚"]): return "魚介"
        elif any(w in n for w in ["牛乳", "チーズ", "バター", "卵"]): return "乳製品・卵"
        elif any(w in n for w in ["醤油", "味噌", "砂糖", "塩", "油"]): return "調味料"
        return "その他"

    if st.button("✨ 食材を追加する"):
        if fn:
            cat = guess_cat(fn)
            st.session_state.inventory.append({"category": cat, "name": fn, "quantity": fq.strip()})
            st.success(f"「{fn}」を追加しました！"); st.rerun()
        else: st.warning("食材名を入力してください。")
            
    st.divider()
    st.subheader("おうちにある食材")
    if st.session_state.inventory:
        for i, item in enumerate(st.session_state.inventory):
            c1, c2, c3 = st.columns([2, 3, 2])
            with c1: nc = st.text_input("カテゴリ", value=item['category'], key=f"c_{i}")
            with c2: nn = st.text_input("食材名", value=item['name'], key=f"n_{i}")
            with c3: nq = st.text_input("数量", value=item['quantity'], key=f"q_{i}")
            b_u, b_d = st.columns(2)
            with b_u:
                if st.button("💾 更新", key=f"up_{i}"):
                    st.session_state.inventory[i] = {"category": nc, "name": nn, "quantity": nq}
                    st.success("更新！"); st.rerun()
            with b_d:
                if st.button("🗑️ 削除", key=f"dl_{i}"):
                    st.session_state.inventory.pop(i); st.rerun()
            st.markdown("---")
    else: st.info("食材はありません。")

elif m == "⚙️ キッチン用品":
    st.header("⚙️ キッチン用品")
    ti = st.text_input("キッチン用品名", value="ヘルシオ")
    
    def get_ft(name):
        n = name.lower()
        if "ヘルシオ" in n: return "過熱水蒸気でノンフライ調理やジューシーな焼き物が得意です。"
        elif "バルミューダ" in n: return "外はサクッと中はもちもちのトーストが焼けます。"
        elif "圧力鍋" in n: return "根菜や塊肉も短時間で柔らかく仕上がります。"
        return "便利な調理器具です。"

    tfi = st.text_area("特徴・得意なこと", value=get_ft(ti))
    if st.button("💾 キッチン用品を登録する"):
        if ti:
            st.session_state.tools.append({"name": ti, "feature": tfi})
            st.success("登録しました！"); st.rerun()
        else: st.warning("名前を入力してください。")
            
    st.divider()
    st.subheader("おうちにあるキッチン用品")
    if st.session_state.tools:
        for i, tool in enumerate(st.session_state.tools):
            st.markdown(f"**🍳 {tool['name']}**\n{tool['feature']}")
            if st.button("🗑️ 削除", key=f"dt_{i}"):
                st.session_state.tools.pop(i); st.rerun()
            st.markdown("---")
    else: st.info("用品はありません。")

elif m == "🍲 なに食べよう？":
    st.header("🍲 なに食べよう？")
    so = st.selectbox("今日の気分を選んでね", ["おまかせ", "時短・簡単", "ヘルシー", "がっつりスタミナ", "ヘルシオでジューシーに", "自由に入力する"])
    cs = st.text_input("リクエストを入力") if so == "自由に入力する" else so
        
    if st.button("✨ 献立を考えてもらう！"):
        with st.spinner("うしさんが考えています..."):
            it = ", ".join([f"{x['name']} ({x['quantity']})" if x['quantity'].strip() else x['name'] for x in st.session_state.inventory])
            tt = ", ".join([f"{x['name']} ({x['feature']})" for x in st.session_state.tools])
            try:
                ak = st.secrets.get("GEMINI_API_KEY", "")
                if ak:
                    genai.configure(api_key=ak)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    res = model.generate_content(f"在庫: {it or 'なし'}\n用品: {tt or 'なし'}\nリクエスト: {cs}\n献立を1つ提案して。")
                    txt = res.text
                else:
                    txt = "**メニュー：トマトと豚肉のジューシー炒め**\n- 材料: トマト, 豚肉\n- 作り方: 炒めるだけ！"
                st.session_state.history.insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "style": cs, "content": txt})
                st.markdown("### 💡 提案された献立")
                st.markdown(txt)
            except Exception as e: st.error(f"エラー: {e}")

elif m == "📜 履歴":
    st.header("📜 履歴")
    if st.session_state.history:
        for idx, h in enumerate(st.session_state.history):
            with st.expander(f"🕒 {h['time']} - {h['style']}"):
                st.markdown(h['content'])
    else: st.info("履歴はまだありません。")

elif m == "⭐ お気に入り":
    st.header("⭐ お気に入りのレシピ")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"- 🍳 **{fav}**")
    else: st.info("お気に入りはありません。")
