from openai import OpenAI
import streamlit as st
import hmac # 비밀번호 비교를 위해 hmac 모듈 사용

# Streamlit 앱 제목
st.title("연수 챗봇")

# --- 비밀번호 인증 부분 시작 ---
def check_password():
    """
    사용자가 올바른 비밀번호를 입력했는지 확인합니다.
    """
    def password_entered():
        """
        비밀번호 입력 시 호출되는 콜백 함수입니다.
        입력된 비밀번호와 저장된 비밀번호를 비교합니다.
        """
        # st.secrets에서 'password' 키로 비밀번호를 가져옵니다.
        # secrets.toml에 설정된 'CHATBOT_PASSWORD'를 사용합니다.
        if hmac.compare_digest(st.session_state["password"], st.secrets["CHATBOT_PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 비밀번호는 세션에 저장하지 않습니다.
        else:
            st.session_state["password_correct"] = False

    if not st.session_state.get("password_correct", False):
        # 비밀번호가 올바르지 않으면 입력 폼을 보여줍니다.
        with st.form("Login"):
            st.text_input("비밀번호를 입력하세요:", type="password", key="password")
            st.form_submit_button("로그인", on_click=password_entered)

        if "password_correct" in st.session_state:
            st.error("❌ 비밀번호가 틀렸습니다.")
        return False
    return True

if check_password():
    # --- 비밀번호 인증 부분 끝 ---

    client = OpenAI()

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4.1" # GPT-4.1은 존재하지 않는 모델명입니다. 아마도 "gpt-4"를 의도하신 것 같습니다.

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("무엇을 도와드릴까요?"): # 한글로 변경
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
