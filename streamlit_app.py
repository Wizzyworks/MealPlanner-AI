import streamlit as st
import requests
import json

st.set_page_config(page_title="Desi Meal Planner", page_icon="food", layout="centered")

st.title("My Meal Planner Agent")
st.markdown("### ₹400/week se luxury tak — Weight loss, Diabetes, Muscle gain, Mess life")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Bhai plan bana do..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon bhai..."):
            try:
                # 3 retries with delay (ADK cold start ke liye)
                for i in range(3):
                    resp = requests.post(
                        "http://localhost:8000/plan",
                        json={"message": prompt},
                        timeout=120
                    )
                    if resp.status_code == 200:
                        reply = resp.json().get("plan", "Done bhai!")
                        break
                    time.sleep(5)
                else:
                    reply = "Server thoda slow hai bhai, ek baar aur try kar"
            except:
                reply = "Backend off hai bhai – pehle terminal mein 'uvicorn app:app --reload' chala le"
        
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})