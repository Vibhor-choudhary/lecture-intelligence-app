import streamlit as st
import requests

st.set_page_config(page_title="Lecture Intelligence", layout="centered")

st.title("Lecture Intelligence App")
st.write("This is a placeholder Streamlit app. Replace app.py with your real application code.")

if st.button("Ping example.com"):
    try:
        r = requests.get("https://example.com", timeout=5)
        st.success(f"Ping succeeded: status {r.status_code}")
    except Exception as e:
        st.error(f"Ping failed: {e}")
