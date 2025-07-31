import streamlit as st
from QAbyUser_id import simp

st.title("Sample APP")

user_id = st.text_input("Enter your user id")
app_name = st.text_input("Enter the app name")

if st.button("Show Chat"):
    if user_id and app_name:
        response = simp(user_id,app_name)
        with open("session_chat_export.csv", "rb") as f:
            st.download_button(
                label="Download CSV",
                data=f,
                file_name="chat_export.csv",
                mime="text/csv"
            )
        for res in response:
            if res.get("type") == "human":
                st.header("Question")
                st.write(res.get("content"))
            elif res.get("type") == "ai":
                st.header("Answer")
                st.write(res.get("content"))
                if res.get("sql_query") is not None:
                    st.write(res.get("sql_query"))
                else:
                    intent = res.get("intent_handled")
                    st.write(intent.get("intent"))
    else:
        st.error("You should provide both user id and app name.")
