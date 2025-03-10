from openai import AzureOpenAI
import streamlit as st
import os  
from dotenv import load_dotenv
import sys

# .envファイルを読み込む
load_dotenv()
  
# Azure OpenAI の API キーとエンドポイントを環境変数(setを使い、パワーシェルで直書き込んで）から取得  
#azure_endpoint = os.environ["CHATBOT_AZURE_OPENAI_ENDPOINT"] 
#api_key = os.environ["CHATBOT_AZURE_OPENAI_API_KEY"] 
#deployment_name = "take-gpt-4o-mini" # 先ほど作成したモデルのデプロイ名に置き換えてください
#api_version = "2025-01-01-preview" # 先ほど作成したモデルの API バージョンに置き換えてください


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

# チャット履歴を保持するリスト＿１ ＝＝＝＝＝＝＝＝＝ 
#このコードは、チャット履歴を保持するためのシンプルなリストを定義しています。
#このリストはプログラムが実行されている間だけ保持され、プログラムが終了すると消えてしまいます。
#chat_history = [  
#    {"role": "system", "content": "You are a helpful assistant."}  
#]

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝  
# チャット履歴を保持するリスト＿２ 
# Streamlit のセッションステートを使ってチャットの履歴を管理
#ユーザーがページを更新しても（ブラウザを閉じるまで）履歴が保持される
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝ 

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ユーザーからのメッセージに対して応答を生成する関数_１＝＝＝＝＝＝＝＝＝  

#def get_response(message):  
#    # ユーザーのメッセージを履歴に追加  
#    chat_history.append({"role": "user", "content": message})  
#    # ChatGPT からの応答を取得  
#    response = client.chat.completions.create(  
#        model=deployment_name, 
#        messages=chat_history  
#    ) 
#    # 応答を履歴に追加  
#    assistant_message = response.choices[0].message.content.strip()  
#    chat_history.append({"role": "assistant", "content": assistant_message})
#    return assistant_message  
    

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝ 
# ユーザーからのメッセージに対して応答を生成する関数_２
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝ 

def get_response(prompt: str = ""):  
    # ユーザーのメッセージを履歴に追加 
    st.session_state.chat_history.append({"role": "user", "content": prompt})  
    # モデルに送信するメッセージを作成, セキュリティの観点から chat_history オブジェクトは直接渡さない
    system_message = [{"role": "system", "content": "You are a helpful assistant."}]
    chat_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history
    ]
    
    response = client.chat.completions.create(  
        model=deployment_name, 
        messages=system_message + chat_messages,
        stream=True
    )
    return response


# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# チャット履歴にメッセージを追加する関数
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
def add_history(response):
    st.session_state.chat_history.append({"role": "assistant", "content": response})   

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# アプリケーション終了関数
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
def shutdown_app():
    st.warning("アプリケーションを終了します。")
    sys.exit()

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# Streamlit アプリケーションの UI を構築
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# Streamlit アプリケーションの UI を構築
st.title("ChatGPT-like clone")

# チャット履歴の表示 
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# ユーザーの入力を受け取る  
#if prompt := st.chat_input("What is up?"):
if prompt := st.text_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        stream = get_response(prompt)
        response = st.write_stream(stream)
        add_history(response)


# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# チャット履歴をリセットするボタン
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
if st.button("リセット"):
    st.session_state.chat_history = []

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# アプリケーション終了ボタン
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
if st.button("終了"):
    shutdown_app()


#if __name__ == "__main__":  #Pythonスクリプトが(コマンドラインやターミナルから)直接実行された場合のみ以下のコードを実行
#    while True:  # 無限ループ：ユーザーが "exit" または "quit" と入力するまで続ける
#        user_input = input("You: ")  
#        if user_input.lower() in ["exit", "quit"]:  
#            break  
#        print("ChatGPT:", get_response(user_input))   
