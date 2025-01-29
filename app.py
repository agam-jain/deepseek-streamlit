import streamlit as st
from openai import OpenAI
import re

st.set_page_config(
    page_title="Chat playground",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

remove = False
def processed_stream(stream):
    global remove
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta == '<think>':
            remove = True
        elif delta == '</think>':
            remove = False
        else:
            if not remove:
                yield chunk


def main():
    """
    The main function that runs the application.
    """

    st.title('🤖 DeepSeek R1 Chatbot')
    with st.sidebar:
        st.header("📚 User Guide")
        st.markdown("""
        ### How to Use
        1. **Start Chatting**: Type your message in the input box at the bottom of the chat
        2. **Continue Conversation**: The chatbot remembers your conversation, so you can ask follow-up questions
        3. **View History**: Scroll up to see your chat history
        
        ### Tips
        - Be specific with your questions
        - Ask follow-up questions for clarification
        - Use the reset button to start a fresh conversation
        
        ### Need Help?
        If you encounter any issues, try resetting the chat using the button below.
        """)

    url = st.secrets['OLLAMA_URL']
    client = OpenAI(
        base_url=url,
        api_key="ollama",  # required, but unused
    )

    selected_model = 'deepseek-r1:7b'
    message_container = st.container(height=400, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            st.session_state.messages.append(
                {"role": "user", "content": prompt})

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                # stream response
                response = st.write_stream(processed_stream(stream))
            st.session_state.messages.append(
                {"role": "assistant", "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")
    if st.button("Reset Chat"):
        st.session_state.messages = [
            ]
        st.rerun()




if __name__ == "__main__":
    main()