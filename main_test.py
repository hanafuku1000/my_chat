from openai import AzureOpenAI
import streamlit as st
import os  
from dotenv import load_dotenv
import sys  # sysモジュールをインポート

# .envファイルを読み込む
load_dotenv()

# Azure OpenAI の API キーとエンドポイントを環境変数ファイルから取得
azure_endpoint = os.getenv("CHATBOT_AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("CHATBOT_AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("CHATBOT_AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("CHATBOT_AZURE_OPENAI_API_VERSION")

# Azure OpenAI クライアントを作成
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

# セッションステートを初期化する関数
def reset_session_state():
    st.session_state.chat_history = []
    st.session_state.input_temp = ""
    st.session_state.user_input = ""

# Streamlit のセッションステートを使ってチャットの履歴を管理
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "input_temp" not in st.session_state:
    st.session_state.input_temp = ""

# ユーザーからのメッセージに対して応答を生成する関数
def get_response(prompt: str = ""):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    system_message = [{"role": "system", "content": "You are a helpful assistant."}]
    chat_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=system_message + chat_messages,
        stream=True
    )
    return response

# チャット履歴にメッセージを追加する関数
def add_history(response):
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Streamlit アプリケーションの UI を構築
st.title("ChatGPT-like clone")

# チャット履歴の表示
with st.container():
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

# 最新の発言と応答を表示
if "input_temp" in st.session_state and st.session_state.input_temp:
    with st.chat_message("user"):
        st.markdown(st.session_state.input_temp)

    with st.chat_message("assistant"):
        stream = get_response(st.session_state.input_temp)
        response = st.write_stream(stream)
        add_history(response)

    # 入力をクリア
    st.session_state.input_temp = ""

# ユーザーの入力を受け取る
user_input = st.text_input("What is up?", key="user_input", value="", on_change=lambda: st.session_state.update({"input_temp": st.session_state.user_input, "user_input": ""}))

# カーソルをインプットボックスに設定するJavaScriptを埋め込む
focus_script = """
<script>
    setTimeout(function() {
        document.getElementById('user_input').focus();
    }, 100);
</script>
"""
st.components.v1.html(focus_script, height=0, width=0)

# チャット履歴をリセットするボタン
if st.button("リセット"):
    st.session_state.chat_history = []
    st.session_state.input_temp = ""
    # ページをリロードするためのJavaScript
    reload_script = """
    <script>
        window.location.reload();
    </script>
    """
    st.components.v1.html(reload_script, height=0, width=0)

# アプリケーション終了ボタン
if st.button("終了"):
    st.warning("アプリケーションを終了します。")
    sys.exit()



