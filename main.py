from openai import AzureOpenAI
import streamlit as st
import streamlit.components.v1 as components
import os  
import sys  # sysモジュールをインポート

# Azure OpenAI の API キーとエンドポイントを環境変数から取得
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
    st.rerun()  # ページをリフレッシュ

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
if st.session_state.input_temp:
    with st.chat_message("user"):
        st.markdown(st.session_state.input_temp)

    with st.chat_message("assistant"):
        stream = get_response(st.session_state.input_temp)
        response = st.write_stream(stream)
        add_history(response)

    # 入力をクリア
    st.session_state.input_temp = ""

# ユーザーの入力を受け取る関数
def handle_input():
    st.session_state.input_temp = st.session_state.user_input
    st.session_state.user_input = ""  # UIのリフレッシュ
    
    

# ユーザーの入力を受け取るテキスト入力フィールド
st.text_input(
    "What is up?",  # 入力フィールドのラベルとして表示されるテキスト。通常はユーザーに対して入力内容を示す。
    key="user_input",  # セッションステート内でこの入力フィールドの値を管理するための一意のキー。
    value="",  # 入力フィールドの初期値。ここでは空の文字列が設定されています。
    on_change=handle_input,  # 入力を送信したら自動クリア
    placeholder="Type your message...",  # 入力フィールドに表示されるプレースホルダーテキスト。ユーザーが入力を開始する前に表示されます。
    help="Enter your message and press Enter.",  # 入力フィールドの横に表示されるヘルプテキスト。ユーザーに入力方法を説明します。
    label_visibility="collapsed"  # 入力フィールドのラベルを非表示にするオプション。この場合、ラベル "What is up?" は表示されません。
)


# チャット履歴をリセットするボタン
if st.button("リセット"):
    reset_session_state()

# アプリケーション終了ボタン
if st.button("終了"):
    st.warning("アプリケーションを終了します。")
    sys.exit()


# 初期表示時にカーソルを設定するスクリプト
initial_focus_script = """
<script>
    setTimeout(function() {
        var inputBox = document.querySelector('input[data-baseweb="input"]');
        if (inputBox) {
            inputBox.focus();
        }
    }, 100);
</script>
"""
components.html(initial_focus_script, height=0, width=0)
