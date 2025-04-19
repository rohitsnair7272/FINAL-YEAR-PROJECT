import streamlit as st
import hashlib
from mongo_utils import shopkeepers_col
import re

# Set page layout
st.set_page_config(page_title="Login", layout="centered")

# Completely hide the sidebar and its space
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], .css-1d391kg {
            display: none !important;
        }
        .block-container {
            padding-left: 1rem !important;
        }
        header[data-testid="stHeader"] {
            padding-left: 1rem !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Session management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

st.title("🔐 Shopkeeper Login")

# If already logged in
if st.session_state.logged_in:
    st.success(f"👋 Welcome, {st.session_state.username}")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

else:
    email = st.text_input("📧 Email")
    password = st.text_input("🔐 Password", type="password")

    if st.button("Login"):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.warning("Please enter a valid email.")
        else:
            user = shopkeepers_col.find_one({})
            if user and user["email"] == email and user["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = email
                st.success("✅ Login successful!")
                st.switch_page("pages/dashboard.py")
            else:
                st.error("❌ Invalid credentials")

# Links only if user not registered yet
user_exists = shopkeepers_col.find_one({})
if not user_exists:
    st.page_link("pages/register.py", label="🆕 New user? Register here")

st.page_link("pages/forgot_password.py", label="🔑 Forgot Password?")
